import discord
from discord import app_commands
import itertools

from dotenv import load_dotenv
import os
from functions_event_info import *
from functions_reporting import *
from util_server_data import *

load_dotenv()

data = ServerDataHandler()
TOKEN = os.getenv('DISC_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

@tree.command(name="nextset", description="Find the next set in the current set tournament")
async def nextSet(interaction, tournament_name: str):
    sets = getNextSetFromDiscord(interaction.user.id, tournament_name)
    if sets == None:
        await interaction.response.send_message("No sets found")
    else:
        sets = list(itertools.accumulate(map(toStringSetSingles, sets), lambda x, y: x + "\n" + y))
        await interaction.response.send_message(sets)
    return sets

@tree.command(name="getsets", description="Get sets pending report")
async def getSets(interaction: discord.Interaction):
    if data.read_data(interaction.guild.id, "sets_to_report") == None:
        await interaction.response.send_message("No sets to report")
    else:
        sets = list(map(print_set, (data.read_data(interaction.guild.id, "sets_to_report"))))
        s = ""
        for set in sets:
            s += set + "\n"
        await interaction.response.send_message(s)

@tree.command(name="clearsets", description="Removes all sets stored")
async def clearSets(interaction: discord.Interaction):
    data.write_data(interaction.guild.id, "sets_to_report", [])
    await interaction.response.send_message("Cleared")

@tree.command(name = "whoami", description = "Get your user id")
async def whoami(interaction):
    user = interaction.user.id
    await interaction.response.send_message(user)
    return user

@tree.command(name="report", description="Report a set from a tournament")
async def report(interaction: discord.Interaction, tournament: str):
    #needed to cope with how slow start gg's api is
    await interaction.response.defer()
    sets = getNextSetFromDiscord(interaction.user.id, tournament)
    def set_to_string(set):
        return '(' + set['identifier'] + ') ' + set['fullRoundText'] + ' \n' + set['slots'][0]['entrant']['name'] + " vs " +  set['slots'][1]['entrant']['name'] 

    set_titles = list(map(set_to_string, sets))
    options = list(map(lambda title: discord.SelectOption(label=title, value=title), set_titles))
    class SetSelectView(discord.ui.View):
        @discord.ui.select(options=options)
        async def select_callback(self, interaction: discord.Interaction, select):
            view = GameReportView(data, interaction, 3, select.values[0])
            await interaction.response.send_message(select.values[0], view=view, ephemeral=True)
    
    await interaction.followup.send(view=SetSelectView())

@tree.command(name = "reportsettest", description="Report a bo5 set")
async def reportset(interaction):
    TITLE = "Test Title"
    view = GameReportView(data, interaction, 3, TITLE)
    await interaction.response.send_message(TITLE, view=view, ephemeral = True)

@tree.command(name = "getparticipants", description="Get participants for an event")
async def getParticipants(interaction, tournament_name : str):
    participants = getAllUsersFromEvent(tournament_name)
    s = ""
    for element in participants:
        s += element[0] + ", "

    await interaction.response.send_message(s)

@bot.event
async def on_ready():
    await tree.sync()
    print(f'We have logged in as {bot.user}')

bot.run(TOKEN)