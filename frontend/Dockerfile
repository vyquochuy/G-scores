# Stage 1: Build static assets
FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY index.html tsconfig.json vite.config.ts tailwind.config.js postcss.config.js ./
COPY src ./src

RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:1.25-alpine

COPY --from=build /app/dist /usr/share/nginx/html

RUN printf 'server {\n\
    listen 80;\n\
    server_name localhost;\n\
\n\
    location / {\n\
        root /usr/share/nginx/html;\n\
        index index.html index.htm;\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
\n\
    location /api/ {\n\
        proxy_pass http://backend:8000/api/;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n\
        proxy_set_header X-Forwarded-Proto $scheme;\n\
    }\n\
}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
