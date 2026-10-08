"""Screenshot local HTML with Google Fonts served from local @fontsource files.
usage: shoot.py <html> <out.png|jpg> <width> <height|full> [dark] [js-to-run]"""
import sys, pathlib, base64
from playwright.sync_api import sync_playwright
FD = pathlib.Path(__import__("os").environ.get("FONTS_DIR","fonts/node_modules/@fontsource"))
FACES = [("Barlow Condensed","barlow-condensed",[500,600,700]),("IBM Plex Mono","ibm-plex-mono",[400,500,600]),("IBM Plex Sans","ibm-plex-sans",[400,500,600,700])]
def font_css():
    out=[]
    for fam,pkg,ws in FACES:
        for w in ws:
            f=FD/pkg/"files"/f"{pkg}-latin-{w}-normal.woff2"
            if f.exists():
                out.append(f"@font-face{{font-family:'{fam}';font-weight:{w};font-style:normal;src:url(data:font/woff2;base64,{base64.b64encode(f.read_bytes()).decode()}) format('woff2')}}")
    return "\n".join(out)
CSS=font_css()
def shoot(html,out,w,h,dark=False,js=None,page=None):
    pass
if __name__=="__main__":
    html,out,w,h=sys.argv[1],sys.argv[2],int(sys.argv[3]),sys.argv[4]
    dark=len(sys.argv)>5 and sys.argv[5]=="dark"
    js=sys.argv[6] if len(sys.argv)>6 else None
    with sync_playwright() as p:
        b=p.chromium.launch()
        ctx=b.new_context(viewport={"width":w,"height":900 if h=="full" else int(h)},color_scheme="dark" if dark else "light",device_scale_factor=1)
        ctx.route("https://fonts.googleapis.com/**",lambda r:r.fulfill(status=200,content_type="text/css",body=CSS))
        ctx.route("https://fonts.gstatic.com/**",lambda r:r.abort())
        pg=ctx.new_page(); errs=[]
        pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m:m.type=="error" and errs.append(m.text))
        pg.goto(pathlib.Path(html).resolve().as_uri()); pg.wait_for_timeout(500)
        if js: pg.evaluate(js); pg.wait_for_timeout(300)
        ow=pg.evaluate("document.documentElement.scrollWidth")
        kw={"path":out,"full_page":h=="full"}
        if out.endswith(".jpg"): kw.update(type="jpeg",quality=92)
        pg.screenshot(**kw)
        print(out,"scrollWidth",ow,"errors",errs)
        b.close()
