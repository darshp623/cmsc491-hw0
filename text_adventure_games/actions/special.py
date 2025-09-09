from . import base
from ..things import Character, Item, Location


class UnlockDoor(base.Action):
    """
    Unlock a door with a key.
    """
    ACTION_NAME = "unlock"
    ACTION_DESCRIPTION = "Unlock a door with a key"
    ACTION_ALIASES = ["unlock door"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.location = self.character.location
        
        # parse command to find door and key
        # look for "unlock door with key"
        if "with" in command:
            parts = command.split("with")
            door_part = parts[0].strip()
            key_part = parts[1].strip()
            
            # find door in location
            self.door = self.parser.match_item(door_part, self.location.items)
            # find key in chars inventory
            self.key = self.parser.match_item(key_part, self.character.inventory)
        else:
            # try and find door and key without "with"
            self.door = self.parser.match_item("door", self.location.items)
            self.key = self.parser.match_item("key", self.character.inventory)

    def check_preconditions(self) -> bool:
        """
        Preconditions:
        * There must be a door
        * The character must be at the same location as the door
        * The door must be locked
        * The character must have the key in their inventory
        """
        if not self.was_matched(self.door, "I dont see a door here."):
            return False
        if not self.was_matched(self.key, "You dont have a key."):
            return False
        if not self.location.here(self.character):
            return False
        if not self.location.here(self.door):
            return False
        if not self.character.is_in_inventory(self.key):
            return False
        if not self.door.get_property("is_locked"):
            self.parser.fail("The door is already unlocked.")
            return False
        return True

    def apply_effects(self):
        """
        Effects:
        * Unlocks the door
        """
        self.door.set_property("is_locked", False)
        description = "You unlock the door with the key."
        self.parser.ok(description)


class ReadRunes(base.Action):
    """
    Reading the runes on the candle will banish the ghost from the dungeon.
    """
    ACTION_NAME = "read runes"
    ACTION_DESCRIPTION = "Read runes off of the candle"
    ACTION_ALIASES = ["read"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.location = self.character.location
        
        # find candle in chars inventory
        self.candle = self.parser.match_item("candle", self.character.inventory)
        # find ghost in curr location
        self.ghost = None
        for char_name, char in self.location.characters.items():
            if "ghost" in char_name.lower():
                self.ghost = char
                break

    def check_preconditions(self) -> bool:
        """
        Preconditions:
        * There must be a candle with strange runes on it
        * The character must have the candle in their inventory
        * The ghost must be in this location
        * The candle must be lit
        """
        if not self.was_matched(self.candle, "You dont have a candle."):
            return False
        if not self.character.is_in_inventory(self.candle):
            return False
        if not self.ghost:
            self.parser.fail("Theres no ghost here to banish.")
            return False
        if not self.candle.get_property("is_lit"):
            self.parser.fail("The candle must be lit to read the runes.")
            return False
        if self.ghost.get_property("is_banished"):
            self.parser.fail("The ghost has already been banished.")
            return False
        return True

    def apply_effects(self):
        """
        Effects:
        * Banishes the ghost, causing it to drop its inventory
        """
        # banish the ghost
        self.ghost.set_property("is_banished", True)
        
        # remove ghost from location
        self.location.remove_character(self.ghost)
        
        # drop ghosts inventory
        items_to_drop = list(self.ghost.inventory.keys())
        for item_name in items_to_drop:
            item = self.ghost.inventory[item_name]
            self.ghost.remove_from_inventory(item)
            self.location.add_item(item)
        
        description = "You intone the ancient words. A chilling wail echoes... then silence. The ghost is banished."
        self.parser.ok(description)


class ProposeToPrincess(base.Action):
    """
    Propose marriage to the princess.
    """
    ACTION_NAME = "propose"
    ACTION_DESCRIPTION = "Propose marriage to someone"
    ACTION_ALIASES = ["propose to princess"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.location = self.character.location
        
        # find princess in curr location
        self.princess = None
        for char_name, char in self.location.characters.items():
            if "princess" in char_name.lower():
                self.princess = char
                break

    def check_preconditions(self) -> bool:
        """
        Preconditions:
        * The two characters must be in the same place
        * Neither can be married yet
        * Princess must be present
        """
        if not self.princess:
            self.parser.fail("Theres no one here to propose to.")
            return False
        if not self.location.here(self.princess):
            return False
        if self.character.get_property("is_married"):
            self.parser.fail("You are already married.")
            return False
        if self.princess.get_property("is_married"):
            self.parser.fail("The princess is already married.")
            return False
        return True

    def apply_effects(self):
        """
        Effects:
        * They said "Yes!"
        * They are married.
        * If one is a royal, they are now both royals
        """
        # set marriage status
        self.character.set_property("is_married", True)
        self.princess.set_property("is_married", True)
        
        # if princess is royal, make character royal too
        if self.princess.get_property("is_royal"):
            self.character.set_property("is_royal", True)
        
        description = "With a sweet smile, the princess accepts your proposal. You are now betrothed!"
        self.parser.ok(description)


class WearCrown(base.Action):
    """
    Wear a crown.
    """
    ACTION_NAME = "wear crown"
    ACTION_DESCRIPTION = "Put a crown on your head"
    ACTION_ALIASES = ["wear"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.location = self.character.location
        
        # find crown in chars inventory
        self.crown = self.parser.match_item("crown", self.character.inventory)

    def check_preconditions(self) -> bool:
        """
        Preconditions:
        * The crown must be in the characters inventory
        """
        if not self.was_matched(self.crown, "You dont have a crown."):
            return False
        if not self.character.is_in_inventory(self.crown):
            return False
        if self.crown.get_property("is_worn"):
            self.parser.fail("You are already wearing the crown.")
            return False
        return True

    def apply_effects(self):
        """
        Effects:
        * The character is now wearing the crown
        """
        self.crown.set_property("is_worn", True)
        description = "You put the crown on your head. You feel regal!"
        self.parser.ok(description)


class SitOnThrone(base.Action):
    """
    Sit on the throne, if you are royalty.
    """
    ACTION_NAME = "sit on throne"
    ACTION_DESCRIPTION = "Sit on the throne, if you are royalty"
    ACTION_ALIASES = ["sit throne", "sit"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.location = self.character.location
        
        # find throne in curr location
        self.throne = self.parser.match_item("throne", self.location.items)

    def check_preconditions(self) -> bool:
        """
        Preconditions:
        * The character must be in same location as the throne
        * The character must be a royal
        * The character must be wearing a crown
        """
        if not self.was_matched(self.throne, "There's no throne here."):
            return False
        if not self.location.here(self.character):
            return False
        if not self.character.get_property("is_royal"):
            self.parser.fail("Only royalty may sit upon this throne.")
            return False
        
        # check if char is wearing a crown
        wearing_crown = False
        for item_name, item in self.character.inventory.items():
            if "crown" in item_name.lower() and item.get_property("is_worn"):
                wearing_crown = True
                break
        
        if not wearing_crown:
            self.parser.fail("You should be wearing the crown to claim the throne.")
            return False
        
        return True

    def apply_effects(self):
        """
        Effects:
        * The character becomes the reigning monarch
        * Game is won
        """
        # set the char as reigning
        self.character.set_property("is_reigning", True)
        
        description = "You sit upon the throne as the court erupts in cheers. You are crowned ruler. You win!"
        self.parser.ok(description)
