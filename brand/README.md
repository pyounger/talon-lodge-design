# Brand assets — drop zone

Put raw brand materials here and tell Claude the filename. From these, we build the
canonical token set, a living `style-guide.html`, and the Angular theme.

## 1. Logo  → save files in `brand/logo/`
- **Format:** SVG preferred (scales cleanly). Otherwise high-res PNG with a transparent background.
- **Variants (as many as you have):**
  - Primary / horizontal
  - Stacked (logo above wordmark)
  - Icon / mark only (for app icons, favicons)
  - Reversed / white version (for dark backgrounds)
- If you only have one version, that's fine — send it and we work from there.

## 2. Colors  → list hex codes below (or let Claude pull them from the logo)
- **Primary / brand:** `#______`
- **Secondary:** `#______`
- **Accent** (CTAs, highlights): `#______`
- **Dark neutral** (text): `#______`
- **Light neutral** (page background): `#______`
- **Semantic** — success `#______` · warning `#______` · error `#______`
- Don't have these? Send the logo and Claude drafts a full palette from it.

## 3. Typography
- **Headings font:** ____________
- **Body font:** ____________
- **Numbers/mono (optional):** ____________
- **Source:** Google Fonts (free/web-safe) OR licensed — if licensed, drop the font
  files (`.woff2` / `.ttf`) in `brand/fonts/`.

## 4. Buttons & shape
- **Corners:** sharp □ · slightly rounded ▢ · fully pill ⬭
- **Primary button:** solid fill / outline / with shadow?
- Undecided? Claude will show 2–3 options to pick from.

## 5. Nice-to-have (sets the "feel")
- **Photography style:** a sentence, or 2–3 sample images in `brand/imagery/`
- **Icon style:** line / solid / rounded
- **Voice & tone:** a sentence (e.g. "warm, precise, understated luxury")

---
**Fastest start:** just add the **logo** + any **brand colors** you already have, tell
Claude the filenames, and a full first-draft style guide comes back for you to refine.
