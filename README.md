# Magic Hair Styler — AirStyler 5-in-1 landing page

A single-file, conversion-focused product landing page for the AirStyler 5-in-1 Magic Hair Styler. Vanilla HTML / CSS / JS, served by Nginx inside a small Alpine container. Built to deploy on Dokku (or any Docker host) in one `git push`.

## What's on the page

- Hero with headline, visible price (£49.99 vs £79.99), rating, primary Stripe CTA
- Trust strip (free worldwide shipping, 30-day returns, secure checkout, human support)
- Finish selector (White/Gold, Pink, Navy/Gold, Black) with live image + CTA label swap
- 5-in-1 feature grid, results gallery, technology grid, comparison table
- Testimonials with schema.org Review markup
- 10-item FAQ with `<details>` accordion and FAQPage structured data
- Final CTA, policies (`<details>` sections, indexable for SEO), dark footer
- Sticky mobile "Buy now" bar
- `robots.txt`, `sitemap.xml` (with image entries), Product/Organization/WebSite/FAQPage JSON-LD

## Project structure

```
.
├── index.html        # Complete landing page (inline CSS + JS)
├── nginx.conf        # gzip, long-cache static, security headers
├── Dockerfile        # Nginx:alpine container
├── robots.txt
├── sitemap.xml
├── images/           # WebP product + lifestyle imagery (~1.2 MB total)
├── .dockerignore
└── README.md
```

## Stripe

All four finish CTAs point at a single Stripe Payment Link:

```
https://buy.stripe.com/5kQ5kD97K1nM97dh0Ecs800
```

One payment link is deliberate — the four "finishes" are cosmetic and the customer's colour preference is captured at fulfilment. If you later create separate Stripe Payment Links per colour, either:

1. Set the per-colour URL on each `<button class="swatch">` via a `data-stripe` attribute, and update the `#shop-cta` `href` inside the click handler at the bottom of `index.html`, **or**
2. Use a single Stripe Checkout Session with a "colour" custom field (recommended — zero code to maintain).

## Updating the copy or imagery

All text, prices, swatches, reviews, FAQ and schema live in `index.html`. Images are in `images/` as WebP. The hero image is preloaded at the top of the file (`<link rel="preload" as="image" ...>`) — if you rename it, update that line too.

## Deploying on Dokku

```bash
# 1. On your Dokku host (once)
dokku apps:create magic-hair-styler
dokku domains:add magic-hair-styler magichairstyler.com
dokku letsencrypt:enable magic-hair-styler

# 2. From this repo (once)
git remote add dokku dokku@YOUR_VPS_IP:magic-hair-styler

# 3. Deploy
git push dokku main
```

Dokku detects the `Dockerfile`, builds the container, and runs it behind its own Nginx (our `nginx.conf` sits *inside* the container and is used by the nginx that serves the app).

### Subsequent updates

```bash
git add .
git commit -m "Update landing page"
git push dokku main
```

### Status / logs

```bash
dokku logs magic-hair-styler --tail
dokku ps:report magic-hair-styler
```

## Performance

- Total image weight: ~1.2 MB (down from ~15 MB) thanks to WebP.
- Hero image preloaded; everything else `loading="lazy" decoding="async"`.
- `nginx.conf` enables gzip and sets aggressive cache headers for static assets (30 days, `immutable`) and a short cache for HTML/XML (10 minutes) so content updates are picked up quickly.
- No frameworks, no bundlers, no third-party JS.

## SEO

- `<title>`, meta description, canonical, Open Graph / Twitter Card
- Four JSON-LD blocks: Product (with offers, shipping, returns, reviews, aggregateRating), Organization, WebSite, FAQPage
- `robots.txt` + `sitemap.xml` (with `image:image` entries)
- Semantic heading hierarchy (one `h1`, section-scoped `h2`s, `h3` for cards)
- Descriptive image alt text, telephone/email marked up, `hreflang`-ready `lang="en"`

## Licence / branding

© 2025 Ares Sentinel Limited, trading as Magic Hair Styler. All rights reserved.
