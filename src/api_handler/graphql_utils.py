from src.data.character_data import LIST_OF_CHARS
from src.game_objects.game import Game
from src.game_objects.gameset import GameSet
from src.game_objects.entrant import Entrant
from src.utils.gql_handler import make_gql_request


def fromDiscordIdGetPlayerId(tour_slug, discord_id):
    gql_string = """
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
    variables = {
        "slug": tour_slug,
        "pquery": {
            "page": 1,
            "perPage": 500
        }
    }

    data = make_gql_request(gql_string, variables)

    participants = data['tournament']['participants']['nodes']
    for participant in participants:
        if participant['user']['authorizations'] is not None:
            if participant['user']['authorizations'][0]['externalId'] == str(discord_id):
                return participant['player']['id']

    return None


def get_called_sets_from_tour_slug(tournament_slug: str, discord_id: int) -> dict:
    gql_string = """
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
    }
    """
    player_id = fromDiscordIdGetPlayerId(tournament_slug, discord_id)
    variables = {
        "slug": tournament_slug,
        "eventFilters": {},
        "setFilters": {
            "playerIds": player_id,
            "state": [2]
        }
    }

    response = make_gql_request(gql_string, variables)
    print(response)
    response_sets = []

    for event in response['tournament']['events']:
        response_sets.extend(event['sets']['nodes'])

    def response_set_to_game_set(r_set: dict) -> GameSet:
        entrants: list[Entrant] = list(map(lambda slot: Entrant(name=slot['entrant']['name'],
                                                                userid=slot['entrant']['id']), r_set["slots"]))
        return GameSet(round_name=r_set["fullRoundText"], entrants=entrants, set_id=r_set['id'])

    sets = {}
    for response_set in response_sets:
        gs: GameSet = response_set_to_game_set(response_set)
        sets[gs.set_id] = gs

    return sets


def report_set(set_to_report: GameSet = None) -> None:
    gql_string = """
    mutation reportSet($setId: ID!, $winnerId: ID!, $gameData: [BracketSetGameDataInput]) {
      reportBracketSet(setId: $setId, winnerId: $winnerId, gameData: $gameData) {
        id
        state
      }
    }
    """
    reformatted_games = []
    gc = 1
    for game in set_to_report.games:
        reformatted_games.append({
            "winnerId": game.winner.id,
            "gameNum": gc,
            "selections": [{
                "entrantId": game.entrants[0].id,
                "characterId": LIST_OF_CHARS[game.characters[0]]['id']
            }, {
                "entrantId": game.entrants[1].id,
                "characterId": LIST_OF_CHARS[game.characters[1]]['id']
            }]
        })
        gc += 1
    variables = {
        "setId": set_to_report.set_id,
        "winnerId": set_to_report.winner,
        "gameData": reformatted_games
    }
    make_gql_request(gql_string, variables, is_mutate=True)
