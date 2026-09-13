#!/usr/bin/env python3
"""Venge Vineyards, Calistoga -> magnus-food-venge.html

Waiting on photographs. The stories in this section are photograph-led: each
slide is written to a specific frame, the way the Croatia pages were, so the
writing cannot sensibly come first. SHOTS below is the list the story needs.
Drop the files into venge/ under these names and run this; it reports what is
still missing rather than building a page full of gaps.

Nothing here asserts a fact about the estate. The headings and bodies are
written once the photographs and the confirmed details are both in hand -
this is a commercial page for a real producer, and getting a blend or a
vintage wrong on it is worse than shipping it a week later.
"""
import base64, io, os

SP = os.path.dirname(os.path.abspath(__file__))
V  = os.path.join(SP, 'venge')

# filename, what the frame should show, working heading
SHOTS = [
 ('approach.jpg',    'The drive in - gate, track, the first sight of the property',
                     'The road in'),
 ('vines.jpg',       'A block of vines close enough to read the fruit and the soil',
                     'What they farm'),
 ('tasting.jpg',     'The tasting table or porch, laid, with the view beyond it',
                     'Where you taste'),
 ('pour.jpg',        'A pour in progress - hands, bottle, glass, close',
                     'The pour'),
 ('cellar.jpg',      'Barrels or tanks, working cellar rather than a showroom',
                     'The small lots'),
 ('bottles.jpg',     'The bottles together, labels legible',
                     'What to take home'),
]

def uri(name):
    with open(os.path.join(V, name), 'rb') as f:
        return 'data:image/jpeg;base64,%s' % base64.b64encode(f.read()).decode()

missing = [n for n, _, _ in SHOTS if not os.path.exists(os.path.join(V, n))]
if missing:
    print('venge/ is short %d of %d photographs:\n' % (len(missing), len(SHOTS)))
    for name, wants, _ in SHOTS:
        here = os.path.exists(os.path.join(V, name))
        print('  [%s] %-14s %s' % ('ok' if here else '  ', name, wants))
    print('\nConfirmed: Venge is a Talon winemaking partner - that is the spine')
    print('of the story, Calistoga to a table in the Tongass.\n')
    print('Still needed before this can be written:')
    print('  - the wines to name, with the vintages you want on the page')
    print('  - which of them are poured at the lodge, and whether guests can buy')
    print('  - who to credit for the photographs')
    raise SystemExit(0)

raise SystemExit('Photographs are present. The slide copy still has to be '
                 'written to them - see the module docstring.')
