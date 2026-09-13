import base64, os, io
SP = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(SP, 'talon', 'web')
ASSET = os.path.join(SP, 'talon', 'assets')

def uri(name, folder=None):
    d = folder or WEB
    mt = 'image/png' if name.endswith('.png') else 'image/jpeg'
    with open(os.path.join(d, name), 'rb') as f:
        return 'data:%s;base64,%s' % (mt, base64.b64encode(f.read()).decode())

# four cards, each with its own destination — replacing eight that all said "Explore Resort"
CARDS = [
 ("A day on the salt", "angler-with-salmon.jpg",
  "Kings, silvers and Pacific halibut, with every prime ground inside thirty minutes of the dock. Fish with "
  "veteran Alaskan captains who have run these waters for decades, or take the wheel yourself and tailor the "
  "day. Whale watching, eagles overhead and the occasional brown bear come free with the crossing.",
  "Plan a fishing day"),
 ("Freshwater in the Tongass", "flyfishing-pool.jpg",
  "Steelhead in spring, then sockeye, pink and silver as the season turns. Native rainbow and cutthroat run "
  "throughout the late-May to early-September season. The water is reached by float plane, ATV or boat, and "
  "most of it sees a handful of anglers a year.",
  "Plan a fly-out"),
 ("The massage pavilion", "spa-pavilion-interior.jpg",
  "Open-air, built out over the water. Aromatherapy, body wraps and hot stones, and a wood-fired Japanese "
  "soaking tub positioned for the view rather than the plumbing. The wellness porch looks out on a stretch "
  "of coast with nothing built on it.",
  "Visit the spa"),
 ("Wildlife, unavoidably", "bald-eagle.jpg",
  "Sitka blacktail deer, brown bears, bald eagles and river otters in the forest; whales, orcas, seals and "
  "puffins in the water. Bordering America's largest national forest, on an island nobody else lives on, "
  "none of it is scheduled and all of it turns up.",
  "See the island"),
]

cards = ''.join(
  '''<article class="feat">
       <div class="shot"><img src="%s" alt="%s" loading="lazy"></div>
       <div class="body"><h3>%s</h3><p>%s</p><a class="cta" href="#">%s</a></div>
     </article>''' % (uri(img), t, t, body, cta)
  for t, img, body, cta in CARDS)

# the curated wall — photographs not already used above, so the page does not repeat itself
WALL = [
 ('netting-salmon.jpg',      'A guide netting a salmon boatside'),
 ('plated-salmon.jpg',       'Alaska king salmon plated in the dining room'),
 ('deck-firepit-sunset.jpg', 'The fire-pit deck at sunset'),
 ('two-anglers.jpg',         'Two anglers with a bright fish in the river'),
 ('wine-pour.jpg',           'Pouring at a guest winemaker evening'),
 ('brown-bear-river.jpg',    'A brown bear fishing the river'),
 ('couple-at-waterfall.jpg', 'A couple with a fish below the waterfall'),
 ('plated-dessert.jpg',      'Dessert from the visiting chef series'),
 ('float-plane-wading.jpg',  'Anglers wading beside the float plane'),
 ('deck-firepit.jpg',        'The fire pit after dinner'),
]
wall = ''.join(
  '<a class="tile" href="#" aria-label="%s"><img src="%s" alt="%s" loading="lazy">'
  '<span class="ig">&#9634;</span></a>' % (alt, uri(img), alt)
  for img, alt in WALL)

HOME = 'https://claude.ai/code/artifact/b7babd23-ad62-412c-9c20-b668a598cd00'

html = io.open(os.path.join(SP, 'resort-template.html'), encoding='utf-8').read()
html = (html.replace('__HOME__', HOME)
            .replace('__GRIFFIN__', uri('magnus-griffin.png', ASSET))
            .replace('__TALONMARK__', uri('talon-lodge-logo.png', ASSET))
            .replace('__HERO__', uri('sitka-edgecumbe-sunset.jpg'))
            .replace('__ISLAND__', uri('float-plane-mountains.jpg'))
            .replace('__TABLE__', uri('chefs-outdoor-kitchen.jpg'))
            .replace('__VIDEOPOSTER__', uri('waterfront-pavilion.jpg'))
            .replace('__CARDS__', cards)
            .replace('__WALL__', wall))
io.open(os.path.join(SP, 'magnus-resort-talon.html'), 'w', encoding='utf-8').write(html)
print('built magnus-resort-talon.html  %.0f KB' % (len(html) / 1024))
