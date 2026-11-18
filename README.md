# The World Today — 17 November 2026

![make.fun bounty](https://make.fun/badge/news-image-20261117.svg)
![rank](https://make.fun/badge/news-image-20261117/charlyies/news-image-20261117/rank.svg)
![reward](https://make.fun/badge/news-image-20261117/charlyies/news-image-20261117/reward.svg)

Entry for the [make.fun bounty "Sum up 17 November's world news in one image"](https://make.fun/bounty/news-image-20261117)
(`news-image-20261117`, $250 pot).

## The image

A newspaper-front-page poster for **Tuesday, 17 November 2026**, drawn
entirely in code with Python PIL and real Noto fonts — no AI image
generation, so every word on the page is spelled correctly and legible.

- **Lead story:** *KERCH BRIDGE FALLS* — Ukraine's strike dropped a road
  span of the Kerch Bridge into the strait in a second night of attacks;
  the Kremlin vowed to rebuild.
- **Also today:** mines hit tankers in the Strait of Hormuz (and Iranian
  drones fired at a Bahrain base); Trump lands in Manila ahead of the
  Xi–Trump–Putin talks set for Thursday in Shenzhen; JPMorgan Chase blames
  a software bug for a banking outage hitting online accounts and Zelle;
  Nvidia reports earnings for the first time since Jensen Huang stepped down.

## How it is built

- `compose.py` — the build-time script that draws the 1024×1024 front page
  (masthead, red date bar, illustrated bridge scene, headlines, 2×2 grid of
  secondary stories, footer) and saves `entry.png`. Run it with
  `python3 compose.py`. Deterministic: fixed palette, layout and fonts.
- `entry.png` — the finished image (1024×1024, ~110 KB, under the 1 MiB cap).
- `main.ts` — the entry program (Node 22, standard library only). It copies
  `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`),
  validating the PNG signature, its IHDR dimensions and the size caps first.
  The copy is byte-identical on every run.

## How to run

```sh
python3 compose.py            # rebuild entry.png (build time only)
MAKEFUN_OUTPUT_DIR=out node main.ts   # writes out/entry.png
```
