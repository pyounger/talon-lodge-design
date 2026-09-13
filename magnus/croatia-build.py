import base64, os, io
SP = os.path.dirname(os.path.abspath(__file__))
C  = os.path.join(SP, 'croatia'); A = os.path.join(SP, 'talon', 'assets')

def uri(name, folder):
    mt = 'image/png' if name.endswith('.png') else 'image/jpeg'
    with open(os.path.join(folder, name), 'rb') as f:
        return 'data:%s;base64,%s' % (mt, base64.b64encode(f.read()).decode())

# (image, alt, title|None, body|None) — a slide with no body runs full bleed
SLIDES = [
 ('pile-gate-bridge.jpg',
  'Visitors crossing the stone bridge to the Pile Gate, Dubrovnik',
  'You arrive on foot',
  'No road runs through the old city. Every visitor crosses this bridge and walks in under the arch, past the '
  'statue of Saint Blaise standing in his niche &mdash; the city&rsquo;s patron, and the figure you will meet '
  'again on doorways, gates and towers all week. The flag above the tower reads <i>Libertas</i>. This is the '
  'bridge at nine in the morning. By noon, when the tenders have emptied, you queue for the same forty paces.'),

 ('onofrio-fountain.jpg',
  'Onofrio&rsquo;s Large Fountain, its dome and inscription plaque',
  'Water, since 1438',
  'Twenty paces inside the gate the street opens onto Onofrio&rsquo;s Large Fountain, built as the end of an '
  'aqueduct that carried spring water down to the city. The plaque names the architect &mdash; Onofrio della '
  'Cava, <i>Parthenopeo</i>, of Naples &mdash; and the year it was finished. The great earthquake of 1667 took '
  'the ornamented upper storey; what stands is the plain dome that survived it, ringed with carved spouts. '
  'The water still runs and is still cold.'),

 ('small-fountain.jpg',
  'Onofrio&rsquo;s Small Fountain, carved with masks, on a street corner beside a caf&eacute;',
  'And the small one',
  'At the far end of the main street stands the same architect&rsquo;s other fountain, fed by the same '
  'aqueduct and built at a fraction of the size: a bowl on a twisted stem, a ring of carved masks, water '
  'still running out of them. It sits on a corner between caf&eacute; tables and almost everybody walks past '
  'it. That makes it the better one to fill a bottle at, because there is never a queue.'),

 ('mascaron.jpg',
  'A carved stone face with an open mouth set into a wall',
  'Look down',
  'Mouths like this one are set all through the old town. Some belong to fountains. Some sit low in a plain '
  'wall with no plaque, no explanation and no crowd in front of them. They reward looking down: the best '
  'carving in Dubrovnik is rarely at eye level, and it has been worn smooth by six hundred years of hands.'),

 ('jesuit-church.jpg',
  'The interior of a Jesuit church with a marble floor laid on the diagonal',
  'And then look up',
  'The same instinct that finds carved mouths at knee height will walk straight past this. Behind a plain '
  'door, a Jesuit church &mdash; the order&rsquo;s monogram set in the pediment, barley-sugar columns around '
  'the altar, and a floor of grey and white marble laid on the diagonal so the room seems to run at you. '
  'Stone holds the night&rsquo;s cool until late afternoon. On a thirty-degree day that is reason enough '
  'to go in.'),

 ('street-vendor.jpg',
  'A street vendor in Renaissance costume selling souvenir hearts by the fountain',
  'Two euros for Libertas',
  'By mid-morning the square in front of the fountain belongs to the sellers. This one works in Renaissance '
  'dress with a basket of gilded hearts, each stamped with the city&rsquo;s name and the year. It is easy to '
  'be sniffy about it. Don&rsquo;t be &mdash; Dubrovnik has been selling its own reputation since it was a '
  'republic, and doing it with rather more charm than most.'),

 ('sweet-shop.jpg',
  'Barrels of brightly coloured sweets in a shop off the main street',
  'What the Stradun sells now',
  'Barrels of sweets by the kilo, giant marshmallow macarons, a gluten-free badge on everything and two '
  'shoppers working their way down the row. The main street trades almost entirely in visitors now, and this '
  'is the honest state of it at noon. The remedy is a staircase. Turn off the Stradun and climb &mdash; two '
  'minutes uphill the shops stop, the laundry starts, and you are in the city that still lives here.'),
]

out = []
for i, (img, alt, title, body) in enumerate(SLIDES):
    src = uri(img, C)
    cap, stage = '', 'stage'
    if body:
        stage = 'stage captioned'
        cap = ('<div class="cap">%s<hr class="rule"><p>%s</p></div>'
               % ('<h2>%s</h2>' % title if title else '', body))
    out.append('<div class="slide%s"><div class="%s"><figure>'
               '<img src="%s" alt="%s"%s></figure>%s</div></div>'
               % (' on' if i == 0 else '', stage, src, alt,
                  '' if i == 0 else ' loading="lazy"', cap))

html = io.open(os.path.join(SP, 'croatia-template.html'), encoding='utf-8').read()
html = html.replace('__GRIFFIN__', uri('magnus-griffin.png', A)).replace('__SLIDES__', ''.join(out))
io.open(os.path.join(SP, 'magnus-adventure-croatia.html'), 'w', encoding='utf-8').write(html)
print('built magnus-adventure-croatia.html  %.0f KB' % (len(html)/1024))
