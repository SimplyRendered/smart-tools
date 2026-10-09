"""Record a 1080x1920 Instagram reel (with Kokoro voiceover) of an app being used.
Scripts live in _build/reels.json: {slug: {no, name, hook, steps:[[caption, seconds, js]], vo:[hook line, one per step, end line]}}.
Env: FONTS_DIR (fontsource), TTS_DIR (kokoro-v1.0.int8.onnx + voices-v1.0.bin from github.com/thewh1teagle/kokoro-onnx releases), VOICE (default af_heart).
usage: FONTS_DIR=... python _build/reel.py <slug> <out.mp4>
The app is served over a local http server and shown inside a branded stage page.
Each app's script is in REELS below: a hook line, then steps of (caption, seconds, js-run-inside-app)."""
import sys, pathlib, json, subprocess, threading, http.server, socketserver, functools, tempfile, shutil, time
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from shoot import CSS
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).parent.parent

# helpers available inside the app frame: set(id,value), slide(id,from,to,ms), scrollTo(sel), click(sel)
REELS = json.loads((pathlib.Path(__file__).parent/"reels.json").read_text())


# Voiceover lines: hook, one per step, end card
VO = {k: v["vo"] for k, v in REELS.items()}
TTS_DIR = pathlib.Path(__import__("os").environ.get("TTS_DIR","tts"))
VOICE = __import__("os").environ.get("VOICE","af_heart")
def make_vo(slug, tmp):
    from kokoro_onnx import Kokoro
    import soundfile as sf
    k = Kokoro(str(TTS_DIR/"kokoro-v1.0.int8.onnx"), str(TTS_DIR/"voices-v1.0.bin"))
    out=[]
    for i,line in enumerate(VO[slug]):
        a, sr = k.create(line, voice=VOICE, speed=1.05, lang="en-us" if VOICE[0]=="a" else "en-gb")
        f = tmp/f"vo_{i}.wav"; sf.write(str(f), a, sr); out.append((f, len(a)/sr))
    return out

STAGE = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0E1A26;--sheet:#132233;--ink:#E4ECF2;--ink2:#9DB0C0;--rule:#2A3D52;--grid:#1B2D40;--red:#FF7A5C}
html,body{width:1080px;height:1920px;overflow:hidden;background:var(--bg);color:var(--ink);font-family:'IBM Plex Sans',sans-serif;
 background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px);background-size:40px 40px}
.top{position:absolute;left:40px;right:40px;top:60px;display:flex;justify-content:space-between;align-items:center;border:3px solid var(--ink);background:var(--sheet);font:500 26px/1 'IBM Plex Mono',monospace;color:var(--ink2)}
.top div{padding:20px 26px} .top b{color:var(--red);font-weight:500}
.cap{position:absolute;left:40px;right:40px;top:170px;min-height:250px;display:flex;align-items:center}
.cap h1{font:700 92px/0.98 'Barlow Condensed',sans-serif;text-transform:uppercase;letter-spacing:.005em;transition:opacity .35s,transform .35s}
.cap h1.out{opacity:0;transform:translateY(16px)}
.cap h1 em{font-style:normal;color:var(--red)}
.frame{position:absolute;left:40px;right:40px;top:450px;height:1260px;border:3px solid var(--ink);background:var(--sheet);overflow:hidden;transition:opacity .5s,transform .5s}
.frame.hide{opacity:0;transform:translateY(60px)}
iframe{border:0;width:600px;height:752px;display:block;transform:scale(1.6667);transform-origin:0 0}
.bot{position:absolute;left:40px;right:40px;bottom:60px;display:flex;justify-content:space-between;align-items:center}
.bot .bio{border:3px solid var(--red);color:var(--red);font:600 40px/1 'IBM Plex Mono',monospace;padding:22px 26px}
.bot .h{font:700 46px/1 'Barlow Condensed',sans-serif}
.end{position:absolute;inset:0;background:var(--bg);display:flex;flex-direction:column;justify-content:center;padding:0 80px;opacity:0;transition:opacity .5s;
 background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px);background-size:40px 40px}
.end.on{opacity:1}
.end .k{font:600 34px/1 'IBM Plex Sans',sans-serif;letter-spacing:.16em;text-transform:uppercase;color:var(--red)}
.end h2{font:700 150px/0.95 'Barlow Condensed',sans-serif;text-transform:uppercase;margin-top:30px}
.end h2 em{font-style:normal;color:var(--red)}
.end p{font:500 46px/1.35 'IBM Plex Sans',sans-serif;color:var(--ink2);margin-top:40px}
.end .bio{margin-top:70px;align-self:flex-start;border:4px solid var(--red);color:var(--red);font:600 54px/1 'IBM Plex Mono',monospace;padding:30px 34px}
.end .h{margin-top:30px;font:700 64px/1 'Barlow Condensed',sans-serif}
</style></head><body>
<div class="top"><div><b>__NO__</b></div><div>FREE TOOL · __NAME__</div><div>@smart_tools_every_week</div></div>
<div class="cap"><h1 id="cap">__HOOK__</h1></div>
<div class="frame hide" id="fr"><iframe id="app" src="/__SLUG__/index.html"></iframe></div>
<div class="bot"><div class="h">Free · works offline</div><div class="bio">Link in bio → __NO__</div></div>
<div class="end" id="end"><div class="k">New free tool</div><h2>__NAME_UP__<br><em>is free.</em></h2>
<p>Use it online or download one HTML file that works offline. No sign-up.</p><div class="bio">Link in bio → __NO__</div><div class="h">@smart_tools_every_week</div></div>
</body></html>"""

HELPERS = r"""
window.__h = (function(){
 const d=document; const fire=(e)=>{e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}))};
 const sleep=ms=>new Promise(r=>setTimeout(r,ms));
 return {
  set(id,v){const e=d.getElementById(id);e.value=v;fire(e)},
  async slide(id,a,b,ms){const e=d.getElementById(id);const n=Math.max(2,Math.round(ms/40));for(let i=0;i<=n;i++){e.value=a+(b-a)*i/n;fire(e);await sleep(ms/n)}},
  async type(id,txt){const e=d.getElementById(id);e.focus({preventScroll:true});e.value='';fire(e);for(const ch of txt){e.value+=ch;fire(e);await sleep(140)}e.blur()},
  click(sel){d.querySelector(sel).click()},
  scrollTo(sel){const t=d.querySelector(sel);window.scrollTo({top:t.getBoundingClientRect().top+window.scrollY-20,behavior:'smooth'})},
  async dragPt(i,dx,dy,ms){const sv=d.getElementById('plan');const g=sv.querySelectorAll('.pt')[i];const c=g.querySelector('circle');
    const r=sv.getBoundingClientRect();const k=r.width/640;const x0=r.left+(+c.getAttribute('cx'))*k,y0=r.top+(+c.getAttribute('cy'))*k;
    const n=Math.round(ms/40); const px=dx*k,py=dy*k;
    c.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,clientX:x0,clientY:y0,pointerId:1}));
    for(let s=1;s<=n;s++){sv.dispatchEvent(new PointerEvent('pointermove',{bubbles:true,clientX:x0+px*s/n,clientY:y0+py*s/n,pointerId:1}));await sleep(ms/n)}
    sv.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,pointerId:1}))}
 }})();
"""

def main(slug, out):
    cfg = REELS[slug]
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        vo = make_vo(slug, tmp)
        starts = []
        stage = (STAGE.replace("__NO__", cfg["no"]).replace("__NAME_UP__", cfg["name"].upper().replace("&","&amp;"))
                 .replace("__NAME__", cfg["name"].upper().replace("&","&amp;")).replace("__HOOK__", cfg["hook"]).replace("__SLUG__", slug))
        (ROOT/"_reel_stage.html").write_text(stage)
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
        class Q(http.server.SimpleHTTPRequestHandler):
            def log_message(self,*a): pass
        srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(ROOT)))
        port = srv.server_address[1]; threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as p:
                b = p.chromium.launch()
                ctx = b.new_context(viewport={"width":1080,"height":1920}, color_scheme="dark",
                                    record_video_dir=str(tmp), record_video_size={"width":1080,"height":1920})
                ctx.route("https://fonts.googleapis.com/**", lambda r: r.fulfill(status=200, content_type="text/css", body=CSS))
                pg = ctx.new_page(); t0 = time.time()
                mark = lambda: starts.append(time.time()-t0)
                pg.goto(f"http://127.0.0.1:{port}/_reel_stage.html"); pg.wait_for_timeout(600)
                fr = pg.frame_locator("#app"); frame = [f for f in pg.frames if f.url.endswith(f"/{slug}/index.html")][0]
                frame.evaluate(HELPERS)
                frame.evaluate("(()=>{const b=document.getElementById('dlbar');if(b)b.style.display='none';const st=document.createElement('style');st.textContent='html::-webkit-scrollbar{display:none}html{scrollbar-width:none}';document.head.appendChild(st)})()")
                mark(); pg.wait_for_timeout(int(max(2.3, vo[0][1]+0.5)*1000))   # hook
                pg.evaluate("document.getElementById('fr').classList.remove('hide')"); pg.wait_for_timeout(900)
                for si,(cap, secs, js) in enumerate(cfg["steps"]):
                    mark()
                    pg.evaluate("c=>{const h=document.getElementById('cap');h.classList.add('out');setTimeout(()=>{h.textContent=c;h.classList.remove('out')},300)}", cap)
                    pg.wait_for_timeout(450)
                    if js:
                        code = "(()=>{(async()=>{const {set,slide,type,click,scrollTo,dragPt}=window.__h;" + js + "})();return 1})()"
                        frame.evaluate(code)
                    pg.wait_for_timeout(int(max(secs, vo[si+1][1]+0.35)*1000))
                pg.evaluate("document.getElementById('end').classList.add('on')"); mark(); pg.wait_for_timeout(int(max(3.2, vo[-1][1]+0.9)*1000))
                vid = pg.video.path(); ctx.close(); b.close()
        finally:
            srv.shutdown(); (ROOT/"_reel_stage.html").unlink(missing_ok=True)
        # trim the first 0.5 s, then lay each voice line at its scene start
        TRIM = 0.5
        ins = ["-ss", str(TRIM), "-i", vid]
        filt = []
        for i,(f,dur) in enumerate(vo):
            ins += ["-i", str(f)]
            delay = max(0, int((starts[i] - TRIM + (0.55 if i>0 else 0.2))*1000))
            filt.append(f"[{i+1}:a]adelay={delay}|{delay},apad[a{i}]")
        mix = "".join(f"[a{i}]" for i in range(len(vo))) + f"amix=inputs={len(vo)}:normalize=0,volume=1.6[aout]"
        subprocess.run(["ffmpeg","-y","-loglevel","error",*ins,"-filter_complex",";".join(filt)+";"+mix,
                        "-map","0:v","-map","[aout]","-shortest","-vf","fps=30,format=yuv420p","-c:v","libx264","-preset","medium","-crf","20",
                        "-profile:v","high","-c:a","aac","-b:a","160k","-ar","44100","-movflags","+faststart",str(out)], check=True)
    print("reel", slug, out)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
