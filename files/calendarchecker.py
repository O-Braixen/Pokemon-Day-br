#Does checks on the pokemon.ics file: Which Pokemon has correct names, which have malformed names, and which ones do not exist on the calendar at all.

import csv
from icalendar import Calendar, Event
from datetime import datetime, timezone
import pytz
import shutil

#checks all entries in the calendar to make sure there's no pokemon with malformed names
#if there are, add them to a list and print it out

g = open('files/pokemon.ics','rb')
gcal = Calendar.from_ical(g.read())
with open('files/natdex.csv', newline='') as f:
    reader = csv.reader(f)
    pokedex = list(reader)

utc_dt = datetime.now(timezone.utc)
togay = utc_dt.astimezone()

year = togay.strftime("%Y")

missingpokemon = pokedex.copy()

correctnames = []
malformednames = []

for number in range(1, 365): #365 days in a year!
    day_num = str(number)
    day_num.rjust(3 + len(day_num), '0')
    Day2Test = datetime.strptime(year + "-" + day_num, "%Y-%j").strftime("%d")
    Month2Test = datetime.strptime(year + "-" + day_num, "%Y-%j").strftime("%m")

    togay = datetime(int(year), int(Month2Test), int(Day2Test), 00, 00, 10)
    togay = togay.astimezone(pytz.timezone("Asia/Tokyo"))
    for event in gcal.walk('vevent'):
        start = event.get('dtstart') #what day?
        summary = event.get('summary') #date name
        dater = start.dt.strftime("%m/%d") #convert to MM/DD

        isittime = togay.strftime("%m/%d") == dater #determine if the current event this iteration matches up with today's date!
        if isittime == True:
            summary = summary.replace(' Day ', ' ')
            summary = summary.split()
            #Generate new hashtag, the ones on the calendar are Untrustable, and i'm too lazy to fix them
            GotName = False
            PokeDex = 0
            for pokemon in pokedex:
                if pokemon[1] == summary[0]:
                    summary[1] = "#" + pokemon[2] + "の日"
                    GotName = True
                    PokeDex = pokemon[0]
            #insert pokemon into the list
            if GotName:
                correctnames.append(summary)
                for index, pocketmonster in enumerate(missingpokemon):
                    if pocketmonster[0] == PokeDex:
                        del missingpokemon[index]
            else:
                malformednames.append(summary)
            print(summary)

print("RESULTS!")
print("Correct names:")
print(correctnames)
print("Malformed names:")
print(malformednames)
print("Writing Missing Pokemon to list...")

rows = []
for index, writer in enumerate(missingpokemon):
    if index > 0:
        rows.append(writer)

for poke in rows:
    poke[2] = "#" + poke[2] + "の日"

fields = ['No.', 'Name', 'Name(JPN)']

try:
    shutil.copyfile("files/missing.csv", "files/missing.csv.bak")
    print("Backed up original missing.csv file!")
except:
    pass

with open("files/missing.csv", 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)
    csvwriter.writerows(rows)
    csvfile.close()