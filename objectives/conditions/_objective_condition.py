import objectives.conditions._field_condition as field_condition
import objectives.conditions._battle_condition as battle_condition
import objectives.conditions._menu_condition as menu_condition

from constants.objectives.conditions import name_type, ObjectiveConditionType

import data.event_bit as event_bit
import data.battle_bit as battle_bit
import data.event_word as event_word

ConditionType = ObjectiveConditionType
class ObjectiveCondition:
    def __init__(self, condition_type, *args):
        self.args = args

        self.condition_type = condition_type

        self.field_class = getattr(field_condition, condition_type.name + "Condition")
        self.battle_class = getattr(battle_condition, condition_type.name + "Condition")
        self.menu_class = getattr(menu_condition, condition_type.name + "Condition")

        # modify class names for clearer output
        class_name = ''.join([character for character in self.NAME if character.isalnum()])
        if class_name[0].isdigit():
            class_name = '_' + class_name
        self.field_class.__name__ = class_name
        self.field_class.__qualname__ = class_name

        self.battle_class.__name__ = class_name
        self.battle_class.__qualname__ = class_name

        self.menu_class.__name__ = class_name
        self.menu_class.__qualname__ = class_name

    def field(self, *args, **kwargs):
        return self.field_class(*(self.args + args), **kwargs)

    def battle(self, *args, **kwargs):
        return self.battle_class(*(self.args + args), **kwargs)

    def menu(self, *args, **kwargs):
        return self.menu_class(*(self.args + args), **kwargs)

    def __str__(self, *args):
        return name_type[self.NAME].string_function(*args)

    def base_address(self):
        # TODO: abstract out where we store the base address?
        return self.battle_class.base_address()
