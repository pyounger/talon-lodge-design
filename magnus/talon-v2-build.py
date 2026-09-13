import base64, os, io
SP = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(SP, 'talon', 'web'); ASSET = os.path.join(SP, 'talon', 'assets')
def uri(n, d=WEB):
    mt='image/png' if n.endswith('.png') else 'image/jpeg'
    with open(os.path.join(d,n),'rb') as f:
        return 'data:%s;base64,%s'%(mt, base64.b64encode(f.read()).decode())

# focal point per photograph, exactly as the control panel stores it (x%, y%)
FOCAL = {
  'float-plane-mountains.jpg': (52, 58),   # the plane and the shoreline
  'chefs-outdoor-kitchen.jpg': (46, 52),
  'angler-with-salmon.jpg':    (44, 40),   # the fish, not the sky
  'flyfishing-pool.jpg':       (50, 62),   # the water
  'deck-firepit-sunset.jpg':   (50, 44),
  'bald-eagle.jpg':            (40, 38),   # the bird, high and left of centre
}
def pos(img):
    x, y = FOCAL.get(img, (50, 50))
    return 'object-position:%d%% %d%%' % (x, y)

SCENES = [
 ("An island in the Inside Passage", "float-plane-mountains.jpg",
  "Talon sits off Baranof Island with the Tongass at its back and Mount Edgecumbe across the sound. The prime "
  "saltwater grounds are half an hour out; the freshwater is reached by float plane, ATV or boat. You are not "
  "commuting to the wilderness &mdash; you are staying in it.", "See the island"),
 ("Four chefs, twenty-four guests", "chefs-outdoor-kitchen.jpg",
  "The ratio is the point. Three culinary masters run the kitchen and a visiting chef series brings a fourth, "
  "cooking for a room of twenty-four. Wild berries from the property, an organic garden, and seafood landed "
  "the same day.", "Meet the team"),
 ("A day on the salt", "angler-with-salmon.jpg",
  "Kings, silvers and Pacific halibut, with every prime ground inside thirty minutes of the dock. Fish with "
  "veteran Alaskan captains, or take the wheel yourself. Whales, eagles and the occasional brown bear come "
  "free with the crossing.", "Plan a fishing day"),
 ("Freshwater in the Tongass", "flyfishing-pool.jpg",
  "Steelhead in spring, then sockeye, pink and silver as the season turns. Native rainbow and cutthroat "
  "throughout. Most of this water sees a handful of anglers a year.", "Plan a fly-out"),
 ("The wood-fired soaking tub", "deck-firepit-sunset.jpg",
  "Tucked at the Massage and Spa Pavilion, the wellness porch looks out on a stretch of coast with nothing "
  "built on it. The Japanese soaking tub is wood fired and positioned for the view rather than the plumbing.",
  "Visit the spa"),
 ("Wildlife, unavoidably", "bald-eagle.jpg",
  "Sitka blacktail deer, brown bears, bald eagles and river otters in the forest; whales, orcas, seals and "
  "puffins in the water. None of it is scheduled and all of it turns up.", "See the wildlife"),
]
scenes = ''.join(
  '''<section class="scene%s">
       <div class="shot"><img src="%s" alt="%s" style="%s" loading="lazy"></div>
       <div class="panel"><h2>%s</h2><hr><p>%s</p><a class="btn" href="#">%s</a></div>
     </section>''' % (' right' if i%2 else '', uri(img), t, pos(img), t, body, cta)
  for i,(t,img,body,cta) in enumerate(SCENES))

WALL = ['netting-salmon.jpg','plated-dessert.jpg','two-anglers.jpg','wine-pour.jpg','brown-bear-river.jpg',
        'couple-at-waterfall.jpg','float-plane-wading.jpg','deck-firepit.jpg','waterfront-pavilion.jpg',
        'spa-pavilion-interior.jpg']
wall = ''.join('<a class="tile" href="#"><img src="%s" alt="" loading="lazy"><span class="ig">&#9634;</span></a>'
               % uri(n) for n in WALL)

HOME='https://claude.ai/code/artifact/b7babd23-ad62-412c-9c20-b668a598cd00'
html = io.open(os.path.join(SP,'talon-v2-template.html'),encoding='utf-8').read()
for k,v in (('__GRIFFIN__',uri('magnus-griffin.png',ASSET)),('__CREST__',uri('talon-lodge-logo.png',ASSET)),
            ('__HERO__',uri('sitka-edgecumbe-sunset.jpg')),('__VID__',uri('waterfront-pavilion.jpg')),
            ('__T1__',uri('netting-salmon.jpg')),('__T2__',uri('plated-salmon.jpg')),
            ('__T3__',uri('spa-pavilion-interior.jpg')),('__SCENES__',scenes),('__WALL__',wall),
            ('__HOME__',HOME),('__TALON__','#')):
    html = html.replace(k,v)
io.open(os.path.join(SP,'magnus-talon-v2.html'),'w',encoding='utf-8').write(html)
print('built magnus-talon-v2.html  %.0f KB'%(len(html)/1024))
