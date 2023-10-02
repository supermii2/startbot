import discord
from discord import app_commands

from src.commands.commands import add_commands_to_tree


class StartBot(discord.Client):
    def __init__(self, token):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.token = token
        self.command_tree = app_commands.CommandTree(self)
        add_commands_to_tree(self.command_tree)

        @self.event
        async def on_ready():
            await self.command_tree.sync()
            print(f'We have logged in as {self.user}')

    def run_bot(self):
        self.run(token=self.token)
