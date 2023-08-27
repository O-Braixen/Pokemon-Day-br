#   "What Pokémon Day is it today?" Python bot for social media.

#ALSO TODO: Fix Discord posting the same thing from previous day if current day is blank

from icalendar import Calendar, Event
import datetime
import pytz
import random
import csv
import configparser
import urllib.request
import shutil
import os
from num2words import num2words
import pickle
import asyncio
from PIL import Image
import schedule
import time

#Setup config file
config = configparser.ConfigParser()
config.read('config.ini')

#If no config file exists and/or is just blank, make one!
if len(config.sections()) == 0:
    print("Config file not found or corrupt! Generating a new one and exiting! Open config.ini and configure everything!")
    try:
        shutil.copyfile("config.ini", "config.ini.bak")
        print("Backed up original ini file!")
    except:
        pass
    with open('config.ini', 'w') as f:
        f.write("[OPTIONS]" + "\n")
        f.write("#Set 'Continous' to true if you plan on running this once, and leaving it in the background! Set to false if you plan on manually running it when you want instead (i.e. via crontab)" + "\n")
        f.write("Continous = true" + "\n")
        f.write("#Set DownloadAllPics to true to download every picture needed. Set to false to only download the ones that are needed!" + "\n")
        f.write("DownloadAllPics = false" + "\n")
        f.write("#Set TestMode to true to prevent the script from actually posting to Twitter, Mastodon, and Discord, and to print the results out instead" + "\n")
        f.write("TestMode = true" + "\n")
        f.write("#Set TestDate to true to test a date provided in the python script. Requires TestMode to be true. Set Month2Test and Day2Test!" + "\n")
        f.write("#Note: This is not compatible with 'Continous', and might result in an error!" + "\n")
        f.write("TestDateMode = false" + "\n")
        f.write("Month2Test = 4" + "\n")
        f.write("Day2Test = 17" + "\n")
        f.write("#Place the path you wish to download all of the images from here!" + "\n")
        f.write("#NOTICE: URL needs to be in unicode! This will not work if the url contains a % sign!" + "\n")
        f.write("PokePics = https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/" + "\n")
        f.write("#If the filenames use precedeing 0's (i.e. 002.png), make sure 'zfiller' is set to true!" + "\n")
        f.write("zfiller = false" + "\n")
        f.write("#Put the download for your calendar file here! If not provided, it won't download, and assume one already exists." + "\n")
        f.write("#NOTICE: URL needs to be in unicode! This will not work if the url contains a % sign!" + "\n")
        f.write("CalDown = https://calendar.google.com/calendar/ical/j5gnr9l1o867fke2cocmjieaa8@group.calendar.google.com/public/basic.ics" + "\n")
        f.write("\n")
        f.write("[Discord API]" + "\n")
        f.write("enabled = false" + "\n")
        f.write("#Place your Discord Bot Token key here! DO NOT share this with anyone!" + "\n")
        f.write("bot_token = cooltoken" + "\n")
        f.write("#Channel where your discord bot will post. MAKE SURE YOUR BOT HAS PERMISSION TO CHAT THERE!!!!!" + "\n")
        f.write("channel = cool-channel-name" + "\n")
        f.write("\n")
        f.write("[Twitter API]" + "\n")
        f.write("enabled = false" + "\n")
        f.write("#Place your Twitter API keys here! NOTE: You need Elevated access for Twitter API v1.1!" + "\n")
        f.write("client_key = coolkey" + "\n")
        f.write("client_secret = coolkeysecret" + "\n")
        f.write("access_token = coolaccesstoken" + "\n")
        f.write("access_secret = coolaccesstokensecret" + "\n")
        f.write("\n")
        f.write("[Mastodon API]" + "\n")
        f.write("enabled = false" + "\n")
        f.write("#Set 'visiblity' to something else if you want! Options can be 'direct', 'private', 'unlisted', and 'public'." + "\n")
        f.write("#I'd recommend setting it to 'private' if you're testing this out on a brand new account" + "\n")
        f.write("visibility = unlisted" + "\n")
        f.write("#Replace with your instance's URL (example: mastodon.social, donphan.social, etc.)" + "\n")
        f.write("instance_url = https://example.com" + "\n")
        f.write("#Place your Mastodon API keys here!" + "\n")
        f.write("client_key = coolkey" + "\n")
        f.write("client_secret = coolkeysecret" + "\n")
        f.write("access_token = coolaccesstoken" + "\n")
        f.close()
    exit()

#Enable the APIs as needed!
def checkapi():
    global twitterapi
    global mastodonapi
    global discordapi
    global discord
    global tweepy
    global mastodon
    global Mastodon
    
    twitterapi = config['Twitter API'].getboolean('enabled')
    mastodonapi = config['Mastodon API'].getboolean('enabled')
    discordapi = config['Discord API'].getboolean('enabled')
    if discordapi:
        try:
            import discord
        except:
            print("Discord API module not loaded!")
            discordapi = False
        else:
            print("Discord API module loaded")
            discordapi = True
    else:
        print("Discord API not enabled in options")
        discordapi = False

    if twitterapi:
        try:
            import tweepy
        except:
            print("Twitter API module not loaded!")
            twitterapi = False
        else:
            print("Twitter API module loaded")
            twitterapi = True
    else:
        print("Twitter API not enabled in options")
        twitterapi = False

    if mastodonapi:
        try:
            from mastodon import Mastodon
        except:
            print("Mastodon.py module not loaded!")
            mastodonapi = False
        else:
            print("Mastodon.py module loaded")
            mastodonapi = True
    else:
        print("Mastodon API not enabled in options")
        mastodonapi = False

checkapi()

#Set some other variables up from the options!
Continous = config['OPTIONS'].getboolean('Continous')
TestMode = config['OPTIONS'].getboolean('TestMode')
TestDateMode = config['OPTIONS'].getboolean('TestDateMode')
DownloadAllPics = config['OPTIONS'].getboolean('DownloadAllPics')
zfiller = config['OPTIONS'].getboolean('zfiller')
Month2Test = int(config['OPTIONS']['Month2Test'])
Day2Test = int(config['OPTIONS']['Day2Test'])
PokePics = config['OPTIONS']['PokePics']
try:
    CalFile = config['OPTIONS']['CalDown']
except:
    pass #don't error out, the script handles there being an invalid calendar download correctly

if TestMode:
    print("Test Mode enabled, will only print results!")

#Download pictures
if not os.path.isdir("pic"):
    os.mkdir("pic")
picdir = os.listdir("pic")

def filecheckndown(number):
    pather = "pic/" + number + ".png"
    download = PokePics + number + ".png"
    if not os.path.isfile(pather):
        print("Downloading: " + download + " to: " + pather)
        urllib.request.urlretrieve(download, pather)
    else:
        print("File " + pather + " exists!")

if DownloadAllPics and len(picdir) < 1008:
    print("Incomplete picture directory, downloading pictures from provided path!")
    for number in range(1, 1009):
        numerer = str(number)
        if zfiller:
            numerer = numerer.zfill(3)
        filecheckndown(numerer)

#Get today's date in JST, and then convert it to MM/DD
def getdaytoday(silent):
    global togay
    global togaystr
    global tomorrow
    global tomorrowstr
    global jobtime
    global jobtime2
    utc_dt = datetime.datetime.now(datetime.timezone.utc)
    togay = utc_dt.astimezone()
    if not silent:
        print("Date & Time (Local):", togay)
    yourtimezone = togay.utcoffset()

    year = togay.strftime("%Y")

    if TestDateMode:
        togay = datetime.datetime(int(year), Month2Test, Day2Test, 00, 00, 10)
        togay = togay.astimezone(pytz.timezone("Asia/Tokyo"))
    else:
        togay = togay.astimezone(pytz.timezone("Asia/Tokyo"))
    if not silent:
        print("Date & Time (JST):", togay)

    japantimezone = togay.utcoffset()
    yourtimezone = int((yourtimezone.seconds + (yourtimezone.days * 86400)) / 3600)
    japantimezone = int((japantimezone.seconds + (japantimezone.days * 86400)) / 3600)

    if not silent:
        print("Your Timezone's UTC Offset: ", yourtimezone)
        print("Japan's UTC Offset: ", japantimezone)
    
    tomorrow = togay + datetime.timedelta(days=1)
    #convert date to string, makes it easier to compare dates!
    togaystr = togay.strftime("%m/%d")
    tomorrowstr = togay.strftime("%m/%d")

    #Get time delta, used for setting up the job:
    td = japantimezone - yourtimezone
    timemidnight = abs(td - 24)
    if timemidnight >= 24:
        timemidnight -= 24
    jobtime = str(timemidnight).zfill(2)+":00"
    if not silent:
        print("Time Delta from JST: ", td)
        print("Job time (midnight JST):", jobtime)

    #Get the secondary job time, to boost posts!
    timemidday = timemidnight + 12
    if timemidday >= 24:
        timemidday -= 24
    jobtime2 = str(timemidday).zfill(2)+":00"
    if not silent:
        print("Boost job time (noon JST):", jobtime2)

getdaytoday(False)

#Generate filenames function, used twice in script so we split it out into a function!
def generatefilenames(pokedex, name, appender):
    for pokemon in pokedex:
        pokename = name[0]
        #special exceptions, specifically related to the CSV file used
        if pokename == "Nidoran":
            pokename = "Nidoran♀"
        if pokemon[1] == pokename:
            numerer = pokemon[0]
            numerer = str(numerer) #convert number to string
            if zfiller:
                numerer = numerer.zfill(3)
            #print(numerer)
            appender.append(numerer)

#Generate list of Pokemon w/ associated Pokedex numbers
with open('files/natdex.csv',encoding='utf-8', newline='') as f:
    reader = csv.reader(f)
    pokedex = list(reader)

# Authenticate to social media!
if twitterapi:
    try:
        twitter_client_key = config['Twitter API']['client_key']
        twitter_client_secret = config['Twitter API']['client_secret']
        twitter_access_token = config['Twitter API']['access_token']
        twitter_access_secret = config['Twitter API']['access_secret']
        #authentication begins here
        twitter_authenticator = tweepy.OAuthHandler(twitter_client_key, twitter_client_secret)
        twitter_authenticator.set_access_token(twitter_access_token, twitter_access_secret)
        twitter_api = tweepy.API(twitter_authenticator, wait_on_rate_limit=True)
    except:
        print("WARNING: Twitter API settings can not be found! Did you type them in correctly?")
    else:
        print("Loaded Twitter API settings")

    try:
        twitter_api.verify_credentials()
    except:
        print("Error during Twitter Authentication!")
        twitterapi = False #set to false to prevent api calls
    else:
        print("Twitter Authentication OK!")

if mastodonapi:
    try:
        mastodon_instance_url = config['Mastodon API']['instance_url']
        mastodon_visibility = config['Mastodon API']['visibility']
        mastodon_client_key = config['Mastodon API']['client_key']
        mastodon_client_secret = config['Mastodon API']['client_secret']
        mastodon_access_token = config['Mastodon API']['access_token']
        #authentication begins here
        mastodon_api = Mastodon(
            client_id = mastodon_client_key,
            client_secret = mastodon_client_secret,
            access_token = mastodon_access_token,
            api_base_url = mastodon_instance_url
        )
    except:
        print("WARNING: Mastodon API settings can not be found! Did you type them in correctly?")
    else:
        print("Loaded Mastodon API settings")
    
    try:
        Mastodon.account_verify_credentials(mastodon_api)
    except:
        print("Error during Mastodon Authentication!")
        mastodonapi = False #set to false to prevent api calls
    else:
        print("Mastodon Authentication OK!")

twitterposts = []
mastoposts = []

#Last Call, done for in case the script crashes and needs to post!
lastcall = configparser.ConfigParser()
def lastcallsave():
    with open('lastcall.ini', 'w') as configfile:    # save
        lastcall.write(configfile)
        configfile.close()

def lastcallload():
    lastcall.read('lastcall.ini')

lastcallrun = False
print("Checking lastcalled file...")
lastcallload()
if len(lastcall.sections()) == 0:
    print("Last call file not found!")
    with open('lastcall.ini', 'w') as f:
        f.write("[CALL]" + "\n")
        f.write("#NOTICE: DON'T TOUCH ANYTHING IN HERE!" + "\n")
        f.write("date = N/A" + "\n")
        f.write("mastodone = false" + "\n") #haha mastodon, mastodone, i am Funny
        f.write("twitterdone = false" + "\n")
        f.write("discorddone = false")
        f.close()
    lastcallload()
print("Lastcalled found/created!")
if lastcall['CALL']['date'] == togaystr:
    print("Lastcall matches today's date, no need to run. Setting 'Done' values to defaults for in case!")
    lastcall['CALL']['mastodone'] = "false"
    lastcall['CALL']['twitterdone'] = "false"
    lastcall['CALL']['discorddone'] = "false"
    lastcallsave()
else:
    print("Lastcall does not match today's date! Running script now, regardless of Continous mode!")
    lastcallrun = True

def pokepost():
    print("Starting script in 3 seconds...")
    time.sleep(3)
    print("Starting!")
    global TestMode
    global twitterapi
    global twitter_api
    global discordapi
    global mastodonapi
    global mastodon_api
    global togay
    global tomorrow
    global listodates
    global twitterposts
    global mastoposts
    global pokemontoday

    twitterposts = [] #reset both lists so we can freshly gather new IDs
    mastoposts = []

    print("Re-checking current time!")
    getdaytoday(False) #yes it does it twice technically, but only at the start-up of the script!
    checkapi()

    #Download and initiate calendar
    try:
        urllib.request.urlretrieve(CalFile)
    except:
        print("Could not download up-to-date calendar file!")
    else:
        try:
            shutil.copyfile("files/pokemon.ics", "files/pokemon.ics.bak")
        except:
            pass
        urllib.request.urlretrieve(CalFile, "files/pokemon.ics")
        print("Downloaded latest calendar file from URL")

    try:
        g = open('files/pokemon.ics','rb')
        gcal = Calendar.from_ical(g.read())
    except:
        print("calendar file seems corrupt, restoring backup")
        shutil.copyfile("files/pokemon.ics.bak", "files/pokemon.ics")
        g = open('files/pokemon.ics','rb')
        gcal = Calendar.from_ical(g.read())

    listodates = []
    def getdateinfo():
        global listodates
        global togaystr
        global togay
        global listodates
        global pokemontoday
        listodates = []
        print("Date used: " + togaystr)
        for event in gcal.walk('vevent'):
            start = event.get('dtstart') #what day?
            summary = event.get('summary') #date name
            dater = start.dt.strftime("%m/%d") #convert to MM/DD

            isittime = togay.strftime("%m/%d") == dater #determine if the current event this iteration matches up with today's date!
            if isittime == True:
                summary = summary.replace(' Day ', ' ')
                summary = summary.split()
                #Generate new hashtag, the ones on the calendar are Untrustable, and i'm too lazy to fix them
                for pokemon in pokedex:
                    if pokemon[1] == summary[0]:
                        summary[1] = "#" + pokemon[2] + "の日"
                #insert pokemon into the list
                listodates.insert(len(listodates), summary)
        pokemontoday = len(listodates)

    getdateinfo()

    #Function to generate the message with everything!
    if mastodonapi:
        #Create an emoji cache, as to not hammer the API server. If they have the pokemon emoji then they have them, y'know? It's not like this'll be updated much :p
        if not os.path.isfile("files/emojicache.bin") or os.stat("files/emojicache.bin").st_size == 0:
            mastodonemojis = Mastodon.custom_emojis(mastodon_api)
            with open('files/emojicache.bin', 'wb') as f:
                pickle.dump(mastodonemojis, f, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            with open('files/emojicache.bin', 'rb') as f:
                mastodonemojis = pickle.load(f)

    def generatephrase(NoLimit):
        #datenatural = togay.strftime("%B") + " " + num2words(int(togay.strftime("%d")), to="ordinal_num") #today's date in a natural sounding way
        global datenatural
        datenatural = togay.strftime("%d") + "/" + togay.strftime("%m")
        global postresponse
        global filenames
        global lastposttwitter
        global lastpostmastodon
        global media_ids
        global pokemonid
        global pokemonname
        pokemonid = []
        pokemonname = []
        i=0
        print("Gerando frase!")
        postresponse = "Olá pessoal" #reset the phrase
        filenames = [] #reset the filenames used for pictures
        tablertime = listodates[:4] #table used for the phrases; get only the first 4 items in the list
        if NoLimit:
            tablertime = listodates #take it all instead!

        #Generate different permutations of text, for fun!
        if random.random() < 0.50:
            postresponse = postresponse + "! já é o dia " + datenatural
        else:
            postresponse = postresponse + ", já é dia " + datenatural

        if random.random() < 0.50:
            postresponse = postresponse + "! lá no japão e hoje comemora-se o "
        else:
            postresponse = postresponse + " lá no japão e sabia que hoje e dedicado "

        if random.random() < 0.50:
            postresponse = postresponse + "atualmente para o "
        else:
            postresponse = postresponse + "atualmente para o "

        #Combine all the days together to form the tweet!

        for name in tablertime:
            #Generate Phrase
            index = tablertime.index(name)
            if index == len(tablertime)-1: #last entry
                postresponse = postresponse + "dia do " + name[0] +"!"
                pokemonname.insert(i,name[0])
                i=i+1
            elif index == len(tablertime)-2: #2nd to last entry
                postresponse = postresponse + "dia do " + name[0] + "! e também "
                pokemonname.insert(i,name[0])
                i=i+1
            else:
                postresponse = postresponse + "dia do " + name[0] + "!, "
                pokemonname.insert(i,name[0])
                i=i+1
            generatefilenames(pokedex, name, filenames)
            
        for ind, name in enumerate(filenames):
            filecheckndown(name) #check to see if file exists, if not, download it
            filenames[ind] = "pic/" + name + ".png" #append .png for use in actual posting
            print("To post: " + filenames[ind])
            pokemonid.insert(i,name)
            i=i+1

        #Line split, we need to do the hashtags now!
        postresponse = postresponse + "\n"
        global pokejapa
        pokejapa = []
        for name in tablertime:
            postresponse = postresponse + name[1] + "  "
            pokejapa.insert(i,name[1])
            i=i+1

        print("Twitter Post: " + postresponse)
        if mastodonapi:
            mastopost = postresponse
            #For mastodon specifically, if the server has the pokemon emojis we need, we use them in the post!
            mastopost = mastopost + "\n"
            for item in tablertime:
                name = item[0]
                name = name.lower()
                for emoji in mastodonemojis:
                    if name == emoji.shortcode:
                        mastopost = mastopost + ":" + name + ": "
            print("Mastodon Post: " + mastopost)
        
        #Home stretch! Now just post the stuff!
        if not TestMode: #don't post if testmode is enabled!
            if twitterapi and not lastcall['CALL'].getboolean('twitterdone'):
                media_ids = []
                for filename in filenames:
                    res = twitter_api.media_upload(filename)
                    media_ids.append(res.media_id)
                twitterposts.append(twitter_api.update_status(status=postresponse, media_ids=media_ids).id)
                if len(listodates) <= 4: #if we're less than 4, we're at the last entry
                    lastcall['CALL']['twitterdone'] = "true" 
                    lastcallsave()
            else:
                print("Twitter API is", twitterapi, "and twtiterdone is", lastcall['CALL'].getboolean('twitterdone'))

            if mastodonapi and not lastcall['CALL'].getboolean('mastodone'):
                media_ids = []
                for filename in filenames:
                    res = Mastodon.media_post(mastodon_api, media_file = filename)
                    media_ids.append(res)
                mastoposts.append(mastodon_api.status_post(mastopost, media_ids = media_ids, visibility = mastodon_visibility).id)
                if len(listodates) <= 4: #if we're less than 4, we're at the last entry
                    lastcall['CALL']['mastodone'] = "true"
                    lastcallsave()
            else:
                print("Mastodon API is", mastodonapi, "and mastodone is", lastcall['CALL'].getboolean('mastodone'))

        del listodates[:4] #remove first 4 entries from the list, so that we set up for the next iteration! or so that we just end the script :P

    while len(listodates) > 0:
        generatephrase(False)

    #Now we store the posts we've made into CSV files so we can easily reboost them later if the script crashes or something.
    if len(mastoposts) == 0: #fill up either list so that all rows are filled
        for number in range(0, len(twitterposts)):
            mastoposts.append(0)
    elif len(twitterposts) == 0:
        for number in range(0, len(mastoposts)):
            twitterposts.append(0)

    fields = ['MastoIDs', 'TweetIDs']
    rows = []

    print(fields)
    
    for number in range(0, max(len(twitterposts), len(mastoposts))): #fill up rows with lists we can inject our stuff into; needs to be seperate lists!
        rows.append([])

    for i, id in enumerate(mastoposts):
        rows[i].append(id)
    for i, id in enumerate(twitterposts):
        rows[i].append(id)
    
    print(rows)

    if not TestMode:
        with open("files/posts.csv", 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(fields)
            csvwriter.writerows(rows)
            csvfile.close()
        print("Stored post IDs in CSV!")
        #Do note this overwrites anything that was saved before!


    #Discord is complicated, so it's the last section here. A bit janky, but this will work.
    twitterapi = False
    mastodonapi = False

    if not TestMode:
        if discordapi and not lastcall['CALL'].getboolean('discorddone'):
            getdateinfo() #reset date info, we need a new table!
            #First, let's generate smaller images to use in discord!
            discordnums = []
            discordfilenames = []
            #Generate filenames
            for name in listodates:
                generatefilenames(pokedex, name, discordnums)
            
            #Resize images!
            for number in discordnums:
                picture = "pic/" + number + ".png"
                smallpicture = "pic/" + number + "-discord.png"
                if not os.path.isfile(smallpicture): #don't run since we've already resized the image!
                    pokeimage = Image.open(picture)
                    imgsize = list(pokeimage.size) #result is a tuple, we need a list to modify it!
                    for i, res in enumerate(imgsize):
                        imgsize[i] = int(res/5) #needs to be an integer, not a float
                    imgsize = tuple(imgsize) #convert back, the resize function requires a tuple
                    resized_image = pokeimage.resize(imgsize)
                    resized_image.save(smallpicture)
                    print("Resized: " + picture + " to: " + smallpicture)
                    discordfilenames.append(smallpicture)
                else:
                    print("Resized image already exists for " + picture + "!")
                    discordfilenames.append(smallpicture)

            try:
                discord_bot_token = config['Discord API']['bot_token']
                discord_channel = config['Discord API']['channel']
            except:
                print("WARNING: Discord API settings can not be found! Did you type them in correctly?")
            else:
                print("Loaded Discord API settings")

            #Now begins the fun part, asynchronous functions! I barely knew what to do here, but the code works, and that's what matters.
            class MyClient(discord.Client):
                def __init__(self):
                    super().__init__(intents=discord.Intents.default())
                async def on_ready(self):
                    print('bot fez login')
                    print('"' + self.user.name + '", id:', self.user.id)
                    #channelid = 888567677784829982 #ID CANAL BH
                    channelid = 1140647240927543496 #ID CANAL TESTE
                    i = 0
                    for guild in self.guilds:
                        for channel in guild.channels:
                            if str(channel) == discord_channel:
                                channelid = int(channel.id)
                    channel = self.get_channel(channelid)

                    print("Using channel ID:", channelid, "for channel:", channel)
                    print('------')
                    

                    while len(listodates) > 0:
                        generatephrase(True)
                        
                    try:
                        if not TestMode:
                            sendfiles = []
                            embed_fields = []  # Lista para acumular os campos do Embed
                            pokemon_names = []  # Lista para acumular os nomes dos Pokémon
                            print("Getting files to append")
                            
                            for filez in discordfilenames:
                                imagemembed = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/' + pokemonid[i] + '.png'
                                sender = discord.File(filez)
                                print("appending: " + filez)
                                sendfiles.append(sender)
                                
                                resposta = discord.Embed(
                                    colour=discord.Color.yellow(),
                                    title="Dia do " + pokemonname[i] + "!",
                                    # description=postresponse
                                )
                                resposta.set_thumbnail(url=imagemembed)
                                resposta.add_field(name="<:pokeball:1048529728484692018>  Pokémon", value=pokemonname[i], inline=True)
                                resposta.add_field(name="<:pokedex:1048529795547414548> Dex Nacional ", value="ID: " + pokemonid[i], inline=True)
                                resposta.add_field(name="📅 Data ", value=datenatural, inline=True)
                                #resposta.add_field(name="⛩️ Nome Japones ", value=pokejapa[i], inline=True)
                                #resposta.set_footer(text="Sistema em beta")
                                
                                embed_fields.append(resposta)  # Acumula os campos do Embed
                                pokemon_names.append(pokemonname[i])  # Acumula os nomes dos Pokémon
                                
                                i += 1
                            if pokemon_names:  # Verifica se há campos do Embed acumulados
                                
                                if len(pokemon_names) == 1:
                                    final_embed = embed_fields[0]
                                    message_content = f"Bom dia <@&1079858130072109086> hoje é dia do Pokémon: {pokemon_names[0]}"
                                    channel_message = await channel.send(content=message_content, embed=final_embed)
                                elif len(pokemon_names) <= 4:
                                    final_embed = embed_fields
                                    pokemon_names_text = ', '.join(pokemon_names)  # Transforma a lista de nomes em uma string
                                    message_content = f"Bom dia <@&1079858130072109086> hoje é dia dos Pokémon: {pokemon_names_text}"
                                    channel_message = await channel.send(content=message_content, embeds=final_embed)
                                else:
                                    pokemon_names_text = ', '.join(pokemon_names)  # Transforma a lista de nomes em uma string
                                    message_content = f"Bom dia <@&1079858130072109086> hoje é dia dos Pokémon: {pokemon_names_text}"
                                    channel_message = await channel.send(content=message_content)
                                    
                            #await channel.send(content=message_content, embed=final_embed)
                            print("mensagem enviada no discord")    

                            await client.close()
                        else:
                            for filez in discordfilenames:
                                print("appending (test mode) : " + filez)
                            await client.close()
                    except:
                        await client.close()


            #loop = asyncio.get_event_loop()
            client = MyClient()
            try:
                asyncio.new_event_loop()
                asyncio.set_event_loop(asyncio.new_event_loop())
                client.run(discord_bot_token)
            except:
                print("ERROR! Discord bot is unable to run! Did you type in the correct tokens?")
    
    lastcall['CALL']['discorddone'] = "true"
    lastcallsave()

    print("Everything ran successfully, setting date to today! And resetting all values back to false!")
    lastcall['CALL']['date'] = togay.strftime("%m/%d")
    lastcall['CALL']['mastodone'] = "false"
    lastcall['CALL']['twitterdone'] = "false"
    lastcall['CALL']['discorddone'] = "false"
    lastcallsave()

    #Finally, we check tomorrow!
    print("Done with today's date, checking tomorrow's date for issues...")
    togay = tomorrow
    togaystr = tomorrowstr
    WasTestModeOn = TestMode
    TestMode = True

    getdateinfo()
    while len(listodates) > 0:
        generatephrase(False)

    print("Turning TestMode back to what it used to be:", WasTestModeOn)
    TestMode = WasTestModeOn

#Schedule a job 12 hours later to retweet/boost the post(s)!
def reboost():
    #Read CSV file if lists are empty; script must've crashed or exited!
    if len(twitterposts) == 0 and len(mastoposts) == 0:
        print("Now reading post IDs from CSV...")
        with open('files/posts.csv', newline='') as f:
            reader = csv.reader(f)
            postids = list(reader)

        print(postids)

        for i, id in enumerate(postids):
            if i > 0: #don't use first row, it has the names
                mastoposts.append(id[0])
                twitterposts.append(id[1])
    
    #Now we boost/retweet!
    for tweet in twitterposts:
        print(tweet)
        if int(tweet) != 0: #don't do if it's blank
            try:
                twitter_api.retweet(int(tweet))
            except:
                print("Failed to retweet ", tweet)
    for toot in mastoposts:
        print(toot)
        if int(toot) != 0: #don't do if it's blank
            try:
                mastodon_api.status_reblog(int(toot))
            except:
                print("Failed to boost ", toot)


def schedulethejobs():
    schedule.every().day.at(jobtime).do(pokepost)
    schedule.every().day.at(jobtime2).do(reboost)

rescheduletherescheduler = False #not a confusing variable name whatsoever

#Schedule a job every hour to check for time differences, mianly used for Daylight Savings detection!
def checkdifference():
    global rescheduletherescheduler
    timebefore = jobtime
    getdaytoday(True)
    if timebefore != jobtime:
        print("Time difference detected, resetting the job schedule!")
        schedule.clear()
        schedulethejobs()
        rescheduletherescheduler = True

if Continous:
    schedulethejobs()
    schedule.every().hour.do(checkdifference)
    if lastcallrun: #bypasses the schedule just once
        lastcallrun = False
        pokepost()
    while True:
        schedule.run_pending()
        time.sleep(1)
        if rescheduletherescheduler:
            schedule.every().hour.do(checkdifference)
            print("Jobs reset!")
            rescheduletherescheduler = False
        #print("amount today:", pokemontoday)
else:
    pokepost()
    #print("amount today:", pokemontoday)
