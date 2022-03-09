from data.metamorph_group import MetamorphGroup
from data.structures import DataArray
from data.item_names import name_id
import args

class MetamorphGroups:
    DATA_START = 0x047f40
    DATA_END = 0x047fa7

    def __init__(self, rom, items):
        self.rom = rom
        self.data = DataArray(self.rom, self.DATA_START, self.DATA_END, MetamorphGroup.DATA_SIZE)
        self.items = items

        self.groups = []
        self.item_locations = {}
        for item_id in range(0, 255):
            self.item_locations[item_id] = []

        for index in range(len(self.data)):
            group = MetamorphGroup(index, self.data[index])
            for index in [group.items.index(i) for i in group.items]:
                item_id = group.items[index]

                self.item_locations[item_id].append((group.id, index))
                # TODO ADD TO LOG?
            self.groups.append(group)


    def remove_fenix_downs(self):
        self.groups[1].items[1] = name_id["Potion"] # replace with potion

    def remove_exp_eggs(self):
        self.groups[18].items[3] = name_id["Rename Card"] # replace with rename card

    def replace_item(self, item_id, new_id):
        for [group_id, item_index] in self.item_locations[item_id]:
            self.groups[group_id].items[item_index] = new_id

    def get_replacement_item(self, item_id, exclude):
        import random
        from data.chest_item_tiers import tiers
        same_item_tier = next((tier for tier in tiers if item_id in tier), [])
        replacements = [i for i in same_item_tier if i not in exclude]
        replacement = random.choice(replacements) if len(replacements) else None
        return None if replacement is None else replacement

    def mod(self):
        for id in args.remove_item_ids:
            if len(self.item_locations[id]):
                replacement_id = self.get_replacement_item(id, args.remove_item_ids)
                if replacement_id is not None:
                    self.replace_item(id, replacement_id)

    def write(self):
        for index, group in enumerate(self.groups):
            self.data[index] = group.data()

        self.data.write()

    def log(args):
        from log import format_option
        # log = [name()]

        # entries = options(args)
        # for entry in entries:
        #     log.append(format_option(*entry))



        return log
