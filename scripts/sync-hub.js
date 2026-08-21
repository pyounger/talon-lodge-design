// Re-embed every prototype tool into test-hub.html and keep the app catalog in sync.
// The hub bundles each tool as a base64 <script id="src-<id>"> blob; this refreshes
// them all from their current source files and adds any new tool below.
// Run from anywhere:  node talon-lodge-design/scripts/sync-hub.js
const fs = require('fs');
const path = require('path');
const DIR = path.resolve(__dirname, '..');            // talon-lodge-design/
const HUB = path.join(DIR, 'test-hub.html');

// id -> source file. Keep in sync with the inline TOOLS list in test-hub.html.
const MAP = {
  team:'team-admin.html', activities:'activities-admin.html', menu:'menu-admin.html',
  beverages:'beverage-admin.html', cocktails:'cocktail-admin.html', massagemenu:'massage-menu.html',
  fishtypes:'fish-types.html', packages:'packages-admin.html', settings:'settings-admin.html',
  vendors:'vendors-admin.html', access:'access-admin.html', scheduling:'scheduling-demo.html',
  approvals:'approvals.html', massagesched:'massage-schedule.html', boats:'boat-assignments.html',
  rooms:'room-assignments.html', flights:'flight-info.html', meals:'meal-orders.html',
  fishproc:'fish-processing.html', photos:'guest-photos.html', guestlist:'package-guest-list.html',
  daily:'daily-report.html', display:'daily-display.html', sigdisp:'signature-display.html',
  booking:'booking-engine.html', portal:'guest-portal.html', testdata:'test-data.html',
  guide:'test-guide.html'
};

const enc = f => Buffer.from(fs.readFileSync(path.join(DIR, f), 'utf8'), 'utf8').toString('base64');

const missing = Object.values(MAP).filter(f => !fs.existsSync(path.join(DIR, f)));
if (missing.length) { console.error('MISSING FILES:', missing); process.exit(1); }

let hub = fs.readFileSync(HUB, 'utf8');

// 1. register the new tool in the inline TOOLS catalog (after "photos")
const photosTool = '{"id":"photos","label":"Guest photos","desc":"Photo per guest for recognition (phone/iPad)","group":"Operate"}';
if (hub.indexOf('"id":"guestlist"') < 0) {
  if (hub.indexOf(photosTool) < 0) { console.error('Could not find the photos TOOLS entry to anchor to.'); process.exit(1); }
  hub = hub.replace(photosTool, photosTool + ',{"id":"guestlist","label":"Package Guest List","desc":"View/edit/add guests per package · repeat-guest badge","group":"Operate"}');
}

// 2. grant it to the Front desk role by default (admin/manager already get '*')
hub = hub.replace(
  '"frontdesk","name":"Front desk","apps":["photos","rooms","flights","daily","booking","portal","approvals","scheduling"]',
  '"frontdesk","name":"Front desk","apps":["photos","guestlist","rooms","flights","daily","booking","portal","approvals","scheduling"]'
);

// 3. re-embed every tool's source (refresh), inserting the new blob if absent
let refreshed = 0, inserted = 0;
Object.keys(MAP).forEach(id => {
  const tag = '<script type="text/plain" id="src-' + id + '">' + enc(MAP[id]) + '</' + 'script>';
  const re = new RegExp('<script[^>]*id="src-' + id + '"[^>]*>[\\s\\S]*?<\\/script>');
  if (re.test(hub)) { hub = hub.replace(re, tag); refreshed++; }
  else if (id === 'guestlist') {
    const reP = /<script[^>]*id="src-photos"[^>]*>[\s\S]*?<\/script>/;
    hub = hub.replace(reP, m => m + '\n' + tag); inserted++;
  } else { console.warn('  no src blob for', id, '(skipped)'); }
});

fs.writeFileSync(HUB, hub, 'utf8');
console.log('test-hub.html rebuilt · ' + (hub.length / 1024).toFixed(0) + ' KB · ' + refreshed + ' refreshed, ' + inserted + ' inserted');
