import discord.app_commands

from src.interaction_objects.game_report_view import GameReportView


def add_commands_to_tree(tree: discord.app_commands.CommandTree) -> None:
    @tree.command(name="whoami", description="Get your user id")
    async def whoami(interaction: discord.Interaction):
        user = interaction.user.id
        await interaction.response.send_message(user)

    @tree.command(name="report")
    async def report(interaction: discord.Interaction, tournament: str):

        view = GameReportView(interaction, 3, tournament)
        await interaction.response.send_message(view=view, ephemeral=True)
