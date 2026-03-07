import os
import time

from gql import Client, gql
from gql.graphql_request import GraphQLRequest
from gql.transport.requests import RequestsHTTPTransport

STARTGG_API_KEY = os.environ.get("STARTGG_API_KEY")

SET_VOD_MUTATION = gql("""
mutation ($setId: ID!, $vodUrl: String) {
  updateVodUrl(setId: $setId, vodUrl: $vodUrl) {
    id
  }
}
""")

GET_USER_ID_FROM_SLUG = gql("""
query Tags($slug: String) {
  user(slug: $slug) {
    id,
  }
}
""")

GET_EVENTS_BY_USER_ID = gql("""
query Tags($userId: ID, $page: Int, $perPage: Int, $gameId: [ID]) {
  user(id: $userId) {
    events(query: {
      page: $page,
      perPage: $perPage,
      filter: {
        videogameId: $gameId
      }
    }) {
      pageInfo {
        totalPages
      },
      nodes {
        userEntrant(userId: $userId) {
          participants {
            gamerTag,
            user {
              id
            }
          }
        }
      }
    }
  }
}
""")

def get_set_vod_request(set_id: str, video_url: str):
    params = {"setId": set_id, "vodUrl": video_url}
    return GraphQLRequest(request=SET_VOD_MUTATION, variable_values=params)

def batch_set_vods(client: Client, requests: list[GraphQLRequest]):
    client.execute_batch(requests)

def get_user_id(client, slug: str):
    params = {"slug": slug}
    request = GraphQLRequest(request=GET_USER_ID_FROM_SLUG, variable_values=params)
    response = client.execute(request)
    return response["user"]["id"]

def get_user_tags(client, user_id: int, game_id: int):
    current_page = 1
    num_pages = 2

    # 270 was found to be the largest possible value where complexity < 1000
    # This could technically be increased by splitting the totalPages request into a separate query,
    # but I'm assuming, on average, most players will have < 3 pages of results
    results_per_page = 270

    tags = set()
    while current_page <= num_pages:
        params = {
            "userId": user_id,
            "page": current_page,
            "perPage": results_per_page,
            "gameId": game_id,
        }
        current_page += 1
        request = GraphQLRequest(request=GET_EVENTS_BY_USER_ID, variable_values=params)
        response = client.execute(request)
        for event in response["user"]["events"]["nodes"]:
            for participant in event["userEntrant"]["participants"]:
                if not participant.get("user"):
                    continue
                if participant["user"]["id"] == user_id:
                    tags.add(participant["gamerTag"])
        num_pages = response["user"]["events"]["pageInfo"]["totalPages"]
    return tags

def get_client(api_key=None):
    api_key = api_key or STARTGG_API_KEY
    transport = RequestsHTTPTransport(
        url="https://api.start.gg/gql/alpha",
        headers={
            "Authorization": f"Bearer {api_key}",
        },
    )
    return Client(transport=transport)
