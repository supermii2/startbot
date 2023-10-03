import discord.app_commands

from src.api_handler.graphql_utils import get_called_sets_from_tour_slug
from src.game_objects.gameset import GameSet
from src.interaction_objects.game_report_view import GameReportView


def add_commands_to_tree(tree: discord.app_commands.CommandTree) -> None:
    @tree.command(name="whoami", description="Get your user id")
    async def whoami(interaction: discord.Interaction):
        user = interaction.user.id
        await interaction.response.send_message(user)

    @tree.command(name="report")
    async def report(interaction: discord.Interaction, tournament: str):
        await interaction.response.defer()
        sets = get_called_sets_from_tour_slug(tournament_slug=tournament, discord_id=interaction.user.id)

        options = []
        for key in sets.keys():
            options.append(discord.SelectOption(label=sets[key].__str__(), value=key))
        class SetSelectView(discord.ui.View):
            @discord.ui.select(options=options)
            async def select_callback(self, msg_interaction: discord.Interaction, selected: discord.ui.Select):
                selected_set: GameSet = sets[int(selected.values[0])]

                view = GameReportView(interaction=msg_interaction, size=3, title=selected_set.round_name,
                                      entrants=selected_set.entrants, set_id=selected_set.set_id)
                await msg_interaction.response.send_message(view=view, ephemeral=True)

        await interaction.followup.send(view=SetSelectView(), ephemeral=True)
