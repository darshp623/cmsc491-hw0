from .base import Block


class GuardBlock(Block):
    """
    Blocks progress in this direction until the guard is subdued.
    """
    
    def __init__(self, location, guard, connection):
        super().__init__("guard block", "The castle guard bars your way. Youll need to deal with him first.")
        self.location = location
        self.guard = guard
        self.connection = connection
    
    def is_blocked(self) -> bool:
        # check if guard is still present and conscious
        if self.guard and self.location.here(self.guard):
            if self.guard.get_property("is_unconscious") or self.guard.get_property("is_dead"):
                return False  # guard is subdued, pass
            return True  # guard is still active, blocked
        return False  # no guard present, pass


class DarknessBlock(Block):
    """
    Blocks progress in this direction until player has a lit light source.
    """
    
    def __init__(self, location, connection):
        super().__init__("darkness block", "Its too dark to go down the stairs safely.")
        self.location = location
        self.connection = connection
    
    def is_blocked(self) -> bool:
        # check if any char at this location has a lit light source
        for character_name, character in self.location.characters.items():
            for item_name, item in character.inventory.items():
                if (item.get_property("is_lightable") and 
                    item.get_property("is_lit")):
                    return False  # found a lit light source, pass
        return True  # no lit light source found, blocked


class LockedDoorBlock(Block):
    """
    Blocks progress in this direction until the door is unlocked.
    """
    
    def __init__(self, location, door, connection):
        super().__init__("locked door block", "The door at the top is locked.")
        self.location = location
        self.door = door
        self.connection = connection
    
    def is_blocked(self) -> bool:
        # check if door is locked
        return self.door.get_property("is_locked", True)


class Locked_Door(Block):
    """
    Blocks progress in this direction until a character unlocks the door.
    """

    def __init__(self, location, door, connection):
        super().__init__("locked door", "The door is locked")
        self.location = location
        self.door = door
        self.connection = connection

        loc_direction = self.location.get_direction(self.connection)
        self.location.add_item(self.door)
        self.location.add_block(loc_direction, self)

        con_direction = self.connection.get_direction(self.location)
        self.connection.add_item(self.door)
        self.connection.add_block(con_direction, self)

        self.door.set_property("is_locked", True)
        self.door.add_command_hint("unlock door")

    def is_blocked(self) -> bool:
        # Conditions of block:
        # * There is a door
        # * The door locked
        if self.door and self.door.get_property("is_locked"):
            return True
        return False

    def to_primitive(self):
        data = super().to_primitive()

        if self.location and hasattr(self.location, "name"):
            data["location"] = self.location.name
        elif "location" in data:
            data["location"] = self.location

        if self.door and hasattr(self.door, "name"):
            data["door"] = self.door.name
        elif "door" in data:
            data["door"] = self.door

        if self.connection and hasattr(self.connection, "name"):
            data["connection"] = self.connection.name
        elif "connection" in data:
            data["connection"] = self.connection

        return data

    @classmethod
    def from_primitive(cls, data):
        location = data["location"]
        door = data["door"]
        connection = data["connection"]
        instance = cls(location, door, connection)
        return instance
