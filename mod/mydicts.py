"""A file containing all of the data to be used with the PCSG server"""
import json
from os import path
from time import ctime 

guild_id = 693608235835326464

all_roles = {
    "CAPE": 764214191782756392,
    "CSEC": 764214207192760401,
    "PENDING_MEMBER": 830907979301388368,
    "FAMILY": 755633133600112651,
    "NEWBIE": 762190942316134400,
    "SEASONED": 762192895477415966,
    "EXPERIENCED": 762192810924441610,
    "ADVANCED": 762870198481977375,
    "ELITIST": 762193027979542581,
    "MUTED": 701972373053636649,
    "STAGE_0": 834837579433115709,
    "STAGE_1": 785341063984316476, 
    "STAGE_2": 834837741937098823,
    "STAGE_3": 834838252670025769,
    "STAGE_4_CSEC": 834838264581587055,
    "STAGE_4_CAPE": 834838268150415370,
    "STAGE_5_YEAR": 840061447357595669,
    "STAFF": 796126171477180487
}

register_channels = {
    700174264782815232: "COUNTRIES",
    762068609278410752: "GROUPS",
    762068938686595152: "PROFICIENCY",
    718473529452003329: "CAPE",
    755875615587958814: "CSEC",
    839580152131485696: "SPECIALTIES",
    831265040434331649: "VERIFY"
}

progression_role_ids = {
    785341063984316476: "Stage 1",
    834837741937098823: "Stage 2",
    834838252670025769: "Stage 3",
    834838268150415370: "Stage 4 CAPE",
    834838264581587055: "Stage 4 CSEC",
    840061447357595669: "Stage 5 Year",
    830907979301388368: "Unverified Student"
}

proficiency_to_stage = {
    764214191782756392: 834838268150415370,
    764214207192760401: 834838264581587055
}

# Links the respective registration channel to the role needed to view it
register_channels_to_progression_roles = dict(zip(list(register_channels.keys()), list(progression_role_ids.keys())))

progression_roles = {
    834837579433115709: 785341063984316476,
    785341063984316476: 834837741937098823,
    834837741937098823: 834838252670025769,
    834838252670025769: 0,
    834838268150415370: 840061447357595669,
    834838264581587055: 840061447357595669,
    840061447357595669: 830907979301388368,
    830907979301388368: [755633133600112651, 762190942316134400]
}

group_roles = {
    "🕑": "duo",
    "🕒": "trio",
    "🕓": "quartet",
    "🕔": "qunitet",
    "✅": "Confirm"
}

group_roles_ids = {
    "duo": 765011328532086805,
    "trio": 765011376976166942,
    "quartet": 765011399524614169,
    "qunitet": 765011419598815233,
    "decuplet": 765011478775463947,
    "vigintet": 765011552007880736
}

channels = {
    "CSEC":755875615587958814,
    "CAPE": 718473529452003329,
    "REP_FLAG": 700174264782815232,
    "PERSONALIZE_CHANNEL": 830914205078782072,
    "VERIFY": 831265040434331649,
    "NAME_CHANGES": 785986850736963675,
    "ROLE_CHANGES": 785986876531015711,
    "MESSAGE_LOGS": 785993210522107925,
    "BULK_DELETES": 786003742813192233,
    "JOIN_LEAVES": 786016910668070952,
    "ERROR_ROOM": 828638567236108308,
    "WELCOME_CHANNEL": 700214669003980801,
    "MEMBER_COUNT_CHANNEL": 764418047246729227,
    "MEMBERS_IN_VC_COUNT_CHANNEL": 764427421876748298,
    "BOT_ROOM": 831275896429477980,
    "PROFICIENCY": 762068938686595152,
    "MONITOR": 838916745062383616,
    "WARN_LOGS": 861553807673524234
}

# Dictionary containing all emojis and their links to their roles.
reactions = {
    "PROFICIENCY": {
        "📘": "csec",
        "📖": "cape",
        },
    "CSEC": {
        "📈":"5-add maths",
        "🌾":"5-agricultural science",
        "🧬":"5-biology",
        "🏗":"5-building tech",
        "🌋":"5-caribbean history",
        "🏛":"5-certificate in business studies",
        "🧪":"5-chemistry",
        "🧵":"5-clothing and textiles",
        "💳":"5-economics",
        "⌨":"5-edpm",
        "🔌":"5-electrical engineering",
        "📕":"5-english a",
        "📗":"5-english b",
        "🍽":"5-food and nutrition",
        "🇨":"5-french",
        "🗺":"5-geography",
        "🧠":"5-hsb",
        "🖥":"5-information technology",
        "⚗":"5-integrated science",
        "📉":"5-maths",
        "⚙":"5-mechanical engineering",
        "🎶":"5-music",
        "📠":"5-office admin",
        "⚽":"5-physical education",
        "🧲":"5-physics",
        "💵":"5-poa",
        "💷":"5-pob",
        "🙏":"5-religious education",
        "🏡":"5-resources and family management",
        "🎎":"5-social studies",
        "🇪":"5-spanish",
        "✏":"5-technical drawing",
        "🎭":"5-theatre arts",
        "🎨":"5-visual arts",
    },
    "CAPE": {
        "💲":"6-accounting",
        "🥬":"6-agricultural science",
        "🎮":"6-animation and game design",
        "📊":"6-applied maths",
        "🌌":"6-arts and design",
        "🦠":"6-biology",
        "🛠":"6-building and mechanical engineering drawing",
        "📙":"6-caribbean studies",
        "🌡":"6-chemistry",
        "📘":"6-communication studies",
        "💻":"6-computer science",
        "🎥":"6-digital media",
        "💱":"6-economics",
        "💡":"6-electrical electronic engineering tech",
        "💰":"6-entrepreneurship",
        "🏞":"6-environmental science",
        "🗂":"6-financial services studies",
        "🍔":"6-food and nutrition",
        "🇨":"6-french",
        "🏝️": "6-geography",
        "🌍":"6-geography",
        "♻":"6-green engineering",
        "🗾":"6-history",
        "💾":"6-information tech",
        "🔢":"6-integrated maths",
        "⚖":"6-law",
        "📖":"6-literature in english",
        "🏧":"6-logistics and supplies chain oppositions",
        "💼":"6-management of business",
        "💃":"6-performing arts",
        "🏀":"6-physical education",
        "🔋":"6-physics",
        "📐":"6-pure maths",
        "🗿":"6-sociology",
        "🇻":"6-spanish",
        "🏖":"6-tourism",
    },
    "GROUPS": {
        "🕑": "duo",
        "🕒": "trio",
        "🕓": "quartet",
        "🕔": "quintet",
    },  
    "COUNTRIES": {
        "\U0001f1f2\U0001f1f8" : "Montserrat",
        "\U0001f1e6\U0001f1ec" : "Antigua and Barbuda",
        "\U0001f1e7\U0001f1f8": "Bahamas",
        "\U0001f1e7\U0001f1ff" : "Belize",
        "\U0001f1e9\U0001f1f2" : "Dominica",
        "\U0001f1ec\U0001f1e9" : "Grenada",
        "\U0001f1ec\U0001f1fe" : "Guyana",
        "\U0001f1ed\U0001f1f9" : "Haiti",
        "\U0001f1f1\U0001f1e8" : "St.Lucia",
        "\U0001f1f0\U0001f1f3" : "St.Kitts and Nevis",
        "\U0001f1f8\U0001f1f7" : "Suriname",
        "\U0001f1ef\U0001f1f2" : "Jamaica",
        "\U0001f1f9\U0001f1f9" : "Trinidad and Tobago",
        "\U0001f1e7\U0001f1e7" : "Barbados",
        "\U0001f1fb\U0001f1e8" : "St.Vincent and the Grenadines",
        "\U0001f1fb\U0001f1ec" : "British Virgin Islands",
        "\U0001f1e6\U0001f1ee" : "Anguilla",
        "\U0001f1e9\U0001f1ea" : "Germany",
        "\U0001f1f0\U0001f1fe" : "Cayman Islands"
    },
    "SPECIALTIES": {
        "\U0001f4ab": "Unit 1",
        "\U00002b50": "Unit 2",
        "\U0001f31f": "Form 4",
        "\U00002728": "Form 5"
    },
    "VERIFY": {
        "✅": [all_roles["FAMILY"], all_roles["NEWBIE"]]
        }
}

country_dict = {
    "\U0001f1f2\U0001f1f8" : "Montserrat",
    "\U0001f1e6\U0001f1ec" : "Antigua and Barbuda",
    "\U0001f1e7\U0001f1f8": "Bahamas",
    "\U0001f1e7\U0001f1ff" : "Belize",
    "\U0001f1e9\U0001f1f2" : "Dominica",
    "\U0001f1ec\U0001f1e9" : "Grenada",
    "\U0001f1ec\U0001f1fe" : "Guyana",
    "\U0001f1ed\U0001f1f9" : "Haiti",
    "\U0001f1f1\U0001f1e8" : "St.Lucia",
    "\U0001f1f0\U0001f1f3" : "St.Kitts and Nevis",
    "\U0001f1f8\U0001f1f7" : "Suriname",
    "\U0001f1ef\U0001f1f2" : "Jamaica",
    "\U0001f1f9\U0001f1f9" : "Trinidad and Tobago",
    "\U0001f1e7\U0001f1e7" : "Barbados",
    "\U0001f1fb\U0001f1e8" : "St.Vincent and the Grenadines",
    "\U0001f1fb\U0001f1ec" : "British Virgin Islands",
    "\U0001f1e6\U0001f1ee" : "Anguilla",
    "\U0001f1e9\U0001f1ea" : "Germany",
    "\U0001f1f0\U0001f1fe" : "Cayman Islands"
}

resource_categories = {
    "CAPE": {
        "business": ["accounting", "management of business", "economics", "entrepreneurship", "financial services studies", "logistics and supply chain", "tourism"],
        "humanities": ["art and design", "caribbean studies", "communication studies", "food and nutrition", "geography", "history", "law", "performing arts", "sociology"],
        "languages": ["french", "literatures in english", "spanish"],
        "sciences-and-maths": ["agricultural science", "applied mathematics", "biology", "chemistry", "environmental science", "physical education", "physics", "pure mathematics", "integrated maths"],
        "technology": ["animation and game design", "building and mechanical engineering drawing", "computer science", "digital media", "electronic and electrical engineering technology", "geometrical and mechanical engineering", "green engineering", "information technology"]
    },
    "CSEC":{
        "business": ["electronic document preparation management", "principles of accounts", "principles of business", "economics", "office admin"],
        "sciences-and-maths": ["biology", "chemistry", "physics", "physical education", "math", "add math", "hsb", "agricultural science", "integrated science"],
        "technology": ["electronic electrical engineering technology", "mechanical engineering technology", "building technology", "information technology", "technical drawing"],
        "languages": ["english A", "english b", "spanish", "french"],
        "humanities": ["geography", "social studies", "history", "religious education", "clothing and texting", "food and nutrition", "resource and family management", "music", "visual arts", "theatre arts"],

    }
}

csec_subjects = {
    "math": "math-1",
    "english": "eng-a-1",
    "office": "office-administration",
    "pob": "pob",
    "principles of business": "pob",
    "poa": "poa",
    "principles of accounts": "poa",
    "it": "it",
    "information tech": "it",
    "social studies": "social-studies",
    "spanish": "spanish",
    "economics": "economics",
    "physics": "physics",
    "bio": "biology",
    "chem": "chemistry",
    "french": "french",
    "bt": "bt",
    "building": "bt",
    "td": "td",
    "technical": "td",
    "agri": "agri-sci",
    "food": "food-nutrition",
    "pe": "pe", 
    "physical": "pe",
    "hsb": "hsb",
    "human": "hsb",
    "integrated science": "integrated science",
    "science": "integrated science",
    "clothing": "agri-sci-1",
    "add": "add-math",
    "geo": "geography",
    "english b": "eng-b",
    "history": "history",
    "edpm": "edpm",
    "electronic": "edpm"
}

logs = []

if path.exists("logs.json"):
    with open("logs.json") as f:
        try:
            logs = json.load(f)
        except json.JSONDecodeError:
            pass

async def log(modcmd, action, culprit, reason):
    """Function used to save logs"""
    mydict = {"Command":modcmd, "Action":action, "Done By":culprit, "Reason": reason, "Time": ctime()}
    
    logs.append(mydict)

    with open("logs.json", "w") as f:
        json.dump(logs, f, indent=4)