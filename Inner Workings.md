![What Pokémon Day is it today? (inner workings)](misc/md/header3.png)

This document contains a brief overview of the inner workings of this code, hopefully in a way that people can understand! I wrote this up for funsies really, just because I thought it'd be a neat read.

![Initialization](misc/md/header4.png)

When the script first starts, it initializes a configuration file if nessecary. If `DownloadAllPics` is set to true, then, if there's an incomplete set, or if there's no pictures at all, it grabs all the nessecary pictures from a service known as PokéAPI! They store all of their pictures like **85.png** to represent the National Pokédex number for each Pokémon. If `DownloadAllPics` isn't set to true, then we download the individual files much later instead.

Then, it gets today's date & time according to the system clock. Once that's done, it changes the timezone into JST in order to accurately gather what the current date is in Japan, ideal for running the script a little bit past midnight JST. If `TestDate` is set, then instead of using today's date, it will use whatever's in the configuration file by the month and day. The script converts the date into a string (i.e. "02/07" for Feburary 7th) so it can compare to the calendar later.

![Getting time!](misc/md/header5.png)

This shouldn't be so hard right? Well, for the purposes of this script, I need it to run whenever it's midnight in JST. This, compounded on top of the need to account for when it is or isn't daylight savings in my timezone (JST doesn't practice daylight savings, ergo time differences occur) necessitated me to make an elegant way of telling the time differences.

This script uses it's own scheduler (provided by a python library) to determine when it's time to start everything else this script needs to do, i.e. get calendar info, post the actual stuff, etc! So, with that said, let's calculate the time!

Using various libraries, we can get an accurate time delta between our current timezone and JST. For this example, we'll use my timezone, *EST*, and assume we're not currently in Daylight Savings. My timezone's UTC offset is -5, while JST's UTC offset is 9. Combined together, we get a time delta of 14. Now how do we use this? Simple, we do `24 - 14`, with 24 being the hours in a day of course, which gives us **10**! That's when midnight is in Japan, but in our local timezone! We also take this and add 12 to get the time for the second job this script does, which is to retweet/boost our post in the future, for those who might've missed out on it the initial time around! 

Additionally there's code to account for overflows, i.e. if midnight JST is 1 PM for you, the boosting job's time would end up reading out as *25* hours instead! So we just subtract 24 from it if it goes above or is equal to 24, giving us the first hour of the day instead, problem solved!

From this point, one of two things will happen; either we wait for the correct time to post, or if "Continous" isn't turned on in the config, we just go ahead and post! Either way, when this happens, an intentional pause happens and the console outputs "Starting script in 3 seconds..."; this is meant to be a buffer to prevent posts from accidently going out when you didn't realize you set up the settings wrong (i.e. continous is turned off)!

![Calendar](misc/md/header6.png)

After initialization, we move on to the calendar. This is used because it's much, much easier to handle adding events, shuffling around events, etc. using a calendar interface rather than having to manually plug everything into, say, a spreadsheet. And of course it provides the added benefit of this calendar being more useful than just being used for a bot.

Using the provided `natdex.csv` file (created intitially by using data from PokéAPI), it converts the CSV into a readable list for Python, used for obtaining the Pokédex number of each individual Pokémon, which is used to get the correct picture needed for uploading.

Now, the script will try to download the calendar file from the provided configuration file. If it can't download it for any reason, it will assume one already exists and skips over this part. But if we can download, then if one is found, it creates a backup of the original .ics file, and downloads the new one in place. Now, it will attempt to initialize the calendar into a variable, by reading every entry in the calendar file. If an error occurs, it will assume the calendar download is corrupted, and replace the calendar file with the previously made back up, and try again.

Once the calendar file is initialized into a list, it iterates over the calendar to convert all of this into a more usable form for the script, in the form of a new list. The iteration function goes like so: It gets the event's date (i.e. Feburary 22), gathers the event name (i.e. Komala Day #ネッコアラの日), and then converts the date into a different form ("Feburary 22" -> "02/22"), used to compare against today's date, which we got eariler. If the date matches with today, then it will be added to a new list. 

I will elaborate more on the lists after this but first: These are split out into their own individual values. Take "Sylveon Day #ニンフィアの日" for instance. The value will be split up into "Sylveon", and "#ニンフィアの日", while dropping the "Day" entirely from this. This is to make phrase generation easier, since the Pokémon's name, and their associated hashtag (which is their Japanese name, followed by what is the equivalent of **'s Day**) need to be seperated. It's also important to keep the Pokémon's name free from having "Day" so that we can more easily look up their name for their image later on, we can just add it into the phrase later on anyways!

The list is nested, and can hold multiple pairs of up to 4 individual Pokémon. This is used because Twitter and Mastodon restricts how many images can be uploaded in a single post, and even if it didn't work like this, it'd also hit the 280 character limit anyways. If the first list is filled up with 4 Pokémon, it will move on to a second list. If that is somehow filled up (it most likely shouldn't), it will go on to a third list, and so on. Theoretically if there were somehow 50 Pokémon in a single day (there isn't), this script would handle it!

![Phrases](misc/md/header7.png)

Now, we move on to generating the phrase we need to post. A lot of what is done here is just stuff I did to add character, to make it not as monotonous when a new post is being put out.

The phrase generation portion uses a function so that it can be used for when there's multiple tweets (i.e. 6 Pokémon means 4 for the first post, 2 for the second). It starts by starting off with "Hello everyone", because that's just a friendly phrase yeah? Next, it goes through a set of randomizations, just so the phrase isn't the same one for every single tweet posted. There are various sets of phrases that can be tacked on at this point, going from "Hello everyone, today is February 21st! And it's currently..", to "Hello everyone! Today is February 21st, and it's now..", etc. etc.

Next, we go onto combining all the different Pokémon that is going to be represented in this tweet. If it's the last entry, it ends with ".. Day!", if it's the second to last entry, it does ".. Day, and ..", otherwise it does ".. Day, ..". It's set up like this so that if there's just 1 Pokémon today, it will treat it as the last entry, since that's what it technically is!

After that, we begin to gather the file-names, which will be discussed in the next section. Then after that, the hashtags are gathered from the splitting of the value found earlier (the "Sylveon", and "#ニンフィアの日" thing). A line break is first formed, then each hashtag is put next to each other with a space seperating them. With that, the phrase is fully generated! The result is something like this:
```
Hello everyone, today is February 18th! And it's now Dragonite Day, and Snivy Day!
#カイリューの日  #ツタージャの日
```

All of this is stored in a variable called `postresponse`!

For Mastodon exclusively, the instance this runs on might have Pokémon emojis (the one the official bot uses does), and as such, it'd be nice to use them! For this, we make another line break, and using a cache of the emojis the server has, we compare the list of today's Pokémon with the list of emojis the server has. If it finds the emoji, then we use that emoji! It's formatted like this: ":sylveon: :pikachu:", etc.

![Filenames](misc/md/header8.png)

This is part of the phrase generation function, but it's worth splitting out here. Now, we get to use the CSV file from earlier.

One would think the easiest method would involve using each individual Pokémon's names as the files (i.e. "Pikachu.png"), however that comes with the drawback that I'd need to manually download **898** images. On top of that, it would be a hassle to include all of these in this repo, and I'm especially not about to draw 898 Pokémon for this project.

So, what do we do? We use National Pokédex. If you know your Pokémon, you know they have their own National Pokédex number (i.e. 001 for Bulbasaur, 025 for Pikachu, 700 for Sylveon, etc.), and as such we can easily use this to extrapolate what image we need to use, since the aformentioned PokéAPI stores official artwork for each individual Pokémon by their National Pokédex number.

The CSV file contains each Pokémon by their National Pokédex ID, ergo we can just compare them to their National Pokédex number, which is what the script does. There are special exceptions for Lucario and Nidoran, since the calendar lists their names with unique attributes, requiring such modification. Once those special exceptions are taken care of, we compare their name against the CSV list, to see what pokédex number they are associated with. Once found, if `zfiller` is enabled in settings, it will add trailing zeroes (i.e. *0*69), and generate the filename (i.e. `069`), which then gets added to a list specifically for filenames. The reason why `zfiller` exists is for filenames that require it, i.e. the official Pokémon website did it in this way, which is what this script initially relied on!

The filename isn't fully complete yet, and that's for a reason. The default settings has this script automatically download the needed pictures from the PokéAPI repository, on a per-use basis, so as an example, this script would try to download `https://coolwebsite.com/assets/69.png` to the pic folder. However, it won't download it if the file already exists in the first place! After the check and download is done, then it appends ".png" to the end, i.e. `69.png` so that it can be uploaded!

![Posting!](misc/md/header9.png)

After all of this, getting the calendar, getting the phrase, and getting the required pictures, now we're ready to post! This is the part of the script that actually relies on the Twitter/Mastodon API! For everything mentioned here about the API, it applies to both the Twitter and Mastodon API!

If we're in TestMode (used to test things, duh!), instead of creating the post, we generate the phrase in the console, to show what phrase would've been posted, alongside what images would've been attached, and that's it!

If we're not in TestMode, then we do the following: Create a list called `media_ids`, and use Twitter's and/or Mastodon's media upload API to upload the needed images to the websites. All of their IDs are appended to `media_ids`, for use in the post. Once that's done, we create the post, using the variable titled `postresponse`, and the image IDs list. And viola, after all of this, we've made the post! The post ID is stored in a list for either Twitter or Mastodon, either called `twitterposts` or `mastoposts`! We use this to reference later, mainly to retweet later! The values in both of those lists are stored in a file called `posts.csv`, which will be used if the scrpit unexpectedly closes and we need to retrieve the IDs for boosting/retweeting.

And now, we've made the first posts! If there's >4 Pokémon, then the first 4 entries of the list is removed, and we start back at **Phrases** again! This keeps repeating until the list is empty, then we're done!

![Tomorrow?](misc/md/header10.png)

This script does one last final thing; it sets the date one day forward and checks the resulting outcome for the next day! This is so whenever I check the console output, I can verify that the next day won't have any issues. It sets `TestMode` to be true so that the output isn't also posted by accident! After it's all done, it reverts TestMode to the last value it was set (i.e. if it was on, it stays on, if it wasn't, it turns back off)

![Boosting](misc/md/header11.png)

At the start of the script we got the time delta for midnight JST. Well, in that process, we also got the time for noon JST as well, since that's just midnight + 12 yeah? We do this to account for people waking up in different timezones who might be following the account, or just as a little reminder for anyone in general!

Earlier we stored the output of the posts we just made, it's a whole list of things relating to the post, such as info about who posted it, what time it was done, but most importantly were the IDs. We take these IDs, and we shove 'em into the API to retweet/boost them, and...yeah, we do just that! We just iterate through the list to get all of the IDs to retweet/boost, simple!

![But why?](misc/md/header12.png)

Why go through all this effort just for a Twitter/Mastodon/Discord bot? Frankly, because it's fun!

I've wanted to do serious coding for a good long while now, going back to when I started making crude lua scripts for my Roblox places back in the early 2010's. In the past 2 years, I started lua scripting for both Sonic Robo Blast 2, and Super Mario Bros. X2, which was really fun! I figured since I knew lua, Python shouldn't be that hard to learn, so, I eventually found an application where I'd want to use it: For my "What Pokémon Day is it today?" Twitter!

Up until this python script was made, I've been doing this all by hand. Whenever a day on the calendar approached, I'd have to manually look up the images, paste them into Twitter, schedule them to post at the right time, and go from there. This could've all been easily automated, so...I automated it! And I had lots of fun learning Python just to do this!