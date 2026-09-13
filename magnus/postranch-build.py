import base64, os, io
SP = os.path.dirname(os.path.abspath(__file__))
ASSET = os.path.join(SP, 'talon', 'assets'); PR = os.path.join(SP, 'postranch')
def uri(n, d=ASSET):
    mt='image/png' if n.endswith('.png') else 'image/jpeg'
    with open(os.path.join(d,n),'rb') as f:
        return 'data:%s;base64,%s'%(mt, base64.b64encode(f.read()).decode())

# Rewritten from the live page. Facts are theirs; the sentences are not.
SCENES = [
 ("Built into the ridge, not on it",
  "Rooms are dug into the slope or lifted on legs so that nothing stands above the tree line. The tree "
  "houses are raised to spare the redwood roots. The ocean rooms carry sod roofs you could walk across "
  "without noticing them. The architecture&rsquo;s whole ambition is to not be the view.",
  "See the rooms"),
 ("Sierra Mar, on the edge",
  "Lunch on an open terrace, dinner behind floor-to-ceiling glass, both of them looking straight down the "
  "coast. The kitchen forages hyper-locally and grows the rest in the chef&rsquo;s garden, so the distance "
  "from ground to plate is measured in yards. Breakfast is included; lunch and dinner run three to six "
  "courses, with a list built around the region rather than around prestige.",
  "See the restaurant"),
 ("Water, and wood smoke",
  "Two infinity pools, one at the cliff edge, and hot tubs placed for the view rather than the plumbing. "
  "Every room has a wood-burning fireplace. The gardens are drought-tolerant natives instead of lawn, which "
  "is the correct answer to this coast and happens to look better.",
  "See the grounds"),
 ("What the place is actually for",
  "No televisions. An on-site mercantile covers what you forgot, and a gallery shows work by artists who "
  "live along this coast. But the reason to come is the two hours after dinner, when there is nothing to do "
  "and nowhere brighter to look than the water.",
  "Plan a stay"),
]
scenes = ''.join(
  '''<section class="scene%s">
       <div class="shot"><div class="sceneplate"><p class="nm">%s</p><hr>
         <p class="note">Photography to come</p></div></div>
       <div class="panel"><h2>%s</h2><hr><p>%s</p><a class="btn" href="#">%s</a></div>
     </section>''' % (' right' if i%2 else '', t, t, body, cta)
  for i,(t,body,cta) in enumerate(SCENES))

wall = ''.join('<a class="tile" href="#"><div class="sceneplate"><p class="note">#postranchinn</p></div></a>'
               for _ in range(10))

HOME='https://claude.ai/code/artifact/b7babd23-ad62-412c-9c20-b668a598cd00'
html = io.open(os.path.join(SP,'postranch-template.html'),encoding='utf-8').read()
for k,v in (('__GRIFFIN__',uri('magnus-griffin.png')),
            ('__HERO__',uri('hero-infinity-pool.jpg', PR)),('__SCENES__',scenes),
            ('__WALL__',wall),('__HOME__',HOME),('__TALON__','https://claude.ai/code/artifact/afd0fd6e-5e0f-4c9d-ae28-2a7a82953f5e')):
    html = html.replace(k,v)
io.open(os.path.join(SP,'magnus-resort-postranch.html'),'w',encoding='utf-8').write(html)
print('built magnus-resort-postranch.html  %.0f KB'%(len(html)/1024))
