import base64, io, os, re
SP  = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(SP, 'img'); ASSET = os.path.join(SP, 'talon', 'assets')
def uri(n, d=IMG):
    mt='image/png' if n.endswith('.png') else 'image/jpeg'
    with open(os.path.join(d,n),'rb') as f:
        return 'data:%s;base64,%s'%(mt, base64.b64encode(f.read()).decode())

HOME  = 'https://claude.ai/code/artifact/b7babd23-ad62-412c-9c20-b668a598cd00'
TALON = 'https://claude.ai/code/artifact/afd0fd6e-5e0f-4c9d-ae28-2a7a82953f5e'

# Copy carried over from the homepage rewrite. The scene bands stay as plates
# until there are facts and photographs to fill them; inventing either would be
# worse than an honest gap on a page that recommends someone else's hotel.
PAGES = [
 dict(slug='castle', name='Castle Hot Springs',
      h1='A canyon with its own hot springs &mdash; the Arizona desert, an hour from anywhere',
      where='A private canyon in the Sonoran Desert &mdash; Arizona',
      pillars=('Soak','Restore','Wander'),
      alt='A swimmer in the spring-fed pool beneath palms and red canyon rock',
      focal='50% 46%',
      body=["A canyon with its own hot springs, reached by a road that goes nowhere else, with saguaro "
            "standing over the cabins.",
            "The water comes out of the ground warm and has done for a very long time. Palms grow where the "
            "spring runs. The red rock closes in on both sides, and the nearest town is a long way off.",
            "Arizona has no shortage of desert resorts. This is the one where the geology does the work."],
      scenes=['The springs','The cabins','The farm','The canyon'],
      tri=[('The Springs','Water out of the ground at bathing temperature, in three pools down the canyon.'),
           ('The Cabins','Scattered along the creek under the palms, with the rock wall behind them.'),
           ('The Table','A working farm on the property, and a kitchen that cooks what it grows.')],
      book=('Open most of the year',
            'Desert summers are severe and the season runs around them. Check dates before booking flights '
            'into Phoenix.')),
 dict(slug='wailea', name='Hotel Wailea',
      h1='Fifteen suites above the beach &mdash; Maui, deliberately off the sand',
      where='Above Wailea Beach &mdash; Maui, Hawaii',
      pillars=('Arrive','Linger','Return'),
      alt='A couple on the sand beneath an orange umbrella, turquoise water beyond',
      focal='50% 56%',
      body=["Fifteen suites on a hillside above the resort strip, adults only, and the only Relais &amp; "
            "Ch&acirc;teaux property in Hawaii.",
            "It is deliberately not on the beach. That is the whole design. Everything below it is busy; "
            "the hotel is not, and the beach is a short ride down whenever you want it.",
            "Maui rewards people who book the quiet thing and travel the last half mile."],
      scenes=['The suites','The table','The beach','The hillside'],
      tri=[('The Suites','Fifteen of them, adults only, each one looking down the coast.'),
           ('The Table','The only Relais &amp; Ch&acirc;teaux kitchen in the islands.'),
           ('The Beach','Wailea Beach below, reached by the hotel rather than shared with it.')],
      book=('Open all year',
            'Maui is busiest over the winter holidays and through spring break. Everything else is easier.')),
 dict(slug='clayoquot', name='Clayoquot Wilderness Lodge',
      h1='Canvas on a river in the rainforest &mdash; Vancouver Island, by float plane',
      where='Bedwell River, Clayoquot Sound &mdash; British Columbia',
      pillars=('Fly in','Go out','Sit still'),
      alt='White safari tents on a raised deck above still water, conifers and morning mist behind',
      focal='60% 52%',
      body=["Canvas tents with woodstoves and proper beds, pitched on a river in temperate rainforest, "
            "reachable only by float plane or boat.",
            "Bears, whales and steelhead within an hour of the tent. Mist off the water most mornings. No "
            "road in, which is the point rather than the inconvenience.",
            "Safari staging, Pacific Northwest weather."],
      scenes=['The tents','The river','The wildlife','The table'],
      tri=[('The Tents','Canvas, woodstoves, proper beds, raised on decks above the water.'),
           ('The River','Steelhead and salmon in the Bedwell, with nobody else on it.'),
           ('The Wildlife','Black bears on the estuary, whales in the sound, eagles throughout.')],
      book=('A short summer season',
            'The lodge runs through the warm months only, and everyone arrives by float plane or boat. '
            'Book the flight and the tent together.')),
]

tpl = io.open(os.path.join(SP,'postranch-template.html'), encoding='utf-8').read()

for pg in PAGES:
    s = tpl
    s = s.replace('<title>Post Ranch Inn</title>', '<title>%s</title>' % pg['name'], 1)
    s = s.replace('<div class="nm">Post Ranch Inn</div>', '<div class="nm">%s</div>' % pg['name'], 1)
    s = s.replace('>Post Ranch Inn</p>', '>%s</p>' % pg['name'], 1)
    s = re.sub(r'<h1>.*?</h1>', '<h1>%s</h1>' % pg['h1'], s, count=1, flags=re.S)
    s = s.replace('<span>Unplug</span><span>Indulge</span><span>Reconnect</span>',
                  ''.join('<span>%s</span>' % w for w in pg['pillars']), 1)
    s = s.replace('<span>&rsaquo;</span>Post Ranch Inn', '<span>&rsaquo;</span>%s' % pg['name'], 1)
    s = s.replace("f.title = 'Post Ranch Inn';", "f.title = '%s';" % pg['name'], 1)
    s = s.replace('#postranchinn', '#' + pg['slug'])
    s = s.replace('postranchinn.com', pg['slug'] + '.com')
    s = s.replace('.hero>.shot img{object-position:53% 48%}',
                  '.hero>.shot img{object-position:%s}' % pg['focal'], 1)
    s = s.replace('alt="A swimmer in the cliff-edge infinity pool at dusk, looking out over the Pacific"',
                  'alt="%s"' % pg['alt'], 1)
    # the three tiles
    for (old_h3, old_p), (new_h3, new_p) in zip(
            [('The Table','Sierra Mar, on the edge of the ridge. Foraged, grown in the chef&rsquo;s garden, three to six courses.'),
             ('The Rooms','Tree houses on legs to spare the redwood roots; ocean rooms under sod roofs.'),
             ('The Water','Two infinity pools, one at the cliff edge, and hot tubs placed for the view.')],
            pg['tri']):
        s = s.replace('<h3>%s</h3>' % old_h3, '<h3>%s</h3>' % new_h3, 1)
        s = s.replace('<p>%s</p>' % old_p, '<p>%s</p>' % new_p, 1)
    # tile plate captions
    for old_nm, (new_nm, _) in zip(['Sierra Mar','The rooms','The pools'], pg['tri']):
        s = s.replace('<p class="nm">%s</p>' % old_nm, '<p class="nm">%s</p>' % new_nm, 1)
    s = s.replace('<p class="nm">The ridge</p>', '<p class="nm">%s</p>' % pg['scenes'][0], 1)
    # the booking band
    s = s.replace('<h2>Open all year</h2>', '<h2>%s</h2>' % pg['book'][0], 1)
    s = re.sub(r'<p>Big Sur weather turns fast.*?</p>', '<p>%s</p>' % pg['book'][1], s, count=1, flags=re.S)

    # the three standfirst paragraphs
    start = s.index('<p>Post Ranch Inn stands on a ridge')
    end   = s.index('</p>', s.index('nowhere brighter to look than the ocean')) + 4
    s = s[:start] + '\n    '.join('<p>%s</p>' % b for b in pg['body']) + s[end:]
    # scene bands
    scenes = ''.join(
      '''<section class="scene%s">
           <div class="shot"><div class="sceneplate"><p class="nm">%s</p><hr>
             <p class="note">Photography to come</p></div></div>
           <div class="panel"><h2>%s</h2><hr>
             <p>Copy for this section is waiting on details from the property.</p>
             <a class="btn" href="#">Explore</a></div>
         </section>''' % (' right' if i%2 else '', t, t)
      for i,t in enumerate(pg['scenes']))
    for k,v in (('__GRIFFIN__',uri('magnus-griffin.png',ASSET)),
                ('__HERO__',uri('hero-%s.jpg' % pg['slug'])),
                ('__SCENES__',scenes),('__WALL__',''),('__HOME__',HOME),('__TALON__',TALON)):
        s = s.replace(k,v)
    out = os.path.join(SP,'magnus-resort-%s.html' % pg['slug'])
    io.open(out,'w',encoding='utf-8').write(s)
    body = s[:s.index('class="about"')]          # everything above the shared footer
    leaks = [w for w in ('Post Ranch','Sierra Mar','Big Sur','Tongass','Sitka','redwood',
                         'infinity pools') if w in body]
    print('%-34s %5.0f KB   leaks: %s' % (os.path.basename(out), len(s)/1024, leaks or 'none'))
