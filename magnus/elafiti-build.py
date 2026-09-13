import base64, os, io
SP = os.path.dirname(os.path.abspath(__file__))
E  = os.path.join(SP, 'elafiti'); A = os.path.join(SP, 'talon', 'assets')
DUBROVNIK = 'https://claude.ai/code/artifact/669911a2-6688-499d-bd9b-562f23ba9979'
HVAR      = 'https://claude.ai/code/artifact/3b50398f-5d8d-4eaa-ae2a-995d76a92a39'
FOOD      = 'https://claude.ai/code/artifact/7af05126-72f1-4684-ac1d-d95bbff074bf'

def uri(name, folder):
    mt = 'image/png' if name.endswith('.png') else 'image/jpeg'
    with open(os.path.join(folder, name), 'rb') as f:
        return 'data:%s;base64,%s' % (mt, base64.b64encode(f.read()).decode())

SLIDES = [
 ('old-port-quay.jpg',
  'The old port of Dubrovnik with small boats and the Revelin fortress',
  'Where the boats go from',
  'Round the back of the walls is a working harbour: wooden excursion boats, skiffs with outboards, the '
  'fortress squared off at the entrance and the modern city climbing the hill behind. Read the hulls again '
  '&mdash; every registration here starts DB. This is the one part of the old town that is still doing the '
  'job it was built for, and it is a two-minute walk from the busiest street in Croatia.'),

 ('leaving-old-harbour.jpg',
  'The walled city and its old harbour seen from a departing boat',
  'The angle it was built for',
  'Five minutes out you get the thing the walls were designed to present &mdash; the whole city from the sea, '
  'rising straight out of it. Every visitor photographs this from the land. Almost nobody sees it from the '
  'water, which is the direction the architects were worried about.'),

 ('rock-passage.jpg',
  'A narrow channel between two limestone cliffs with open sea beyond',
  'Through the cliffs',
  'The coast here is limestone cut into channels barely wider than the boat, cliffs going straight down into '
  'water so clear you can watch the rock continue beneath you. There is no beach, no path, no way in except '
  'the one you came by. This is the fifteen minutes that will justify the hire on its own.'),

 ('anchored-cove.jpg',
  'A speedboat at anchor in a clear cove under a pine-topped cliff',
  'Anchor, and get in',
  'The whole point of the day is this: cut the engine somewhere with no road to it, drop the ladder and swim. '
  'Bring more water than you think and something for your feet, because everywhere you land is rock. The '
  'flag on the stern is the courtesy you owe the coastguard; the shade is the one you owe yourselves.'),

 ('island-harbour.jpg',
  'A small island harbour with a gulet, a ferry and a sailing yacht',
  'Another century, same morning',
  'The harbours out here take a dozen boats, not a hundred: a wooden gulet, the island ferry, somebody&rsquo;s '
  'charter yacht, cypresses running up the hill behind. Two of the three inhabited islands allow no cars, '
  'which you notice first as a sound rather than a fact. Go on the scheduled ferry and it costs very little; '
  'hire a boat and you choose the bay.'),

 ('sand-beach.jpg',
  'A sandy bay with loungers and umbrellas, a village across the water',
  'Sand, which is rare here',
  'Dalmatia is a rock coast. Its beaches are pebble, shingle and slab, and you learn to bring something to '
  'sit on. So a genuine sandy bay is a local event, and it gets organised accordingly &mdash; note the sign '
  'reserving this stretch for hotel guests. There is almost always a public run of the same sand just round '
  'the headland. Walk five minutes and look for where the families are.'),

 ('lobster-pasta.jpg',
  'A whole lobster served over tagliatelle in a steel pan with serving tongs',
  'Lunch, at island pace',
  'Lobster split over tagliatelle in a tomato and wine broth, brought to the table in the pan it was cooked '
  'in, with tongs and a spoon so you serve each other. Like the fish, it is sold by weight &mdash; agree the '
  'price before the pan leaves the kitchen. Then give it two hours, because the boat is not going anywhere '
  'and neither is the afternoon.'),
]

out = []
for i, (img, alt, title, body) in enumerate(SLIDES):
    cap = '<div class="cap"><h2>%s</h2><hr class="rule"><p>%s</p></div>' % (title, body)
    out.append('<div class="slide%s"><div class="stage captioned"><figure>'
               '<img src="%s" alt="%s"%s></figure>%s</div></div>'
               % (' on' if i == 0 else '', uri(img, E), alt,
                  '' if i == 0 else ' loading="lazy"', cap))

html = io.open(os.path.join(SP, 'elafiti-template.html'), encoding='utf-8').read()
html = (html.replace('__GRIFFIN__', uri('magnus-griffin.png', A))
            .replace('__DUBROVNIK__', DUBROVNIK).replace('__HVAR__', HVAR).replace('__FOOD__', FOOD)
            .replace('__SLIDES__', ''.join(out)))
io.open(os.path.join(SP, 'magnus-adventure-elafiti.html'), 'w', encoding='utf-8').write(html)
print('built magnus-adventure-elafiti.html  %.0f KB' % (len(html)/1024))
