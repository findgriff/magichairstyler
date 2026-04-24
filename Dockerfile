FROM nginx:alpine

# Site assets
COPY index.html /usr/share/nginx/html/index.html
COPY robots.txt /usr/share/nginx/html/robots.txt
COPY sitemap.xml /usr/share/nginx/html/sitemap.xml
COPY images/ /usr/share/nginx/html/images/

# Nginx: gzip, long-cache static assets, security headers
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
