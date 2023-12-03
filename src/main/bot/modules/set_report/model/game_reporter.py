from collections import Counter
from enum import Enum

import discord

from commons.model.discord_objects import MultipleSelect
from commons.model.tournament_objects import TourPlayer, TourSet, TourGame, CharacterSelection, TourCharacter
from modules.set_report.model.chars import LIST_OF_CHARS
from modules.set_report.utils import report_set_to_gql


class _CharacterReporter(MultipleSelect):
    def __init__(self, selector_view: discord.ui.View, original_view: 'GameReportView', player: TourPlayer):
        self.original_view = original_view
        self.player = player

        options = [discord.SelectOption(label=ch,
                                        value=ch,
                                        emoji=discord.PartialEmoji.from_str(LIST_OF_CHARS[ch]["emoji"])
                                        ) for ch in LIST_OF_CHARS if ch is not None]

        super().__init__(options, selector_view, 1)

    async def confirm(self, interaction: discord.Interaction):
        TourGame.character_selections = [cs for cs in TourGame.character_selections if cs.player != self.player]
        character_selected = TourCharacter(LIST_OF_CHARS[self.values[0]]['id'])
        TourGame.character_selections.append(CharacterSelection(character_selected, self.player))
        self.original_view.update_view()
        await interaction.response.edit_message(view=self.original_view)


class _GameRow:
    view: 'GameReportView'
    tour_game: TourGame
    p1: TourPlayer
    p2: TourPlayer

    class _GameRowButtons(Enum):
        LEFT_CHAR = 0
        LEFT_WIN = 1
        SPACER = 2
        RIGHT_WIN = 3
        RIGHT_CHAR = 4

    class CharacterButton(discord.ui.Button):
        row: '_GameRow'
        player: TourPlayer

        def __init__(self, row: '_GameRow', player: TourPlayer, is_p1: bool):
            self.row, self.player = row, player
            super().__init__(label="",
                             style=discord.ButtonStyle.gray,
                             row=row.get_row_num(),
                             emoji=discord.PartialEmoji.from_str(LIST_OF_CHARS[None]['emoji'])
                             )

            previous_row = self.row.get_previous_row()
            if previous_row is not None:
                button_index = _GameRow._GameRowButtons.LEFT_CHAR.value if is_p1 \
                    else _GameRow._GameRowButtons.RIGHT_CHAR.value
                self.emoji = previous_row.buttons[button_index].emoji

        async def callback(self, interaction: discord.Interaction):
            selector_view = discord.ui.View(timeout=None)
            _CharacterReporter(selector_view, self.row.view, self.player)
            await interaction.response.edit_message(view=selector_view)

    class SpacerButton(discord.ui.Button):
        def __init__(self, row: '_GameRow'):
            super().__init__(label=f"Game {str(row.get_row_num() + 1)}",
                             style=discord.ButtonStyle.gray,
                             row=row.get_row_num(),
                             disabled=True
                             )

        async def callback(self, interaction: discord.Interaction):
            raise Exception("Spacer Button Pressed: Should be impossible")

    class WinButton(discord.ui.Button):
        row: '_GameRow'
        winning_player: TourPlayer

        def __init__(self, row: '_GameRow', winning_player: TourPlayer):
            self.row, self.winning_player = row, winning_player
            super().__init__(label="W",
                             style=discord.ButtonStyle.green,
                             row=row.get_row_num()
                             )

        async def callback(self, interaction: discord.Interaction):
            current_row_num = self.row.get_row_num()
            view = self.row.view

            self.row.tour_game.winner = self.winning_player
            view.tour_set.games[current_row_num] = self.row.tour_game

            # Re-enable the other button
            self.row.buttons[_GameRow._GameRowButtons.LEFT_WIN.value].disabled = False
            self.row.buttons[_GameRow._GameRowButtons.RIGHT_WIN.value].disabled = False

            # Disable the selected button
            self.disabled = True

            # Remove all subsequent game rows from view

            if current_row_num < view.num_rows() - 1:
                view.game_rows = view.game_rows[:current_row_num + 1]
                view.tour_set.games = view.tour_set.games[:current_row_num + 1]

            # Check if Set is Completed
            if view.check_win():
                view.clear_items()
                await interaction.response.edit_message(content="Set Reported!", view=view)
                view.report()

            # Set not completed, add another game row
            else:
                view.game_rows.append(_GameRow(view))
                view.update_view()
                await interaction.response.edit_message(view=view)

    def __init__(self, view: 'GameReportView'):
        self.view = view
        self.p1, self.p2 = view.tour_set.players[0], view.tour_set.players[1]
        self.buttons = [_GameRow.CharacterButton(self, self.p1, True),
                        _GameRow.WinButton(self, self.p1),
                        _GameRow.SpacerButton(self),
                        _GameRow.WinButton(self, self.p2),
                        _GameRow.CharacterButton(self, self.p2, False)]

        self.tour_game = TourGame.empty_tour_game(view.tour_set.players, self.get_row_num() + 1)
        self.update_view()

    def update_view(self):
        for button in self.buttons:
            self.view.add_item(button)

    def get_row_num(self):
        for i, row in enumerate(self.view.game_rows):
            if self is row:
                return i

    def get_previous_row(self):
        row_num = self.get_row_num()
        return None if row_num == 0 else self.view.game_rows[row_num - 1]


class GameReportView(discord.ui.View):
    interaction: discord.Interaction
    tour_set: TourSet
    game_rows: list[_GameRow]

    def __init__(self, interaction, tour_set):
        super().__init__(timeout=None)

        self.interaction = interaction
        self.tour_set = tour_set
        self.game_rows = [_GameRow(self)]

    def update_view(self):
        self.clear_items()
        for game_row in self.game_rows:
            game_row.update_view()

    def num_rows(self):
        return len(self.game_rows)

    def check_win(self) -> bool:
        winners = Counter([game.winner.entrant_id for game in self.tour_set.games if game is not None])
        leader_id = max(winners, key=winners.get)
        if winners[leader_id] >= self.tour_set.req_wins:
            self.tour_set.winner_id = leader_id
            return True
        else:
            return False

    def report(self) -> None:
        report_set_to_gql(self.tour_set)
