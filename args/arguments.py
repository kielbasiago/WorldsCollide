from argparse import _StoreTrueAction
import json
class Object:
    def toJSON(self):
        return self.__dict__
                          #//, default=lambda o: o.__dict__,
            # sort_keys=True, indent=4)

blacklist = [
    'help',
    'input_file',
    'output_file',
    'seed_id',
    'debug',
    'no_rom_output',
    'stdout_log'
]
class Arguments:
    def __init__(self):
        import importlib
        self.groups = [
            "settings",
            "objectives",
            "starting_party", "characters", "swdtechs", "blitzes", "lores", "rages", "dances", "steal", "commands",
            "xpmpgp", "scaling", "bosses", "encounters", "boss_ai",
            "espers", "natural_magic",
            "starting_gold_items", "items", "shops", "chests",
            "graphics",
            "coliseum", "auction_house", "challenges", "bug_fixes", "misc",
        ]
        self.group_modules = {}
        for group in self.groups:
            self.group_modules[group] = importlib.import_module("args." + group)

        from argparse import ArgumentParser
        self.parser = ArgumentParser()

        self.parser.add_argument("-i", dest = "input_file", required = True, help = "FFIII US v1.0 rom file")
        self.parser.add_argument("-o", dest = "output_file", required = False, help = "Modified FFIII US v1.0 rom file")
        self.parser.add_argument("-sid", dest = "seed_id", required = False, help = "Seed unique id (website)")
        self.parser.add_argument("-debug", dest = "debug", action = "store_true", help = "Debug mode")

        self.parser.add_argument("-nro", dest = "no_rom_output", action = "store_true", help = "Do not output a modified rom file")
        self.parser.add_argument("-slog", dest = "stdout_log", action = "store_true", help = "Write log to stdout instead of file")

        for group in self.group_modules.values():
            group.parse(self.parser)

        self.parser.parse_args(namespace = self)

        self.flags = ""
        self.seed_rng_flags = ""
        for group_name, group in self.group_modules.items():
            group.process(self)
            group_flags = group.flags(self)

            self.flags += group_flags
            if group_name != "graphics":
                # graphics flags are not used for seeding rng
                self.seed_rng_flags += group_flags
        self.flags = self.flags.strip()
        self.seed_rng_flags = self.seed_rng_flags.strip()

        # seed game based on given flags as well so players can't change them for competitions without changing the rest of the game
        from seed import seed_rng
        self.seed = seed_rng(self.seed, self.seed_rng_flags)

        import sprite_hash, version
        self.sprite_hash = sprite_hash.generate_hash(self.seed + self.seed_rng_flags + version.__version__)

        import os
        self.website_link = None
        if self.seed_id:
            # ignore any output_file argument and add given seed id to output name
            name, ext = os.path.splitext(self.input_file)
            self.output_file = f"{name}wc_{self.seed_id}{ext}"

            self.website_link = f"ff6wc.com/seed/{self.seed_id}"
        elif self.output_file is None:
            # if no output_file given add seed to output name
            name, ext = os.path.splitext(self.input_file)
            self.output_file = f"{name}_wc_{self.seed}{ext}"

        if self.debug:
            self.spoiler_log = True


        meta = {}
        import sys
        flags = sys.argv

        groups = self.parser._action_groups

        for group in groups:
            title = group.title
            description = group.description
            actions = group._group_actions
            group_title =  getattr(group, 'title', '')

            for action in actions:
                if action.dest in blacklist:
                    continue
                for meg in self.parser._mutually_exclusive_groups:
                    if action in (meg._group_actions or []):
                        action.mutually_exclusive_group_title = meg.title

                meta[action.dest] = Object()
                meta[action.dest].key = action.dest

                if isinstance(action, _StoreTrueAction):
                    meta[action.dest].type = 'bool'
                else:
                    meta[action.dest].type = action.type.__name__ if action.type else str.__name__

                meta[action.dest].flag = action.option_strings[0]

                if action.default:
                    meta[action.dest].default = action.default
                if action.help:
                    meta[action.dest].description = action.help
                if action.nargs:
                    meta[action.dest].nargs = action.nargs
                if action.metavar:
                    meta[action.dest].args = action.metavar
                if action.choices is not None and isinstance(action.choices, list) and not isinstance(action.choices, range):
                    meta[action.dest].allowed_values = list(action.choices)
                if type(group_title):
                    meta[action.dest].group = group_title if type(group_title) == str else None if group_title == None else group_title()
                if getattr(action, 'mutually_exclusive_group_title', None) is not None:
                    meta[action.dest].mutually_exclusive_group = action.mutually_exclusive_group_title
                if getattr(action, 'choices', None) is not None:
                    if isinstance(action.choices, range):
                        meta[action.dest].options = {
                            'min_val': action.choices[0] if isinstance(action.choices, range) else None,
                            'max_val': action.choices[-1] if isinstance(action.choices, range) else None
                        }

        final = {key: value.toJSON() for key, value in meta.items()}

        import json
        file_name = self.output_file.replace('.smc', '.json')
        with open("./wc-metadata.json", "w") as out_file:
            out_file.write(json.dumps(final, indent = 4))

    def _process_min_max(self, arg_name):
        values = getattr(self, arg_name)
        if values:
            if values[0] > values[1]:
                values[0], values[1] = values[1], values[0]
            setattr(self, arg_name + "_min", values[0])
            setattr(self, arg_name + "_max", values[1])

if __name__ == "__main__":
    import os, sys

    # execute from parent directory for import paths
    sys.path[0] = os.path.join(sys.path[0], os.path.pardir)

    args = Arguments()
    print(args.flags)
