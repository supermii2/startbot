from discord import Interaction
from discord.app_commands import CommandTree

from modules.set_report.model.set_selector import SetSelectView


def add_commands(tree: CommandTree):
    @tree.command(name="report")
    async def report(interaction: Interaction, tournament: str):
        await interaction.response.send_message("Loading!")
        SetSelectView(interaction, tournament, interaction.user.id)