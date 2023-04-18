import cobble.bot
import cobble.command
import cobble.permissions
import customcommands
import os
import discord
dirPath = os.path.dirname(os.path.realpath(__file__))


tolBot = cobble.bot.Bot(dirPath+"/config.json", "tolBot", ".")


tolBot.addCommand(cobble.command.HelpCommand(tolBot))
tolBot.addCommand(cobble.command.ListCommand(tolBot))
tolBot.addCommand(customcommands.RegisterCommand(tolBot))
tolBot.addCommand(customcommands.LeaderboardCommand(tolBot))
tolBot.addCommand(customcommands.SubmitCommand(tolBot))
tolBot.addCommand(customcommands.ProfileCommand(tolBot))
tolBot.addCommand(customcommands.SetupCommand(tolBot))
tolBot.addCommand(customcommands.UpdateSetupCommand(tolBot))
tolBot.addCommand(customcommands.ILSubmitCommand(tolBot))
tolBot.addCommand(customcommands.BatchSubmitCommand(tolBot))
tolBot.addCommand(customcommands.ILBoardCommand(tolBot))
tolBot.addCommand(customcommands.ILPBsCommand(tolBot))
tolBot.addCommand(customcommands.SumOfILsCommand(tolBot))
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
    
    if message.content[0] == tolBot.prefix:
        permissionLevel = cobble.permissions.getUserPermissionLevel(message.author, tolBot.admins)

        await message.channel.send(await tolBot.processCommand(message, message.content[1:], permissionLevel))



client.run(tolBot.token)