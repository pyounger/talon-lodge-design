import base64, os, io
SP = os.path.dirname(os.path.abspath(__file__))
W = os.path.join(SP, 'talon', 'web'); A = os.path.join(SP, 'talon', 'assets')

def uri(name, folder):
    mt = 'image/png' if name.endswith('.png') else 'image/jpeg'
    with open(os.path.join(folder, name), 'rb') as f:
        return 'data:%s;base64,%s' % (mt, base64.b64encode(f.read()).decode())

# Curator.io feed id for #alaskaadventure. Blank this string to drop the third
# party entirely and publish the hand-curated mosaic below instead.
CURATOR = ''

# stand-in frames for the in-house mosaic, used whenever CURATOR is blank

FEED = [
 ('flyfishing-pool.jpg',        'Fly fishing a green pool below a waterfall'),
 ('bald-eagle.jpg',             'A bald eagle in a spruce'),
 ('deck-firepit-sunset.jpg',    'The fire-pit deck at sunset'),
 ('float-plane-mountains.jpg',  'A float plane moored below the mountains'),
 ('two-anglers.jpg',            'Two anglers with a salmon in the river'),
 ('sitka-edgecumbe-sunset.jpg', 'Mount Edgecumbe at sunset across Sitka Sound'),
 ('couple-at-waterfall.jpg',    'A couple with a fish at the waterfall'),
 ('brown-bear-river.jpg',       'A brown bear fishing the river'),
 ('float-plane-wading.jpg',     'Anglers wading beside a float plane'),
 ('angler-with-salmon.jpg',     'An angler holding a bright salmon'),
 ('netting-salmon.jpg',         'A guide netting a salmon boatside'),
 ('waterfront-pavilion.jpg',    'The waterfront pavilion on the island'),
]
MINI = ['deck-firepit.jpg','plated-dessert.jpg','spa-pavilion-interior.jpg',
        'plated-salmon.jpg','wine-pour.jpg','chefs-outdoor-kitchen.jpg']

def post(name, alt, folder=W, lazy=True):
    return ('<figure class="post"><img src="%s" alt="%s"%s>'
            '<a class="ig" href="#" aria-label="View on Instagram">&#9634;</a></figure>'
            % (uri(name, folder), alt, ' loading="lazy"' if lazy else ''))

posts = ''.join(post(n, a, W, i > 2) for i, (n, a) in enumerate(FEED))
mini  = ''.join(post(n, 'A Magnus Moment') for n in MINI)

html = io.open(os.path.join(SP, 'experience-template.html'), encoding='utf-8').read()
html = (html.replace('__GRIFFIN__', uri('magnus-griffin.png', A))
            .replace('__HERO__', uri('brown-bear-river.jpg', W))
            .replace('__CURATOR__', CURATOR).replace('__POSTS__', posts).replace('__MINI__', mini))
io.open(os.path.join(SP, 'magnus-experience-alaska.html'), 'w', encoding='utf-8').write(html)
print('built magnus-experience-alaska.html  %.0f KB' % (len(html)/1024))
