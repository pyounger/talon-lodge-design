# talonlodge.com — Performance Audit

Findings and a prioritised remediation plan for the **public marketing site**
(`pyounger/talonlodge`), with the constraint that the existing design is preserved.
Every recommendation below is a *delivery* change: markup, layout, typography and
imagery come out visually identical unless explicitly flagged otherwise.

This is an audit. It proposes; nothing here has been implemented.

---

## 0. Scope, method, and what could not be verified

**Audited:** the `pyounger/talonlodge` repository at commit `94c8bf6c` ("Update banners.php"),
last pushed **2022-08-17**. 35,212 files, 12 GB — a full FTP dump of the cPanel document root
(`/home2/talonlod/public_html/`).

**Method:** static analysis of the tree. All file sizes, counts and averages below were measured
directly from the repository and are reproducible with the commands in Appendix A.

**Two limits on confidence, stated up front:**

1. **The snapshot may be stale.** The repo is three years behind. If the live server has been
   patched, re-themed, or had its PHP version raised since August 2022, some findings will be
   out of date. Everything below should be re-confirmed against production before work starts.
2. **The live site could not be reached.** Network policy in the audit environment blocks
   `talonlodge.com`, so no real-world waterfall, Lighthouse run, or Core Web Vitals field data
   informs this document. Transfer-size figures marked *(est.)* are inferred from measured file
   sizes plus typical compression ratios — they are estimates, not measurements.

What this means practically: the *causes* identified here are real and evidenced in the code.
The *magnitudes* need one Lighthouse run against production to firm up.

---

## 1. Findings at a glance

Ordered by payoff against effort. "Design risk" is the chance the change is visible to a visitor.

| # | Finding | Evidence | Est. saving | Effort | Design risk |
|---|---------|----------|-------------|--------|-------------|
| 1 | JPEG quality set to **100** | `app/config/galleries.php:75` | ~75% of image bytes | Low | None |
| 2 | No `mod_deflate` — HTML/CSS uncompressed | `.htaccess` (absent) | ~60 KB/page | Low | None |
| 3 | No `mod_expires` — no cache policy on images | `.htaccess` (absent) | Repeat visits | Low | None |
| 4 | No WebP/AVIF anywhere (0 of ~5,000 images) | format census | 30–50% on top of #1 | Medium | None |
| 5 | `index_old.php` loaded as a `<script>` | `index.php:10` | 1 blocking request | Low | None |
| 6 | Dead Google Analytics `ga.js` | `frontend.tpl` | 1 request, ~17 KB | Low | None |
| 7 | Two render-blocking gallery scripts, absolute `http://` | `frontend.tpl:20-21` | Unblocks render | Low | None |
| 8 | jQuery UI 1.8.17 full build for a datepicker | `assets.php` | ~40 KB gz | Medium | None |
| 9 | 302 (not 301) non-www redirect, chained | `.htaccess` | 1 hop | Low | None |
| 10 | Font Awesome from retired MaxCDN | `frontend.tpl:15` | Possible hang | Low | None |
| 11 | PHP 5.4 (EOL 2015) | `.htaccess:3` | Throughput | High | None |
| 12 | 273 MB of Flash, 310 MB of image masters public | `static/flash/`, `uploads/` | Server only | Low | None |

---

## 2. Images — the dominant cost

### 2.1 The resize pipeline works; the quality setting does not

Credit where it is due: the site has a **real, granular derivative pipeline**. Images are
resized to purpose-built dimensions, not scaled down in the browser:

| Variant | Count | Total | Average |
|---------|-------|-------|---------|
| `-orig` (masters) | 575 | 310.4 MB | 553 KB |
| `-799-495` | 463 | **166.1 MB** | **367 KB** |
| `-1245-612` | 108 | 15.8 MB | 150 KB |
| `-309-179` | 202 | 10.2 MB | 52 KB |
| `-225-128` | 272 | 7.7 MB | 29 KB |
| `-129-84` | 575 | 7.0 MB | 13 KB |

The problem is the encoder setting, in one line:

```php
// app/config/galleries.php:75
$CPF_CONFIG['APP']['PHOTOS']['JPEG_QUALITY'] = 100;
```

Reinforced by three defaults in `app/utils/image.php`:

```php
public static function resize_image($file_in, $file_out, $width, $height, $jpeg_quality = 100, ...)   // :34
public static function crop($file_in, $file_out, $crop_width, $crop_height, $x, $y, $w, $h, $jpeg_quality = 100)  // :118
imagejpeg($result, $from, 100);   // :168 — hardcoded
```

**JPEG quality 100 is the single worst available setting.** It disables essentially all
quantisation, producing files 4–5× larger than quality 78 with no perceptible difference —
the extra bytes encode sensor noise, not detail.

The `-799-495` figure is the proof: **367 KB average for an 799×495 image**. A well-encoded
JPEG at that size is 60–90 KB. Those 463 files should total roughly 35 MB, not 166 MB.

### 2.2 Recommendation

1. **Change the setting** to `78` (quality 75–82 is the standard band; 78 is a safe default).
   One line. Affects all newly generated derivatives.
2. **Batch re-encode existing derivatives** from the retained `-orig` masters. The masters are
   all present, so this is lossless in practice — derivatives are regenerated from source rather
   than re-compressed from already-compressed files.
3. **Add WebP/AVIF** with `<picture>` and a JPEG fallback. A further 30–50% on top of step 1.
   This one touches markup, but only to wrap existing `<img>` tags — rendered output is identical.

Steps 1 and 2 alone should cut image bytes by roughly three quarters. On a gallery page showing
a dozen `-799-495` images, that is approximately 4.4 MB → 1.0 MB *(est.)*.

Note: no image tooling (ImageMagick, PIL, cwebp, avifenc) was available in the audit environment,
so the re-encode has not been trial-run. The estimate rests on standard JPEG quality/size curves
and should be validated on a sample of 20 images before committing to a batch run.

### 2.3 Format census

Across the served tree: **0 WebP, 0 AVIF.**

| Directory | JPEG | PNG | GIF | SVG | WebP | AVIF |
|-----------|------|-----|-----|-----|------|------|
| `uploads/` | 4,536 | 16 | 2 | 0 | 0 | 0 |
| `static/` | 64 | 280 | 40 | 2 | 0 | 0 |

Individual files in the served tree reach 9.3 MB (`alaskafishinglodge/Uploads/Photos/Talon Lodge
Photo-74.jpg`), 6.1 MB, 5.0 MB. These sit in publicly reachable directories. Whether any page
links them directly needs checking against production; either way they should not be served raw.

---

## 3. Server configuration

### 3.1 No compression for HTML or out-of-bundle CSS

`.htaccess` contains **no `mod_deflate` block**. The asset bundle is gzipped by `gzipit.php`,
but everything outside it is served raw:

- `complete-responsive.css` — **57 KB**, loaded on every page, uncompressed (~10 KB gzipped)
- `static/css/frontend/gallery/gallery-view.css` — same
- All HTML output from the PHP application

A single `<IfModule mod_deflate.c>` block covering `text/html`, `text/css`, `application/javascript`
and `image/svg+xml` is a few lines and risks nothing.

### 3.2 No cache policy on images or static files

No `mod_expires` block and no `Cache-Control` headers. Apache will still send `Last-Modified`,
so browsers revalidate rather than re-download — but that is a round trip per image per visit
that a proper `Expires` header eliminates entirely.

`gzipit.php` already demonstrates the right pattern for bundled assets (`CP_HEADER_EXPIRES_VALUE`
= 2037, plus ETag). Images deserve the same, keyed off their immutable filenames.

### 3.3 Redirect chain

Three issues in `.htaccess`:

```apache
RewriteCond %{HTTP_HOST} !^www.(.*)$
RewriteRule (.*) http://www.%{HTTP_HOST}%{REQUEST_URI} [R,L]
```

1. **`[R]` is a 302**, not a 301. Search engines treat it as temporary and browsers do not cache it,
   so the hop is paid on every visit. Should be `[R=301,L]`.
2. **The target is `http://`.** On an HTTPS site this forces `https → http → https`, adding a full
   round trip and briefly dropping the connection to plaintext.
3. A separate trailing-slash rule adds another 301.

Worst case a visitor pays three redirects before the first byte of HTML. Consolidating to a single
301 straight to the canonical `https://www.` origin removes two.

Every hardcoded URL in the templates is also `http://` — see §4.3.

### 3.4 PHP 5.4

```apache
# .htaccess:1-3
# Use PHP5.4 as default
AddHandler application/x-httpd-phpbeta .php
```

PHP 5.4 reached end of life in **September 2015** — no security patches for a decade. PHP 8.x is
routinely 2–3× faster on the same code.

This is flagged as high effort and is **not** part of the quick-win set. A custom 2011-era
framework (CPF + Smarty + Outlet ORM) will not run unmodified on PHP 8 — it will need a
compatibility pass. Worth planning; not worth blocking the image work on.

The `.htaccess.php-upgrade-backup` file suggests an upgrade was attempted at some point. Whoever
administers the server should confirm what version actually runs today.

---

## 4. Dead weight on every page load

### 4.1 The homepage loads an IP logger as JavaScript

```php
// index.php
require_once('cpf/boot.php');
?>
<script type="text/javascript" src="./index_old.php"></script>
```

`index_old.php` is not JavaScript. It is a PHP script that opens `htaccess.log`, appends the
visitor's IP, server address, host, user agent and timestamp, and closes it — then emits an empty
HTML document, which the browser tries to parse as JS and discards.

Every page view pays a blocking request and a file-append for a log nobody reads. Delete the
script tag. (See §7 — this file is also worth a second look for other reasons.)

### 4.2 Analytics that stopped working years ago

```js
_gaq.push(['_setAccount', 'UA-3585651-1']);
ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
```

This is **`ga.js`**, the *classic* Analytics library — two generations obsolete (classic →
Universal → GA4). Universal Analytics properties stopped processing data in **July 2023**, and
`UA-` property IDs are inert.

So the site currently collects **no analytics at all** while still paying for the request. Either
migrate to GA4 or remove it — but be aware that if anyone is still reading Analytics reports for
this site, they are reading nothing.

### 4.3 Render-blocking third-party and cross-origin scripts

From `frontend.tpl`, all in `<head>`, all blocking:

```html
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.5.0/css/font-awesome.min.css">
<script src="http://www.talonlodge.com/static/javascript/frontend/fancygallery/galleryjquery.js"></script>
<script src="http://www.talonlodge.com/static/javascript/frontend/fancygallery/galleryfancy.js"></script>
```

Three problems:

- **MaxCDN/BootstrapCDN has been retired.** A stylesheet from a dead host blocks rendering until
  it fails or times out. Self-host Font Awesome, or subset it — a lodge site uses perhaps a dozen
  glyphs out of 600+.
- **The gallery scripts use absolute `http://` URLs to the site's own origin.** On an HTTPS site
  browsers block these as mixed content, which means the fancy gallery may already be broken in
  production. They are also fetched as a separate origin rather than as relative paths, defeating
  connection reuse. Make them relative and fold them into the bundle.
- Both load on **every page**, not just gallery pages.

A **Zopim live chat** widget (`app/templates/includes/frontend.chat.tpl`) also loads site-wide.
It is async, so lower priority — but Zendesk has retired the classic Zopim widget, so this is
worth confirming it still functions.

### 4.4 A dev hostname in the production layout

`frontend.tpl` references `http://www.dev.talonlodge.com` (currently commented out, but present).
Dev hosts should not appear in production templates at all.

---

## 5. Front-end bundle

The bundle is **better than it looks**. `gzipit.php` concatenates, minifies (`CP_CSSMIN` and
`CP_JSMIN` are both `true`), gzips at level 9, and sets ETag plus a 2037 `Expires`. It is a
2011-vintage tool doing PHP work per request where a build step and static files would be
cheaper, but it is doing the right things.

Measured raw sizes from `app/config/assets/assets.php`:

| Bundle | Files | Raw | Est. transfer (min+gzip) |
|--------|-------|-----|--------------------------|
| `css-frontend` | 27 | 121 KB | ~22 KB *(est.)* |
| `js-frontend` | 17 | **453 KB** | ~135 KB *(est.)* |

### 5.1 jQuery UI is 46% of the JavaScript and is used for one widget

```
210,895 bytes   frontend/jquery/jquery-ui-1.8.17.custom.min.js
```

Scanning `app.js`, `init.js` and the layout for jQuery UI API calls returns exactly one widget:
`datepicker`, at 8 call sites. No dialog, tabs, accordion, autocomplete, sortable, or draggable.

A datepicker-only jQuery UI build is roughly 30–40 KB — **saving ~170 KB raw, ~40 KB gzipped**,
with pixel-identical output. This is the largest single JS win and carries no design risk, because
a custom build of the same library version renders the same markup.

### 5.2 Unminified jQuery in the bundle

The manifest references `frontend/jquery/jquery-1.6.1.js` — the **unminified** 91 KB source.
Minification at the bundle level partly compensates, but shipping the minified build is free.

Note also that **two jQuery versions** exist in the tree (1.6.1 on the frontend, 1.7.1 on the
backend). Both are from 2011.

### 5.3 Flash remnants

`jquery.swfobject.js` ships in the frontend bundle, and `app/templates/controls/frontend_banner.tpl`
still branches on `$ban->extension == 'swf'` to inject a Flash object. **Flash has been dead since
December 2020** — that code path can only fail. Removing it also removes a dependency.

### 5.4 Smaller items

- **Layout tables.** `main-page.tpl` builds the page with `<table class="table table-bordered
  table-striped">`. Bootstrap classes on table-based layout. It works, and rewriting it to grid
  is a genuine redesign risk — **left alone deliberately**, noted for completeness.
- **`maximum-scale=1`** in the viewport meta blocks pinch-zoom. An accessibility problem, and
  ignored by modern iOS anyway. Removing it changes nothing visually.
- **XHTML 1.0 Transitional doctype** — legacy parsing mode. Low impact; changing it is a
  regression-test job, not a quick win.
- **Manual cache-busting.** `$CPF_CONFIG['APP']['ASSETS']['VERSION'] = 42` must be bumped by hand.
  Forget, and visitors keep stale CSS. A content hash would be self-maintaining.

---

## 6. Repository and server hygiene

Not visitor-facing, but it makes every deploy, backup and clone slower, and it is why the
repository is 12 GB.

| Path | Size | What it is |
|------|------|-----------|
| `dev/` | 3.5 GB | A second full copy of the site |
| `profiles/` | 2.4 GB | Guest profile images |
| `uploads/` | 931 MB | Live uploads (incl. 310 MB of masters) |
| `profiles_old_bk/` | 682 MB | Backup copy of the above |
| `static/flash/` | 273 MB | Flash video — dead since 2020 |
| `final/` | 129 MB | Another copy |
| `blog/` | 115 MB | WordPress |
| `wordpress/` | 38 MB | A *second* WordPress |
| `error_log` | 9.2 MB | Committed error log |

`static/flash/` holds 26 files of `.f4v` video, plus `.f4vx` and `.f4vxx` duplicates — someone
renamed extensions to disable them rather than deleting. `sportsfishing.f4v` and `.f4vx` are
33.1 MB and 32.9 MB: the same video twice.

There are also **seven `.htaccess` variants** in the document root (`.bak.1397241211`,
`.bak.1399378286`, `.bak.1452202072`, `.php-upgrade-backup`, `.htaccessA`, `htaccessB`). Only one
is live. The rest are confusing at best.

**Recommendation:** these are *server* directories that should never have been in version control.
Archive them off-server, then add a `.gitignore`. Removing them from git history is a separate,
more disruptive job — worth doing, but not first.

---

## 7. Security observations

Outside the performance brief, but found during the audit and too material to leave unsaid.
**Recommendation: have whoever administers the server review these.** None of them block the
performance work.

1. **Probable historical SEO-spam injection.** The commented-out redirects in `.htaccess` target
   URLs like `/MOKOZ/team-talon-positions/`, `/UmWVZ/`, `/NeUYZ/`, `/VYfWZ/`, `/XoXPZ/NKTVZ/` —
   random five-character paths under the site root. That naming is the signature of injected spam
   pages. Someone appears to have cleaned up by adding redirects. Whether the entry point was ever
   found is a separate question.
2. **The IP logger.** `index_old.php` (§4.1) writes visitor IPs and user agents to a flat file on
   every page load, wired in via a `<script>` tag. That is not a normal analytics pattern.
3. **PHP 5.4** — a decade without security patches (§3.4).
4. **Public masters.** 310 MB of full-resolution originals sit in a web-reachable directory.
5. **Committed error log.** `error_log` (9.2 MB) exposes absolute server paths
   (`/home2/talonlod/public_html/...`) and stack traces in a repository.

---

## 8. Recommended sequence

Grouped so each stage is independently reviewable, independently revertible, and ordered so the
cheapest wins land first.

### Stage 1 — Configuration (hours; no markup touched)
- `JPEG_QUALITY` 100 → 78, plus the three defaults in `app/utils/image.php`
- Add `mod_deflate` for HTML, CSS, JS, SVG
- Add `mod_expires` for images, fonts and static assets
- Non-www redirect: `[R]` → `[R=301]`, target `https://`

### Stage 2 — Remove dead weight (hours; nothing visible changes)
- Delete the `index_old.php` script tag
- Remove or replace `ga.js`
- Self-host and subset Font Awesome
- Make the gallery scripts relative, move them into the bundle, load only where used
- Remove the Flash branch from the banner control and drop `jquery.swfobject.js`
- Remove `maximum-scale=1`

### Stage 3 — Image re-encode (days; batch job)
- Validate quality 78 on a 20-image sample
- Batch regenerate all derivatives from `-orig` masters
- Add WebP/AVIF with `<picture>` and JPEG fallback

### Stage 4 — Bundle (days; needs regression testing)
- Replace full jQuery UI with a datepicker-only build
- Point the manifest at minified jQuery
- Consider a content hash for cache-busting

### Stage 5 — Separate projects (weeks; plan, don't rush)
- PHP 5.4 → 8.x compatibility pass
- Server and repository cleanup
- Security review

Stages 1 and 2 are a day's work between them and should deliver most of the perceived speed-up.
Stage 3 delivers the bulk of the byte reduction.

---

## 9. Before any of this starts

1. **Confirm the snapshot.** Diff `pyounger/talonlodge` against the live document root. Three
   years is long enough for this audit to be describing a site that no longer exists.
2. **Run Lighthouse against production**, mobile and desktop, on the homepage, a gallery page and
   the reservation page. That converts the *(est.)* figures here into measurements and gives a
   baseline to prove improvement against.
3. **Confirm the PHP version actually running**, which may differ from what `.htaccess` declares.
4. **Confirm HTTPS**, which determines whether §3.3 and §4.3 are live bugs or latent ones.
5. **Check whether the fancy gallery currently works.** If it is mixed-content blocked, that is a
   functional bug this audit found incidentally.

---

## Appendix A — Reproducing the measurements

```bash
# Image variant sizes (§2.1)
cd uploads/photos/frontend
for v in orig 1245-612 799-495 309-179 225-128 129-84; do
  find . -name "*-$v.jpg" -printf "%s\n" \
    | awk -v v="$v" '{t+=$1;n++} END {if(n)printf "%-10s n=%-4d %6.1f MB  avg=%5.0f KB\n", v, n, t/1048576, t/n/1024}'
done

# Format census (§2.3)
find uploads static -type f -iregex '.*\.\(jpg\|jpeg\|png\|gif\|webp\|avif\|svg\)$' \
  | sed 's/.*\.//' | tr 'A-Z' 'a-z' | sort | uniq -c | sort -rn

# Bundle sizes (§5) — file lists come from app/config/assets/assets.php
# Directory weights (§6)
du -sh */ | sort -rh
```

---

*Audit performed against `pyounger/talonlodge` @ `94c8bf6c`. Figures marked (est.) are inferred
from measured file sizes, not observed in production.*
