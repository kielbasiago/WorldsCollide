
from constants.objectives.results import ResultType

class ObjectiveMetadata:
    def __init__(self, objective: ResultType):
        self.objective = objective
        self.id = objective.id
        self.name = objective.name

    def to_json(self):
        formatter = self.objective.format_string
        if "{:+d}" in formatter:
            format_string = formatter.replace('{:+d}', "{{ . }}")
        elif "{}" in formatter:
            format_string = formatter.replace('{}', "{{ . }}")
        else:
            format_string = formatter
        return {
            'id': self.objective.id,
            'name': self.objective.name,
            'value_range': self.objective.value_range,
            'format_string': format_string
        }