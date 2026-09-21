# Overwinter

*Four people, one weather station, twenty days until a plane.*

The plane that brought you to Cape Ferrin left an hour ago and cannot come back until there is light enough to land on. You are the cook; you took the job because nobody else would. The store is in the galley, and the store is your job. Nobody has asked you to count it.

When you do, it is five days short.

Overwinter is a text adventure built on [tak](https://github.com/Stephenson-Software/tak), the text-adventure kit, and a sibling of [Tidewater](https://github.com/Stephenson-Software/Tidewater). No time loop this time: the winter runs on, everything you learn lasts, everything you say is remembered, and the twentieth morning says plainly what you did.

## Play

`pip install -r requirements.txt` needs `git` on your PATH: the kit is installed from its GitHub tag.

**In your browser** — the game runs in your tab, saves live in your browser:

```bash
pip install -r requirements.txt
python3 web/build_zip.py     # once, and after any src/ change or tak upgrade
python3 web/serve.py         # then open http://127.0.0.1:8080
```

**In a terminal:**

```bash
pip install -r requirements.txt
./run.sh                     # or: PYTHONPATH=src python3 -m overwinter
```

**As a server** (the browser is a terminal for a game running on your machine; everyone who opens the page shares it): `./run.sh web`, then open `http://127.0.0.1:8000`. `OVERWINTER_WEB_HOST`/`OVERWINTER_WEB_PORT` move either server.

**Docker:** `docker build -t overwinter . && docker run -p 8080:8080 overwinter` serves the browser build.

## The story

A cook, a station, a count that does not add up, and four people who each know part of why. The game tells it in pieces; the journal's "What is happening to you" page assembles the pieces you have found, in plain words, from the first day. The whole of it, spoilers included, is in [docs/STORY.md](docs/STORY.md).

## How it works

The winter is twenty days long, three watches to a day, and every action costs a watch. Six places on the station — the galley, Marit's office, the radio room, the generator shed, the bunkroom, the strip — and one across the bay. Talk to people; read the log. Some of what you hear is a **fact**, and facts go in your journal and open new questions on other people's menus. Facts point at each other, Outer Wilds fashion: under each one the journal lists where it leads that you haven't been, without naming what is there. There are eighteen facts, and the trail from the store to the man across the bay is five of them long.

The count is real arithmetic and the header shows it: rations on the shelf, mouths at the table, days until the plane. The store as found is fifteen days at four. The 1958 depot on the headland is three more; a seal, with the right person at the breathing hole, is two; half rations double what is left at a cost the ending will name. Any two of those and there is food on the shelf when the plane comes. None of them, and the store runs out on the fifteenth night — and what happens then answers the count whether or not you went looking.

Some of what people ask you is a **choice**, not a question, and unlike a time loop nothing forgets it. *Marit will remember that.* Keep her secret or tell her you won't; tell Dov there are five and then find him a reason to wait — or don't, and learn that walking away from that conversation is also a choice; tell Marit about Teo's generator nights or cover for him and freeze on the storm night; bring Aksel in or leave him his winter; and on the strip, when he asks you to say four, answer him. Three endings — five on the plane, the dark flight on the twelfth day, and Aksel staying for the ship — and each one's last page says what happened, what you did that made it happen, and what it cost whom, in that order.

The state is one tier (`state.py`): the day and the watch, the facts and the day each was learned, the flags (every one named in `flags.py`), the food, where Aksel is, and the ending once there is one. The clock is `winter.py`: the end of every day eats the store and consults the calendar — the ice holding on the fifth, the storm on the eighth, the dark flight on the twelfth if it was called, the plane on the twentieth. Scenes never decide any of that for themselves.

The winter is seeded, so the same wait at the same hole gives up the same seal, and a reloaded save continues the same sequence.

## Saves

Numbered slots under `data/` (or `OVERWINTER_SAVE_DIR`), one `save.json` each, validated against `schemas/save.json` on every load and save. A save that can't be read is listed as damaged, never overwritten, and copied aside if you open it anyway.

## Usage reporting

Overwinter reports one `startup` event and one `save-loaded` event (program name and version only) to `trace.danielstephenson.dev`, on by default, and prints a one-line notice the first time an install does so. `OVERWINTER_USAGE_REPORTING_ENABLED=false`, `TRACE_USAGE_REPORTING=off` or `DO_NOT_TRACK=1` turns it off, the browser build never reports, and what is collected and why is written up in the [trace client's README](https://github.com/Stephenson-Software/trace-client-python#turning-it-off).

## Development

```bash
pip install pytest pytest-cov -r requirements.txt
./test.sh
```

`tests/test_game.py` plays the whole winter through a scripted front-end, to each ending; if a menu label moves or a gate breaks, that test says which.

## License
This project is licensed under the **Stephenson Software Non-Commercial License (Stephenson-NC)**.  
© 2026 Daniel McCoy Stephenson. All rights reserved.  

You may use, modify, and share this software for **non-commercial purposes only**.  
Commercial use is prohibited without explicit written permission from the copyright holder.  

Full license text: [Stephenson-NC License](https://github.com/Stephenson-Software/stephenson-nc-license) (also in [LICENSE](LICENSE))  
SPDX Identifier: `Stephenson-NC`
