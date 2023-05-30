import cobble.bot
import cobble.command
import cobble.permissions
from customcommands import *
import os
import discord
dirPath = os.path.dirname(os.path.realpath(__file__))


tolBot = cobble.bot.Bot(dirPath+"/config.json", "tolBot", ".")


tolBot.addCommand(cobble.command.HelpCommand(tolBot))
tolBot.addCommand(cobble.command.ListCommand(tolBot))

# Get the path of the commands directory
commandsDir = os.path.join(os.path.dirname(__file__), "customcommands")

# Iterate over the files in the commands directory
for filename in os.listdir(commandsDir):
    if filename.endswith(".py"):
        # Remove the file extension to get the command name
        commandName = filename[:-3]

        if commandName == "customvalidations":
            continue
        
        # Import the command module dynamically
        module = __import__(f"customcommands.{commandName}", fromlist=[commandName])
        
        # Get the command class from the module
        commandClass = getattr(module, commandName + "Command")

        tolBot.addCommand(commandClass(tolBot))



intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content:
        if message.content[0] == tolBot.prefix:
            permissionLevel = cobble.permissions.getUserPermissionLevel(message.author, tolBot.admins)

            response, postCommand = await tolBot.processCommand(message, message.content[1:], permissionLevel)
            await message.channel.send(response[:(min(len(response), 1999))])
            if postCommand:
                postCommand()




client.run(tolBot.token)