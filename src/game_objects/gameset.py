from src.game_objects.game import Game
from src.game_objects.entrant import Entrant


class GameSet:
    def __init__(self, round_name: str = "", state: int = None, entrants: list[Entrant] = None, games: list[Game] = None,
                 winner: int = None, set_id: int = None):
        self.round_name, self.state, self.entrants, self.games, self.winner = round_name, state, entrants, games, winner
        self.set_id = set_id
        if self.entrants is None:
            self.entrants = []

        if self.games is None:
            self.games = []

    def __str__(self) -> str:
        return f'{self.round_name} | {self.entrants[0]} vs {self.entrants[1]}'

    def print_full_set(self) -> str:
        s = f"{self.round_name}\n"
        for game in self.games:
            s = f"{game.__str__()}\n"
        return s
