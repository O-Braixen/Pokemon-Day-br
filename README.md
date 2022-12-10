![What Pokémon Day is it today? (python code)](misc/md/header1.png)

This repo contains the code used to run "**What Pokémon Day is it today?**" on [Twitter](https://twitter.com/WhatPokeDayIsIt), and [Mastodon](https://donphan.social/@WhatPokeDayIsIt), and Discord! I've released this source code, mainly to also allow users to run this on their own Discord server, but also just for fun! If you want to read about how this code functions (in layman's terms), check out [this MD file](Inner Workings.md)!

Special thanks goes to [PokéAPI](https://pokeapi.co) for providing a lot of the data used here, i.e. Pokémon's names, their National Pokédex numbers, etc!

![Usage](misc/md/header2.png)

To use this, first make sure you are running Python 3.9.9/3.10.x. Python 3.8 *might* work, but it's untested and as such unsupported; anything lower than 3.8 will not work. Ensure you also have **pip** installed. If you plan on using this for Twitter, you'll need to have **Elevated Access** for the API. If you want to use this for Mastodon, just make sure your instance allows bots, and that you can generate one!

And if you plan on using this for Discord, ensure you have permissions to add bots, and just follow the [instructions here](https://novus.readthedocs.io/en/stable/discord.html); for permissions in the **Inviting Your Bot** section, just tick "*Send Messages*" and "*Read Messages/View Channels*", and make sure to get your *Bot Token*!

Click [here](https://gitlab.com/EeveeEuphoria/pokeday/-/releases/), go to the latest release, and click **Download Me! (zip)** to download the files needed. Once done, extract it somewhere you'll want to easily access. Next, navigate to the extracted directory, then use `pip install -r requirements.txt` to install all the modules used for this. If this doesn't work, use `python3 -m pip install -r requirements.txt`, or if you're on Windows, use `py -3 -m pip install -r requirements.txt`.

**This is important:** depending on your use-case for this, you'll want to install the corresponding pip package. If you want to use this for *Discord*, use `pip install novus`, for *Mastodon*, use `pip install Mastodon.py` and for *Twitter*, do `pip install tweepy`. If these commands errors out, replace `pip install` with `python3 -m pip install -U`, or if you're on Windows, use `py -3 -m pip install -U`.

If you plan on using the `createcsv.py` script, you'll also need to use PokéBase for PokéAPI usage; just use `pip install pokebase`.

Once that's done, run `main.py` to initialize the configuration file used for this, and to test that the script actually functions. If all goes well, you should see an output like this: `Config file not found or corrupt! Generating a new one and exiting!`

You should now see a `config.ini` file in your folder, open it in your favorite flavor of text editor. There will be comments showing how to set this up from here!

When you run the script now, if you get no errors, then tada, it all works! Do note that if you have "Continous" set to false, you'll need to *manually* run this script at the correct time; you shouldn't need to do this since the script can run all by it's own at the correct times, but if you desire that control, you have the ability to do that! The only other feature you'll miss out is the automatic retweet/boost function that occurs after 12 hours.

If you plan on re-using the code for this project in something else, you can get your own .ics file from Google Calendars. Go to the settings of the calendar in question, scroll down to **Integrate calendar** and find *Public address in iCal format*, you can use that as the URL instead.

If you want to customize this for your own usage (i.e. non-Pokémon related usages), you'll have to do your own scripting from here! I've tuned this script specifically for the intricacies of using a calendar file, full of dates that have titles like "Sylveon Day #ニンフィアの日", etc. There's plenty of comments within the code to hopefully explain how this all works!