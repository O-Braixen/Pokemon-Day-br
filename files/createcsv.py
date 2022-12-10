#Creates the natdex.csv file if it does not already exist

import shutil
import pokebase as pb
import csv
from googletrans import Translator

translator = Translator()
rows = []

for number in range(1, 140):
    namer = pb.pokemon_species(number).names
    genero = pb.pokemon_species(number).genera
    writer = [str(number)]
    names = []
    genera= []
    for item in namer: #convert to easy to use list
        names.append([str(item.language), str(item.name)])
    for item in genero: #convert to easy to use list
        genera.append([str(item.language), str(item.genus)])

    for name in names:
        if name[0] == "en":
            writer.insert(1, name[1])
            print(name[1])
        elif name[0] == "ja":
            writer.insert(2, name[1])
            print(name[1])
        #elif name[0] == "roomaji":
        #    writer.insert(3, name[1])
        #    print(name[1])
        #for genus in genera:
        #    if genus[0] == "en":
        #        translated_text = translator.translate(genus[1], dest='pt')
        #        writer.insert(4, translated_text.text)
        #        print(translated_text.text)
        #    if len(writer) > 1:
        #        break
        if len(writer) > 3:
            break
    
    rows.append(writer)

print(rows)

fields = ['No.', 'Name(EN)', 'Name(JPN)','genus','Name(KO)']

try:
    shutil.copyfile("files/natdex.csv", "files/natdex.csv.bak")
    print("Backed up original missing.csv file!")
except:
    pass

with open("files/natdex.csv", 'w',encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)
    csvwriter.writerows(rows)
    csvfile.close()