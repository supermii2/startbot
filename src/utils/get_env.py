from dotenv import load_dotenv
import os

load_dotenv()


def get_start_token():
    return os.getenv('START_TOKEN')


def get_start_url():
    return os.getenv('START_URL')


def get_discord_token():
    return os.getenv('DISC_TOKEN')