# 鯉 · The koi on my profile

Behind the streak card swims a pixel-art koi. It isn't a fixed drawing: it grows out of my public GitHub activity and redraws itself.

> The koi itself is drawn by **[git-koi](https://github.com/yalongwastaken/git-koi)** by [Anthony Yalong (@yalongwastaken)](https://github.com/yalongwastaken), released under the MIT licence. All the credit for the fish, its colours and its patterns goes to that project; this profile only adds the swimming, the pond and the glass card around it.

## Where the fish comes from

git-koi draws it every night (00:20 UTC) from the account's public data:

- **Base body:** the body chosen in the workflow (`white`). The others are `black`, `asagi`, `tea`, `gold` and `platinum`.
- **Patches = languages.** Each language in my public repos (and in public repos I contribute to) is mapped, by its GitHub colour, to the nearest koi pigment: red (*beni*), orange, yellow (*ki*) or blue (*ai*). Grey or colourless languages become black (*sumi*). The strongest pigment sets the main pattern, the second adds spots or sides, and the third tints the fin roots.
- **Size = contributions.** With few contributions the koi is young, small and pale. As contributions add up it grows and shows its full colours.
- **Streaks.** The current streak paints the fin edges gold. The longest streak makes the colours more vivid.

## How it swims

- Every day it follows a new random path: it changes course and speed, keeps off the edges, and passes behind the card, which acts as frosted glass.
- It swims straight on straight stretches and bends into its turns.
- Now and then it slows down and rises to the surface, the way koi do when they feed: its mouth breaks the water and leaves ripples.

## How it's made

- [`.github/workflows/koi.yml`](../.github/workflows/koi.yml) draws `koi/koi.gif` with git-koi.
- [`.github/workflows/streak-koi.yml`](../.github/workflows/streak-koi.yml) fetches the [GitHub Readme Streak Stats](https://github.com/DenverCoder1/github-readme-streak-stats) card every 6 hours and runs [`.github/scripts/streak_koi.py`](../.github/scripts/streak_koi.py). The script straightens the koi's frames, generates the day's path and combines everything into one animated SVG: [`koi/streak-koi.svg`](streak-koi.svg).
- It's an SVG rather than a GIF so it always moves, with no play button.

[← Back to profile](https://github.com/S34mu5)
