
from event.event_reward import RewardType


def name():
    return "Check Rewards"

char_esper_item_reward = "cei"
esper_item_reward = "ei"
item_reward = "i"
no_reward = "none"

allowed_values = [
    char_esper_item_reward,
    esper_item_reward,
    item_reward,
]

def parse(parser):
    from constants.check_presets import preset_keys
    advanced_checks = parser.add_argument_group("Check Rewards")

    presets = advanced_checks.add_mutually_exclusive_group()
    presets.name = "Check Presets"

    presets.add_argument('-checks', "--check-preset", type = str,
                choices = preset_keys, help = "A preset used to modify certain checks to rewards characters, espers, or items.")

    presets.add_argument("-nfce", "--no-free-characters-espers", action = "store_true",
                help = "Remove character/esper rewards from: Auction House, Collapsing House, Figaro Castle Throne, Gau's Father's House, Kohlingen Inn, Mt. Zozo, Narshe Weapon Shop, Sealed Gate, South Figaro Basement, Tzen Thief, Zone Eater")

    advanced_checks.add_argument("-firr", "--force-item-rewards", type = str,
                help = "Forces list of checks to give an ITEM reward")

    advanced_checks.add_argument("-ferr", "--force-esper-rewards", type = str,
                help = "Forces list of checks to give an ESPER reward")

    advanced_checks.add_argument("-feirr", "--force-esper-item-rewards", type = str,
                help = "Forces list of checks to give an (ESPER | ITEM) reward")

    advanced_checks.add_argument("-fcrr", "--force-character-rewards", type = str,
                help = "Forces list of checks to give an CHARACTER reward")

    advanced_checks.add_argument("-drewards", "--dragon-rewards", default = None, type = str,
                choices = [char_esper_item_reward, esper_item_reward, item_reward, no_reward],
                help = "Specifies the rewards of dragons. Only applies to dragons outside of Kefka's Tower")

def process(args):
    from constants.check_presets import key_preset, NO_FREE_CHARACTERS_ESPERS
    args.character_rewards = []
    args.esper_item_rewards = []
    args.esper_rewards = []
    args.item_rewards = []
    
    if args.dragon_rewards == char_esper_item_reward:
        args.dragon_reward = RewardType.CHARACTER | RewardType.ESPER | RewardType.ITEM
    elif args.dragon_rewards == esper_item_reward:
        args.dragon_reward = RewardType.ESPER | RewardType.ITEM
    elif args.dragon_rewards == no_reward:
        args.dragon_reward = RewardType.NONE
    else:
        args.dragon_reward = RewardType.ITEM
        
    if args.no_free_characters_espers:
        args.check_preset = NO_FREE_CHARACTERS_ESPERS.key

    if args.check_preset:
        check_preset = key_preset[args.check_preset]
        bits = [int(check.bit) for check in check_preset.locations]
        if check_preset.reward == RewardType.CHARACTER:
            args.character_rewards = bits
        if check_preset.reward == (RewardType.ESPER | RewardType.ITEM):
            args.esper_item_rewards = bits
        if check_preset.reward == RewardType.ESPER:
            args.esper_rewards = bits
        if check_preset.reward == RewardType.ITEM:
            args.item_rewards = bits
    else:
        if args.force_character_rewards:
            args.character_rewards =  [int(check) for check in args.force_character_rewards.split(',')]

        if args.force_esper_item_rewards:
            args.esper_item_rewards =  [int(check) for check in args.force_esper_item_rewards.split(',')]

        if args.force_esper_rewards:
            args.esper_rewards =  [int(check) for check in args.force_esper_rewards.split(',')]

        if args.force_item_rewards:
            args.item_rewards =  [int(check) for check in args.force_item_rewards.split(',')]


def flags(args):
    flags = ""

    if args.check_preset:
        flags += f" -checks {args.check_preset}"

    if args.force_character_rewards:
        flags += f" -fcrr {args.force_character_rewards}"

    if args.force_esper_item_rewards:
        flags += f" -feirr {args.force_esper_item_rewards}"

    if args.force_esper_rewards:
        flags += f" -ferr {args.force_esper_rewards}"

    if args.force_item_rewards:
        flags += f" -firr {args.force_item_rewards}"

    if args.dragon_rewards:
        flags += f" -drewards {args.dragon_rewards}"

    return flags

preset_title = "Check Preset"
def options(args):
    opts = {}
    
    if args.check_preset:
        opts[preset_title] = args.character_rewards or args.esper_item_rewards or args.esper_rewards or args.item_rewards
    else:
        opts[preset_title] = "None"

    if args.dragon_reward == RewardType.NONE:
        opts['Dragon Rewards'] = 'None'
    elif args.dragon_reward & RewardType.CHARACTER:
        opts['Dragon Rewards'] = "C+E+I"
    elif args.dragon_reward & RewardType.ESPER:
        opts['Dragon Rewards'] = "E+I"
    else:
        opts['Dragon Rewards'] = "Item"

    return [(key, value) for (key, value) in opts.items()]

def _format_check_log_entries(check_ids):
    from constants.checks import check_name
    check_entries = []
    for check_id in check_ids:
        check_entries.append(("", check_name[check_id]))
    return check_entries

def menu(args):
    from menus.submenu_force_item_reward_checks import FlagsCheckPreset

    entries = options(args)
    for index, entry in enumerate(entries):
        key, value = entry
        if key == preset_title:
            if value:
                entries[index] = (preset_title, FlagsCheckPreset(preset_title, value, args.check_preset)) # flags sub-menu
            else:
                entries[index] = (preset_title, [])

    return (name(), entries)

def log(args):
    from log import format_option
    log = [name()]

    entries = options(args)
    for entry in entries:
        key, value = entry
        if key == preset_title:
            if len(value) == 0:
                entry = (key, value)
            else:
                entry = (key, "") # The entries will show up on subsequent lines
            log.append(format_option(*entry))
            from constants.check_presets import key_preset
            for check_entry in _format_check_log_entries(value):
                log.append(format_option(*check_entry))
        else:
            log.append(format_option(*entry))

    return log
