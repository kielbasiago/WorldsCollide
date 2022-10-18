def name():
    return "Bosses"

def parse(parser):
    bosses = parser.add_argument_group("Bosses")

    bosses_battles = bosses.add_mutually_exclusive_group()
    bosses_battles.add_argument("-bbs", "--boss-battles-shuffle", action = "store_true",
                        help = "Boss battles shuffled")
    bosses_battles.add_argument("-bbr", "--boss-battles-random", action = "store_true",
                        help = "Boss battles randomized")
    bosses.add_argument("-bmbd", "--mix-bosses-dragons", action = "store_true",
                        help = "Shuffle/randomize bosses and dragons together")
    bosses.add_argument("-srp3", "--shuffle-random-phunbaba3", action = "store_true",
                        help = "Apply Shuffle/Random to Phunbaba 3 (otherwise he will only appear in Mobliz WOR)")
    bosses.add_argument("-bnds", "--boss-normalize-distort-stats", action = "store_true",
                        help = "Normalize lower boss stats and apply random distortion")
    bosses.add_argument("-bnu", "--boss-no-undead", action = "store_true",
                        help = "Undead status removed from bosses")

    boss_exp = bosses.add_mutually_exclusive_group()
    boss_exp.add_argument("-be", "--boss-experience", action = "store_true",
                        help = "Boss battles award experience")
    boss_exp.add_argument("-bef", "--boss-experience-flat", type = int,
                          nargs = 2, metavar = ("MIN", "MAX"), choices = range(500),
                          help = "Each boss will provide the base XP value per level")

def process(args):
    if args.boss_experience_flat:
        args._process_min_max("boss_experience_flat")

def flags(args):
    flags = ""

    if args.boss_battles_shuffle:
        flags += " -bbs"
    elif args.boss_battles_random:
        flags += " -bbr"

    if args.mix_bosses_dragons:
        flags += " -bmbd"
    if args.shuffle_random_phunbaba3:
        flags += " -srp3"
    if args.boss_normalize_distort_stats:
        flags += " -bnds"
    if args.boss_experience:
        flags += " -be"
    if args.boss_experience_flat:
        flags += f" -bef {args.boss_experience_flat_min} {args.boss_experience_flat_max}"
    if args.boss_no_undead:
        flags += " -bnu"

    return flags

def options(args):
    boss_battles = "Original"
    if args.boss_battles_shuffle:
        boss_battles = "Shuffle"
    elif args.boss_battles_random:
        boss_battles = "Random"

    boss_exp = "None"
    if args.boss_experience:
        boss_exp = "Classic"
    elif args.boss_experience_flat:
        boss_exp = f"Flat {args.boss_experience_flat_min}-{args.boss_experience_flat_max}"

    return [
        ("Boss Battles", boss_battles),
        ("Mix Bosses & Dragons", args.mix_bosses_dragons),
        ("Shuffle/Random Phunbaba 3", args.shuffle_random_phunbaba3),
        ("Normalize & Distort Stats", args.boss_normalize_distort_stats),
        ("Boss Exp", boss_exp),
        ("No Undead", args.boss_no_undead),
    ]

def menu(args):
    entries = options(args)
    for index, entry in enumerate(entries):
        key, value = entry

        if key == "Shuffle/Random Phunbaba 3":
            entries[index] = ("Mix Phunbaba 3", value)
        elif key == "Normalize & Distort Stats":
            entries[index] = ("Normalize & Distort", value)
    return (name(), entries)

def log(args):
    from log import format_option
    log = [name()]

    entries = options(args)
    for entry in entries:
        log.append(format_option(*entry))

    return log
