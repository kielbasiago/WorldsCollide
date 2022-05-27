def name():
    return "Challenges"

def parse(parser):
    challenges = parser.add_argument_group("Challenges")
    # Legacy flags - Thse will be mapped to --remove-items args
    challenges.add_argument("-nmc", "--no-moogle-charms", action = "store_true",
                            help = "Moogle Charms will not appear in coliseum/auction/shops/chests/events")
    challenges.add_argument("-nee", "--no-exp-eggs", action = "store_true",
                            help = "Exp. Eggs will not appear in coliseum/auction/shops/chests/events")
    challenges.add_argument("-nil", "--no-illuminas", action = "store_true",
                            help = "Illuminas will not appear in coliseum/auction/shops/chests/events")

    challenges.add_argument("-ri", "--remove-items", type = str,
                        help = "Remove items from game. They will no longer appear in coliseum/auction/shops/chests/events, though can still be accessed via objective results.")
    challenges.add_argument("-nu", "--no-ultima", action = "store_true",
                            help = "Ultima cannot be learned from espers/items/natural magic")
    challenges.add_argument("-nfce", "--no-free-characters-espers", action = "store_true",
                            help = "Remove character/esper rewards from: Auction House, Collapsing House, Figaro Castle Throne, Gau's Father's House, Kohlingen Inn, Narshe Weapon Shop, Sealed Gate, South Figaro Basement")
    challenges.add_argument("-pd", "--permadeath", action = "store_true",
                            help = "Life spells cannot be learned. Fenix Downs unavailable (except from starting items). Buckets/inns/tents/events do not revive characters. Phoenix casts Life 3 on party instead of Life")

def process(args):
    from data.item_names import id_name
    if args.remove_items:
        args.remove_item_ids =   [int(i) for i in args.remove_items.split(',')]
        args.remove_item_names = [id_name[i] for i in args.remove_item_ids]

def flags(args):
    flags = ""

    if args.remove_items:
        flags += f" -ri {args.remove_items}"
    if args.no_ultima:
        flags += " -nu"
    if args.no_free_characters_espers:
        flags += " -nfce"
    if args.permadeath:
        flags += " -pd"

    return flags

def options(args):
    return [
        ("Remove Items", args.remove_item_names),
        ("No Ultima", args.no_ultima),
        ("No Free Characters/Espers", args.no_free_characters_espers),
        ("Permadeath", args.permadeath),
    ]

def menu(args):
    entries = options(args)
    for index, entry in enumerate(entries):
        key, value = entry
        if key == "No Free Paladin Shields":
            entries[index] = ("No Free Paladin Shlds", entry[1])
        elif key == "No Free Characters/Espers":
            entries[index] = ("No Free Chars/Espers", entry[1])
    return (name(), entries)

def log(args):
    from log import format_option
    log = [name()]

    entries = options(args)
    for entry in entries:
        log.append(format_option(*entry))

    return log
