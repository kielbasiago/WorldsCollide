from objectives.results._objective_result import *
from objectives.results._add_sub_stat import add_stat_character, sub_stat_character

STAMINA_ADDRESS = 0x161c

character_add = {}
character_sub = {}

def add_stamina(character):
    if character not in character_add:
        character_add[character] = add_stat_character(character, STAMINA_ADDRESS, "stamina")
    return character_add[character]

def sub_stamina(character):
    if character not in character_sub:
        character_sub[character] = sub_stat_character(character, STAMINA_ADDRESS, "stamina")
    return character_sub[character]

class Field(field_result.Result):
    def src(self, count, character_name, character):
        if count < 0:
            return [
                field.LongCall(START_ADDRESS_SNES + sub_stamina(character), -count),
            ]
        elif count > 0:
            return [
                field.LongCall(START_ADDRESS_SNES + add_stamina(character), count),
            ]
        return []

class Battle(battle_result.Result):
    def src(self, count, character_name, character):
        if count < 0:
            return [
                asm.LDA(-count, asm.IMM8),
                asm.STA(field.LongCall.ARG_ADDRESS, asm.DIR),
                asm.JSL(START_ADDRESS_SNES + sub_stamina(character)),
            ]
        elif count > 0:
            return [
                asm.LDA(count, asm.IMM8),
                asm.STA(field.LongCall.ARG_ADDRESS, asm.DIR),
                asm.JSL(START_ADDRESS_SNES + add_stamina(character)),
            ]
        return []

class Result(ObjectiveResult):
    NAME = "Stamina Random"
    def __init__(self, min_count, max_count):
        import args
        from seed import get_random_instance
        random = get_random_instance(f"{args.subseed_check}--condition-{self.NAME}")

        from constants.entities import id_character, CHARACTER_COUNT
        character = random.randint(0, CHARACTER_COUNT - 1)
        character_name = id_character[character]

        count = random.randint(min_count, max_count)
        super().__init__(Field, Battle, count, character_name, character)
