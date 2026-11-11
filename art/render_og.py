#!/usr/bin/env python3
"""Render web/og.png, the picture a shared link to Overwinter unfurls with.

    python3 art/render_og.py --strata-golden /path/to/strata-golden \\
        --og-card /path/to/community-site-kit/tools/og-card

The picture is art/og.scene (the strip at noon on day 20, the station's lamps
lit), drawn offline and headless by Strata's golden-image tool at 2400x1260,
the same way art/render.py draws the location stills:

    strata-golden render art/og.scene <out.png> --surface headless

Build strata-golden from Strata's source at the tag named in OG["strata"]
(see art/render.py for the cmake lines). The title, tagline and address are
then set over it by community-site-kit's og-card tool (tools/og-card/og_card.py,
its compose() step only), so the card's type and dark scrim match the other
link-preview cards made with that tool. Check that tool out at OG["og_card"]
and install its requirements.txt (Pillow) first. The PNG is committed; CI never
re-renders it. The <meta> tags in web/index.html carry OG["alt"].
"""

import argparse
import os
import subprocess
import sys
import tempfile

ART = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(ART)
SCENE = os.path.join(ART, "og.scene")
OUTPUT = os.path.join(ROOT, "web", "og.png")

OG = {
    "strata": "v0.7.0",
    "og_card": "5e3329e2f50d9700ad60979270557fb0e3de98f8",
    "title": "Overwinter",
    "wordmark": "A text adventure",
    "subtitle": "Four people, one station, twenty days until a plane.",
    "url": "overwinter.danielstephenson.dev",
    "accent": "#7fb0d0",
    "alt": (
        "A snowy airstrip at polar twilight lit by a lamp on a post, the station's red huts with glowing windows "
        "and a windsock behind it, a dark ridge against a faint red sky, beside the title Overwinter."
    ),
}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--strata-golden", default=os.environ.get("STRATA_GOLDEN"), required=False)
    parser.add_argument("--og-card", required=True, help="community-site-kit's tools/og-card directory")
    args = parser.parse_args(argv)
    if not args.strata_golden:
        parser.error("--strata-golden (or STRATA_GOLDEN) is required")

    sys.path.insert(0, os.path.abspath(args.og_card))
    import og_card  # noqa: E402  (community-site-kit tools/og-card)
    from PIL import Image

    env = dict(os.environ)
    env.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")
    env.setdefault("GALLIUM_DRIVER", "llvmpipe")
    with tempfile.TemporaryDirectory() as tmp:
        render = os.path.join(tmp, "og-scene.png")
        subprocess.run([args.strata_golden, "render", SCENE, render, "--surface", "headless"], check=True, env=env)
        image = Image.open(render).convert("RGBA")
        spec = {
            "title": OG["title"],
            "wordmark": OG["wordmark"],
            "subtitle": OG["subtitle"],
            "url": OG["url"],
            "accent": OG["accent"],
            "credit": "Rendered with Strata",
        }
        card = og_card.compose(image.tobytes(), image.size, spec, ART, OG["strata"].lstrip("v"))
    card.save(OUTPUT, format="PNG", optimize=True)
    print("wrote %s" % OUTPUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
