FROM nginx:alpine

# Copy the HTML file to the nginx web root
COPY index.html /usr/share/nginx/html/index.html

# Expose port 80
EXPOSE 80

# The default CMD from the nginx:alpine image is already set to start nginx
