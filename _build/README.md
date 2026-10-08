# Build kit (used by the weekly Claude run)
- `shoot.py` – screenshot helper (serves Google Fonts from local @fontsource; set FONTS_DIR)
- `arch_render.py` – renders 1080×1350 Instagram carousel JPEGs from a posts JSON
- `registry.json` – tools built so far, next T-number, idea backlog
- `posts-*.json` – the slide/caption source for each week
Each app lives in `/<slug>/index.html` (online) and `/<slug>/<slug>.html` (download copy, identical).
Slides live in `/posts/<YYYY-MM-DD>_<slug>_<NN>.jpg` and are given to Metricool as raw.githubusercontent.com URLs.
