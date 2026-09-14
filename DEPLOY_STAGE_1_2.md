# Deploying stages 1 & 2 — talonlodge.com

Handover note for whoever pushes the site live. Covers the performance work on
`pyounger/talonlodge` branch `claude/perf-stage-1-config`: 14 changed files
covering image compression, HTTP caching, and moving the site onto the TLS
certificate it already had. No design, layout or copy changes.

Shareable version: https://claude.ai/code/artifact/d9370719-82e3-4e27-b9d8-d5b38e82a16c

Target: `/home2/talonlod/public_html/`

---

## Before you start

**`.htaccess` is a hidden file.** Most FTP clients don't show dotfiles until you
turn it on. It's the most important file in the batch — if it doesn't land, the
TLS fix doesn't happen.

**Transfer in binary mode.** The existing `.htaccess` terminates its older lines
with `CR CR LF`, an artifact of some past FTP client. ASCII-mode transfer will
rewrite those endings. Apache tolerates the file as it stands.

**Upload only these fourteen files.** Do not sync the whole repository over the
document root — it is a 12 GB snapshot from 2022 containing `dev/`, two
WordPress installs and several stale backups. Pushing all of it would overwrite
three years of uploads and guest photos.

---

## What's in the batch

**Server config**
- `.htaccess` — gzip compression, cache headers, TLS enforcement, and the
  trailing-slash rule no longer downgrading to `http`.

**Image quality**
- `app/config/galleries.php` — JPEG quality 100 → 82.
- `app/utils/image.php` — same change to three defaults the config doesn't reach.

**URL scheme**
- `cpf/boot.php` — generated URLs and `<base href>` follow the request scheme
  instead of being hardcoded to `http`.

**Templates** (absolute `http://` URLs repointed so they don't break or
downgrade under TLS)
- `app/templates/layouts/frontend.tpl`
- `app/templates/layouts/pages/frontend/privacy.tpl`
- `app/templates/controls/menu_custom/main_menu.tpl`
- `app/templates/includes/frontend.header.tpl`
- `app/templates/includes/frontend.footer.tpl`
- `app/templates/frontend_reservation.view.tpl`
- `app/templates/frontend_bluffhouse.view.tpl`
- `app/templates/frontend_brochure.default.tpl`
- `app/templates/mail/request.tpl`
- `app/templates/mail/admin_request.tpl`

---

## Deploying

Order matters: the templates must be in place before the redirect starts forcing
HTTPS, or the gallery breaks for as long as the gap lasts.

1. **Back up the current `.htaccess`.** This is the rollback path.
2. **Upload the thirteen PHP and template files** — everything except
   `.htaccess`. Safe on their own; the site is still on `http` and unchanged.
3. **Load the site and confirm nothing moved.** Homepage, a gallery page, the
   reservation page. If anything is off, stop — the redirect is untouched, so
   rolling back is just restoring the previous files.
4. **Upload `.htaccess`.** This is the risky step: it forces every visitor onto
   HTTPS. Test it the moment it lands. On a redirect loop or error, restore the
   backup immediately.
5. **Check in a private browser window** — an ordinary one may have the old
   redirect cached.

---

## Verifying

- [ ] Site loads over HTTPS with a padlock; `http://talonlodge.com` lands on
      `https://www.talonlodge.com`.
- [ ] No mixed-content warnings in the console on the homepage, a gallery page
      and the reservation page. *(Most likely failure — see below.)*
- [ ] The photo gallery opens and works. Its scripts were among the files
      repointed, so this is the best single test that the templates landed.
- [ ] `curl -I -H 'Accept-Encoding: gzip' https://www.talonlodge.com/` reports
      `Content-Encoding: gzip`.
- [ ] Any photo request carries an `Expires` header roughly a year out.
- [ ] Main navigation links stay on HTTPS — no bouncing via `http`.
- [ ] A newly uploaded photo is roughly a quarter the size of an older file at
      the same dimensions.

---

## If something goes wrong

Restoring the backed-up `.htaccess` undoes TLS enforcement, compression and
caching in one move. The other thirteen files are inert on their own.

**Caveat:** the redirect is a **301**, which browsers cache hard. Anyone already
redirected to HTTPS will keep going there after a rollback until their cache
clears. Not a reason to avoid the deploy — a reason to have someone watching
when it lands.

**Templates not updating.** Smarty has `COMPILE_CHECK` enabled and should
recompile automatically. If a page looks stale:

```
rm /home2/talonlod/public_html/tmp/*.file.*.php
```

They regenerate on the next request. Nothing else in `tmp/` needs touching.

**Mixed-content warnings that don't match any file here.** Every absolute
`http://` URL in the templates has been dealt with. Persistent warnings mean the
URLs are stored in the **database** — page content, gallery records, banner rows
— which no file in this batch touches. That's a content fix; report it back
rather than working around it.

---

## Not included

The existing photo library is untouched; the quality change affects only images
generated from here on. Re-encoding the ~166 MB of oversized derivatives already
on the server is Stage 3.

HSTS was deliberately left out. Worth adding once TLS has been stable for a week
or two, but difficult to unwind once browsers have cached it.
