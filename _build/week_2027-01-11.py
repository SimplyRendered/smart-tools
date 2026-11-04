"""Writes _build/posts-2027-01-11.json and posts/<date>_<slug>_caption.md for T-55..T-57; asserts every caption <= 480 chars."""
import json, pathlib
ROOT = pathlib.Path(__file__).parent.parent
CTA = "⬇️ Free download / use online:\nsimplyrendered.github.io/smart-tools/{slug}\n(tap the link in our bio → {no})"
RCTA = "⬇️ simplyrendered.github.io/smart-tools/{slug}\n(link in bio → {no})\nFollow for a new free architecture tool every Mon, Wed & Fri."
P = [
 dict(date="2027-01-11", slug="hip-roof", no="T-55", name="Hip Roof Geometry",
  hook="Is the hip rafter really common × 1.414?", emoji="🏠",
  sub="Free Hip Roof Geometry tool. True hip length, backing angle and every jack rafter.",
  what="Enter the wall plate, pitch and overhang. It gives the true hip, backing angle, jack rafters and roof area on a live plan.",
  ticks=["True hip from √(2R² + rise²)","Jack rafter cut list","Hip backing angle"],
  q="Hip or gable on your next house? 👇", save="Save this for your next roof plan.",
  list=["True hip and common rafter","Backing angle for the hip","Jack rafters with cut lengths","Roof area and cutting summary"],
  steps=["Enter the wall plate size","Set pitch and overhang","Set rafter spacing","Read hips and jacks"],
  shot2=("Cut list","Every jack rafter, ready to cut","hip-roof_data.png"),
  tags="#hiproof #roofdesign #roofframing #rafter #hiprafter #jackrafter #carpentry #timberframe #roofpitch #architecture #architect #architecturestudent #architecturetools #freetools #smarttoolseveryweek",
  alt=["Hip roof plan with hips, ridge, common and jack rafters","Full screenshot of the Hip Roof Geometry tool","Feature list","Table of jack rafter lengths and cut lengths","Four steps to use the tool","Tool running on a phone","Follow @smart_tools_every_week, link in bio"],
  reel="Hip = common rafter × 1.414? ❌\nOn a 12 × 8 m roof at 30° that says 7.51 m. The true hip is 7.03 m ✅\nHip Roof Geometry gives hips, backing angle and every jack rafter. Free, no sign-up, works offline."),
 dict(date="2027-01-13", slug="bifold-door", no="T-56", name="Bi-fold Door Planner",
  hook="Does a 3 m bi-fold really open 3 m?", emoji="🚪",
  sub="Free Bi-fold Door Planner. Panel width, folded stack and the real clear opening.",
  what="Enter the opening, frame and panels. It gives each panel width, the stack, the real clear opening and where a lead door works.",
  ticks=["Fold it open on a live plan","2 to 8 panels compared","Lead door: odd count per side"],
  q="How many panels would you use? 👇", save="Save this for your next door schedule.",
  list=["Panel width from the opening","Folded stack and projection","Real clear opening","Lead (traffic) door check"],
  steps=["Enter the opening","Set panels and fold side","Check frame and thickness","Fold it open"],
  shot2=("Compare","Every panel count for this opening","bifold-door_data.png"),
  tags="#bifolddoors #bifold #foldingdoors #doordesign #glassdoors #aluminiumdoors #patiodoors #doorschedule #interiordesign #architecture #architect #architecturestudent #architecturetools #freetools #smarttoolseveryweek",
  alt=["Plan of bi-fold panels folded open with the clear opening, and elevation with the lead door","Full screenshot of the Bi-fold Door Planner","Feature list","Table comparing 2 to 8 panels for the opening","Four steps to use the tool","Tool running on a phone","Follow @smart_tools_every_week, link in bio"],
  reel="3 m bi-fold = 3 m clear? ❌\nThe frame and the folded stack take space: a 3-panel door in a 3000 mm opening clears 2664 mm ✅\nBi-fold Door Planner gives panel width, stack and lead door. Free, no sign-up, works offline."),
 dict(date="2027-01-15", slug="brick-bond", no="T-57", name="Brick Bond Planner",
  hook="Does every course start with a full brick?", emoji="🧱",
  sub="Free Brick Bond Planner. English, Flemish, stretcher and header bond, course by course.",
  what="Pick the brick, bond and wall size. It sets out every course with queen closers and bats and finds straight joints.",
  ticks=["Live elevation and plan","Straight joints flagged in red","Bricks counted with wastage"],
  q="English or Flemish on your drawings? 👇", save="Save this for your next brickwork sheet.",
  list=["Every course set out","Queen closers and bats placed","Straight joints flagged","Bricks per m² and total"],
  steps=["Pick the brick size","Choose the bond","Enter wall length and height","Read joints and bricks"],
  shot2=("Spot the mistake","No queen closer: straight joints in red","brick-bond_bad.png"),
  tags="#brickbond #englishbond #flemishbond #brickwork #masonry #brickwall #buildingconstruction #constructiondetails #bricklaying #architecturestudent #architecture #architect #architecturetools #freetools #smarttoolseveryweek",
  alt=["Brick wall elevation in English bond with queen closers, and a plan of two courses","Full screenshot of the Brick Bond Planner","Feature list","English bond elevation without queen closers, straight joints marked in red","Four steps to use the tool","Tool running on a phone","Follow @smart_tools_every_week, link in bio"],
  reel="Full brick at both ends of every course? ❌\nIn English bond this 2.4 m wall gets 108 straight joints. A queen closer after the corner header: 0 ✅\nBrick Bond Planner sets out every course and counts the bricks. Free, no sign-up, works offline."),
]
posts = []
for p in P:
    cap = f"{p['hook']} {p['emoji']}\nNew free tool: {p['name']}.\n{p['what']}\n" + "\n".join("✅ "+t for t in p['ticks']) + "\n" + CTA.format(**p) + f"\n{p['q']}\n{p['save']}"
    rcap = p['reel'] + "\n" + RCTA.format(**p)
    assert len(cap) <= 480, (p['slug'], len(cap)); assert len(rcap) <= 480, (p['slug'], 'reel', len(rcap))
    k, t, img = p['shot2']
    posts.append(dict(date=p['date'], slug=p['slug'], no=p['no'], name=p['name'], slides=[
        dict(t="hook", title=p['hook'], sub=p['sub'], img=f"{p['slug']}_views.png"),
        dict(t="shot", kicker="The tool", title=f"{p['name']}, live", img=f"{p['slug']}_top.png"),
        dict(t="list", kicker="What it does", title="What you get", items=p['list']),
        dict(t="shot", kicker=k, title=t, img=img),
        dict(t="steps", kicker="How to use", title="Four steps", items=p['steps']),
        dict(t="phone", kicker="On site", title="Works on your phone and offline.", img=f"{p['slug']}_phone.png"),
        dict(t="cta")], caption=cap, hashtags=p['tags'], alt=p['alt']))
    md = (f"# {p['no']} {p['name']} — post {p['date']} (carousel), reel the next day\n\n## Carousel caption ({len(cap)} characters)\n\n```\n{cap}\n```\n\n"
          f"## First comment (hashtags)\n\n```\n{p['tags']}\n```\n\n## Reel caption ({len(rcap)} characters)\n\n```\n{rcap}\n```\n\n"
          f"## Reel first comment (hashtags)\n\n```\n{p['tags'].replace('#architecturestudent','#architecturereels')}\n```\n\n## Alt text per slide\n\n" + "\n".join(f"{i+1:02d}. {a}" for i, a in enumerate(p['alt'])) + "\n")
    (ROOT/'posts'/f"{p['date']}_{p['slug']}_caption.md").write_text(md)
    print(p['slug'], len(cap), len(rcap))
(ROOT/'_build'/'posts-2027-01-11.json').write_text(json.dumps(posts, ensure_ascii=False, indent=1))
