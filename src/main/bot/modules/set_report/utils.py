from commons.model.tournament_objects import TourGame, TourSet, TourPlayer
from utils.graphql_utils import mutate_request, query_request

REPORT_SET_GQL_MUTATION = """
mutation reportSet($setId: ID!, $winnerId: ID!, $gameData: [BracketSetGameDataInput]) {
    reportBracketSet(setId: $setId, winnerId: $winnerId, gameData: $gameData) {
    id
    state
    }
}"""

GET_START_ID_FROM_DISCORD_ID_QUERY = """
    query fromDiscordIdGetUserId($slug: String, $pquery: ParticipantPaginationQuery!) {
        tournament(slug: $slug) {
            participants (query: $pquery) {
                nodes {
                    gamerTag
                    player {
                        id
                    }
                    user {
                        id
                        authorizations(types: [DISCORD]) {
                            id
                            externalId
                            externalUsername
                        }
                    }
                }
            }
        }
    }
"""

GET_ALL_SETS_WITH_START_ID_QUERY = """
query getSetsFromEvent($slug: String, $eventFilters : EventFilter, $setFilters : SetFilters) {
    tournament(slug: $slug) {
        events (filter: $eventFilters) {
            sets (perPage: 500, filters: $setFilters) {
                nodes {
                    id
                    fullRoundText
                    slots {
                        entrant {
                        name
                        id
                        }
                    }
                }
            }
        }
    }
}"""


def format_game(tour_game: TourGame, game_number: int) -> dict:
    d = {"winnerId": tour_game.winner.entrant_id, "gameNum": game_number, "selections": [{
        "entrantId": character_selection.player.entrant_id,
        "characterId": character_selection.character.char_id,
    } for character_selection in tour_game.character_selections]}

    return d


def response_set_to_game_set(r_set: dict, first_to_num: int) -> TourSet:
    req_wins = first_to_num
    set_id = r_set['id']
    players = [TourPlayer(slot['entrant']['id'], slot['entrant']['name']) for slot in r_set['slots']]
    title = r_set["fullRoundText"]
    return TourSet.empty_tour_set(req_wins, set_id, players, title)


def from_discord_id_get_player_id(tour_slug: str, discord_id: int):
    variables = {
        "slug": tour_slug,
        "pquery": {
            "page": 1,
            "perPage": 500
        }
    }

    data = query_request(GET_START_ID_FROM_DISCORD_ID_QUERY, variables)
    participants = data['tournament']['participants']['nodes']
    for participant in participants:
        if participant['user']['authorizations'] is not None:
            if participant['user']['authorizations'][0]['externalId'] == str(discord_id):
                return participant['player']['id']

    return None


def report_set_to_gql(tour_set: TourSet) -> None:
    assert tour_set.is_completed()

    set_id = tour_set.set_id
    winner_id = tour_set.winner_id

    game_data: list[dict] = [format_game(tour_game, i + 1) for tour_game, i in enumerate(tour_set.games)]

    variables = {
        "setId": set_id,
        "winnerId": winner_id,
        "gameData": game_data,
    }

    mutate_request(REPORT_SET_GQL_MUTATION, variables)


def get_called_sets_from_tour_slug(tour_slug: str, discord_id: int, req_wins: int) -> list[TourSet]:
    player_id = from_discord_id_get_player_id(tour_slug, discord_id)
    variables = {
        "slug": tour_slug,
        "eventFilters": {},
        "setFilters": {
            "playerIds": player_id,
            "state": [2]
        }
    }

    response = query_request(GET_ALL_SETS_WITH_START_ID_QUERY, variables)
    response_sets = []

    for event in response['tournament']['events']:
        response_sets.extend(event['sets']['nodes'])

    if not response_sets:
        return []

    return [response_set_to_game_set(r_set, req_wins) for r_set in response_sets]
