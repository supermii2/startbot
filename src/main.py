from dotenv import load_dotenv
import os

from src.client.client import StartBot

load_dotenv()
TOKEN = os.getenv('DISC_TOKEN')

client = StartBot(TOKEN)
client.run_bot()
