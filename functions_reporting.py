import discord
from class_multiselect import *
from util_server_data import *
from enum import Enum

from character_data import *

class GameRow():
    class GameRowButtons(Enum):
        LEFT_CHAR = 0
        LEFT_WIN = 1
        SPACER = 2
        RIGHT_WIN = 3
        RIGHT_CHAR = 4

    class CharacterReport(MultipleSelect):
        def __init__(self, view: discord.ui.View, parent, isP1, orig_interaction: discord.Interaction):
            self.parent, self.isP1, self.orig_interaction = parent, isP1, orig_interaction
            options = []
            for ch in LIST_OF_CHARS.keys():
                if ch != None:
                    options.append(discord.SelectOption(label=ch, value=ch, emoji=discord.PartialEmoji.from_str(LIST_OF_CHARS[ch]["emoji"])))
                    super().__init__(options, view, 1)

        async def confirm(self, interaction: discord.Interaction):
            if self.isP1:
                self.parent.p1_char = self.values[0]
                self.parent.buttons[GameRow.GameRowButtons.LEFT_CHAR.value].emoji = LIST_OF_CHARS[self.values[0]]["emoji"]
            else:
                self.parent.p2_char = self.values[0]
                self.parent.buttons[GameRow.GameRowButtons.RIGHT_CHAR.value].emoji = LIST_OF_CHARS[self.values[0]]["emoji"]
            self.parent.view.update_view()
            #TODO
            await interaction.response.edit_message(content=self.parent.view.title,view=self.parent.view)

    class WinButton(discord.ui.Button):
        def __init__(self, parent, isP1: bool):
            self.parent, self.isP1 = parent, isP1
            super().__init__(label="W",style=discord.ButtonStyle.green, row=parent.row)

        async def callback(self, interaction: discord.Interaction):
            # Set Result
            self.parent.isP1Win = self.isP1
            
            #Disable/Re-enable Row Buttons
            self.disabled = True
            if self.isP1:
                self.parent.buttons[GameRow.GameRowButtons.RIGHT_WIN.value].disabled = False
            else:
                self.parent.buttons[GameRow.GameRowButtons.LEFT_WIN.value].disabled = False

            #Remove all subsequent game rows from view
            current_row = self.parent.row
            view = self.parent.view
            if current_row + 1 != len(view.game_rows):
                view.game_rows = view.game_rows[:current_row + 1]

            #Check if Set is Completed
            if view.check_win():
                view.clear_items()
                await interaction.response.edit_message(content="Set Reported!", view=view)
                view.report()

            #Set not completed, add another gamerow
            else:
                view.game_rows.append(GameRow(view, current_row + 1))
                view.update_view()
                await interaction.response.edit_message(view=view)

    class CharacterButton(discord.ui.Button):
        def __init__(self, parent, isP1: bool):
            self.parent, self.isP1 = parent, isP1
            super().__init__(label="", 
                             style=discord.ButtonStyle.gray,
                             row=parent.row, 
                             emoji=discord.PartialEmoji.from_str(LIST_OF_CHARS[None]['emoji'])
                             )

            previous_row = self.parent.previous_row()
            if previous_row != None:
                if self.isP1:
                    self.emoji = previous_row.buttons[GameRow.GameRowButtons.LEFT_CHAR.value].emoji
                    self.parent.p1_char = previous_row.p1_char
                else:
                    self.emoji = previous_row.buttons[GameRow.GameRowButtons.RIGHT_CHAR.value].emoji
                    self.parent.p2_char = previous_row.p2_char


        async def callback(self, interaction: discord.Interaction):
            selector_view = discord.ui.View(timeout=None)
            GameRow.CharacterReport(selector_view, self.parent, self.isP1, interaction)
            await interaction.response.edit_message(content="Character Selector", view=selector_view)

    class SpacerButton(discord.ui.Button):
        def __init__(self, parent):
            self.parent= parent
            label = "Game " + str(self.parent.row + 1)
            super().__init__(label=label, 
                             style=discord.ButtonStyle.gray,
                             row=parent.row,
                             disabled=True
                             )

        async def callback(self, interaction: discord.Interaction):
            raise Exception("Spacer Button Pressed: Should be impossible")

    def __init__(self, view, row):
        self.view = view
        self.row = row
        #Recorded Variables
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

class GameReportView(discord.ui.View):
    def __init__(self, data, interaction, size, title):
        self.data, self.interaction, self.size, self.title = data, interaction, size, title
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
            if game_row.isP1Win == True:
                p1wins += 1
            elif game_row.isP1Win == False:
                p2wins += 1

        if p1wins >= self.size or p2wins >= self.size:
            return True
        else:
            return False
    
    def report(self) -> None:
        if (self.data.read_data(self.interaction.guild.id, "sets_to_report")) == None:
            self.data.write_data(self.interaction.guild.id,"sets_to_report", [])

        set = {
            "title" : self.title,
            "games" : list(map(lambda x: {
                "isP1Win" : x.isP1Win,
                "p1char" : x.p1_char,
                "p2char" : x.p2_char
            }, self.game_rows))
        }

        self.data.read_data(self.interaction.guild.id, "sets_to_report").append(set)
        pass

def print_set(set: dict) -> str:
    s = ""
    s += set['title'] + "\n"
    for game in set["games"]:
        s += LIST_OF_CHARS[game["p1char"]]["emoji"]
        s += " **W** - L " if game["isP1Win"] else " L - **W** "
        s += LIST_OF_CHARS[game["p2char"]]["emoji"]
        s += "\n"
    return s
