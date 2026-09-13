import base64, os, io
SP = os.path.dirname(os.path.abspath(__file__))
H  = os.path.join(SP, 'hvar'); A = os.path.join(SP, 'talon', 'assets')
DUBROVNIK = 'https://claude.ai/code/artifact/669911a2-6688-499d-bd9b-562f23ba9979'

def uri(name, folder):
    mt = 'image/png' if name.endswith('.png') else 'image/jpeg'
    with open(os.path.join(folder, name), 'rb') as f:
        return 'data:%s;base64,%s' % (mt, base64.b64encode(f.read()).decode())

SLIDES = [
 ('hvar-harbour.jpg',
  'The waterfront and bell tower of Hvar town seen from the water',
  'Arrive by sea',
  'There is an airport on the mainland and none on the island, so everyone comes in across the water and '
  'everyone arrives at the same place &mdash; this curve of quay, the bell tower above it, fishing boats '
  'tied three deep against the visiting ones. The white modernist block on the front is the Adriana; the '
  'bell tower behind it is your landmark for finding the way back out of the lanes. Stand on deck for the '
  'last ten minutes of the crossing. It is the best view of the town you will get all week, and it is free.'),

 ('pakleni-cove.jpg',
  'Boats moored in a clear turquoise cove in the Pakleni Islands',
  'Twenty minutes out',
  'The Pakleni Islands sit just off the harbour mouth, close enough to swim to in the imagination and a '
  'short taxi-boat in practice. Read the hulls: the registrations ending HV are Hvar boats, and half of them '
  'are working as taxis by ten in the morning. Hire one for the day, or take the scheduled runs and pay a '
  'tenth as much for the same water.'),

 ('beach-club.jpg',
  'Sun loungers and a jetty at a beach club above a pine-fringed bay',
  'The lounger economy',
  'The bays nearest town are organised: loungers in rows, a jetty, a bar at the end of it, a price per bed '
  'for the day. It is comfortable and it is not cheap, and it is a fair trade if you want shade and a drink '
  'brought to you. Walk fifteen minutes around the headland and the same sea is free, on rock instead of '
  'cushion.'),

 ('grilled-squid.jpg',
  'Grilled squid served over broad beans and greens with a glass of white wine',
  'Lunch is whatever came in',
  'Squid over broad beans and wild greens, olive oil, parsley, and a cold local white. This is the plate to '
  'order everywhere on the island and it will be different every time. Ask what the white is: Hvar grows '
  '<i>bogdanu&scaron;a</i>, a grape you will struggle to find off the island, and the reds along this coast '
  'are almost all <i>plavac mali</i>. Neither travels much. That is the reason to drink them here.'),

 ('terrace-table.jpg',
  'A table laid for four on a terrace above a bay full of moored boats',
  'The table at the end of it',
  'Dinner is booked above the bay you swam in, laid for four, an hour before anyone sits down. The boats you '
  'passed at noon are still below, lit now. Eat late &mdash; nine is normal, eight is early &mdash; and give '
  'the terrace the whole evening rather than the hour before the last boat back.'),
]

out = []
for i, (img, alt, title, body) in enumerate(SLIDES):
    src = uri(img, H)
    cap = ('<div class="cap"><h2>%s</h2><hr class="rule"><p>%s</p></div>' % (title, body))
    out.append('<div class="slide%s"><div class="stage captioned"><figure>'
               '<img src="%s" alt="%s"%s></figure>%s</div></div>'
               % (' on' if i == 0 else '', src, alt,
                  '' if i == 0 else ' loading="lazy"', cap))

html = io.open(os.path.join(SP, 'hvar-template.html'), encoding='utf-8').read()
html = (html.replace('__GRIFFIN__', uri('magnus-griffin.png', A))
            .replace('__DUBROVNIK__', DUBROVNIK)
            .replace('__SLIDES__', ''.join(out)))
io.open(os.path.join(SP, 'magnus-adventure-hvar.html'), 'w', encoding='utf-8').write(html)
print('built magnus-adventure-hvar.html  %.0f KB' % (len(html)/1024))
