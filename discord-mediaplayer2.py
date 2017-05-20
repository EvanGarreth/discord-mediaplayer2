#!/bin/python3
import asyncio, dbus, discord

SECONDS_BETWEEN_CHECKS = 10
# In the discord client, hold ctrl+shift+i and look for the token value in Local Storage under the Application tab
CLIENT_TOKEN = "REPLACE_THIS"
# The desired MediaPlayer2 service name. Can be changed to any MediaPlayer2 compatible application (ex: Rythmbox, VLC, Spotfiy)
SERVICE = "org.mpris.MediaPlayer2.spotify"

client = discord.Client()
currentGame = None
playerInterface = None

@client.event
async def on_ready():
    displayUserInfo()
    await checkCurrentlyPlayingSong()

async def checkCurrentlyPlayingSong():
    while True:
        if playerIsRunning():
            hookPlayerInterface()
            game = createGame()
            if game != currentGame: # Perform this check so that we don't spam the API with a redundant status
                await updateUserGame(game)
        await asyncio.sleep(SECONDS_BETWEEN_CHECKS)

def playerIsRunning():
    return dbus.SessionBus().name_has_owner(SERVICE)

def hookPlayerInterface():
    global playerInterface
    playerBus = dbus.SessionBus().get_object(SERVICE, "/org/mpris/MediaPlayer2")
    playerInterface = dbus.Interface(playerBus, "org.freedesktop.DBus.Properties")

async def updateUserGame(newGame):
    global currentGame
    print("Changing {} to {}".format(str(currentGame), str(newGame)))
    currentGame = newGame
    await client.change_presence(game=newGame)

def createGame():
    metaData = playerInterface.Get("org.mpris.MediaPlayer2.Player", "Metadata")
    if metaData: # metaData is None when spotify is started up w/o hitting play
        status = "♪ {} - {}".format(metaData["xesam:title"], metaData["xesam:artist"][0])
        return discord.Game(name=status)

def displayUserInfo():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)

if __name__ == "__main__":
    client.run(CLIENT_TOKEN, bot=False)
