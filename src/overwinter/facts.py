# @author Daniel McCoy Stephenson
"""Everything the player can come to know.

A fact is the unit of progress in Overwinter. There is no reset here - the
winter runs on - but the design is the same as Tidewater's: what opens a
door is what you know, never how many days have gone by. Each fact has a
title for the journal and the line the journal shows under it. Order here
is the order the journal lists them in, roughly the order a player is
likely to learn them.

Facts point at each other. A fact's "leads" are the things it hints can be
learned next - each a target fact id and the line the journal shows while
that target is still unknown. The line never names the target; it says
where to look, the way a rumour does. That web is what makes the journal a
map of the station rather than a checklist.
"""

THE_STORE = "the_store"
THE_MANIFEST = "the_manifest"
THE_SLEDGE = "the_sledge"
THE_OLD_HUT = "the_old_hut"
THE_ICE = "the_ice"
THE_FIFTH = "the_fifth"
AKSELS_WINTER = "aksels_winter"
MARITS_ARITHMETIC = "marits_arithmetic"
THE_DEPOT = "the_depot"
THE_SEALS = "the_seals"
THE_RULE = "the_rule"
SEVENTY_ONE = "seventy_one"
DOVS_GAME = "dovs_game"
TEOS_NIGHTS = "teos_nights"
THE_PLANE = "the_plane"
# The endings. One of these is the last thing a player learns.
THE_DARK_FLIGHT = "the_dark_flight"
FIVE_OUT = "five_out"
AKSEL_STAYED = "aksel_stayed"

FACTS = {
    THE_STORE: {
        "title": "The store",
        "text": "You counted the store yourself: fifteen days of food at four, "
        "and the plane cannot come for twenty. Nobody has said so. Marit "
        "signed for more than this.",
        "leads": [
            {
                "to": THE_MANIFEST,
                "text": "Everything that was loaded off the ship was counted "
                "and sent to the mainland by radio. Whoever sent it has the "
                "figure.",
            },
            {
                "to": MARITS_ARITHMETIC,
                "text": "Marit has wintered here eight times. She does not "
                "miscount food. If the store is short, she knows why.",
            },
            {
                "to": THE_PLANE,
                "text": "Twenty days is what everyone says. Somebody knows "
                "what the plane actually needs to land, and whether it has "
                "ever come sooner.",
            },
        ],
    },
    THE_MANIFEST: {
        "title": "The manifest",
        "text": "Dov sent the manifest in September: fourteen crates of stores "
        "landed, signed for by Marit - twenty-one days at four. Ten crates "
        "are in the galley. Four are somewhere else on this island.",
        "leads": [
            {
                "to": THE_SLEDGE,
                "text": "Four crates do not walk. Something carried them, and "
                "the man who keeps the machines would know if it was used.",
            },
        ],
    },
    THE_SLEDGE: {
        "title": "The sledge went out before you came",
        "text": "Teo says the snowmobile had three hours on its meter the day "
        "he arrived, and the sledge runners were wet. Somebody made a trip "
        "across the bay and back with a load, before the plane that brought "
        "you both.",
        "leads": [
            {
                "to": THE_OLD_HUT,
                "text": "Across the bay is nothing - or nothing anyone has "
                "mentioned. The station log goes back sixty years. It would "
                "say what is over there.",
            },
        ],
    },
    THE_OLD_HUT: {
        "title": "The old hut",
        "text": "From the log, 1961: the station moved to this side of the bay "
        "and the old hut was closed up, stove and bunks left in, 'against "
        "need'. It is still standing. It is an hour across the ice, or a "
        "day round the headland on foot.",
        "leads": [
            {
                "to": THE_ICE,
                "text": "An hour across the ice, if the ice holds. Marit's log "
                "has a table of when it has held, every winter for eight.",
            },
            {
                "to": THE_FIFTH,
                "text": "A hut with a stove and four crates of food in it is "
                "not being kept against need. Somebody is over there.",
            },
        ],
    },
    THE_ICE: {
        "title": "When the bay ice holds",
        "text": "The bay is safe to walk once the sea ice has had three still "
        "nights after the first hard frost. Marit's table says that is the "
        "fifth day this year. Before then it is the headland or nothing.",
    },
    THE_FIFTH: {
        "title": "There are five of you",
        "text": "Aksel Rue is in the old hut. He was the cook here for four "
        "winters, until this one. He has a stove, a bunk, and four crates "
        "with the station's stencil on them. He was on the ship out in "
        "August, on paper. He never went.",
        "leads": [
            {
                "to": AKSELS_WINTER,
                "text": "A man does not spend a winter alone in a hut for no "
                "reason. He will tell you his if you sit long enough.",
            },
            {
                "to": MARITS_ARITHMETIC,
                "text": "Somebody signed him off the ship and carried his "
                "crates across. Only one person here could do both.",
            },
            {
                "to": THE_RULE,
                "text": "Five people on an island whose paperwork says four. "
                "The man who sends the paperwork has rules about that.",
            },
        ],
    },
    AKSELS_WINTER: {
        "title": "Why Aksel stayed",
        "text": "Aksel failed the medical in the spring - on age, nothing else; "
        "he is sixty-seven. He was told he would not winter again. He came "
        "out on the supply ship as a visitor and asked Marit for one more, "
        "and she gave it to him. There is nowhere he would rather be, and "
        "nobody waiting anywhere else.",
        "leads": [
            {
                "to": THE_SEALS,
                "text": "Four winters cooking here and he is not thin. Aksel "
                "knows how to feed himself off this island, and he could "
                "show you.",
            },
        ],
    },
    MARITS_ARITHMETIC: {
        "title": "Marit's arithmetic",
        "text": "Marit signed Aksel off the manifest and carried his crates "
        "across before the ice went. Her plan for the station's gap was the "
        "old depot on the headland and the seals off the point, fetched once "
        "the ice held. The ice held late this year and the storm is coming. "
        "She says the sum still closes. She did not mean anyone to have to "
        "check it.",
        "leads": [
            {
                "to": THE_DEPOT,
                "text": "'The old depot on the headland.' It is in the log "
                "somewhere, with a year on it.",
            },
            {
                "to": THE_SEALS,
                "text": "'The seals off the point.' Marit has never hunted "
                "them. Somebody on this island has.",
            },
        ],
    },
    THE_DEPOT: {
        "title": "The 1958 depot",
        "text": "From the log, 1958: an emergency depot laid in a stone cairn "
        "on the headland - pemmican and hard bread in sealed tins, 'for "
        "twelve days at one man'. Nobody has opened it since. It is an "
        "afternoon's walk. Some of it will have gone.",
    },
    THE_SEALS: {
        "title": "The breathing holes",
        "text": "Aksel knows the seal holes off the point and the way to wait "
        "at one. A seal is two days of food for the whole station. It takes "
        "a still day, patience, and him - he will not tell you where they "
        "are, only show you.",
    },
    THE_RULE: {
        "title": "Dov's rule",
        "text": "Dov's standing orders: any person on the island not on the "
        "wintering list is reported to Base on the next schedule, no "
        "exceptions. Base would order a flight. Dov does not break rules. "
        "He has not been told, because Marit knows that.",
        "leads": [
            {
                "to": SEVENTY_ONE,
                "text": "'Base would order a flight' - in the dark, in this "
                "weather. The log would say whether that has ever been done, "
                "and how it went.",
            },
            {
                "to": DOVS_GAME,
                "text": "Dov keeps his schedule the way other men keep "
                "promises. Listen to what goes out on it.",
            },
        ],
    },
    SEVENTY_ONE: {
        "title": "The 1971 flight",
        "text": "From the log, 1971: a wintering man took a fever in December "
        "and Base sent the plane in the dark. It went into the ridge on the "
        "approach. The pilot, Haugen, was killed. The sick man recovered "
        "on his own in January. The log's next line, in the leader's hand: "
        "'We should have waited.'",
    },
    DOVS_GAME: {
        "title": "Dov's chess game",
        "text": "The nightly chess by Morse is with Sunniva, the operator at "
        "Base. The moves are real, but there are more words on the key "
        "than any game needs. It is not chess. It is the only hour of Dov's "
        "day he would not trade for anything, and it is why the schedule is "
        "sacred to him.",
    },
    TEOS_NIGHTS: {
        "title": "Teo's nights",
        "text": "Teo cannot sleep in the dark, so he runs the generator "
        "through the night for the lights, and has since the plane left. "
        "The fuel margin Marit planned for the storm is gone. On the storm "
        "nights the generator will run dry unless the night hours are cut.",
    },
    THE_PLANE: {
        "title": "What the plane needs",
        "text": "The Otter needs an hour of usable light on the strip and a "
        "wind under thirty knots. The light comes back on the twentieth "
        "day. It carries six. It has come sooner than that once in sixty "
        "years, and never since.",
    },
    THE_DARK_FLIGHT: {
        "title": "The dark flight",
        "text": "Dov reported a fifth man on the island. Base sent the plane in "
        "the dark, on the twelfth day, in a two-hour window. It found the "
        "strip. It took Aksel and Marit out, and the rest of you finished "
        "the winter as three.",
    },
    FIVE_OUT: {
        "title": "Five on the plane",
        "text": "The plane came on the twentieth day and five of you got on "
        "it. What the winter cost each of you, and what Marit will answer "
        "for at the other end, is written on the last page.",
    },
    AKSEL_STAYED: {
        "title": "Aksel stayed",
        "text": "Four of you got on the plane. Aksel walked back across the "
        "bay to the hut before the pilot counted heads, because you let him. "
        "The supply ship comes in August. He has the stove, the seal holes, "
        "and what is left of the depot.",
    },
}

# The facts the count turns on, in the order they have to be learned: the
# trail from the store to the man across the bay. The journal marks these
# so a player who has learned a few knows how far there is to go.
TRAIL = [THE_STORE, THE_MANIFEST, THE_SLEDGE, THE_OLD_HUT, THE_FIFTH]

ENDINGS = (THE_DARK_FLIGHT, FIVE_OUT, AKSEL_STAYED)


def title(factId):
    return FACTS[factId]["title"]


def leads(factId):
    """The rumours a fact carries: [(targetFactId, line), ...]."""
    return [(lead["to"], lead["text"]) for lead in FACTS[factId].get("leads", [])]


def text(factId):
    return FACTS[factId]["text"]
