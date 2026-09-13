/**
 * Pull hashtag candidates from Instagram into the Magnus curation queue.
 *
 * Runs on a schedule in Firebase Functions. The control panel cannot do this
 * itself: browsers are blocked from calling the Graph API cross-origin, and the
 * access token must never reach the browser.
 *
 * What this writes is a QUEUE, not the site. Nothing here appears on
 * magnusadventures.com until a person opens the panel, records permission from
 * the photographer and publishes it. That gate lives in the panel, not here.
 *
 * Before this runs you need, once:
 *   1. An Instagram account converted to Business or Creator, linked to a
 *      Facebook Page.
 *   2. A Meta app with instagram_basic and pages_read_engagement, reviewed.
 *   3. A long-lived Page access token, refreshed every 60 days.
 *   4. The numeric IG user id of the account making the query.
 *
 * Set them with:
 *   firebase functions:config:set ig.token="…" ig.user_id="…"
 */

const functions = require('firebase-functions');
const admin = require('firebase-admin');

if (!admin.apps.length) admin.initializeApp();
const db = admin.firestore();

const GRAPH = 'https://graph.facebook.com/v21.0';

/* Instagram allows 30 distinct hashtags per rolling 7 days per account, so keep
   this list short and change it rarely. Each name costs one of the 30. */
const HASHTAGS = [
  'talonlodge',
  'sitkaalaska',
  'magnusadventures',
];

/* recent_media returns only the last 24 hours, so this has to run daily or the
   window closes. top_media is a ranked slice with no time limit. */
const EDGE = 'recent_media';

async function graph(path, params) {
  const url = new URL(GRAPH + path);
  Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
  const res = await fetch(url);
  const body = await res.json();
  if (!res.ok || body.error) {
    throw new Error(`Instagram: ${body.error ? body.error.message : res.status}`);
  }
  return body;
}

async function hashtagId(name, token, userId) {
  /* Ids are stable, so cache them rather than spending a lookup each run. */
  const ref = db.doc(`instagram/hashtags/ids/${name}`);
  const seen = await ref.get();
  if (seen.exists) return seen.data().id;

  const found = await graph('/ig_hashtag_search', {
    user_id: userId, q: name, access_token: token,
  });
  if (!found.data || !found.data.length) throw new Error(`No hashtag "${name}"`);
  const id = found.data[0].id;
  await ref.set({ id, name, cachedAt: new Date().toISOString() });
  return id;
}

async function collect(name, token, userId) {
  const id = await hashtagId(name, token, userId);
  const page = await graph(`/${id}/${EDGE}`, {
    user_id: userId,
    fields: 'id,caption,media_type,media_url,permalink,timestamp',
    limit: 40,
    access_token: token,
  });
  return (page.data || []).filter(m => m.media_type !== 'VIDEO');
}

/**
 * One document per Instagram post, in a queue the panel reads.
 *
 * Note what is NOT here: the photographer's username. Instagram does not return
 * it for hashtag results, by design. Somebody has to open the permalink to see
 * whose picture it is — which is the same step as asking their permission, so it
 * costs nothing extra.
 */
async function queue(media, hashtag) {
  const ref = db.doc(`stories/ig-${media.id}`);
  if ((await ref.get()).exists) return false;   // already seen, or already judged

  await ref.set({
    id: `ig-${media.id}`,
    kind: 'social',
    title: (media.caption || '').split('\n')[0].slice(0, 80) || 'Untitled post',
    where: '',
    blurb: (media.caption || '').slice(0, 400),
    imageUrl: media.media_url,        // expires — see copyOnGrant below
    permalink: media.permalink,
    hashtag: '#' + hashtag,
    handle: '',                       // filled in by whoever asks permission
    rights: 'none',
    rightsAt: '',
    rightsNote: '',
    published: false,
    postedAt: media.timestamp,
    order: 9999,
    updatedAt: new Date().toISOString(),
  });
  return true;
}

exports.pullInstagramHashtags = functions
  .runWith({ timeoutSeconds: 120, memory: '256MB' })
  .pubsub.schedule('every day 06:15')
  .timeZone('America/Anchorage')
  .onRun(async () => {
    const cfg = functions.config().ig || {};
    if (!cfg.token || !cfg.user_id) {
      console.error('Instagram not configured — set ig.token and ig.user_id.');
      return null;
    }

    let added = 0;
    for (const name of HASHTAGS) {
      try {
        const media = await collect(name, cfg.token, cfg.user_id);
        for (const m of media) if (await queue(m, name)) added++;
      } catch (err) {
        /* One bad hashtag must not stop the others. */
        console.error(`Hashtag "${name}" failed: ${err.message}`);
      }
    }
    console.log(`Instagram: queued ${added} new candidate(s).`);
    return null;
  });

/**
 * Instagram's media_url is a signed CDN link that stops working within days.
 * Once permission is granted the picture has to become yours to serve, so copy
 * it into your own bucket. Triggered by the panel setting rights to "granted".
 */
exports.copyOnGrant = functions.firestore
  .document('stories/{id}')
  .onUpdate(async (change, ctx) => {
    const before = change.before.data(), after = change.after.data();
    if (after.kind !== 'social') return null;
    if (before.rights === 'granted' || after.rights !== 'granted') return null;
    if (!after.imageUrl || after.imageUrl.includes('storage.googleapis.com')) return null;

    const res = await fetch(after.imageUrl);
    if (!res.ok) { console.error(`Could not fetch ${ctx.params.id}`); return null; }
    const buf = Buffer.from(await res.arrayBuffer());

    const file = admin.storage().bucket().file(`social/${ctx.params.id}.jpg`);
    await file.save(buf, { contentType: 'image/jpeg' });
    await file.makePublic();

    return change.after.ref.update({
      imageUrl: file.publicUrl(),
      originalUrl: after.imageUrl,
      copiedAt: new Date().toISOString(),
    });
  });
