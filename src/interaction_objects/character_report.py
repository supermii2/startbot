import discord

from src.data.character_data import LIST_OF_CHARS
from src.interaction_objects.multiple_select import MultipleSelect


class CharacterReport(MultipleSelect):
    def __init__(self, view: discord.ui.View):
        options = []
        for ch in LIST_OF_CHARS.keys():
            if ch is not None:
                options.append(discord.SelectOption(label=ch, value=ch, emoji=discord.PartialEmoji.from_str(
                    LIST_OF_CHARS[ch]["emoji"])))

        super().__init__(options, view, 1)
