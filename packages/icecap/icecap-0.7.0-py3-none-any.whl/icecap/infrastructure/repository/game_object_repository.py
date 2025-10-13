from typing import Generator
from icecap.infrastructure.driver import GameDriver
from icecap.domain.models import GameObject, Entity
from icecap.domain.enums import EntityType
from icecap.domain.dto import Position, GameObjectFields
from icecap.infrastructure.driver import ObjectManager
from icecap.infrastructure.name_resolver import NameResolver


class GameObjectRepository:
    """Repository for game object entities.

    This class provides methods to access game object entities in the game.
    """

    def __init__(self, driver: GameDriver):
        self.driver = driver

    def get_game_object_from_entity(
        self,
        entity: Entity,
        object_manager: ObjectManager | None = None,
        name_resolver: NameResolver | None = None,
    ) -> GameObject:
        """Extends an Entity object to a GameObject instance.

        This method takes an Entity object, extracts all the necessary information
        and creates a GameObject object from it.

        You can bring your own name resolver and object manager.
        """
        object_manager = object_manager or self.driver.object_manager
        name_resolver = name_resolver or self.driver.name_resolver

        position = object_manager.get_entity_position(entity)
        game_object_fields = object_manager.get_game_object_fields(entity)
        name = name_resolver.resolve_game_object_name_by_entry_id(game_object_fields.entry)

        game_object = GameObject(
            guid=entity.guid,
            object_address=entity.object_address,
            position=Position(x=position.x, y=position.y, z=position.z, rotation=position.rotation),
            name=name,
            entity_type=EntityType.GAME_OBJECT,
            game_object_fields=GameObjectFields(
                entry_id=game_object_fields.entry,
                display_id=game_object_fields.display_id,
                owner_guid=game_object_fields.created_by,
                state=game_object_fields.bytes1_state,
            ),
        )
        return game_object

    def yield_game_objects(self) -> Generator[GameObject, None, None]:
        """Yield all game object entities around the local player.

        This method iterates through all objects around the player and yields
        only those that are of type GAME_OBJECT. Each entity is extended to a
        GameObject object before being yielded.
        """
        object_manager = self.driver.object_manager
        name_resolver = self.driver.name_resolver

        for entity in object_manager.yield_objects():
            if entity.entity_type != EntityType.GAME_OBJECT:
                continue

            yield self.get_game_object_from_entity(entity, object_manager, name_resolver)

    def refresh_game_object(self, game_object: GameObject) -> GameObject:
        """Refresh the game object data with the latest information from the game.

        This method retrieves the latest data for a game object from the game and
        returns a new GameObject instance with the updated data. The original GameObject
        instance is not modified.
        """
        object_manager = self.driver.object_manager

        position = object_manager.get_entity_position(game_object)
        game_object_fields = object_manager.get_game_object_fields(game_object)

        return GameObject(
            guid=game_object.guid,
            object_address=game_object.object_address,
            position=Position(x=position.x, y=position.y, z=position.z, rotation=position.rotation),
            name=game_object.name,
            entity_type=EntityType.GAME_OBJECT,
            game_object_fields=GameObjectFields(
                entry_id=game_object_fields.entry,
                display_id=game_object_fields.display_id,
                owner_guid=game_object_fields.created_by,
                state=game_object_fields.bytes1_state,
            ),
        )
