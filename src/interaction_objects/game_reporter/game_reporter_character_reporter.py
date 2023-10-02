import discord

from src.data.character_data import LIST_OF_CHARS
from src.interaction_objects.character_report import CharacterReport
from src.interaction_objects.game_reporter.game_reporter_row import GameRow


class GRCharacterReport(CharacterReport):
    def __init__(self, view: discord.ui.View, parent: GameRow, is_p1: bool, orig_interaction: discord.Interaction):
        self.parent, self.is_p1, self.orig_interaction = parent, is_p1, orig_interaction
        super().__init__(view)

    async def confirm(self, interaction: discord.Interaction):
        if self.is_p1:
            self.parent.p1_char = self.values[0]
            self.parent.buttons[GameRow.GameRowButtons.LEFT_CHAR.value].emoji = LIST_OF_CHARS[self.values[0]][
                "emoji"]
        else:
            self.parent.p2_char = self.values[0]
            self.parent.buttons[GameRow.GameRowButtons.RIGHT_CHAR.value].emoji = LIST_OF_CHARS[self.values[0]][
                "emoji"]
        self.parent.view.update_view()
        # TODO
        await interaction.response.edit_message(content=self.parent.view.title, view=self.parent.view)


