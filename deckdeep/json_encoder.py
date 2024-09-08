import json
from deckdeep.custom_types import Health, Energy


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (Health, Energy)):
            return obj.value
        return super().default(obj)
