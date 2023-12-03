from dataclasses import dataclass


class TourCharacter:
    char_id: int

    def __init__(self, char_id):
        self.char_id = char_id


class TourPlayer:
    entrant_id: int
    name: str

    def __init__(self, entrant_id, name):
        self.entrant_id, self.name = entrant_id, name


class CharacterSelection:
    character: TourCharacter
    player: TourPlayer

    def __init__(self, character, player):
        self.character, self.player = character, player


class TourGame:
    """
    Class used to represent a game in a tournament

    It is assumed that all games have exactly two teams.

    Attributes
    ----------
    """
    winner: TourPlayer
    game_num: int
    character_selections: list[CharacterSelection]
    players: list[TourPlayer]

    @classmethod
    def empty_tour_game(cls, players, game_num):
        tour_game = cls()
        tour_game.players = players
        tour_game.game_num = game_num
        return tour_game

    def is_completed(self):
        return self.winner is not None


class TourSet:
    games: list[TourGame]
    req_wins: int
    winner_id: int | None
    set_id: int
    players: list[TourPlayer]
    title: str

    @classmethod
    def empty_tour_set(cls, req_wins, set_id, players, title):
        tour_set = cls()
        tour_set.req_wins, tour_set.set_id, tour_set.players, tour_set.title = req_wins, set_id, players, title
        tour_set.games = [None for _ in (req_wins * 2 - 1)]
        return tour_set

    def is_completed(self):
        return self.winner_id is not None
