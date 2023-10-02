import discord

from src.interaction_objects.game_reporter.game_reporter_row import GameRow


class GameReportView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, size: int = 3, title: str = ""):
        self.interaction, self.size, self.title = interaction, size, title
        self.game_rows = [GameRow(self, 0)]
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
            return True
        else:
            return False

    def report(self) -> None:
        pass
