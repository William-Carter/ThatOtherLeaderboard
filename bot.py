import discord
import os
import controller
import durations
import json


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

dirPath = os.path.dirname(os.path.realpath(__file__))

with open(dirPath+"/config.json") as f:
    config = json.load(f)
token = config["token"]
trustedUsers = config["trustedUsers"]

with open(dirPath+"/version.txt", "r") as f:
    version = f.readlines()[0].strip()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    messageParts = message.content.split(" ")

    if messageParts[0] == ".version":
        await message.channel.send("Tol is currently on version "+version)

    if messageParts[0] == ".help":
        if len(messageParts) == 1:
            await message.channel.send("Commands:\n.help - Display this menu\n.register - Register to That Other Leaderboard\n.submit - Submit a run to that other leaderboard\n\nDo .help [command] for more information on any command")

        else:
            helpMessages = {"submit": 
                            "Submit a run.\nUsage:\n`.submit (category) (time) [date=x] [srcomid=x]`\nValid categories are oob, inbounds, unrestricted, legacy or glitchless\nFields in brackets require identifiers (`field=value`)\nDate should be formatted as yyyy-mm-dd. Current UTC date will be used if not supplied.\nsrcomid refers to the ID of your run on speedrun.com. Only necessary for runs that are currently in queue.\nExample submission:\n`.submit glitchless 16:16.05 date=2022-10-09`",
                            "register":
                            "Register to tol.\nUsage:\n`.register (speedrun.com username)`",
                            "leaderboard":
                            "Show the leaderboard for a given category.\nUsage:\n`.leaderboard (category) [startpoint]`\nTo view runs starting at a certain point in the rankings, add startpoint."}
            if messageParts[1].strip(".")  in helpMessages.keys():
                await message.channel.send(helpMessages[messageParts[1].strip(".")])
            else:
                await message.channel.send(f"No help page for {messageParts[1]}")

    if messageParts[0] == ".submit":
        args = len(messageParts)-1
        if args < 2:
            await message.channel.send("Invalid submission! use `.help submit` for help on submitting.")
        elif messageParts[1] not in ["oob", "inbounds", "unrestricted", "legacy", "glitchless"]:
            await message.channel.send("Invalid category! use `.help submit` for a list of valid categories.")
        elif not durations.seconds(messageParts[2]): # Should maybe be handled in controller.py?
            await message.channel.send("Invalid run duration!")

        else:
            forcePB = False
            date = "now"
            srcomID = None
            for argument in messageParts[3:]:

                argParts = argument.split("=")
                if argParts[0] == "date":
                    date = argParts[1]
                if argParts[0] == "srcomid":
                    srcomID = argParts[1]

            output = controller.addRun(
                message.author.id, 
                messageParts[1], 
                messageParts[2], 
                date = date, 
                srcomID = srcomID
                )
            await message.channel.send(output)


        

    if messageParts[0] == ".register":
        if not len(messageParts) > 1:
            await message.channel.send("Usage:\n.register [speedrun.com username]")
        else:
            response = controller.registerPlayer(message.author.name, message.author.id, messageParts[1])
            await message.channel.send(response)


    if messageParts[0] == ".profile":
        
        
        if len(messageParts) == 1:
            response = f"Profile for {message.author.name}:\n"
            if not controller.playerRegistered(message.author.id):
                await message.channel.send("Account not registered!\n Please register with .register first.")
                personalBests = False
            else:
                personalBests = controller.getProfileFromDiscord(message.author.id)
        else:
            response = f"Profile for {messageParts[1]}:\n"

            personalBests = controller.getProfileFromDiscordName(messageParts[1])
            if not personalBests:
                await message.channel.send("Unknown user")
            
        if personalBests:
            if len(personalBests.keys()) > 0:
                for category in personalBests.keys():
                    position = controller.formatLeaderBoardPosition(controller.getRunPlace(personalBests[category][0], category))
                    time = durations.formatted(personalBests[category][1])
                    forCats = {"oob": "OoB", "inbounds": "Inbounds", "unrestricted": "NoSLA Unr.", "legacy": "NoSLA Leg.", "glitchless": "Glitchless"}
                    response += f"`{forCats[category]}{' '*(15-len(forCats[category]))}{time}{' '*(13-len(time))}{position}`\n"


            else:
                response = "No PBs tracked."
                

            await message.channel.send(response)
            

    if messageParts[0] == ".leaderboard":
        if len(messageParts) == 2:
            response = controller.getLeaderboard(messageParts[1])

        elif len(messageParts) == 3:
            response = controller.getLeaderboard(messageParts[1], messageParts[2])
        else:
            response = "No category supplied"

        await message.channel.send(response)


    if messageParts[0] == ".myruns":
        response = controller.getRunsDisplay(message.author.id)
        await message.channel.send(response)

    if messageParts[0] == ".edit":
        if len(messageParts) != 3:
            response = "Invalid arguments. Do .help edit to see"

    #################################
    # Administrative Commands Below #
    #################################
    if message.author.id in trustedUsers:
        if messageParts[0] == ".update":
                controller.updateLeaderboard()

                


client.run(token)