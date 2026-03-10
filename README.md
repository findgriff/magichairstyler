# AirStyler — The Ultimate 5-in-1 Magic Hair Styler

A high-converting single-product landing page for the AirStyler 5-in-1 Magic Hair Styler, built with vanilla HTML, CSS, and JavaScript. Designed for rapid deployment on Dokku with Nginx.

## Features

- **Single-file design** — All CSS and JavaScript inline for maximum performance
- **Mobile-first responsive** — Excellent on all devices using CSS Grid and Flexbox
- **No dependencies** — Pure vanilla JavaScript, no frameworks or libraries
- **Stripe integration** — Direct links to Stripe Payment Links for all four colour variants
- **SEO-optimized** — Includes schema.org structured data and Open Graph tags
- **Accessible** — Proper heading hierarchy, alt tags, and colour contrast
- **Optimized animations** — Subtle fade-in effects using Intersection Observer API

## Project Structure

```
.
├── index.html          # Complete landing page (all CSS and JS inline)
├── Dockerfile          # Nginx container configuration
├── .dockerignore       # Docker build exclusions
└── README.md           # This file
```

## Customization

### Updating Stripe Payment Links

Each colour variant has a Stripe Payment Link in the code. Search for `// TODO: Replace with` in `index.html` to find all four links:

```javascript
// White/Gold (primary link)
data-stripe="https://buy.stripe.com/5kQ5kD97K1nM97dh0Ecs800"

// Silver/Pink (UPDATE THIS)
// TODO: Replace with Silver/Pink Stripe link

// Navy/Gold (UPDATE THIS)
// TODO: Replace with Navy/Gold Stripe link

// Black (UPDATE THIS)
// TODO: Replace with Black Stripe link
```

Replace each placeholder with the corresponding Stripe Payment Link from your Stripe dashboard.

### Product Images

All product images are sourced from the existing CDN. To change them, update the URLs in the colour swatch data attributes:

```html
<button class="colour-swatch white-gold"
        data-image="https://magichairstyler.com/cdn/shop/files/..."
        ...></button>
```

### Text Content

Edit any text content directly in `index.html`. Key sections:
- **Hero headline & subheadline** — Around line 300
- **Product features** — Around line 400
- **Technology specs** — Around line 450
- **Customer reviews** — Around line 550
- **FAQs** — Around line 620
- **Footer links** — Around line 700

## Deployment on Dokku

### Prerequisites

- A VPS with Dokku installed (see [Dokku installation](https://dokku.com/docs/getting-started/installation/))
- SSH access to your VPS
- A domain name (optional, but recommended)

### Step-by-Step Deployment

1. **Create the Dokku app** on your VPS:
   ```bash
   dokku apps:create magic-hair-styler
   ```

2. **Add a git remote** from your local machine:
   ```bash
   git remote add dokku dokku@YOUR_VPS_IP:magic-hair-styler
   ```

   Replace `YOUR_VPS_IP` with your VPS IP address.

3. **Push the code** to deploy:
   ```bash
   git push dokku main
   ```

   Dokku will automatically detect the Dockerfile and build the container.

4. **Add your domain** (if you have one):
   ```bash
   dokku domains:add magic-hair-styler yourdomain.com
   ```

5. **Enable HTTPS** with Let's Encrypt:
   ```bash
   dokku letsencrypt:enable magic-hair-styler
   ```

6. **Point your domain DNS** to the VPS IP:
   - Log in to your domain registrar
   - Update the A record to point to your VPS IP address
   - Wait for DNS propagation (usually 10 minutes to a few hours)

7. **Cancel your Shopify subscription** once you've verified the new site is live and all traffic is redirected.

### Checking Deployment Status

```bash
# View app logs
dokku logs magic-hair-styler

# View app info
dokku apps:info magic-hair-styler

# List all apps
dokku apps:list
```

### Updating the Page

To push new changes to your live site:

```bash
git add .
git commit -m "Update landing page"
git push dokku main
```

Dokku will rebuild and redeploy automatically.

### Reverting a Deployment

If you need to roll back to a previous version:

```bash
dokku ps:rebuild magic-hair-styler
```

Or check the git history and push a specific commit.

## Performance

The landing page is optimized for speed:
- **Single HTML file** — No additional HTTP requests for CSS/JS
- **Lightweight** — Minimal CSS and vanilla JavaScript only
- **Lazy loading** — Images load as users scroll
- **Minified animations** — Uses native CSS and Intersection Observer API
- **No external dependencies** — Everything is self-contained

## Browser Support

- Chrome/Edge 76+
- Firefox 63+
- Safari 12.1+
- Mobile browsers (iOS Safari 12.2+, Chrome Android)

## SEO

The page includes:
- Semantic HTML structure
- Open Graph tags for social sharing
- Twitter Card tags for Twitter sharing
- schema.org Product structured data (JSON-LD)
- Descriptive alt text on all images
- Proper heading hierarchy

## License

© 2025 Magic Hair Styler. All rights reserved.

## Support

For issues or questions during deployment:

1. Check the Dokku logs: `dokku logs magic-hair-styler`
2. Verify the image loads correctly in your browser's Network tab
3. Ensure your Stripe Payment Links are correctly configured
4. Check that your domain DNS is pointing to the correct VPS IP

---

**Ready to launch?** Follow the deployment steps above to get your landing page live in minutes.
