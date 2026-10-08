"""Render Instagram carousel slides (1080x1350 JPEG) in the drafting/blueprint identity.
usage: arch_render.py posts.json crops_dir out_dir"""
import json, sys, html, pathlib, base64
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from shoot import CSS
from playwright.sync_api import sync_playwright
posts = json.loads(pathlib.Path(sys.argv[1]).read_text()); crops = pathlib.Path(sys.argv[2]); out = pathlib.Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=True)
E = html.escape
def uri(name):
    return "data:image/png;base64," + base64.b64encode((crops/name).read_bytes()).decode()
BASE = CSS + """
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0E1A26;--sheet:#132233;--ink:#E4ECF2;--ink2:#9DB0C0;--rule:#2A3D52;--grid:#1B2D40;--red:#FF7A5C;--blue:#6FB0F0}
body{width:1080px;height:1350px;background:var(--bg);color:var(--ink);font-family:'IBM Plex Sans',sans-serif;overflow:hidden;
 background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px);background-size:40px 40px}
.frame{position:absolute;inset:40px;border:3px solid var(--ink);background:var(--sheet);display:flex;flex-direction:column}
.tb{display:flex;justify-content:space-between;align-items:stretch;border-bottom:3px solid var(--ink);font:500 22px/1 'IBM Plex Mono',monospace;color:var(--ink2)}
.tb div{padding:18px 26px;border-right:2px solid var(--rule)} .tb div:last-child{border-right:0;margin-left:auto}
.tb b{color:var(--red);font-weight:500}
.body{flex:1;padding:56px 60px 40px;display:flex;flex-direction:column;min-height:0}
.kicker{font:600 26px/1 'IBM Plex Sans',sans-serif;letter-spacing:.16em;text-transform:uppercase;color:var(--red)}
h1{font-family:'Barlow Condensed',sans-serif;font-weight:700;text-transform:uppercase;line-height:.95;letter-spacing:.005em}
.body.b-hook h1{font-size:112px;margin-top:22px}
.body.b-hook .sub{font-size:36px;line-height:1.3;color:var(--ink2);margin-top:26px;font-weight:500}
.title{font-size:84px;margin-top:20px}
.img{margin-top:36px;flex:1;min-height:0;display:flex;align-items:flex-start;justify-content:center;overflow:hidden;border:2px solid var(--rule)}
.img img{max-width:100%;max-height:100%;object-fit:contain;display:block}
.body.b-hook .img{margin-top:36px}
ul,ol{list-style:none;margin-top:46px}
li{font-size:44px;line-height:1.22;font-weight:500;padding:30px 0 30px 78px;position:relative;border-top:2px solid var(--rule)}
li:last-child{border-bottom:2px solid var(--rule)}
ul li:before{content:'';position:absolute;left:6px;top:46px;width:30px;height:30px;border:4px solid var(--red)}
ol{counter-reset:n} ol li:before{counter-increment:n;content:counter(n);position:absolute;left:0;top:30px;width:52px;height:52px;background:var(--red);color:var(--bg);
 font:700 34px/52px 'IBM Plex Mono',monospace;text-align:center}
.phonewrap{display:flex;gap:44px;align-items:center;flex:1;min-height:0;margin-top:30px}
.phone{height:780px;aspect-ratio:390/844;border:14px solid #05090e;border-radius:56px;overflow:hidden;background:#000;flex:none;box-shadow:0 0 0 3px var(--rule)}
.phone img{width:100%;height:100%;object-fit:cover;object-position:top;display:block}
.phonewrap .t{flex:1}
.phonewrap h1{font-size:76px}
.body.b-cta h1{font-size:120px;margin-top:40px}
.body.b-cta h1 em{font-style:normal;color:var(--red)}
.body.b-cta .sub{font-size:40px;line-height:1.35;color:var(--ink2);margin-top:40px;font-weight:500}
.body.b-cta .bio{margin-top:auto;border:3px solid var(--red);padding:28px 32px;font:600 46px/1.1 'IBM Plex Mono',monospace;color:var(--red);align-self:flex-start}
.body.b-cta .handle{margin-top:26px;font:700 56px/1 'Barlow Condensed',sans-serif;letter-spacing:.02em}
"""
def slide(post, s, i, n):
    t = s["t"]; tb = f'<div class="tb"><div><b>{E(post["no"])}</b></div><div>FREE TOOL · {E(post["name"].upper())}</div><div>{i}/{n}</div></div>'
    k = f'<div class="kicker">{E(s.get("kicker",""))}</div>' if s.get("kicker") else ""
    if t == "hook":
        b = f'<div class="kicker">New free tool · link in bio</div><h1>{E(s["title"])}</h1><div class="sub">{E(s["sub"])}</div><div class="img"><img src="{uri(s["img"])}"></div>'
    elif t == "shot":
        b = f'{k}<h1 class="title">{E(s["title"])}</h1><div class="img"><img src="{uri(s["img"])}"></div>'
    elif t == "list":
        b = f'{k}<h1 class="title">{E(s["title"])}</h1><ul>' + "".join(f"<li>{E(x)}</li>" for x in s["items"]) + "</ul>"
    elif t == "steps":
        b = f'{k}<h1 class="title">{E(s["title"])}</h1><ol>' + "".join(f"<li>{E(x)}</li>" for x in s["items"]) + "</ol>"
    elif t == "phone":
        b = f'<div class="phonewrap"><div class="phone"><img src="{uri(s["img"])}"></div><div class="t">{k}<h1 style="margin-top:20px">{E(s["title"])}</h1></div></div>'
    else:
        b = ('<div class="kicker">Free · no sign-up</div><h1>Save this.<br><em>A new tool for</em><br><em>architects</em> every week.</h1>'
             f'<div class="sub">Built with Claude. Mondays, Wednesdays and Fridays.</div><div class="bio">Link in bio → {E(post["no"])}</div><div class="handle">@smart_tools_every_week</div>')
        t = "cta"
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{BASE}</style></head><body><div class="frame f-{t}">{tb}<div class="body b-{t}">{b}</div></div></body></html>'
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={"width":1080,"height":1350})
    for post in posts:
        n = len(post["slides"])
        for i, s in enumerate(post["slides"], 1):
            pg.set_content(slide(post, s, i, n)); pg.wait_for_timeout(250)
            over = pg.evaluate("(()=>{const b=document.querySelector('.body');return b.scrollHeight-b.clientHeight})()")
            fn = out/f'{post["date"]}_{post["slug"]}_{i:02d}.jpg'
            pg.screenshot(path=str(fn), type="jpeg", quality=90)
            if over > 2: print("OVERFLOW", fn.name, over)
        cap = post["caption"] + "\n\nHASHTAGS: " + post["hashtags"] + "\n" + "\n".join(f"ALT {j:02d}: {a}" for j, a in enumerate(post["alt"], 1))
        (out/f'{post["date"]}_{post["slug"]}_caption.txt').write_text(cap)
    br.close()
print("done")
