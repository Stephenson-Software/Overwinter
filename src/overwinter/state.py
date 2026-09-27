# @author Daniel McCoy Stephenson
"""The state of one winter, and the save file that holds it.

One tier, because nothing resets: the day and the watch, where the player
is, what they know (facts, and the day each was learned), what has been
done and chosen (flags), how much food is in the store, where Aksel is,
and - once it has happened - which ending the winter came to. The save
file is one JSON object, validated against schemas/save.json on every load
and save.
"""

import random

from overwinter import facts, flags

SAVE_VERSION = 1
SAVE_FILENAME = "save.json"
SCHEMA_PATH = "schemas/save.json"

# The world seed. Constant on purpose: the same winter gives up the same
# seals to the same waits, so a player who reloads is not rolling dice.
WORLD_SEED = 1958

# --- the calendar -----------------------------------------------------------
# Days are counted from the morning after the plane left. The plane cannot
# come back until there is light enough on the strip: the twentieth day.
PLANE_DAY = 20
# The bay ice has had three still nights after the first hard frost.
ICE_SAFE_DAY = 5
# The storm out of the north-east. Nobody goes out.
STORM_DAYS = (8, 9)
# If Dov reports a fifth man, Base sends the plane in the dark on this day.
DARK_FLIGHT_DAY = 12

# Three watches to a day. The hours are nominal - it is dark for all of
# them - but the station keeps them, and so does the header.
WATCHES = ("Morning", "Afternoon", "Evening")
WATCH_HOURS = (8, 14, 20)
MORNING, AFTERNOON, EVENING = 0, 1, 2

# --- the count --------------------------------------------------------------
# Food is counted in rations: one person, one day. Fifteen days at four is
# what the cook finds in the galley; twenty-one is what the manifest says.
STATION_MOUTHS = 4
START_FOOD = 15 * STATION_MOUTHS
MANIFEST_FOOD = 21 * STATION_MOUTHS
# Four crates of six rations went across the bay with Aksel.
AKSEL_CRATES = 24
# The 1958 depot: twelve days at one man, of which half has gone.
DEPOT_FOOD = 12
# One seal feeds the station for two days.
SEAL_FOOD = 8

START_LOCATION = "galley"

# Where Aksel is. "hut" until he is found and brought in, or walks in on
# his own; "flown" after the dark flight; "stayed" is the ending.
AKSEL_HUT = "hut"
AKSEL_STATION = "station"
AKSEL_FLOWN = "flown"
AKSEL_STAYED = "stayed"


class State:
    def __init__(self):
        self.day = 1
        self.watch = MORNING
        self.location = START_LOCATION
        self.facts = []
        # The day each fact was learned on, by fact id. The only history the
        # model keeps beyond the flags.
        self.factDays = {}
        self.unlocked = []
        self.flags = {}
        self.food = START_FOOD
        self.akselAt = AKSEL_HUT
        # Aksel's own crates, eaten at one a day while he is in the hut and
        # pooled with the store when he comes in.
        self.akselFood = AKSEL_CRATES
        self.seals = 0
        self.ending = None
        # How many draws have been taken from the winter's fixed sequence, so
        # a loaded game continues the same winter rather than restarting the dice.
        self.rngDraws = 0

    # --- knowledge --------------------------------------------------------
    def knows(self, factId):
        return factId in self.facts

    def learn(self, factId):
        """Record a fact. Returns True if it was new."""
        if factId not in facts.FACTS:
            raise ValueError("unknown fact %r" % factId)
        if factId in self.facts:
            return False
        self.facts.append(factId)
        self.factDays[factId] = self.day
        return True

    def learnedOn(self, factId):
        """The day a fact was learned, or None if not known."""
        return self.factDays.get(factId)

    # --- the count --------------------------------------------------------
    @property
    def mouths(self):
        return STATION_MOUTHS + (1 if self.akselAt == AKSEL_STATION else 0)

    @property
    def dailyRations(self):
        """What the store loses at the end of a day."""
        if self.flags.get(flags.HALF_RATIONS):
            return (self.mouths + 1) // 2
        return self.mouths

    @property
    def foodDays(self):
        return self.food // self.dailyRations

    @property
    def daysUntilPlane(self):
        return max(0, PLANE_DAY - self.day)

    @property
    def stormy(self):
        return self.day in STORM_DAYS

    @property
    def iceSafe(self):
        return self.day >= ICE_SAFE_DAY

    @property
    def stormNightPassed(self):
        """The first night of the storm - the one the fuel margin decides -
        has been lived through, one way or the other."""
        return self.day > STORM_DAYS[0]

    @property
    def over(self):
        return self.ending is not None

    def draw(self, choices):
        """One draw from the winter's fixed sequence.

        Each draw is a pure function of the world seed and its own index -
        a fresh generator seeded per draw - rather than the next output of one
        long-lived generator. That is what makes a loaded save continue the
        sequence exactly: replaying N draws of a long-lived generator is only
        faithful when every draw consumes the same amount of randomness, and
        random.choice does not."""
        rng = random.Random(WORLD_SEED * 1000003 + self.rngDraws)
        self.rngDraws += 1
        return rng.choice(choices)

    # --- persistence ------------------------------------------------------
    def toDict(self):
        return {
            "version": SAVE_VERSION,
            "day": self.day,
            "watch": self.watch,
            "location": self.location,
            "facts": list(self.facts),
            "factDays": dict(self.factDays),
            "unlocked": list(self.unlocked),
            "flags": dict(self.flags),
            "food": self.food,
            "akselAt": self.akselAt,
            "akselFood": self.akselFood,
            "seals": self.seals,
            "ending": self.ending,
            "rngDraws": self.rngDraws,
        }

    @classmethod
    def fromDict(cls, data):
        state = cls()
        state.day = data["day"]
        state.watch = data.get("watch", MORNING)
        state.location = data.get("location", START_LOCATION)
        state.facts = [f for f in data.get("facts", []) if f in facts.FACTS]
        state.factDays = {
            f: int(n) for f, n in data.get("factDays", {}).items() if f in state.facts
        }
        state.unlocked = list(data.get("unlocked", []))
        state.flags = dict(data.get("flags", {}))
        state.food = data.get("food", START_FOOD)
        state.akselAt = data.get("akselAt", AKSEL_HUT)
        state.akselFood = data.get("akselFood", AKSEL_CRATES)
        state.seals = data.get("seals", 0)
        state.ending = data.get("ending")
        state.rngDraws = data.get("rngDraws", 0)
        return state
