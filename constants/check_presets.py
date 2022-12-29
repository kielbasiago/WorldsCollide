from constants.checks import *

from collections import namedtuple
CheckPreset = namedtuple("CheckPreset", ["key", "name", "reward", "description", "locations"])

AH_CLOSED = CheckPreset(
    "ah",
    "Auction House is Closed",
    RewardType.ITEM,
    "The auction house will<line>only reward ITEMS",
    [
        AUCTION1,
        AUCTION2
    ]
)

NO_FREE_CHARACTERS = CheckPreset(
    'nfc',
    "No Free Characters",
    RewardType.ESPER | RewardType.ITEM,
    "All free checks that can<line>reward characters are<line>guaranteed to reward<line>an ESPER or ITEM",
    [
        COLLAPSING_HOUSE,
        FIGARO_CASTLE_THRONE,
        GAUS_FATHERS_HOUSE,
        KOHLINGEN_CAFE,
        MT_ZOZO,
        SEALED_GATE,
        SOUTH_FIGARO_PRISONER,
    ]
)

NO_FREE_CHARACTERS_ESPERS = CheckPreset(
    'nfce',
    "No Free Characters/Espers",
    RewardType.ITEM,
    "All free checks are<line>guaranteed to reward<line>an ITEM",
    [
        AUCTION1,
        AUCTION2,
        COLLAPSING_HOUSE,
        FIGARO_CASTLE_THRONE,
        GAUS_FATHERS_HOUSE,
        KOHLINGEN_CAFE,
        MT_ZOZO,
        NARSHE_WEAPON_SHOP,
        NARSHE_WEAPON_SHOP_MINES,
        SEALED_GATE,
        SOUTH_FIGARO_PRISONER,
        TZEN_THIEF,
    ]
)

all_presets = [
    AH_CLOSED,
    NO_FREE_CHARACTERS,
    NO_FREE_CHARACTERS_ESPERS,
]

preset_keys = [preset.key for preset in all_presets]
key_preset = {preset.key: preset for (idx, preset) in enumerate(all_presets)}
