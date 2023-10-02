from enum import Enum

class Player:
    def __init__(self, name, id=None):
        self.name, self.id = name, id

class GameSet:
    class Game:
        def __init__(self, entrants:list[Player] = None, winner: int=None, characters: list[list[str]]=None):
            self.entrants, self.winner, self.characters = entrants, winner, characters

    def __init__(self, entrants: list[Player]=[], winner: int=None, games: list[Game]=[]):
        self.entrants, self.winner, self.games = entrants, winner, games

