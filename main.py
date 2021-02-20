from header import *
import discord, asyncio, json, random, time, pickle, math, threading, datetime, string
"""
    I keep checking to make sure its not princessprolapse posting fake nekos
    - Make a system that posts fake nekos
"""
async def load_data():
    for guild in merlin.guilds: 
        if guild.id not in servers:
            servers[guild.id] = Server()
        else:
            servers[guild.id] = update(servers[guild.id], Server)
        for member in guild.members:
            if member.id not in users:
                users[member.id] = User()
            else:
                users[member.id] = update(users[member.id], User)

        for channel in guild.channels:
            if channel.id in cached['c']:
                await runCache(channel)

    # data corruption check
    for server in servers:
        if servers[server] == None:
            servers[server] = Server()
            print("... Found a corrupted server.")

async def runCache(msg, limit=10000):
    d = time.time()
    validChars = list(string.ascii_letters)
    async for message in msg.channel.history(limit=limit):
        if message.author.id == merlin.user.id:
            continue
        if message.content == "" or message.content[0] not in validChars:
            continue
        if message.author.id not in cached:
            cached[message.author.id] = {}
        if msg.channel.id not in cached[message.author.id]:
            cached[message.author.id][msg.channel.id] = []
        cached[message.author.id][msg.channel.id].append(message.content)
    if msg.channel.id not in cached['m']:
        cached['m'].append(msg.channel.id)
    print(f"Cache complete! took {time.time() - d} time")

def give_arguments(string):
    array = []
    # this is a regex thing, guess I'll figure it out someday.
    return array

def passive_generation():
    while True:
        for user in users:
            users[user].currency += 0.00002
        meta.time_passed += 1
        time.sleep(1)

def calculateXP(msg):
    XPGain = len(msg.content)/100+0.004
    if msg.channel.id in msg.sd.special_channels:
        XPGain *= 2
    msg.ud.xp += XPGain # fuck level systems. im going to make something complex to piss off autists
    msg.sd.gainedXP += len(msg.content)/100+0.004
    if msg.og.attachments:
        msg.sd.gainedXP += len(msg.og.attachments)/10+0.01
    if msg.ud.xp > msg.ud.highestXP:
        msg.ud.highestXP = msg.ud.xp # this is for display, so they dont catch on

    # simply variables for complex equations time.
    x, y = msg.ud.xp, msg.ud.level
    if x > 2*y*(math.log10((math.tan(x/y)*math.tan(x/y))*math.pi*math.e)*-1): # (level)log(tan(xp/level)^2*pi*e
        autist_tax = random.randint(0, 100)
        if autist_tax > 98:
            msg.ud.level -= random.randint(1, 3) # :)
            msg.sd.retards += 1
            msg.ud.retard_score += 1
            msg.sd.gainedLevels -= 1
        msg.ud.level += 1
        msg.sd.gainedLevels += 1
        msg.ud.xp = 0

def get_rank():
    array = []
    for user in users:
        array.append([user, users[user].currency])
    def k(sort):
        return sort[1]
    
    array = sorted(array, key=k)
    print(array)
    

async def check_permissions(msg):
    if not msg.meta[0] or msg.author.id == meta.owner_id or eval(f"msg.author.permissions.{msg.meta[0]}"):
        return True
    return False

def user_exists(info, msg=False):
    try:
        info = int(info)
    except:
        pass
    if isinstance(info, int):
        x = merlin.get_user(info)
        if x == None and msg:
            return msg.author
        return x
    elif isinstance(info, str):
        if info.startswith("<@"):
            info = info.strip("!")
        for member in msg.og.guild.members:
            if member.name == info:
                return member
            elif member.mention == info:
                return member
    elif isinstance(info, discord.Member):
        return info
    else:
        return False

def channel_exists(info, msg=False):
    try:
        info = int(info)
    except:
        pass
    if isinstance(info, int):
        x = merlin.get_channel(info)
        if x == None and msg:
            return msg.channel
        return x
    elif isinstance(info, str):
        for channel in msg.og.guild.text_channels:
            if channel.name == info:
                return channel
    elif isinstance(info, discord.TextChannel):
        return info
    else:
        return False

def generateWords(size, dataset):
    sentence = ""
    curSize = 0
    while curSize < size:
        luck = random.randint(1,5)
        pickings = random.choice(dataset).split()
        pickingsVal = 0
        for i in range(luck):
            if len(pickings)-1 < curSize + i:
                if len(pickings) <= 1:
                    break
                if pickingsVal > len(pickings):
                    break
                tooAdd = pickings[random.randint(1, len(pickings)-1)]
                sentence += str(tooAdd)+" "
                curSize += 1
                pickingsVal += 1
                break
            tooAdd = pickings[curSize]
            sentence += str(tooAdd)+" "
            curSize += 1
            pickingsVal += 1
    return sentence
def generateASimulate(i, c): #id of user, channel defaults to false
    # generate the data set -- completely.
    if c:
        data = cached[i][c]
    else:
        data = []
        for t in cached[i]:
            for ddt in cached[i][t]:
                data.append(ddt)
    check = []
    if len(data) > 8000:
        # too long to search through
        for _ in range(8000):
            check.append(random.choice(data))
    else:
        check = data
    size = len(random.choice(check).split())
    if size < 1:
        size = 1
    to_send = generateWords(size, check)
    return to_send

async def SCE(c, msg): # you see, sub-command easifier.
    d = dict_from_class(c())
    if len(msg.split) < 2 or msg.split[1] not in d:
        string = f"{c.__name__} has the following subcommands:"
        for thing in d:
            string = f"{string}\n`{thing}`"
        await msg.channel.send(string)
        return
    else:
        return eval(f"x.{msg.split[1]}(msg)")

async def MessageTask(message, to_format, variable, name, time_wait):
    meta.storage[name] = 1
    while meta.storage[name]:
        await message.edit(content=to_format.format(variable))
        variable += time_wait
        await asyncio.sleep(time_wait)
    return variable

class Merlin(discord.Client):
    async def on_ready(self):
        if not meta.ready:
            await load_data()
            print("-\n", len(servers), "servers\n", len(users), "users\n", len(commands), "commands\n-")
            meta.ready = True
        print("{0.user.name} reporting for duty.".format(merlin))

    async def on_message(self, message):
        if not meta.ready or message.author.id == merlin.user.id:
            meta.denies += 1
            return
        if message.channel.type == "private":
            print("(DM){0.author}: {0.content} ({0.author.id})".format(message))
            meta.dms += 1
        else:
            print("{0.author}: {0.content} ({0.channel.name}, {0.guild.name})".format(message))
            meta.messages += 1
        msg = Message(message)

        try:
            users[message.author.id].messages += 1
        except KeyError:
            users[message.author.id] = User()

        msg.ud = users[message.author.id]
        msg.sd = servers[message.guild.id]

        curGain = len(message.content)/14000+0.00004
        if msg.channel.id in msg.sd.special_channels:
            curGain *= 2
        msg.ud.currency += curGain

        calculateXP(msg)
        if not msg.content.startswith(msg.sd.prefix):
            if msg.author.id not in cached:
                cached[msg.author.id] = {}
            if msg.channel.id in cached['c']:
                if msg.channel.id not in cached[msg.author.id]:
                    cached[msg.author.id][msg.channel.id] = [message.content]
                    cached['c'].append(message.id)
                    if msg.channel.id not in cached['m']:
                        cached['m'].append(msg.channel.id)
                else:
                    cached[msg.author.id][msg.channel.id].append(msg.content)
                    cached['c'].append(message.id)
                    if msg.channel.id not in cached['m']:
                        cached['m'].append(msg.channel.id)

        if msg.content.startswith(msg.sd.prefix):
            await self.on_parse(msg)

        for _ in message.attachments:
            msg.ud.currency += 0.02

        users[message.author.id] = msg.ud
        servers[message.guild.id] = msg.sd

        if meta.time_passed > 30:
            pickle.dump(users, open("users.data", "wb"))
            pickle.dump(servers, open('servers.data', 'wb'))
            pickle.dump(cached, open("cached.data", "wb"))
            meta.time_passed = 0

    async def on_parse(self, msg):
        msg.content = msg.content[len(msg.sd.prefix):]
        if msg.content[:len(msg.sd.prefix)-1] == msg.sd.prefix:
            return
        msg.split = msg.content.split()
        msg.arguments = give_arguments(msg.content[len(msg.split[0])+1:])
        msg.without_content = msg.content[len(msg.split[0])+1:]
        if msg.split[0] in commands:
            msg.meta = commandm[msg.split[0]]
            if await check_permissions(msg):
                if len(msg.split)-1 >= msg.meta[1]:
                    await commands[msg.split[0]](msg)
                else: 
                    if msg.sd.fluff:
                        await msg.channel.send(f"`You did not give enough arguments for {msg.split[0]} to function.`")
            else:
                if msg.sd.fluff:
                    await msg.channel.send(f"`You do not have the permissions for {msg.split[0]}.`")
        else:
            if msg.sd.fluff:
                await msg.channel.send(f"`You {msg.content}, sure.`")

class Commands:
    async def mimic(self, msg):
        await msg.channel.send(msg.without_content)

    async def help(self, msg):
        x = discord.Embed()
        x.title = f"Help for {msg.split[1].capitalize()}"
        x.color = discord.Color.purple()
        meta = commandm[msg.split[1]]
        x.add_field(name="Description", value=meta[2].format(msg), inline=False)
        x.add_field(name="Syntax", value=meta[3].format(msg), inline=False)
        if meta[0]:
            x.add_field(name="Permissions", value=meta[0], inline=True)
        if meta[1]:
            x.add_field(name="Arguments", value=meta[1], inline=True)
        await msg.channel.send(embed=x)

    async def commands(self, msg):
        # parameters - filters to filter commands by.
        # do that later. default is permissions going downwards
        # organize into lists
        organized = {"None": [], "Manage guild": [], "Owner only": []}
        for command in commands:
            command_meta = commandm[command][0]
            if command_meta == 0:
                command_meta = "None"
            command_meta = command_meta.replace("_", " ").capitalize()
            organized[command_meta].append(command)
        x = discord.Embed()
        x.title = "Merlin Commands"
        x.color = discord.Color.purple()
        for permission in organized:
            string = ""
            for command in organized[permission]:
                string = f"{string}\n`{command.ljust(12)}` - {commandm[command][2]}"
            x.add_field(name=permission, value=string, inline=False)
        await msg.channel.send(embed=x)

    async def cash(self, msg):
        if len(msg.split) < 2:
            target = msg.author
        else:
            target = user_exists(msg.split[1], msg=msg)
        if target:
            x = discord.Embed(description=f"**{target}** has **{users[target.id].currency:0.2f} {msg.sd.currency_name.capitalize()}**", color=discord.Color.purple())
            await msg.channel.send(embed=x)
        else:
            await msg.channel.send("`You specified something that wasn't a user.`")

    async def simulate(self, msg):
        if len(msg.split) < 2:
            target = msg.author
        else:
            target = user_exists(msg.split[1], msg=msg)
        if len(msg.split) > 2:
            chnl = channel_exists(msg.split[2], msg=msg).id
        else:
            chnl = 0
        response = generateASimulate(target.id, chnl)
        await msg.channel.send(f"**{target.name} says:**\n> {response}")

    async def insult(self, msg):
        target = user_exists(msg.split[1], msg=msg)
        if target:
            await msg.channel.send(f"{target.mention} {random.choice(msg.sd.insults)}")
        else:
            await msg.channel.send("`Not a valid user.`")
    
    async def objectirray(self, msg):
        string = f"List of insults for server {msg.og.guild.name}"
        for insult in msg.sd.insults:
            string = f"{string}\n`{insult}`"
        await msg.channel.send(string)

    async def objectify(self, msg):
        msg.sd.insults.append(msg.without_content)
        await msg.channel.send(f"`Your shitty insult \"{msg.without_content}\" has been added to the list.`")
    
    async def unobjectify(self, msg):
        try:
            msg.split[1] = int(msg.split[1])
        except:
            pass
        try:
            if isinstance(msg.split[1], int):
                for_removal_message = msg.sd.insults[msg.split[1]]
                msg.sd.insults.remove(msg.sd.insults[msg.split[1]])
            else:
                for_removal_message = msg.split[1]
                msg.sd.insults.remove(msg.split[1])
            await msg.channel.send(f"`Insult {for_removal_message} removed.`")
        except:
            await msg.channel.send("`That insult is not in the list of insults! Use an index or the FULL THING.`")

    async def kill(self, msg):
        target = user_exists(msg.split[1], msg=msg)
        if target:
            luck = random.randint(0, 3)
            kill_strings = [
                f"{msg.author.mention} waits in a lookout tower, waiting for {target.mention}'s usual trip to %s. %d %s pass by, before {msg.author.mention} %s and %s {target.mention} to death."%(
                    random.choice(["the store", "hell", "their favourite waterfall", "their favourite Italian restraunt", "work"]),
                    random.randint(1, 8),
                    random.choice(["minutes", "hours", "weeks", "months", "days"]),
                    [
                        "cocks his rifle, aims",
                        "grabs out his knife, does an epic jump from the tower",
                        "calls in an orbital strike",
                        "slices open his palm for the final drop of blood"
                    ][luck],
                    [
                        "shoots",
                        "stabs",
                        "nukes",
                        "rituals"
                    ][luck]
                )]
            await msg.channel.send(random.choice(kill_strings))
        else:
            await msg.channel.send("`Not a valid user.`")

    async def stats(self, msg):
        errored = False
        if len(msg.split) < 2:
            target = msg.author
        else:
            target = user_exists(msg.split[1])
            if not target:
                target = msg.author
                errored = True
        
        x = discord.Embed()
        x.color = discord.Color.purple()
        x.title = f"Stats for {target.name}" # this is the slowest fucking command
        x.description = "This is a really long message so it doesn't format like GARBAGE"
        user = users[target.id]
        x.add_field(name="Messages", value=user.messages, inline=False)
        x.add_field(name=msg.sd.currency_name.capitalize(), value=f"{user.currency:0.2f}", inline=False)

        x.add_field(name="Level", value=user.level, inline=True)
        x.add_field(name="XP/Required XP", value=f"{user.xp:0.2f}/{2*user.level*math.log10(math.tan(user.xp/user.level)*math.tan(user.xp/user.level)*math.pi*math.e)*-1:0.2f}", inline=True)
        x.add_field(name="Highest XP", value=f"{user.highestXP:0.2f}", inline=True)

        if errored:
            x.footer = "This user gave a parameter for target, but it errored out."

        await msg.channel.send(embed=x)

    async def stimulate(self, msg): # upgrade later,  nobody wants currency anyway.
        luck = random.randint(0, 15)*0.1
        mistake = random.randint(0, 90)
        if mistake > 85:
            luck *= 10
            await msg.channel.send(f"**{msg.author.name}** is zapped with the force of **{luck:0.1f} suns**- er, **{msg.sd.currency_name}**")
        else:
            await msg.channel.send(f"**{msg.author.name}** is zapped with the force of **{luck:0.1f} {msg.sd.currency_name}**")
        msg.ud.currency += luck
    
    async def flip(self, msg):
        def convert(x):
            x = x.lower()
            if x in ["t", "tails"]:
                return 0
            elif x in ["h", "heads"]:
                return 1
            elif x in ["s", "sides"]:
                return 2
            return -1
        def back(x):
            if x == 0:
                return "Tails"
            elif x == 1:
                return "Heads"
            else:
                return "Side"
            return -1
        choice = convert(msg.split[1])
        if choice < 0:
            await msg.channel.send("`Parameter for side to guess should be\n- Heads [heads, h]\n- Tails [tails, t]\n- Side [side, s]`")
            return
        try:
            amount = int(msg.split[2])
        except:
            await msg.channel.send("`Parameter for amount to bet wasn't a number.`")
            return
        if amount > msg.ud.currency:
            await msg.channel.send(f"`You don't have enough {msg.sd.currency_name} for that.`")
            return
        luck = random.randint(0, 1000)
        if luck > 500:
            answer = 0
        elif luck < 500:
            answer = 1
        else:
            answer = 2
        
        special = random.randint(0, 100)
        if special > 95:
            flavor1 = "The coin flips high into the air!"
        elif special > 60:
            flavor1 = "The coin flips up to a decent height."
        elif special > 40:
            flavor1 = "A standard coinflip."
        elif special > 20:
            flavor1 = "Nice one, it hardly even got a chance to flip."
        else:
            flavor1 = "Do you know how to flip?!"

        msg.ud.currency -= amount
        if answer == choice:
            flavor2 = "You guessed right!"
            flavor3 = f"You win {amount*2} back."
            msg.ud.currency += amount*2
        else:
            flavor2 = "You were wrong."
            flavor3 = "You lose your bet."

        await msg.channel.send(f"Your {amount} {msg.sd.currency_name} is bet, and the coin is flipped! {flavor1}\n||{back(answer)}\n{flavor2} - {flavor3}||")
    
    async def change(self, msg):
        class sub:
            async def ldisplay(self, msg):
                if msg.sd.allow_level_display:
                    new = flip(msg.ud.level_display)
                    msg.ud.level_display = new
                    await msg.channel.send(f"{msg.author.mention} your level display has been set to {new}")
                else:
                    await msg.channel.send("Your server does not allow you to display your level.")
        await SCE(sub, msg)

    async def stanch(self, msg):
        # idk how to do this
        class sub:
            async def log(self, msg):
                if len(msg.split) < 3:
                    channel_id = msg.channel.id
                else:
                    channel_id = int(msg.split[2])
                msg.sd.log_channel = channel_id
                await msg.channel.send(f"`Server log channel ({channel_id}) set.`")
            async def verbose(self, msg):
                if len(msg.split) < 3:
                    verbosity = flip(msg.sd.verbose)
                else:
                    verbosity = bool_convert(msg.split[2])
                msg.sd.verbose = verbosity
                await msg.channel.send(f"`Server verbosity set to {str(verbosity)}`")
            async def prefix(self, msg):
                if len(msg.split) < 3:
                    msg.channel.send(f"`Not enough arguments.`")
                else:
                    msg.sd.prefix = msg.split[2]
                    await msg.channel.send(f"`Server prefix set to {msg.split[2]}`")
            async def ldisplay(self, msg):
                new = flip(msg.sd.allow_level_display)
                msg.sd.allow_level_display = new
                await msg.channel.send(f"`Server allowing users to opt-in to displaying their level in their nickname set to {new}`")
        await SCE(sub, msg)

    async def cache(self, msg):
        sent = await msg.channel.send("`Caching this channel...`")
        d = time.time()
        loop.create_task(MessageTask(sent, "`Caching this channel... {0} seconds`", 0, 'cache', 5))
        await runCache(msg)
        meta.storage['cache'] = 0
        x = discord.Embed(title=f"Cache complete! Took {int(time.time() - d)} seconds.", color=discord.Color.purple())
        await sent.edit(content="", embed=x)

    async def fullCache(self, msg):
        sent = await msg.channel.send("`Caching this channel...`")
        d = time.time()
        loop.create_task(MessageTask(sent, "`Full caching this channel, hold on tight... {0} seconds`", 0, 'fcache', 10))
        await runCache(msg, limit=9999999999999999)
        meta.storage['fcache'] = 0
        flavor = ""
        if time.time() - d > 300:
            flavor = ", Jesus Christ"
        elif time.time() - d > 150:
            flavor = ", I'm glad it's done"
        elif time.time() - d > 60:
            flavor = ", that took forever"
        x = discord.Embed(title=f"Full cache complete{flavor}! Took {int(time.time() - d)} seconds.", color=discord.Color.purple())
        await sent.edit(content="", embed=x)

    async def rawsend(self, msg):
        await msg.channel.send(eval(msg.without_content))

    async def specializeThisOne(self, msg):
        msg.sd.special_channels.append(msg.channel.id)
        await msg.channel.send("`Channel added to special channels.`")

    async def clearCache(self, msg):
        num = 0
        for x in cached:
            num += 1
            if x == 'c' or x == 'm':
                cached[x] = []
                continue
            cached[x] = {}
        await msg.channel.send(f"`Cleared the cache in {num} channels.`")

    async def save(self, msg):
        pickle.dump(users, open("users.data", "wb"))
        pickle.dump(servers, open('servers.data', 'wb'))
        pickle.dump(cached, open("cached.data", "wb"))
        await msg.channel.send("I saved it for you master :33")


merlin = Merlin()

users = try_load("users.data", {})
servers = try_load("servers.data", {})
cached = try_load("cached.data", {'m': [], 'c': []})
meta = Meta()

commandm = json.load(open("commands.json"))
commands = dict_from_class(Commands())

loop = asyncio.get_event_loop()

try:
    print("Starting...")
    t = threading.Thread(target=passive_generation)
    t.start()
    loop.run_until_complete(merlin.start("token")) # 
except KeyboardInterrupt:
    loop.run_until_complete(merlin.logout())
finally:
    loop.close()