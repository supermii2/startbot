from src.api_handler.gql_handler import make_gql_request
from src.game_objects.gameset import GameSet


def getSetsFromEvent(tournament_slug: str, event_name: str) -> list[GameSet]:
    gql_string = """
    query getSetsFromEvent($slug: String, $eventFilters : EventFilter) {
        tournament(slug: $slug) {
            events (filter: $eventFilters) {
                sets (perPage: 500) {
                    nodes {
                        fullRoundText
                        identifier
                        state
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
    variables = {
        "slug": tournament_slug,
        "eventFilters": {
            "slug": event_name
        }
    }

    response = make_gql_request(gql_string, variables)
    response_sets = response['tournament']['events'][0]['sets']['nodes']

    def response_set_to_game_set(response_set: dict) -> GameSet:
        entrants = response_sets["slots"]

    sets = []
    for set in response_sets:
        sets.append()

    return sets




def findAllCalledSets(tournamentSlug, eventName):
    CALLED = 3
    return list(filter(lambda x: x['state'] == CALLED, getSetsFromEvent(tournamentSlug, eventName)))


def fromDiscordIdGetPlayerId(tournamentSlug, discordId):
    gqlString = """
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
        "slug": tournamentSlug,
        "pquery": {
            "page": 1,
            "perPage": 500
        }
    }

    data = make_gql_request(gqlString, variables)

    participants = data['tournament']['participants']['nodes']
    for participant in participants:
        if participant['user']['authorizations'] != None:
            if participant['user']['authorizations'][0]['externalId'] == str(discordId):
                return participant['player']['id']

    return None


def fromPlayerIdGetNextSet(tournamentSlug, playerId):
    if playerId == None:
        return None
    VALID_STATES = [1, 2, 3, 4, 5, 6, 7]  # Actual is [3]
    gqlString = """
    query fromPlayerIdGetNextSet($slug: String, $setFilters : SetFilters) {
        tournament(slug: $slug) {
            events {
                sets (perPage: 500, filters: $setFilters) {
                    nodes {
                        fullRoundText
                        identifier
                        totalGames
                        slots {
                            entrant {
                                id
                                name
                            }
                        }
                    }
                }
            }
        }
    }
    """
    variables = {
        "slug": tournamentSlug,
        "setFilters": {
            "playerIds": [playerId],
            "state": VALID_STATES
        }
    }

    data = make_gql_request(gqlString, variables)
    events = data["tournament"]["events"]
    return [item for sublist in map(lambda x: x['sets']['nodes'], events) for item in sublist]


def getNextSetFromDiscord(discord_id, tournament):
    return fromPlayerIdGetNextSet(tournament, fromDiscordIdGetPlayerId(tournament, discord_id))


def getAllUsersFromEvent(tournament):
    gqlString = """
    query getUsersFromEvent($slug: String, $pquery: ParticipantPaginationQuery!) {
        tournament(slug: $slug) {
            participants(query: $pquery) {
                nodes {
                    id
                    gamerTag
                    events {
                        name
                    }
                }
            }
        }
    }
    """
    variables = {
        "slug": tournament,
        "pquery": {
            "page": 1,
            "perPage": 500
        }
    }

    data = make_gql_request(gqlString, variables)
    participants = data['tournament']['participants']['nodes']
    participant_list = list(map(lambda x: (x['gamerTag'], x['events']), participants))

    return participant_list
