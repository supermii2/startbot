# START-BOT
### A Discord bot with start.gg integration

## Installation guide
1. Download the most recent release from the GitHub repository.
2. Run setup.py or otherwise install the required dependencies given by requirements.txt.
3. Add the respective tokens to the .env file.
4. Run the main.py file of the bot.

## Features
### Information Commands
| Command    | Parameters |                Use Case                |
|:-----------|:----------:|:--------------------------------------:|
| ``whoami`` |    None    | Returns the the discord id of the user |

### Reporting Commands
| Command    |                      Parameters                       |                                                             Use Case                                                             |
|:-----------|:-----------------------------------------------------:|:--------------------------------------------------------------------------------------------------------------------------------:|
| ``report`` | ``tournament-slug``:<br> name of tournament to report | Allows the user to set up and report a set in the given tournament. Requires the owner to have valid permissions to report sets. |