"""Assemble a Smart Tools app from the house template.
usage: python make.py <app.py> ...   (each app.py defines APP = dict(...))
Writes /<slug>/index.html and /<slug>/<slug>.html (identical) at the repo root."""
import sys, pathlib, runpy
HERE = pathlib.Path(__file__).parent; ROOT = HERE.parent.parent
CSS = (HERE/'house.css').read_text()
EXTRA = """
:root{--ok:#2F8A57;--okbg:rgba(47,138,87,.12);--bad:#C8432B;--badbg:rgba(200,67,43,.10);--warn:#B7791F}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--ok:#5FD08F;--okbg:rgba(95,208,143,.14);--bad:#FF7A5C;--badbg:rgba(255,122,92,.12);--warn:#F2B84B}}
:root[data-theme="dark"]{--ok:#5FD08F;--okbg:rgba(95,208,143,.14);--bad:#FF7A5C;--badbg:rgba(255,122,92,.12);--warn:#F2B84B}
.pill{display:inline-block;font:600 11px/1 var(--body);letter-spacing:.08em;text-transform:uppercase;padding:5px 7px;border:1px solid currentColor}
.pill.ok{color:var(--ok);background:var(--okbg)} .pill.bad{color:var(--bad);background:var(--badbg)} .pill.warn{color:var(--warn)}
td.ok{color:var(--ok)} td.bad{color:var(--bad)}
.readout .ok{color:var(--ok)} .readout .bad{color:var(--bad)}
.view.full{grid-column:1/-1}
.checks{list-style:none;margin:0;padding:0}
.checks li{display:flex;justify-content:space-between;gap:12px;align-items:center;padding:8px 0;border-bottom:1px solid var(--rule);font:13px/1.35 var(--body)}
.checks li span:first-child{min-width:0}
select{appearance:auto}
"""
def build(app):
    a = app
    meta = "".join(f"<div><b>{k}</b>{v}</div>" for k, v in a["meta"])
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{a['title']}</title>
<meta name="description" content="{a['sub']}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>{CSS}{EXTRA}{a.get('css','')}</style>
</head>
<body>
<div class="sheet">
  <header class="tb">
    <h1>{a['h1']}<small>{a['sub']}</small></h1>
    <div class="meta">{meta}</div>
  </header>
  <div class="dl" id="dlbar"><a class="btn" href="{a['slug']}.html" download="{a['slug']}.html">⬇ Download this app</a><span>Free. One HTML file that works offline. Open it in any browser, no install or sign-up.</span><a class="more" href="../">More free tools →</a></div>
  <div class="main">
    <section class="inputs" aria-label="Inputs">
{a['inputs']}
    </section>
    <section style="min-width:0">
{a['right']}
    </section>
  </div>
  <footer class="foot"><span>Free tool · @smart_tools_every_week · simplyrendered.github.io/smart-tools · built with Claude</span><span>{a['source']}</span></footer>
</div>
<script>
if(location.protocol==="file:"){{const b=document.getElementById("dlbar");if(b)b.hidden=true;}}
const $=id=>document.getElementById(id);
const css=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const NS="http://www.w3.org/2000/svg";
function el(tag,attrs,parent,text){{const e=document.createElementNS(NS,tag);for(const k in attrs)e.setAttribute(k,attrs[k]);if(text!=null)e.textContent=text;parent&&parent.appendChild(e);return e}}
const fmt=(v,d=2)=>Number.isFinite(v)?v.toFixed(d):"–";
{a['js']}
document.querySelectorAll("input,select").forEach(i=>i.addEventListener("input",render));
window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change",render);
new MutationObserver(render).observe(document.documentElement,{{attributes:true,attributeFilter:["data-theme"]}});
render();
</script>
</body>
</html>
"""
    d = ROOT/a['slug']; d.mkdir(exist_ok=True)
    (d/'index.html').write_text(html); (d/f"{a['slug']}.html").write_text(html)
    print("built", a['slug'])
for p in sys.argv[1:]:
    build(runpy.run_path(p)["APP"])
