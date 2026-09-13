#!/usr/bin/env python3
"""Venge Vineyards, Napa -> magnus-food-venge.html

Four photographs, taken on the estate at the end of harvest. The copy is
written to the frames and describes only what is in them: no blend, no
vintage beyond the one legible on a label, no claim about the farming that
the photograph does not show. Everything else waits for the winery to
confirm it.

The Talon partnership is named here and deliberately not on the homepage
card - the owner's call.
"""
import base64, io, os

SP = os.path.dirname(os.path.abspath(__file__))
V  = os.path.join(SP, 'venge')
A  = os.path.join(SP, 'talon', 'assets')

TALON = 'https://claude.ai/code/artifact/5911cc64-baa6-498e-a580-318f24a75b2b'
HOME  = 'https://claude.ai/code/artifact/b7babd23-ad62-412c-9c20-b668a598cd00'

def uri(name, folder):
    mt = 'image/png' if name.endswith('.png') else 'image/jpeg'
    with open(os.path.join(folder, name), 'rb') as f:
        return 'data:%s;base64,%s' % (mt, base64.b64encode(f.read()).decode())

SLIDES = [
 ('house.jpg',
  'A low winery building with a long porch standing above a vineyard, autumn trees behind it '
  'and guests gathered at the foot of the steps',
  'The house above the rows',
  'You see it from the vineyard before you reach it &mdash; a low building with a porch running '
  'its length, set on the rise above the last row. Olive trees along the front, one tree gone '
  'orange beside the roof, and a crowd already collected at the foot of the steps. Nothing about '
  'it announces itself. The vines come first and the building second, which is most of what you '
  'need to know about the order of things here.'),

 ('vines.jpg',
  'A cluster of small dark grapes hanging on the vine among yellowing leaves, with green cover '
  'crop between the rows behind',
  'Still on the vine',
  'Late in the season and there is fruit still hanging. The leaves have gone yellow at the edges, '
  'the berries have pulled in tight and dark, and the skins are thick enough to read from a step '
  'away. Between the rows the cover crop is still green and a drip line runs along the wire. This '
  'is the stretch of the year when the only question left is which block comes in and which one '
  'waits another week.'),

 ('bottles.jpg',
  'A magnum of Venge Vineyards Family Reserve Cabernet on a table with sunflowers, Indian corn '
  'and small pumpkins, rows of empty wine glasses in front and vineyard behind',
  'What gets opened',
  'A magnum of Family Reserve Cabernet, &rsquo;07 on the label, standing where everyone walking '
  'up has to pass it, with two more bottles behind. Sunflowers in a jar, Indian corn, small '
  'pumpkins, a barrel head with the name burned into it &mdash; the whole arrangement is harvest, '
  'and deliberately so. Then the rows of polished glasses in front of it, which tell you how many '
  'people are expected.'),

 ('tasting.jpg',
  'Guests seated at round tables under a wooden pergola on grass, green gingham cloths, with '
  'vineyard rows and hills beyond in low evening sun',
  'The table',
  'Green gingham, plates already worked through, and the sun coming in low and flat under the '
  'pergola. Round tables set on the grass, the vineyard running off behind them towards the hills '
  'on the far side of the valley. The tasting is not held in a room. It happens out among the rows '
  'the wine came from, at the hour when the light does the work for you.'),
]

missing = [n for n, _, _, _ in SLIDES if not os.path.exists(os.path.join(V, n))]
if missing:
    raise SystemExit('venge/ is missing: ' + ', '.join(missing))

out = []
for i, (img, alt, title, body) in enumerate(SLIDES):
    cap = '<div class="cap"><h2>%s</h2><hr class="rule"><p>%s</p></div>' % (title, body)
    out.append('<div class="slide%s"><div class="stage captioned"><figure>'
               '<img src="%s" alt="%s"%s></figure>%s</div></div>'
               % (' on' if i == 0 else '', uri(img, V), alt,
                  '' if i == 0 else ' loading="lazy"', cap))

html = io.open(os.path.join(SP, 'venge-template.html'), encoding='utf-8').read()
html = (html.replace('__GRIFFIN__', uri('magnus-griffin.png', A))
            .replace('__TALON__', TALON).replace('__HOME__', HOME)
            .replace('__SLIDES__', ''.join(out)))

# nothing from the Croatia story it was cut from may survive above the footer
body_only = html[:html.index('class="about"')]
leaks = [w for w in ('Dubrovnik', 'Hvar', 'Elaphiti', 'Dalmatia', 'Croatia', 'turbot')
         if w in body_only]

io.open(os.path.join(SP, 'magnus-food-venge.html'), 'w', encoding='utf-8').write(html)
print('built magnus-food-venge.html  %.0f KB   slides: %d   leaks: %s'
      % (len(html)/1024, len(SLIDES), ', '.join(leaks) if leaks else 'none'))
