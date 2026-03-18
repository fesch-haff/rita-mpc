"""
@author Henri-Welsch
@sources {
    https://charlesreid1.github.io/python-patterns-the-registry.html
    https://realpython.com/python-double-underscore/
    https://developers.home-assistant.io/docs/api/websocket/#subscribe-to-events
}
"""

class Registry:
    _registry = {}

    @classmethod
    def register(cls, name, obj):
        cls._registry[name] = obj

    @classmethod
    def initiate(cls, entities: list[dict]):
        for entity in entities:
            entity_id = entity["entity_id"]

            cls.register(entity_id, entity)
