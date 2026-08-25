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
  guide:'test-guide.html', islandops:'island-ops.html'
};

// Tools that may not be in the hub yet. Each says which existing tool to slot in after,
// plus its catalog entry. Once the hub has the tool these are no-ops, so entries can stay
// here permanently — add a line here whenever you add a prototype to MAP above.
const NEW = {
  guestlist: {after: 'photos',    label: 'Package Guest List', desc: 'View/edit/add guests per package · repeat-guest badge', group: 'Operate'},
  islandops: {after: 'guestlist', label: 'Island Ops',         desc: 'Inventory, set-up & shutdown lists, project notes',     group: 'Operate'}
};

const enc = f => Buffer.from(fs.readFileSync(path.join(DIR, f), 'utf8'), 'utf8').toString('base64');

const missing = Object.values(MAP).filter(f => !fs.existsSync(path.join(DIR, f)));
if (missing.length) { console.error('MISSING FILES:', missing); process.exit(1); }

let hub = fs.readFileSync(HUB, 'utf8');

// 1. register any not-yet-known tool in the inline TOOLS catalog, after its anchor tool
Object.keys(NEW).forEach(id => {
  if (hub.indexOf('"id":"' + id + '"') >= 0) return;              // already in the catalog
  const m = NEW[id];
  const anchor = hub.match(new RegExp('\\{"id":"' + m.after + '"[^}]*\\}'));
  if (!anchor) { console.error('Could not find the "' + m.after + '" TOOLS entry to anchor "' + id + '" to.'); process.exit(1); }
  hub = hub.replace(anchor[0], anchor[0] + ',' + JSON.stringify({id, label: m.label, desc: m.desc, group: m.group}));
  console.log('  + catalog entry for', id);
});

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
  else if (NEW[id]) {
    const reP = new RegExp('<script[^>]*id="src-' + NEW[id].after + '"[^>]*>[\\s\\S]*?<\\/script>');
    if (!reP.test(hub)) { console.error('No "' + NEW[id].after + '" src blob to anchor "' + id + '" to.'); process.exit(1); }
    hub = hub.replace(reP, m => m + '\n' + tag); inserted++;
    console.log('  + embedded', id);
  } else { console.warn('  no src blob for', id, '(skipped)'); }
});

fs.writeFileSync(HUB, hub, 'utf8');
console.log('test-hub.html rebuilt · ' + (hub.length / 1024).toFixed(0) + ' KB · ' + refreshed + ' refreshed, ' + inserted + ' inserted');
