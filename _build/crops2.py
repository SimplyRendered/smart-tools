"""Crops for apps without a .data block: <slug>_readout/_views/_views2/_top/_phone.png.
usage: FONTS_DIR=... python _build/crops2.py <out_dir> <slug> ..."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from shoot import CSS
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).parent.parent
out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    for slug in sys.argv[2:]:
        url = (ROOT/slug/'index.html').resolve().as_uri()
        ctx = b.new_context(viewport={"width":1280,"height":1000}, color_scheme="dark", device_scale_factor=2)
        ctx.route("https://fonts.googleapis.com/**", lambda r: r.fulfill(status=200, content_type="text/css", body=CSS))
        pg = ctx.new_page(); pg.goto(url); pg.wait_for_timeout(500)
        pg.locator(".readout").first.screenshot(path=str(out/f"{slug}_readout.png"))
        pg.locator(".views").nth(0).screenshot(path=str(out/f"{slug}_views.png"))
        pg.locator(".views").nth(1).screenshot(path=str(out/f"{slug}_views2.png"))
        pg.set_viewport_size({"width":1280,"height":820}); pg.evaluate("window.scrollTo(0,0)"); pg.screenshot(path=str(out/f"{slug}_top.png"))
        ctx.close()
        ctx = b.new_context(viewport={"width":390,"height":844}, color_scheme="dark", device_scale_factor=3, is_mobile=True)
        ctx.route("https://fonts.googleapis.com/**", lambda r: r.fulfill(status=200, content_type="text/css", body=CSS))
        pg = ctx.new_page(); pg.goto(url); pg.wait_for_timeout(500)
        pg.screenshot(path=str(out/f"{slug}_phone.png")); ctx.close()
        print("cropped", slug)
    b.close()
