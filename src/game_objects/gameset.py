from src.game_objects.game import Game
from src.game_objects.player import Player


class GameSet:
    def __init__(self, round_name: str = "", state: int = None, entrants: list[Player] = None, games: list[Game] = None,
                 winner: int = None):
        self.round_name, self.state, self.entrants, self.games, self.winner = round_name, state, entrants, games, winner

        if self.entrants is None:
            self.entrants = []

        if self.games is None:
            self.games = []

    def to_string_singles(self) -> str:
        return f'{self.round_name} | {self.entrants[0]} vs {self.entrants[1]}'

    def print_set(self) -> str:
        s = f"{self.round_name}\n"
        for game in self.games:
            s = f"{game.__str__()}\n"
        return s
