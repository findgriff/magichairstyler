# Dev Box Access

Ubuntu server on Hetzner — SSH access for building / hosting a new site.

## Connection

| Field | Value |
| --- | --- |
| Host | `91.98.112.127` |
| User | `root` |
| Port | `22` |
| OS   | Ubuntu 24.04 |
| Resources | 4 vCPU · 8 GB RAM · 160 GB SSD |

Optional `~/.ssh/config` entry so you can type `ssh devbox`:

```ssh-config
Host devbox
    HostName 91.98.112.127
    User root
    IdentityFile ~/.ssh/devbox_ed25519
    ServerAliveInterval 60
```

## SSH key setup

Generate a fresh key pair on **your** machine (the one that will run the agent):

```bash
ssh-keygen -t ed25519 -C "my-site-builder" -f ~/.ssh/devbox_ed25519 -N ""
cat ~/.ssh/devbox_ed25519.pub
```

Copy the public-key line it prints.

Send that **public** key to Craig — he adds it to the server with:

```bash
ssh dev "echo 'PASTE_PUBLIC_KEY_HERE' >> /root/.ssh/authorized_keys"
```

Then test from your side:

```bash
ssh devbox 'hostname && uptime -p'
```

You should see the server hostname and its uptime.

## What's already running on the box

Several sites share this server behind Caddy (the web server). Don't
touch their files/configs — stick to a new directory for your site:

- `/var/www/<your-site>/` — your static files go here
- `/etc/caddy/Caddyfile.d/<your-site>.caddy` — your Caddy site config

Any new site follows the same two-file pattern. If you need a reverse
proxy to a backend app, bind it to `127.0.0.1:<port>` and point Caddy
at it — external ports are firewalled.

After any Caddy config change:

```bash
caddy validate --config /etc/caddy/Caddyfile
systemctl reload caddy
```

## DNS (Cloudflare)

If your new site needs a DNS record, Craig will add it on Cloudflare
pointing at `91.98.112.127` (proxied = orange cloud is fine for normal
sites). Caddy will auto-issue a Let's Encrypt cert on first request
via DNS-01 — no manual cert work required.
