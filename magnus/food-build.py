import base64, os, io
SP = os.path.dirname(os.path.abspath(__file__))
A  = os.path.join(SP, 'talon', 'assets')
DUBROVNIK = 'https://claude.ai/code/artifact/669911a2-6688-499d-bd9b-562f23ba9979'
HVAR      = 'https://claude.ai/code/artifact/3b50398f-5d8d-4eaa-ae2a-995d76a92a39'
ELAFITI   = 'https://claude.ai/code/artifact/12896c08-9872-4589-86f9-dea11227ff26'

def uri(name, folder):
    mt = 'image/png' if name.endswith('.png') else 'image/jpeg'
    with open(os.path.join(folder, name), 'rb') as f:
        return 'data:%s;base64,%s' % (mt, base64.b64encode(f.read()).decode())

F = os.path.join(SP, 'food'); H = os.path.join(SP, 'hvar')

SLIDES = [
 (F, 'fish-case.jpg',
  'A waiter&rsquo;s hand over a refrigerated case of whole fish, lobster and oysters on ice',
  'The case by the door',
  'Sea bass, bream, a turbot lying flat at the back, lobster with its claws banded, oysters wedged in the '
  'ice. A hand goes over the case and names them one at a time. Ask the price per kilo <i>before</i> you '
  'point &mdash; this is the one place on the coast where a bill can surprise you, and it is not because '
  'anyone is cheating. A whole fish for two is simply sold the way meat is sold, by weight.'),

 (H, 'grilled-squid.jpg',
  'Grilled squid served over broad beans and wild greens with a glass of white wine',
  'Restraint is the recipe',
  'Whatever you choose comes back grilled, dressed in olive oil, and put on something green. That is the '
  'whole tradition. Squid over broad beans and wild greens. Fish with <i>bla&scaron;van</i>, the chard and '
  'potato that arrives with everything. No sauce to hide behind, which is why the case by the door matters '
  'more than the kitchen does.'),

 (F, 'steak-slate.jpg',
  'A grilled steak on a slate board with rosemary and coarse sea salt',
  'The other half of the menu',
  'Inland, and after dark, the grill turns to meat &mdash; slate board, coarse salt, a branch of rosemary, '
  'potatoes on the side. Worth knowing for the night when nobody can face another whole fish. Ask whether '
  'anything is done <i>ispod peke</i>, under the bell: meat and vegetables buried under a domed lid and '
  'covered in embers for hours. It usually has to be ordered a day ahead, which is exactly why most '
  'visitors never eat it.'),

 (F, 'pizza.jpg',
  'A thin-crust pizza with ham, artichokes and mushrooms on a gingham cloth, with a beer',
  'And the cheap lunch',
  'None of the above is what you will eat most days. A thin-crust pizza with ham, artichokes and mushrooms, '
  'a cold beer, a gingham cloth and a bill that will not trouble you &mdash; every town on the coast does '
  'this well, and does it all afternoon when the kitchens doing fish by the kilo have closed until seven. '
  'Knowing that is what stops you eating badly at four o&rsquo;clock.'),

 (F, 'burrata.jpg',
  'Burrata on heirloom tomatoes and leaves, with a bottle of balsamic vinegar of Modena behind',
  'Not all of it is Croatian',
  'Burrata on heirloom tomatoes, balsamic of Modena on the table, the bowl itself painted in a pattern you '
  'would find in Sicily. Italy is a short crossing from this coast and always has been; Venice ran much of '
  'it for centuries, and the menus have never pretended otherwise. Order it happily. Just notice that the '
  'tomatoes and the oil are local even when the recipe is not.'),

 (H, 'terrace-table.jpg',
  'A table laid for four on a terrace above a bay full of moored boats',
  'And the wine to go with it',
  'The whites here are worth the attention the food gets. Hvar grows <i>bogdanu&scaron;a</i>; '
  '<i>po&scaron;ip</i> comes off Kor&ccaron;ula; the reds along this coast are almost all '
  '<i>plavac mali</i>. Very little of it is exported in quantity, so the list in front of you is not the '
  'list you can order at home. Ask the waiter what is grown within sight of the table and drink that.'),
]

out = []
for i, (folder, img, alt, title, body) in enumerate(SLIDES):
    cap = '<div class="cap"><h2>%s</h2><hr class="rule"><p>%s</p></div>' % (title, body)
    out.append('<div class="slide%s"><div class="stage captioned"><figure>'
               '<img src="%s" alt="%s"%s></figure>%s</div></div>'
               % (' on' if i == 0 else '', uri(img, folder), alt,
                  '' if i == 0 else ' loading="lazy"', cap))

html = io.open(os.path.join(SP, 'food-template.html'), encoding='utf-8').read()
html = (html.replace('__GRIFFIN__', uri('magnus-griffin.png', A))
            .replace('__DUBROVNIK__', DUBROVNIK).replace('__HVAR__', HVAR)
            .replace('__ELAFITI__', ELAFITI)
            .replace('__SLIDES__', ''.join(out)))
io.open(os.path.join(SP, 'magnus-food-croatia.html'), 'w', encoding='utf-8').write(html)
print('built magnus-food-croatia.html  %.0f KB' % (len(html)/1024))
