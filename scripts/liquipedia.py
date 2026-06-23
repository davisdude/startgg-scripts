import argparse
import datetime

import requests

STAGE_ID_TO_NAME = {
    1: "Mushroom Kingdom",
    2: "Peach's Castle",
    3: "Rainbow Cruise",
    4: "Yoshi's Island",
    5: "Yoshi's Story",
    6: "Kongo Jungle",
    7: "Jungle Japes",
    8: "Great Bay",
    9: "Temple",
    10: "Brinstar",
    11: "Fountain of Dreams",
    12: "Green Greens",
    13: "Corneria",
    14: "Venom",
    15: "Pokémon Stadium",
    16: "Mute City",
    17: "Onett",
    18: "Icicle Mountain",
    19: "Battlefield",
    20: "Final Destination",
    21: "Mushroom Kingdom II",
    22: "Yoshi's Island N64",
    23: "Kongo Jungle N64",
    24: "Brinstar Depths",
    25: "Dream Land",
    26: "Poké Floats",
    27: "Big Blue",
    28: "Fourside",
    29: "Flat Zone",
}

CHARACTER_ID_TO_NAME = {
    1: "bowser",
    2: "cf",
    3: "dk",
    4: "doc",
    5: "falco",
    6: "fox",
    7: "ganon",
    8: "ics",
    9: "puff",
    10: "kirby",
    11: "link",
    12: "luigi",
    13: "mario",
    14: "marth",
    15: "mewtwo",
    16: "gw",
    17: "ness",
    18: "peach",
    19: "pichu",
    20: "pika",
    21: "roy",
    22: "samus",
    23: "sheik",
    24: "yoshi",
    25: "yl",
    26: "zelda",
    # TODO: Shielda
}

ROUND_COUNTS = {}


def get_event_data(event_id: int):
    url = f"https://api.start.gg/phase_group/{event_id}?expand[]=sets&expand[]=entrants&expand[]=seeds&bustCache=false"
    response = requests.get(url)
    return response.json()["entities"]


def get_participant_id_to_gamer_tag(event_data):
    return {
        str(participant_id): gamer_tag
        for entrant in event_data["entrants"]
        for participant_id in entrant["participantIds"]
        if (player_id := entrant["playerIds"].get(str(participant_id))) is not None
        if (player_mutation := entrant["mutations"]["players"].get(str(player_id))) is not None
        if (gamer_tag := player_mutation.get("gamerTag")) is not None
    }


def get_stage_name(game_data, frozen_stages=[]):
    stage_id = game_data["stageId"]
    if stage_id is None:
        return None
    stage_name = STAGE_ID_TO_NAME[stage_id]
    return f"Frozen {stage_name}" if stage_name in frozen_stages else stage_name


def get_winner_value(entrant_1_id, entrant_2_id, winner_id):
    return 1 if (winner_id == entrant_1_id) else 2


def get_round_prefix(set_data):
    round_val = set_data["round"]
    is_losers = round_val < 0
    round_abs = abs(round_val)
    if round_val not in ROUND_COUNTS:
        ROUND_COUNTS[round_val] = 0
    ROUND_COUNTS[round_val] += 1
    return f"{"l" if is_losers else "r"}{round_abs}m{ROUND_COUNTS[round_val]}"


# TODO: Round robin pools
# TODO: Separate WF/GF/LSF/LF
# TODO: GF reset
# TODO: Pools reporting (W/L/out)
# TODO: Doubles
# TODO: Ideally take like slug and top 8/16/32/64/etc and make things formatted better
# TODO: Filter out impossible set counts from game data
# CURL API doesn't report per-game characters, so puts all chars for every game
def get_sets(event_data, frozen_stages=[], default_flag="us"):
    participant_id_to_gamer_tag = get_participant_id_to_gamer_tag(event_data)

    for set_data in event_data["sets"]:
        set_data_strs = []

        vod_url = set_data["vodUrl"]

        entrant_1_tags = [
            participant_id_to_gamer_tag[part_id]
            for part_id in set_data["slots"][0]["participantIds"]
        ]
        entrant_2_tags = [
            participant_id_to_gamer_tag[part_id]
            for part_id in set_data["slots"][1]["participantIds"]
        ]
        if not entrant_1_tags or not entrant_2_tags:
            continue

        round_prefix = get_round_prefix(set_data)
        entrant_1_score = set_data["entrant1Score"] or 0
        entrant_2_score = set_data["entrant2Score"] or 0
        entrant_1_id = set_data["slots"][0]["entrantId"]
        entrant_2_id = set_data["slots"][1]["entrantId"]
        winner_id = set_data["winnerId"]
        winner_value = get_winner_value(entrant_1_id, entrant_2_id, winner_id)
        if entrant_1_score < 0 or entrant_2_score < 0:
            entrant_1_score = "{{win}}" if winner_value == 1 else "DQ"
            entrant_2_score = "{{win}}" if winner_value == 2 else "DQ"

        set_data_strs.extend([
            (
                f"|{round_prefix}p1={(",").join(entrant_1_tags)} "
                f"|{round_prefix}p1flag={default_flag} "
                f"|{round_prefix}p1score={entrant_1_score}"
            ),
            (
                f"|{round_prefix}p2={(",").join(entrant_2_tags)} "
                f"|{round_prefix}p2flag={default_flag} "
                f"|{round_prefix}p2score={entrant_2_score}"
            ),
            f"|{round_prefix}win={winner_value}",
        ])

        entrant_1_chars = [
            CHARACTER_ID_TO_NAME[char_id]
            for char_id in set_data.get("entrant1CharacterIds", [])
        ]
        entrant_2_chars = [
            CHARACTER_ID_TO_NAME[char_id]
            for char_id in set_data.get("entrant2CharacterIds", [])
        ]
        for i, game_data in enumerate(set_data["games"], start=1):
            game_data_strs = []
            stage_name = get_stage_name(game_data, frozen_stages)
            entrant_1_stocks = (game_data.get("entrant1P1Stocks", 0) or 0) % 100
            entrant_2_stocks = (game_data.get("entrant2P1Stocks", 0) or 0) % 100
            winner_value = get_winner_value(entrant_1_id, entrant_2_id, game_data["winnerId"])

            if entrant_1_chars:
                game_data_strs.append(f"|{round_prefix}p1char{i}={(",").join(entrant_1_chars)}")
            if entrant_2_chars:
                game_data_strs.append(f"|{round_prefix}p2char{i}={(",").join(entrant_2_chars)}")
            if (entrant_1_stocks != 0) or (entrant_2_stocks != 0):
                game_data_strs.extend([
                    f"|{round_prefix}p1stock{i}={entrant_1_stocks}",
                    f"|{round_prefix}p2stock{i}={entrant_2_stocks}",
                ])
            game_data_strs.append(f"|{round_prefix}win{i}={winner_value}")
            if stage_name:
                game_data_strs.append(f"|{round_prefix}stage{i}={stage_name}")
            game_data_str = (" ").join(game_data_strs)
            set_data_strs.append(game_data_str)

        if vod_url:
            # TODO: Use different timestamp - this updates when set data is updated
            start_time = set_data["completedAt"]
            dt = datetime.datetime.fromtimestamp(start_time)
            # dt.day strips to avoid %d's 0 in a cross-platform way
            set_data_strs.append(f"|{round_prefix}date={dt:%B} {dt.day}, {dt.year}")
            set_data_strs.append(f"|{round_prefix}details={{{{BracketMatchDetails|reddit=|comment=|vod={vod_url}|interview=}}}}")

        print(("\n").join(set_data_strs))
        print("")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("event_id", type=int)
    parser.add_argument("--frozen-stages", type=str, nargs="+", default=[])
    parser.add_argument("--default-flag", type=str, default="us")
    args = parser.parse_args()

    event_data = get_event_data(args.event_id)
    get_sets(event_data, args.frozen_stages, args.default_flag)
