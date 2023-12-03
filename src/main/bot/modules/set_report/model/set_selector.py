import discord

from modules.set_report.model.game_reporter import GameReportView
from modules.set_report.utils import get_called_sets_from_tour_slug


class SetSelectMenu(discord.ui.Select):
    def __init__(self, sets, options):
        super().__init__(options=options)
        self.sets = sets

    async def callback(self, interaction: discord.Interaction):
        selected_set_id = int(self.values[0])
        selected_set = next(s for s in self.sets if s.set_id == selected_set_id)

        view = GameReportView(interaction, selected_set)
        await interaction.response.send_message(view=view)

class SetSelectView(discord.ui.View):
    def __init__(self, interaction, tour_slug, discord_id):
        super().__init__(timeout=None)
        self.interaction = interaction
        sets = get_called_sets_from_tour_slug(tour_slug, discord_id, 2)

        if len(sets) == 0:
            interaction.response.edit_message("No sets found!")

        else:
            options = [discord.SelectOption(label=s.title, value=str(s.set_id)) for s in sets]
            select_menu = SetSelectMenu(sets, options)
            self.add_item(select_menu)
            interaction.response.edit_message(view=self)
