from util_gql_handler import *

def getSetsFromEvent(tournamentSlug, eventName):
    gqlString = """
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
                            }
                        }
                    }
                }
            }
        }
    }
    """

    variables = {
        "slug" : tournamentSlug,
        "eventFilters" : {
            "slug" : eventName
        }
    }

    data = makeGqlRequest(gqlString, variables)
    
    return data['tournament']['events'][0]['sets']['nodes']

def toStringSetSingles(set):
    return set["fullRoundText"] + " | " + set["slots"][0]["entrant"]["name"] + " vs " + set["slots"][1]["entrant"]["name"]

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
        "slug" : tournamentSlug,
        "pquery" : {
            "page" : 1,
            "perPage" : 500
        }
    }   

    data = makeGqlRequest(gqlString, variables)
    
    participants = data['tournament']['participants']['nodes']
    for participant in participants:
        if participant['user']['authorizations'] != None:
            if participant['user']['authorizations'][0]['externalId'] == str(discordId):
                return participant['player']['id']

    return None


def fromPlayerIdGetNextSet(tournamentSlug, playerId):
    if playerId == None:
        return None
    VALID_STATES = [1,2,3,4,5,6,7] # Actual is [3]
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
        "slug" : tournamentSlug,
        "setFilters" : {
            "playerIds" : [playerId],
            "state" : VALID_STATES
        }
    }

    data = makeGqlRequest(gqlString, variables)
    events = data["tournament"]["events"]
    return [item for sublist in map(lambda x: x['sets']['nodes'], events) for item in sublist] 

def getNextSetFromDiscord(discord_id, tournament):
    return fromPlayerIdGetNextSet(tournament, fromDiscordIdGetPlayerId(tournament, discord_id))

def getAllUsersFromEvent(tournament):
    gqlString="""
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
        "slug" : tournament,
        "pquery" : {
            "page" : 1,
            "perPage" : 500
            }
        }
    
    data = makeGqlRequest(gqlString, variables)
    participants = data['tournament']['participants']['nodes']
    participant_list = list(map(lambda x: (x['gamerTag'], x['events']), participants))

    return participant_list