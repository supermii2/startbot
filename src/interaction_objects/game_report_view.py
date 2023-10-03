import discord

from src.api_handler.graphql_utils import report_set
from src.game_objects.gameset import GameSet
from src.game_objects.entrant import Entrant
from src.interaction_objects.game_reporter.game_reporter_row import GameRow


class GameReportView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, size: int = 3, title: str = "", entrants: list[Entrant] = None,
                 set_id=None):
        self.interaction, self.size, self.title, self.entrants = interaction, size, title, entrants
        self.isP1Win = None
        self.set_id = set_id
        self.game_rows = [GameRow(self, 0, self.entrants)]
        super().__init__(timeout=None)
        self.update_view()

    def update_view(self):
        if len(self.children) != 0:
            self.clear_items()
        for game_row in self.game_rows:
            game_row.update_view_row()

    def check_win(self) -> bool:
        p1wins, p2wins = 0, 0
        for game_row in self.game_rows:
            if game_row.isP1Win is None:
                pass
            elif game_row.isP1Win:
                p1wins += 1
            else:
                p2wins += 1

        if p1wins >= self.size or p2wins >= self.size:
            self.isP1Win = True if p1wins >= self.size else False
            return True
        else:
            return False

    def report(self) -> None:
        games = []
        for game_row in self.game_rows:
            games.append(game_row.toGame())
        winner_id = self.entrants[0].id if self.isP1Win else self.entrants[1].id
        game_set = GameSet(round_name=self.title, entrants=self.entrants, games=games, winner=winner_id,
                           set_id=self.set_id)
        report_set(game_set)
