from enum import Enum

import discord

from src.data.character_data import LIST_OF_CHARS


class GameRow:
    class GameRowButtons(Enum):
        LEFT_CHAR = 0
        LEFT_WIN = 1
        SPACER = 2
        RIGHT_WIN = 3
        RIGHT_CHAR = 4

    class CharacterButton(discord.ui.Button):
        def __init__(self, parent: 'GameRow', is_p1: bool):
            self.parent, self.is_p1 = parent, is_p1
            super().__init__(label="",
                             style=discord.ButtonStyle.gray,
                             row=parent.row,
                             emoji=discord.PartialEmoji.from_str(LIST_OF_CHARS[None]['emoji'])
                             )

            previous_row = self.parent.previous_row()

            # Copy the characters from the previous row
            if previous_row is not None:
                button_index = GameRow.GameRowButtons.LEFT_CHAR.value if self.is_p1 \
                    else GameRow.GameRowButtons.RIGHT_CHAR.value
                self.emoji = previous_row.buttons[button_index].emoji
                self.parent.p1_char = previous_row.p1_char if self.is_p1 else self.parent.p2_char

        async def callback(self, interaction: discord.Interaction):
            from src.interaction_objects.game_reporter.game_reporter_character_reporter import GRCharacterReport
            selector_view = discord.ui.View(timeout=None)
            GRCharacterReport(selector_view, self.parent, self.is_p1, interaction)
            await interaction.response.edit_message(view=selector_view)

    class SpacerButton(discord.ui.Button):
        def __init__(self, parent):
            self.parent = parent
            label = "Game " + str(self.parent.row + 1)
            super().__init__(label=label,
                             style=discord.ButtonStyle.gray,
                             row=parent.row,
                             disabled=True
                             )

        async def callback(self, interaction: discord.Interaction):
            raise Exception("Spacer Button Pressed: Should be impossible")

    class WinButton(discord.ui.Button):
        def __init__(self, parent, is_p1: bool):
            self.parent, self.is_p1 = parent, is_p1
            super().__init__(label="W", style=discord.ButtonStyle.green, row=parent.row)

        async def callback(self, interaction: discord.Interaction):
            # Set Result
            self.parent.isP1Win = self.is_p1

            # Disable/Re-enable Row Buttons
            self.disabled = True
            if self.is_p1:
                self.parent.buttons[GameRow.GameRowButtons.RIGHT_WIN.value].disabled = False
            else:
                self.parent.buttons[GameRow.GameRowButtons.LEFT_WIN.value].disabled = False

            # Remove all subsequent game rows from view
            current_row = self.parent.row
            view = self.parent.view
            if current_row + 1 != len(view.game_rows):
                view.game_rows = view.game_rows[:current_row + 1]

            # Check if Set is Completed
            if view.check_win():
                view.clear_items()
                await interaction.response.edit_message(content="Set Reported!", view=view)  # noqa
                view.report()

            # Set not completed, add another game row
            else:
                view.game_rows.append(GameRow(view, current_row + 1))
                view.update_view()
                await interaction.response.edit_message(view=view)

    def __init__(self, view, row):
        self.view = view
        self.row = row
        # Recorded Variables
        self.isP1Win, self.p1_char, self.p2_char = None, None, None

        self.buttons = [GameRow.CharacterButton(self, True),
                        GameRow.WinButton(self, True),
                        GameRow.SpacerButton(self),
                        GameRow.WinButton(self, False),
                        GameRow.CharacterButton(self, False)]

    def update_view_row(self):
        for button in self.buttons:
            self.view.add_item(button)

    def previous_row(self):
        view = self.view
        current_row = self.row
        if current_row == 0:
            return None
        return view.game_rows[current_row - 1]
