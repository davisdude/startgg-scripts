# TODO: Look into public GQL
# https://www.start.gg/api/-/gql-public?operationName=UserResults&variables={%22publicCache%22:false,%22userId%22:407249,%22perPage%22:10,%22filter%22:{}}&extensions={%22persistedQuery%22:{%22version%22:1,%22sha256Hash%22:%22c99d6f6ee61cd8d74e3ee3601dd723de190d2ff1c6091e48c9feba164c805845%22}}

import argparse
import requests

import startgg_gql

def get_aliases(slugs: list[str], api_key: str, game_id: int):
    client = startgg_gql.get_client(api_key)
    for slug in slugs:
        user_id = startgg_gql.get_user_id(client, slug)
        tags = startgg_gql.get_user_tags(client, user_id, game_id)
        print(f"{slug}: {tags = }")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("slug", type=str, nargs="+")
    parser.add_argument("--api-key", type=str, default=None)
    parser.add_argument("--game-id", type=int, default=1)
    args = parser.parse_args()

    get_aliases(args.slug, args.api_key, args.game_id)
