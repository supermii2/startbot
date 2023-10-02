from src.data.character_data import LIST_OF_CHARS
from src.game_objects.player import Player


class Game:
    def __init__(self, entrants: list[Player] = None, winner: int = None, characters: list[list[str]] = None):
        self.entrants, self.winner, self.characters = entrants, winner, characters

    def __str__(self) -> str:
        s = LIST_OF_CHARS[self.characters[0]]["emoji"]
        s += " **W** - L " if self.winner == 1 else " L - **W** " if self.winner == 2 else " 0 - 0"
        s += LIST_OF_CHARS[self.characters[1]]["emoji"]
        return s
