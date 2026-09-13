#!/usr/bin/env python3
"""Wrap the artifact pages as complete, deployable HTML documents.

The artifact host supplies a doctype, a charset and a viewport tag of its own,
so the published pages carry none.  A file served from Firebase gets none of
that: without a viewport tag a phone lays the page out at 980px and shrinks it.
This emits the same pages as real documents, head tags and all.
"""
import os, re, io

SP   = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(SP, 'dist')

PAGES = [
  dict(src='magnus-home.html', out='index.html',
       desc='Magnus Adventures curates the resorts, adventures and experiences worth '
            'crossing the world for, from Alaskan waters to Hawaii\u2019s Kohala Coast.',
       theme='#20262B'),

  # Resorts
  dict(src='magnus-talon-v2.html', out='resorts/talon-lodge-spa/index.html',
       desc='Talon Lodge & Spa is a floating luxury fishing lodge on Alaska\u2019s Inside '
            'Passage, minutes from Sitka: guided salmon and halibut, a working spa, and '
            'a kitchen built around the day\u2019s catch.',
       theme='#3C3F42'),
  dict(src='magnus-resort-postranch.html', out='resorts/post-ranch-inn/index.html',
       desc='Post Ranch Inn stands a thousand feet above the Pacific at Big Sur \u2014 '
            'adults only, built low into the ridge so the architecture disappears and '
            'the view does not.',
       theme='#2A2E33'),
  dict(src='magnus-resort-castle.html', out='resorts/castle-hot-springs/index.html',
       desc='Castle Hot Springs is a private Sonoran canyon with its own thermal springs, '
            'reached by a road that goes nowhere else \u2014 Arizona\u2019s original '
            'wellness retreat.',
       theme='#2A2E33'),
  dict(src='magnus-resort-wailea.html', out='resorts/hotel-wailea/index.html',
       desc='Hotel Wailea is fifteen suites on a hillside above Wailea Beach \u2014 the '
            'adults-only Relais & Ch\u00e2teaux property on Maui.',
       theme='#2A2E33'),
  dict(src='magnus-resort-clayoquot.html', out='resorts/clayoquot-wilderness-lodge/index.html',
       desc='Clayoquot Wilderness Lodge is canvas on a river in the Vancouver Island '
            'rainforest \u2014 fly in, go out, sit still.',
       theme='#2A2E33'),

  # Adventures
  dict(src='magnus-adventure-croatia.html', out='adventures/dubrovnik-before-the-ships/index.html',
       desc='Dubrovnik before the cruise ships dock: the walls, the limestone streets and '
            'the Adriatic, photographed in the hours the old city belongs to itself.',
       theme='#1B1F24'),
  dict(src='magnus-adventure-elafiti.html', out='adventures/out-to-the-elaphiti/index.html',
       desc='Out to the Elaphiti Islands \u2014 a day on the water north of Dubrovnik, '
            'through rock passages and into harbours with no cars.',
       theme='#1B1F24'),
  dict(src='magnus-adventure-hvar.html', out='adventures/hvar-runs-on-boats/index.html',
       desc='Hvar runs on boats \u2014 how to move around a Dalmatian island where the '
            'harbour, not the road, is the high street.',
       theme='#1B1F24'),

  # Food & Wine
  dict(src='magnus-food-croatia.html', out='food-and-wine/pick-your-fish/index.html',
       desc='Pick your fish \u2014 eating on the Dalmatian coast, where the catch is '
            'chosen from the case and priced by the kilo.',
       theme='#1B1F24'),

  dict(src='magnus-food-venge.html', out='food-and-wine/venge-vineyards/index.html',
       desc='Venge Vineyards, Calistoga \u2014 harvest at the Napa estate, the Maldonado '
            'Chardonnay and the Stagecoach Block I-4 Syrah, and the gathering after.',
       theme='#1B1F24'),

  # Experiences
  dict(src='magnus-experience-alaska.html', out='experiences/alaskaadventure/index.html',
       desc='#alaskaadventure \u2014 the photographs travellers are posting from Alaska, '
            'curated by Magnus Adventures.',
       theme='#35393F'),
]

# the pages link to artifacts while the site is a preview; on Firebase they are paths.
# the cinematic Talon page supersedes the earlier layout, so both ids land in one place.
LINKS = [
  ('https://claude.ai/code/artifact/5911cc64-baa6-498e-a580-318f24a75b2b', '/resorts/talon-lodge-spa/'),
  ('https://claude.ai/code/artifact/afd0fd6e-5e0f-4c9d-ae28-2a7a82953f5e', '/resorts/talon-lodge-spa/'),
  ('https://claude.ai/code/artifact/c3c2f776-936f-4ce3-87cb-d5fbef19c331', '/resorts/post-ranch-inn/'),
  ('https://claude.ai/code/artifact/3ad1ebcd-5d1d-4178-b3b6-8a3c712fc27e', '/resorts/castle-hot-springs/'),
  ('https://claude.ai/code/artifact/216078f7-d048-49a8-8e55-b6b1f60125b4', '/resorts/hotel-wailea/'),
  ('https://claude.ai/code/artifact/56ef0af2-1727-4fed-8e46-eb4de1e260aa', '/resorts/clayoquot-wilderness-lodge/'),
  ('https://claude.ai/code/artifact/669911a2-6688-499d-bd9b-562f23ba9979', '/adventures/dubrovnik-before-the-ships/'),
  ('https://claude.ai/code/artifact/12896c08-9872-4589-86f9-dea11227ff26', '/adventures/out-to-the-elaphiti/'),
  ('https://claude.ai/code/artifact/3b50398f-5d8d-4eaa-ae2a-995d76a92a39', '/adventures/hvar-runs-on-boats/'),
  ('https://claude.ai/code/artifact/7af05126-72f1-4684-ac1d-d95bbff074bf', '/food-and-wine/pick-your-fish/'),
  ('https://claude.ai/code/artifact/a14454b5-d57e-43fb-9c39-fd6d40240682', '/food-and-wine/venge-vineyards/'),
  ('https://claude.ai/code/artifact/b7aabc5e-0477-4d1a-8575-c9793f78cc82', '/experiences/alaskaadventure/'),
  ('https://claude.ai/code/artifact/b7babd23-ad62-412c-9c20-b668a598cd00', '/'),
]

SPLIT = re.compile(r'(?<=</style>)', re.I)

def build(page):
    raw = io.open(os.path.join(SP, page['src']), encoding='utf-8').read()
    for old, new in LINKS:
        raw = raw.replace(old, new)

    # everything up to the last </style> belongs in the head; the rest is the body
    cut  = raw.lower().rindex('</style>') + len('</style>')
    head, body = raw[:cut].strip(), raw[cut:].strip()

    title = re.search(r'<title>(.*?)</title>', head, re.S)
    title = title.group(1) if title else 'Magnus Adventures'

    doc = (
      '<!doctype html>\n<html lang="en">\n<head>\n'
      '<meta charset="utf-8">\n'
      '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
      '<meta name="description" content="%s">\n'
      '<meta name="theme-color" content="%s">\n'
      '<meta property="og:type" content="website">\n'
      '<meta property="og:title" content="%s">\n'
      '<meta property="og:description" content="%s">\n'
      '<meta name="twitter:card" content="summary_large_image">\n'
      '%s\n</head>\n<body>\n%s\n</body>\n</html>\n'
    ) % (page['desc'], page['theme'], title, page['desc'], head, body)

    dest = os.path.join(DIST, page['out'])
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    io.open(dest, 'w', encoding='utf-8').write(doc)
    print('%-40s %6.0f KB' % (page['out'], len(doc)/1024))

os.makedirs(DIST, exist_ok=True)
for p in PAGES:
    build(p)
