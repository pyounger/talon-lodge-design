import base64, io, os, json, re
SP=os.path.dirname(os.path.abspath(__file__)); IMG=os.path.join(SP,'img')
def uri(n):
    with open(os.path.join(IMG,n),'rb') as f:
        return 'data:image/jpeg;base64,'+base64.b64encode(f.read()).decode()

DUBROVNIK = 'https://claude.ai/code/artifact/669911a2-6688-499d-bd9b-562f23ba9979'
ELAFITI   = 'https://claude.ai/code/artifact/12896c08-9872-4589-86f9-dea11227ff26'
HVAR      = 'https://claude.ai/code/artifact/3b50398f-5d8d-4eaa-ae2a-995d76a92a39'
FOODWINE  = 'https://claude.ai/code/artifact/7af05126-72f1-4684-ac1d-d95bbff074bf'
VENGE     = 'https://claude.ai/code/artifact/a14454b5-d57e-43fb-9c39-fd6d40240682'

ADV=[
 ("Dubrovnik Before the Ships","Dubrovnik, Croatia","A walled city with no road through it, best seen in the two hours before the tenders land. From the stone bridge at Pile to a six-hundred-year-old fountain that still runs cold &mdash; and what the old town becomes by lunchtime.","adv-dubrovnik.jpg"),
 ("Out to the Elaphiti","The Elaphiti Islands, Croatia","The answer to Dubrovnik at noon is a boat. Cliff channels barely wider than the hull, a cove with no road to it, two islands that allow no cars, and sand &mdash; which on a coast built of rock is worth crossing water for.","adv-elafiti.jpg"),
 ("Hvar Runs on Boats","Hvar, Croatia","Two hours by catamaran from Split, and from the moment you land the day is organised around water. Lunch is on another island, the beach club is a ten-minute crossing, and dinner is above the bay you spent the afternoon in.","adv-hvar.jpg"),
 ("Scottsdale &ndash; A Dining Mecca","Scottsdale, Arizona","Scottsdale &ndash; a dining mecca showcases exceptional culinary experiences like Course Restaurant, Hush Public House, and Fat Ox, where innovative cuisine, refined ambiance, and world-class service define a sophisticated desert dining adventure.","adv-scottsdale.jpg"),
 ("Dining On the Valley Isle","Maui, Hawaii","Dining on Maui, the Valley Isle, blends ocean-fresh seafood, tropical ingredients, and world-class chefs with sunset views, open-air restaurants, and unforgettable farm-to-table Hawaiian cuisine experiences.","adv-maui.jpg"),
 ("France &ndash; The not so well known route","Annecy &amp; Nice, France","Beginning at the mountain village of Annecy, France and then traveling south to the French Riviera, makes for a spectacular view of French history, beauty and cultural warmth.","adv-france.jpg"),
 ("Land of Kings and Pharaohs","Egypt and Jordan","Sail the timeless Nile, marvel at Giza&rsquo;s pyramids, explore ancient temples, and discover Luxor&rsquo;s grandeur&mdash;Egypt&rsquo;s history unfolds majestically.",None),
 ("Hawaii&rsquo;s Kohala Coast","Hawaii, The Island","Explore the stunning Kohala Coast and indulge in luxurious stays at the Four Seasons Hualalai and Mauna Lani Point. Discover pristine beaches, lush greenery, and endless activities in this paradise.",None),
 ("5 Best Alaska Fishing Lodges and Adventure Resorts","Alaska","The very best Alaska fishing lodges and adventure resorts for your next Alaska vacation. These lodges have passed the Magnus Adventures standards for service, quality, amenities, unique offerings, and an adventure menu that goes beyond Alaska&rsquo;s remarkable fishing.",None),
 ("The Wonders of Istanbul","Istanbul","Hagia Sophia, officially the Hagia Sophia Grand Mosque, is a mosque and major cultural and historical site in Istanbul, Turkey. Originally a Greek Orthodox church, the site has changed between being a mosque and a museum since the fall of the Byzantine Empire.",None),
 ("Relax on the Amalfi Coast","Amalfi Coast","A 50-kilometer stretch of coastline along the southern edge of Italy&rsquo;s Sorrentine Peninsula. Sheer cliffs and a rugged shoreline dotted with small beaches and pastel-colored fishing villages, grand villas, terraced vineyards and cliffside lemon groves.",None),
 ("Oahu Through the iPhone Lens","Oahu, Hawaii","Oahu is named the Gathering Place and is the most populated of the Hawaiian Islands. When you take a drive and bring your iPhone, you will see the beauty of this spectacular island.",None),
 ("Crushing Burgundy","Burgundy, France","Famous for its Burgundy wines, pinot noirs and Chardonnay. Burgundy is crisscrossed by a network of canals, grand ch&acirc;teaux, and some of the finest luxury hotels. Food, wine and history are all served with French hospitality.",None),
 ("Amsterdam to Basel &ndash; A trip on the river","Rhine River","A luxury river cruise down the Rhine will relax all. Amsterdam to Basel with great wine, food, castles, bike rides equals a wonderful luxury vacation.",None),
 ("Napa &ndash; Wine Tasting with a casual twist","Napa, California","Sometimes the best path is the most comfortable path. No pomp, circumstance or fluff. This path takes you to the unassuming places with the most recognized winemakers in Napa Valley.",None),
 ("Cruising Through Tahiti","Tahiti","Tahiti, a magical grouping of South Pacific Islands, comes alive when explored by a small and intimate cruise ship.",None),
 ("Sitka, Alaska &ndash; Alaska&rsquo;s Best Fishing Trip","Sitka, Alaska","Alaska&rsquo;s best fishing destination is your best bet for a great Alaska fishing trip. Sitka sits on the Gulf of Alaska side of Baranof Island. It is the home to a robust commercial fishing industry and is Alaska&rsquo;s sportfishing mecca.",None),
]
RES=[
 ("Talon Lodge &amp; Spa","A private island in the Tongass &mdash; Sitka, Alaska",
  "Fifteen minutes by boat from Sitka, on an island of its own. Four chefs and a three-thousand-bottle "
  "cellar for twenty-four guests, with king salmon thirty minutes from the dock."),
 ("Castle Hot Springs","A private canyon in the Sonoran Desert &mdash; Arizona",
  "A canyon with its own hot springs, reached by a road that goes nowhere else, with saguaro standing over "
  "the cabins. Arizona has no shortage of desert resorts; this is the one where the water comes out of the "
  "ground warm and the nearest town is a long way off."),
 ("Post Ranch Inn","On the cliffs above the Pacific &mdash; Big Sur, California",
  "Built low into a promontory a thousand feet above the sea, so that the architecture disappears and the "
  "view does not. Adults only, no televisions, and famously difficult to book. The reason to go is the "
  "weather coming in off the water."),
 ("Hotel Wailea","Above Wailea Beach &mdash; Maui, Hawaii",
  "Fifteen suites on a hillside above the resort strip, adults only, and the only Relais &amp; Ch&acirc;teaux "
  "property in Hawaii. It is deliberately not on the beach, which is what keeps it quiet while everything "
  "below it is not."),
 ("Clayoquot Wilderness Lodge","Bedwell River, Clayoquot Sound &mdash; British Columbia",
  "Canvas tents with woodstoves and proper beds, pitched on a river in temperate rainforest, reachable "
  "only by float plane or boat. Bears, whales and steelhead within an hour of the tent. Safari staging, "
  "Pacific Northwest weather."),
]
EXP=[
 ("#alaskaadventure","Alaska is the most spectacular place on the planet. Take a tour of Alaska adventure experiences as presented by travelers who have experienced its wonders.","exp-alaska.jpg"),
 ("#flyfishing","Alaska Fly Fishing, Sitka Fly Fishing, BC Fly Fishing. Discover some of the great fly fishing destinations and enjoy the excitement of each.","exp-flyfishing.jpg"),
 ("#4ocean","4,297,182 pounds of trash removed from the ocean and coastlines by paid 4ocean employees since 2017 through the sale of our products.","exp-4ocean.jpg"),
 ("#gopro","GoPro frees people to celebrate the moment, inspiring others to do the same. We believe that sharing our experiences makes them more meaningful.",None),
 ("#natgeo","Since 1888, National Geographic has been bringing the planet to life for millions of readers and explorers. Let your imagination wander.",None),
]

# ---------------------------------------------------------------- panel content
# The control panel exports magnus-content.json. When that file is present it
# wins: the page is built from what somebody edited, not from the lists above.
# With no export the lists are the fallback, so the build never breaks.
def esc(t):
    return (t or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def load_export():
    path = os.path.join(SP, 'magnus-content.json')
    if not os.path.exists(path):
        return {}
    data = json.load(io.open(path, encoding='utf-8'))
    by_kind = {}
    for row in data.get('stories', []):
        by_kind.setdefault(row.get('kind'), []).append(row)
    for rows in by_kind.values():
        rows.sort(key=lambda r: r.get('order') or 0)
    return by_kind

EXPORT = load_export()

def story_img(row):
    """Full-resolution file where we hold one; otherwise a panel upload; else nothing.
       The export's own image is a thumbnail, too small for the page."""
    fn = row.get('imageFile') or ''
    if fn and os.path.exists(os.path.join(IMG, fn)):
        return uri(fn)
    url = row.get('image') or ''
    return url if url.startswith('http') else ''

def slot(label):
    return ('<div class="slot"><span>'+label+'</span></div>')

def card_img(fn,alt,label):
    if fn: return f'<img src="{uri(fn)}" alt="{alt}" loading="lazy">'
    return slot(label)

ADV_LINK = {0: DUBROVNIK, 1: ELAFITI, 2: HVAR}    # the three with pages so far
if EXPORT.get('adventure'):
    ADV = [(esc(r.get('title')), esc(r.get('where')), esc(r.get('blurb')), r.get('imageFile') or None)
           for r in EXPORT['adventure']]
    ADV_LINK = {n: r.get('link') or '' for n, r in enumerate(EXPORT['adventure'])}
    ADV_SRC  = {n: story_img(r) for n, r in enumerate(EXPORT['adventure'])}
else:
    ADV_SRC = {}
# A story that has been built out links from photograph, heading and line; one
# still being written keeps its card and drops the anchors.
def _adv_card(n, t, loc, b, f):
    u    = ADV_LINK.get(n) or ''
    shot = (f'<img src="{ADV_SRC[n]}" alt="{t}" loading="lazy">' if ADV_SRC.get(n)
            else card_img(f, t.replace('&ndash;', '-'), "Photo &middot; " + loc))
    return f'''<article class="card">
        <{f'a class="shot" href="{u}"' if u else 'div class="shot"'}>{shot}</{'a' if u else 'div'}>
        <h3>{f'<a class="plain" href="{u}">{t}</a>' if u else t}</h3>
        <p class="where">{loc}</p><p class="blurb">{b}</p>
        {f'<a class="cta" href="{u}">Explore Adventure</a>' if u
          else '<span class="cta soon">Story in progress</span>'}
      </article>'''

adv=''.join(_adv_card(n, t, loc, b, f) for n,(t,loc,b,f) in enumerate(ADV))

FW=[
 ("Pick Your Fish","Dalmatia, Croatia","The fish is not on the menu &mdash; it is in a case by the door, whole, on ice, priced by the kilo. How ordering works on this coast, what the kitchen does next, and which wines never leave the island they grow on.","food-fish.jpg",FOODWINE),
 ("Venge Vineyards","Calistoga, Napa Valley","A family estate at the north end of Napa Valley: fruit still on the vine at the end of harvest, a Chardonnay and a Syrah off named blocks, and what the kitchen puts beside them.","fw-venge.jpg",VENGE),
 ("The Winemakers","Partners worldwide","Talon&rsquo;s winemaking partners, their cellars and their wine clubs &mdash; and the tables where you can drink what they make.",None,None),
 ("The Chefs","Partners worldwide","The chefs who cook at Talon and the restaurants they run the rest of the year, from island kitchens to city dining rooms.",None,None),
]
# A guide that is written links from photograph, heading and line alike; one
# still to come is the same card without anchors, so nothing leads nowhere.
fw=''.join(
  f'''<article class="card">
        <{f'a class="shot" href="{lk}"' if lk else 'div class="shot"'}>{card_img(f,t,"Photo &middot; "+t)}</{'a' if lk else 'div'}>
        <h3>{f'<a class="plain" href="{lk}">{t}</a>' if lk else t}</h3>
        <p class="where">{loc}</p><p class="blurb">{b}</p>
        {f'<a class="cta" href="{lk}">Read the guide</a>' if lk
          else '<span class="cta soon">Coming soon</span>'}
      </article>''' for t,loc,b,f,lk in FW)

def res_plate(title, where):
    return ('<div class="plate"><p class="nm">' + title + '</p><hr>'
            '<p class="loc">' + where.replace('&mdash;', '&middot;') + '</p></div>')

if EXPORT.get('resort'):
    RES = [(esc(r.get('title')), esc(r.get('where')), esc(r.get('blurb'))) for r in EXPORT['resort']]
    RES_IMG  = {n: (r.get('imageFile') or '') for n, r in enumerate(EXPORT['resort']) if story_img(r)}
    RES_SRC  = {n: story_img(r) for n, r in enumerate(EXPORT['resort']) if story_img(r)}
    RES_LINK_X = {n: (r.get('link') or '') for n, r in enumerate(EXPORT['resort'])}
else:
    RES_SRC, RES_LINK_X = {}, None

RES_IMG  = RES_IMG if EXPORT.get('resort') else {0:'res-talon.jpg', 1:'res-castle.jpg',
                                                 2:'res-postranch.jpg', 3:'res-wailea.jpg',
                                                 4:'res-clayoquot.jpg'}
# the cinematic page, which is what dist/ serves; the earlier article layout
# at 5911cc64 is superseded and the homepage should not still point at it
TALON     = 'https://claude.ai/code/artifact/afd0fd6e-5e0f-4c9d-ae28-2a7a82953f5e'
POSTRANCH = 'https://claude.ai/code/artifact/c3c2f776-936f-4ce3-87cb-d5fbef19c331'
CASTLE    = 'https://claude.ai/code/artifact/3ad1ebcd-5d1d-4178-b3b6-8a3c712fc27e'
WAILEA    = 'https://claude.ai/code/artifact/216078f7-d048-49a8-8e55-b6b1f60125b4'
CLAYOQUOT = 'https://claude.ai/code/artifact/56ef0af2-1727-4fed-8e46-eb4de1e260aa'
RES_LINK = RES_LINK_X if RES_LINK_X else {0: TALON, 1: CASTLE, 2: POSTRANCH,
                                          3: WAILEA, 4: CLAYOQUOT}

# The call to action names the property, so it survives a reorder in the panel.
def res_cta(title):
    t = re.sub(r'\s*(&amp;|&)\s*Spa$', '', title).strip()
    return 'Discover ' + (t or 'Resort')

RES_CTA  = {n: res_cta(t) for n, (t, _s, _b) in enumerate(RES)}
# The whole site exists to feed Talon, so Talon is the card the rail opens on -
# centred, not first. Marked by name rather than by position, because the
# control panel is free to reorder the resorts.
def anchored(title):
    return ' data-anchor' if 'Talon' in title else ''

res=''.join(
  f'''<article class="card"{anchored(t)}>
        <a class="shot" href="{RES_LINK.get(n,'#')}">{f'<img src="{RES_SRC.get(n) or uri(RES_IMG[n])}" alt="{t}" loading="lazy">' if n in RES_IMG else res_plate(t, s)}</a>
        <h3><a class="plain" href="{RES_LINK.get(n,'#')}">{t}</a></h3>
        <p class="where">{s}</p><p class="blurb">{b}</p>
        <a class="cta" href="{RES_LINK.get(n,'#')}">{RES_CTA.get(n,'Discover Resort')}</a>
      </article>''' for n,(t,s,b) in enumerate(RES))

if EXPORT.get('experience'):
    EXP = [(esc(r.get('title')), esc(r.get('blurb')), r.get('imageFile') or None,
            r.get('link') or '') for r in EXPORT['experience']]
else:
    EXP = [(t, b, f, '') for t, b, f in EXP]
if EXPORT.get('food'):
    FW = [(esc(r.get('title')), esc(r.get('where')), esc(r.get('blurb')),
           r.get('imageFile') or None, r.get('link') or None) for r in EXPORT['food']]
if EXPORT.get('pub'):
    PUBS = [(esc(r.get('title')), esc(r.get('where')), r.get('pages') or 0,
             r.get('imageFile') or '', r.get('link') or '#') for r in EXPORT['pub']]
# A hashtag with a page of its own is clickable throughout; one still being
# gathered shows the same card with the call to action greyed out.
exp=''.join(
  f'''<article class="card">
        <div class="shot">{f'<a href="{u}">{card_img(f,t,"Photo &middot; "+t)}</a>' if u
                            else card_img(f,t,"Photo &middot; "+t)}</div>
        <h3>{f'<a class="plain" href="{u}">{t}</a>' if u else t}</h3><p class="blurb">{b}</p>
        {f'<a class="cta" href="{u}">Experience For Yourself</a>' if u
          else '<span class="cta soon">Gathering now</span>'}
      </article>''' for t,b,f,u in EXP)

# Publications, from the e-pubz platform. Slug and client come straight out of
# the prototype's data; the URL is what pubUrl() builds for the Travel industry.
PUBS=[
 ("Alaska Fishing Lodge eBrochure","Talon Lodge &amp; Spa",24,
  "pub-fishing-lodge.jpg","https://travelpubz.com/talon-lodge/alaska-fishing-lodge"),
 ("Guest Welcome Brochure","Talon Lodge &amp; Spa",16,
  "pub-guest-welcome.jpg","https://travelpubz.com/talon-lodge/guest-welcome-brochure"),
 ("Magnus Adventures &mdash; Trip Catalog","Magnus Adventures",28,
  "pub-trip-catalog.jpg","https://travelpubz.com/magnus-adventures/trip-catalog"),
 ("Visit Sitka Magazine 2022&ndash;2023","Visit Sitka",48,
  "pub-visit-sitka.jpg","https://travelpubz.com/visit-sitka/visit-sitka-2022-2023"),
 ("Ultimate Guide to Wild Alaska Salmon","Wild Alaska Seafood",32,
  "pub-salmon-guide.jpg","https://foodpubz.com/wild-alaska-seafood/ultimate-guide-wild-alaska-salmon"),
]
pubs_html=''.join(
  f"""<a class="pub" href="{u}">
        <div class="cover"><img src="{uri(f)}" alt="Cover of {t.replace('&mdash;','-').replace('&ndash;','-')}" loading="lazy">
          <div class="plate"><h3>{t}</h3><p class="by">{by}</p></div>
        </div>
        <div class="spine"><span class="pages">{n} pages</span><span class="go">Read &rsaquo;</span></div>
      </a>""" for t,by,n,f,u in PUBS)

WALL_IMGS = ['ig-1.jpg','ig-2.jpg','ig-3.jpg',
             'wall-plated-salmon.jpg','wall-deck-firepit-sunset.jpg','wall-bald-eagle.jpg',
             'wall-wine-pour.jpg','wall-two-anglers.jpg','wall-float-plane-mountains.jpg']
ig=''.join(f'<img src="{uri(n)}" alt="" loading="lazy">' for n in WALL_IMGS)

HTML=open(os.path.join(SP,'template.html'),encoding='utf-8').read()
HERO_VIDEO=('https://res.cloudinary.com/magnusadventures/video/upload/'
            'v1570549469/Magnus_Vignette_Cut04_xnxdlt_2_vkmxqw.mp4')

# Cloudinary can serve a frame of the film as a full-size JPEG; so_3 is three
# seconds in.  Used as the poster where it loads, ignored where it does not.
HERO_POSTER=('https://res.cloudinary.com/magnusadventures/video/upload/so_3/'
             'v1570549469/Magnus_Vignette_Cut04_xnxdlt_2_vkmxqw.jpg')

HTML=(HTML.replace('__HEROVIDEO__',HERO_VIDEO)
          .replace('__HEROPOSTER__',HERO_POSTER)
          .replace('__HERO__',uri('hero.jpg'))
          .replace('__TALON__',TALON).replace('__POSTRANCH__',POSTRANCH).replace('__CASTLE__',CASTLE).replace('__WAILEA__',WAILEA).replace('__CLAYOQUOT__',CLAYOQUOT).replace('__GRIFFIN__',uri('magnus-griffin.png')).replace('__ADV__',adv).replace('__RES__',res)
          .replace('__EXP__',exp).replace('__FW__',fw).replace('__PUBS__',pubs_html).replace('__IG__',ig))
open(os.path.join(SP,'magnus-home.html'),'w',encoding='utf-8').write(HTML)
print('built magnus-home.html  %.0f KB'%(len(HTML)/1024))
