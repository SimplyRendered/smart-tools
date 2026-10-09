"""Smooth 'usual guess vs the right way' Instagram reel (1080x1920, 30 fps) with a natural Kokoro voiceover and the channel outro.

Scripts: _build/reels2.json  {slug: {...}}  (see sun-shadow there for the full shape)
  no, name                      sheet number and app name
  vo     [s0, s1, ..., sN]       conversational sentences. s0 = the usual (wrong) way, s1..sN-1 = the right way in the app, sN = sign-off
  wrong  {label, cap, html}      scene for s0: pill label, headline, panel HTML (an SVG or big text). A red WRONG stamp lands near the end.
  right  [{cap, actions}]        one per s1..sN-1, actions run inside the app, times in seconds from that sentence's start:
           {"at":0,"dur":0.7,"scroll":610 | "#sel", "offset":-20}
           {"at":0.2,"dur":2.4,"slide":"inputId","from":720,"to":960,"round":1}
           {"at":0,"set":"inputId","value":"1"}
           {"at":0,"dur":1.8,"drag":[pointIndex,dx,dy],"svg":"plan"}
  cmp    {guess, real}           comparison chips under the app: the usual answer (struck out) vs the live value read from selector `real`
  end    {cap}                   sign-off headline (the end card also shows "Link in bio → T-NN")
Every frame is set explicitly and screenshotted, so motion is perfectly smooth (no screen-recording judder).
Env: FONTS_DIR, TTS_DIR (kokoro-v1.0.onnx or kokoro-v1.0.int8.onnx + voices-v1.0.bin), VOICE (af_heart), SPEED (1.05)
usage: python _build/reel2.py <slug> <out.mp4>"""
import sys, os, pathlib, json, subprocess, threading, http.server, socketserver, functools, tempfile, math
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from shoot import CSS
from playwright.sync_api import sync_playwright
import numpy as np

HERE = pathlib.Path(__file__).parent; ROOT = HERE.parent
OUTRO = HERE / "outro.mp4"
FPS = 30; MAX_TOTAL = 19.6
TTS_DIR = pathlib.Path(os.environ.get("TTS_DIR", "tts")); VOICE = os.environ.get("VOICE", "af_heart")

def ease(x):
    x = min(1.0, max(0.0, x)); return 4*x*x*x if x < .5 else 1 - (-2*x + 2)**3/2
def back(x):
    x = min(1.0, max(0.0, x)); c1 = 1.7; c3 = c1 + 1; return 1 + c3*(x-1)**3 + c1*(x-1)**2

def make_vo(lines, speed):
    from kokoro_onnx import Kokoro
    model = TTS_DIR/"kokoro-v1.0.onnx"
    if not model.exists(): model = TTS_DIR/"kokoro-v1.0.int8.onnx"
    k = Kokoro(str(model), str(TTS_DIR/"voices-v1.0.bin"))
    out = []
    for line in lines:
        a, sr = k.create(line, voice=VOICE, speed=speed, lang="en-us" if VOICE[0] == "a" else "en-gb")
        nz = np.where(np.abs(a) > 0.01)[0]                      # trim silence the model adds
        a = a[max(0, nz[0]-int(.03*sr)): nz[-1]+int(.08*sr)] if len(nz) else a
        out.append((a.astype(np.float32), sr))
    return out

STAGE = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0E1A26;--sheet:#132233;--ink:#E4ECF2;--ink2:#9DB0C0;--rule:#2A3D52;--grid:#1B2D40;--red:#FF6B5C;--ok:#3FD08F;--sun:#F2A93B}
html,body{width:1080px;height:1920px;overflow:hidden;background:var(--bg);color:var(--ink);font-family:'IBM Plex Sans',sans-serif}
#bg{position:absolute;inset:-80px;background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px);background-size:40px 40px}
.top{position:absolute;left:40px;right:40px;top:60px;display:flex;justify-content:space-between;align-items:center;border:3px solid var(--ink);background:var(--sheet);font:500 26px/1 'IBM Plex Mono',monospace;color:var(--ink2)}
.top div{padding:20px 26px} .top b{color:var(--red);font-weight:500}
#pill{position:absolute;left:40px;top:190px;font:700 38px/1 'Barlow Condensed',sans-serif;letter-spacing:.08em;text-transform:uppercase;padding:14px 22px;border:3px solid}
#pill.bad{color:var(--red);border-color:var(--red)} #pill.good{color:var(--ok);border-color:var(--ok)}
#cap{position:absolute;left:40px;right:40px;top:262px;height:190px;display:flex;align-items:center}
#cap h1{font:700 84px/0.98 'Barlow Condensed',sans-serif;text-transform:uppercase}
#cap h1 em{font-style:normal;color:var(--red)} #cap h1 i{font-style:normal;color:var(--ok)}
.panel{position:absolute;left:40px;right:40px;top:480px;height:1120px;border:3px solid var(--ink);background:var(--sheet);overflow:hidden}
#wrong{display:flex;flex-direction:column;justify-content:center;align-items:center}
#wrong svg{width:920px;height:auto}
#stamp{position:absolute;right:60px;top:70px;font:700 120px/1 'Barlow Condensed',sans-serif;color:var(--red);border:10px solid var(--red);padding:6px 30px 0;transform-origin:center;letter-spacing:.04em}
iframe{border:0;width:600px;height:672px;display:block;transform:scale(1.6667);transform-origin:0 0}
#cmp{position:absolute;left:40px;right:40px;top:1630px;height:180px;display:grid;grid-template-columns:1fr 1fr;gap:24px}
#cmp div{border:3px solid;display:flex;flex-direction:column;justify-content:center;padding:0 28px;background:var(--sheet)}
#cmp b{font:600 28px/1 'IBM Plex Sans',sans-serif;letter-spacing:.14em;text-transform:uppercase}
#cmp span{font:700 86px/1 'Barlow Condensed',sans-serif;margin-top:12px;white-space:nowrap}
#g{border-color:var(--red)!important;color:var(--red)} #g span{text-decoration:line-through;text-decoration-thickness:6px}
#r{border-color:var(--ok)!important;color:var(--ok)}
#end{position:absolute;inset:0;background:var(--bg);display:flex;flex-direction:column;justify-content:center;padding:0 80px}
#end .k{font:600 34px/1 'IBM Plex Sans',sans-serif;letter-spacing:.16em;text-transform:uppercase;color:var(--ok)}
#end h2{font:700 140px/0.95 'Barlow Condensed',sans-serif;text-transform:uppercase;margin-top:30px}
#end h2 em{font-style:normal;color:var(--ok)}
#end p{font:500 44px/1.35 'IBM Plex Sans',sans-serif;color:var(--ink2);margin-top:40px}
#end .bio{margin-top:60px;align-self:flex-start;border:4px solid var(--red);color:var(--red);font:600 54px/1 'IBM Plex Mono',monospace;padding:30px 34px}
#end .h{margin-top:30px;font:700 60px/1 'Barlow Condensed',sans-serif}
</style></head><body>
<div id="bg"></div>
<div class="top"><div><b>__NO__</b></div><div>FREE TOOL · __NAME__</div><div>@smart_tools_every_week</div></div>
<div id="pill" class="bad"></div>
<div id="cap"><h1 id="h"></h1></div>
<div class="panel" id="wrong">__WRONG__<div id="stamp">✕ WRONG</div></div>
<div class="panel" id="fr"><iframe id="app" src="/__SLUG__/index.html"></iframe></div>
<div id="cmp"><div id="g"><b>✕ Usual guess</b><span>__GUESS__</span></div><div id="r"><b>✓ Real answer</b><span id="rv">?</span></div></div>
<div id="end"><div class="k">✓ The right way · free</div><h2>__ENDCAP__</h2>
<p>Use it online or download one HTML file that works offline. No sign-up.</p><div class="bio">Link in bio → __NO__</div><div class="h">@smart_tools_every_week</div></div>
<script>
const $=id=>document.getElementById(id);
window.apply=s=>{
 $('bg').style.transform=`translate(${s.bgx}px,${s.bgy}px)`;
 const p=$('pill'); if(p.textContent!==s.pill){p.textContent=s.pill} p.className=s.pillc; p.style.opacity=s.pillo; p.style.transform=`translateY(${s.pilly}px)`;
 const h=$('h'); if(h.innerHTML!==s.cap)h.innerHTML=s.cap; h.style.opacity=s.capo; h.style.transform=`translateY(${s.capy}px)`;
 $('wrong').style.opacity=s.wo; $('wrong').style.transform=`translateX(${s.wx}px) scale(${s.wz})`;
 $('stamp').style.opacity=s.so; $('stamp').style.transform=`rotate(-8deg) scale(${s.ss})`;
 $('fr').style.opacity=s.fo; $('fr').style.transform=`translateX(${s.fx}px)`;
 $('cmp').style.opacity=s.co; $('cmp').style.transform=`translateY(${s.cy}px)`; if(s.rv!==null)$('rv').textContent=s.rv;
 $('r').style.opacity=s.ro; $('r').style.boxShadow=`0 0 ${s.glow}px rgba(63,208,143,.55)`;
 $('end').style.opacity=s.eo; $('end').style.transform=`translateY(${s.ey}px)`; $('end').style.visibility=s.eo>0?'visible':'hidden';
};
</script></body></html>"""

APP_JS = r"""
window.__R=(function(){const d=document,st={};
 const fire=e=>{e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}))};
 const dlb=d.getElementById('dlbar');if(dlb)dlb.style.display='none';
 const css=d.createElement('style');css.textContent='html::-webkit-scrollbar{display:none}html{scrollbar-width:none;scroll-behavior:auto!important}*{transition:none!important;animation:none!important}';d.head.appendChild(css);
 return {
  run(ops,realSel){for(const o of ops){
    if(o[0]==='setv'){const e=d.getElementById(o[1]);if(e.type==='range')e.step='any';if(String(e.value)!==String(o[2])){e.value=o[2];fire(e)}}
    else if(o[0]==='scr'){window.scrollTo(0,o[1])}
    else if(o[0]==='drag'){const [_,key,svgId,i,dx,dy,f]=o;const sv=d.getElementById(svgId);
      if(!st[key]){const c=sv.querySelectorAll('.pt')[i].querySelector('circle');const r=sv.getBoundingClientRect();const vb=sv.viewBox.baseVal;const k=r.width/vb.width;
        st[key]={x0:r.left+(+c.getAttribute('cx')-vb.x)*k,y0:r.top+(+c.getAttribute('cy')-vb.y)*k,k,up:false};
        c.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,clientX:st[key].x0,clientY:st[key].y0,pointerId:1}))}
      const s=st[key];if(s.up)continue;sv.dispatchEvent(new PointerEvent('pointermove',{bubbles:true,clientX:s.x0+dx*s.k*f,clientY:s.y0+dy*s.k*f,pointerId:1}));
      if(f>=1){sv.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,pointerId:1}));s.up=true}}}
   const r=realSel?d.querySelector(realSel):null;return {rv:r?r.textContent.trim():null,sy:scrollY}},
  top(sel,off){const t=d.querySelector(sel);return t.getBoundingClientRect().top+scrollY+(off||0)},
  val(id){return parseFloat(d.getElementById(id).value)}
 }})();
"""

def plan_times(vo, gap=0.28, lead=0.2):
    starts, ends, t = [], [], lead
    for a, sr in vo:
        starts.append(t); t += len(a)/sr; ends.append(t); t += gap
    return starts, ends

def main(slug, out):
    cfg = json.loads((HERE/"reels2.json").read_text())[slug]
    speed = float(os.environ.get("SPEED", 1.05))
    while True:
        vo = make_vo(cfg["vo"], speed)
        starts, ends = plan_times(vo)
        T = ends[-1] + 0.9
        outro_d = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(OUTRO)]).decode()) if OUTRO.exists() else 0
        if T + outro_d <= MAX_TOTAL or speed >= 1.25: break
        speed = round(speed + 0.04, 2); print("too long", round(T+outro_d,2), "-> speed", speed)
    print(f"content {T:.2f}s + outro {outro_d:.2f}s = {T+outro_d:.2f}s at speed {speed}")
    nR = len(cfg["right"]); assert nR == len(vo) - 2, "right[] must have one entry per middle vo line"
    tR, tE = starts[1] - 0.15, starts[-1] - 0.1          # right-way scene start, end card start
    stamp_t = starts[0] + (ends[0]-starts[0])*0.72

    sr = vo[0][1]; track = np.zeros(int((T+0.2)*sr), np.float32)
    for (a, _), s in zip(vo, starts): i = int(s*sr); track[i:i+len(a)] += a

    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        import soundfile as sf; sf.write(str(tmp/"vo.wav"), track, sr)
        name = cfg["name"].upper().replace("&", "&amp;")
        stage = (STAGE.replace("__NO__", cfg["no"]).replace("__NAME__", name).replace("__SLUG__", slug)
                 .replace("__WRONG__", cfg["wrong"]["html"]).replace("__GUESS__", cfg["cmp"]["guess"]).replace("__ENDCAP__", cfg["end"]["cap"]))
        (ROOT/"_reel_stage.html").write_text(stage)
        class Q(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *a): pass
        srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(ROOT)))
        port = srv.server_address[1]; threading.Thread(target=srv.serve_forever, daemon=True).start()
        ff = subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","image2pipe","-framerate",str(FPS),"-c:v","mjpeg","-i","-",
                               "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p",str(tmp/"v.mp4")], stdin=subprocess.PIPE)
        try:
            with sync_playwright() as p:
                b = p.chromium.launch()
                ctx = b.new_context(viewport={"width":1080,"height":1920}, color_scheme="dark")
                ctx.route("https://fonts.googleapis.com/**", lambda r: r.fulfill(status=200, content_type="text/css", body=CSS))
                pg = ctx.new_page(); pg.goto(f"http://127.0.0.1:{port}/_reel_stage.html"); pg.wait_for_timeout(800)
                app = [f for f in pg.frames if f.url.endswith(f"/{slug}/index.html")][0]
                app.evaluate(APP_JS); pg.wait_for_timeout(200)
                cache = {}   # per-action start values
                caps = [(0, cfg["wrong"]["cap"], "bad", cfg["wrong"]["label"])] + \
                       [(starts[i+1]-0.15, r["cap"], "good", "✓ The right way") for i, r in enumerate(cfg["right"])]
                n = int(round(T*FPS))
                for fi in range(n):
                    t = fi/FPS
                    # caption: crossfade on change
                    ci = max(i for i, c in enumerate(caps) if c[0] <= t); c0 = caps[ci][0]
                    nxt = caps[ci+1][0] if ci+1 < len(caps) else 1e9
                    fin = ease((t-c0)/0.35) if ci > 0 or True else 1; fout = 1 - ease((t-(nxt-0.18))/0.18) if t > nxt-0.18 else 1
                    capo = min(fin, fout); capy = (1-fin)*24
                    pill_in = ease(t/0.35) if ci == 0 else 1
                    pillo = pill_in if ci == 0 else (ease((t-tR)/0.35) if t < tR+0.35 else 1)
                    if t >= tR and t < tR+0.18: pillo = 0
                    # wrong panel -> app frame
                    k = ease((t-tR)/0.55)
                    s = dict(bgx=-30*t/T, bgy=-50*t/T, pill=caps[ci][3], pillc=caps[ci][2], pillo=pillo, pilly=(1-pillo)*10,
                             cap=caps[ci][1], capo=capo, capy=capy,
                             wo=(1-k)*ease(t/0.3), wx=-140*k, wz=1+0.03*min(1, t/max(tR, .1)),
                             so=ease((t-stamp_t)/0.12), ss=1.6-0.6*back((t-stamp_t)/0.35) if t >= stamp_t else 1.6,
                             fo=k, fx=140*(1-k), co=ease((t-0.3)/0.4), cy=30*(1-ease((t-0.3)/0.4)), rv=None, glow=0, ro=0.4+0.6*ease((t-tR)/0.4),
                             eo=ease((t-tE)/0.45), ey=40*(1-ease((t-tE)/0.45)))
                    # app actions
                    ops = []
                    if tR - 0.2 <= t < tE + 0.5:
                        for si, seg in enumerate(cfg["right"]):
                            s0 = starts[si+1]
                            for ai, a in enumerate(seg.get("actions", [])):
                                key = f"{si}.{ai}"; at = s0 + a.get("at", 0); dur = a.get("dur", 0.001)
                                if t < at: continue
                                f = ease((t-at)/dur) if dur > 0.01 else 1.0
                                if "set" in a:
                                    if key not in cache: cache[key] = 1; ops.append(["setv", a["set"], a["value"]])
                                elif "slide" in a:
                                    if f >= 1 and cache.get(key) == "done": continue
                                    v = a["from"] + (a["to"]-a["from"])*f
                                    if "round" in a: v = round(v/a["round"])*a["round"]
                                    ops.append(["setv", a["slide"], v]); cache[key] = "done" if f >= 1 else 1
                                elif "scroll" in a:
                                    if cache.get(key) == "done": continue
                                    if key not in cache:
                                        y0 = app.evaluate("()=>scrollY"); tg = a["scroll"]
                                        y1 = tg if isinstance(tg, (int, float)) else app.evaluate("([s,o])=>__R.top(s,o)", [tg, a.get("offset", -20)])
                                        cache[key] = (y0, y1)
                                    y0, y1 = cache[key]; ops.append(["scr", y0+(y1-y0)*f])
                                    if f >= 1: cache[key] = "done"
                                elif "drag" in a:
                                    if cache.get(key) == "done": continue
                                    i, dx, dy = a["drag"]; ops.append(["drag", key, a.get("svg", "plan"), i, dx, dy, f])
                                    if f >= 1: cache[key] = "done"
                    res = app.evaluate("([o,r])=>__R.run(o,r)", [ops, cfg["cmp"]["real"]])
                    s["rv"] = res["rv"] if t >= tR else "?"; s["glow"] = 30*max(0, 1-abs(t-(starts[1]+(ends[1]-starts[1])*0.8))/0.6)
                    pg.evaluate("s=>apply(s)", s)
                    ff.stdin.write(pg.screenshot(type="jpeg", quality=93))
                    if fi % 60 == 0: print(f"frame {fi}/{n}", flush=True)
                b.close()
        finally:
            ff.stdin.close(); ff.wait(); srv.shutdown(); (ROOT/"_reel_stage.html").unlink(missing_ok=True)
        V = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p,setsar=1"
        A = "aresample=48000,aformat=channel_layouts=stereo"
        VOF = f"{A},highpass=f=80,acompressor=threshold=-20dB:ratio=2.5:attack=5:release=120:makeup=1.5,loudnorm=I=-14:TP=-1.5:LRA=6,{A},apad,atrim=0:{T:.3f}"
        if OUTRO.exists():
            M = f"{A},acompressor=threshold=-24dB:ratio=3:attack=10:release=200:makeup=2,equalizer=f=2500:t=q:w=1.2:g=-3,loudnorm=I=-17:TP=-2:LRA=8,{A}"
            fc = (f"[0:v]{V}[v0];[1:a]{VOF}[a0];[2:v]{V}[v1];[2:a]{M},afade=t=in:d=0.3,afade=t=out:st={outro_d-0.6:.2f}:d=0.6[a1];"
                  "[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]")
            ins = ["-i", str(tmp/"v.mp4"), "-i", str(tmp/"vo.wav"), "-i", str(OUTRO)]
        else:
            fc = f"[0:v]{V}[v];[1:a]{VOF}[a]"; ins = ["-i", str(tmp/"v.mp4"), "-i", str(tmp/"vo.wav")]
        subprocess.run(["ffmpeg","-y","-loglevel","error",*ins,"-filter_complex",fc,"-map","[v]","-map","[a]",
                        "-c:v","libx264","-preset","medium","-crf","19","-profile:v","high","-c:a","aac","-b:a","192k",
                        "-movflags","+faststart",str(out)], check=True)
    print("reel", slug, out)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
