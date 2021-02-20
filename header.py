import datetime

def try_load(file, default):
    import pickle
    try:
        return pickle.load(open(file, 'rb'))
    except FileNotFoundError:
        print("File not found, loading default.")
        return default # we don't save anymore.

class Message:
    def __init__(self, message):
        self.og = message
        self.content = message.content
        self.channel = message.channel
        self.author = message.author

class Meta:
    ready = False
    owner_id = 540426841203146754

    # stats
    denies = 0
    messages = 0
    dms = 0

    storage = {}

    time_passed = 0

class Server:
    messages = 0
    shade_list = []
    list_type = False

    currency_name = "faith"
    prefix = "~"
    fluff = True
    aliases = {}

    cachedChannels = {} # filled with various CacheMessages

    insults = [
        "empty",
    ]

    special_channels = [] # wtf is this for

    # personal
    log_channel = False
    extreme_logging = False
    verbose = False
    allow_level_display = False
    retards = 0
    gainedXP = 0
    gainedLevels = 0

class User:
    level = 1
    xp = 0

    highestXP = 0

    messages = 0
    currency = 0

    retard_score = 0

    nickname = False
    
    level_display = False

class CacheAuthor:
    def __init__(self, id, name, identifier, mention):
        self.id = id
        self.name = name
        self.identifier = identifier
        self.mention = mention

class CacheMessage:
    def __init__(self, content, author):
        self.content = content
        self.author = author

def flip(b):
    array = ["True", True, 1]
    if b in array:
        return False
    else:
        return True

def bool_convert(b):
    array = ["True", "1", 1, "true", "t"]
    if b in array:
        return True
    else:
        return False

def update(obj, default):
    default = default()
    for attribute, value in default.__dict__:
        if attribute not in obj.__dict__:
            obj = setattr(obj, attribute, value)
    return obj

def dict_from_class(cls):
    #return [m for m in dir(cls) if not m.startswith('__')]
    x = {}
    for attr in dir(cls):
        if not attr.startswith("_"):
            try:
                x[attr] = getattr(cls, attr)
            except (AttributeError, KeyError):
                pass
    return x