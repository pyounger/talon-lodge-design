import base64, os, io
SP = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(SP, 'kohala'); A = os.path.join(SP, 'talon', 'assets')

def uri(name, folder):
    mt = 'image/png' if name.endswith('.png') else 'image/jpeg'
    with open(os.path.join(folder, name), 'rb') as f:
        return 'data:%s;base64,%s' % (mt, base64.b64encode(f.read()).decode())

# (image, alt, title|None, body|None) — a slide with no body is image-only
SLIDES = [
 ('slide1-beach-sunset.jpg', 'Outrigger canoe on the beach at sunset, Kohala Coast',
  'Four Seasons Hualalai',
  'The Four Seasons Hualalai Hotel is a luxurious retreat located on the island of Hawaii, also known as the '
  'Big Island. The hotel is situated on the Kona-Kohala coast, which boasts stunning views of the Pacific Ocean. '
  'The Four Seasons Hualalai offers a unique and exclusive experience, with its luxurious amenities, beautiful '
  'surroundings, and exceptional service.'),
 ('slide2-beach-tree-bar.jpg', 'Guests at the Beach Tree Bar and Lounge at sunset',
  'Dining at Hualalai',
  'The hotel&rsquo;s dining options are also exceptional, with a range of restaurants and bars to choose from. '
  'The Beach Tree Bar and Lounge is a popular spot for casual dining, serving up fresh seafood and classic '
  'Hawaiian dishes. For a more formal dining experience, guests can dine at &lsquo;ULU Ocean Grill, which offers '
  'a modern take on Hawaiian cuisine, featuring fresh, locally sourced ingredients.'),
 ('slide3-sushi.jpg', 'Sushi served oceanfront at sunset', None, None),
 ('slide4-guest-room.jpg', 'A guest room with lanai doors open to the garden',
  None,
  'The hotel features 243 guest rooms, suites, and villas, all of which are designed with a traditional Hawaiian '
  'aesthetic. The rooms are spacious and well-appointed, with high-quality furnishings and comfortable beds. '
  'The suites and villas offer additional amenities such as private plunge pools, outdoor showers, and expansive '
  'living areas.'),
]

out = []
for i, (img, alt, title, body) in enumerate(SLIDES):
    cap = ''
    stage = 'stage'
    if body:
        stage = 'stage captioned'
        cap = ('<div class="cap">%s<hr class="rule"><p>%s</p></div>'
               % ('<h2>%s</h2>' % title if title else '', body))
    out.append('<div class="slide%s"><div class="%s">'
               '<figure><img src="%s" alt="%s"%s></figure>%s</div></div>'
               % (' on' if i == 0 else '', stage, uri(img, K), alt,
                  '' if i == 0 else ' loading="lazy"', cap))

html = io.open(os.path.join(SP, 'adventure-template.html'), encoding='utf-8').read()
html = html.replace('__GRIFFIN__', uri('magnus-griffin.png', A)).replace('__SLIDES__', ''.join(out))
io.open(os.path.join(SP, 'magnus-adventure-kohala.html'), 'w', encoding='utf-8').write(html)
print('built magnus-adventure-kohala.html  %.0f KB' % (len(html)/1024))
