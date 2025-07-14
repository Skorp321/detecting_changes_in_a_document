FROM node:18-alpine AS builder

# Аргументы для передачи переменных окружения при сборке
ARG REACT_APP_API_URL=/api

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .

# Устанавливаем переменные окружения для сборки
ENV REACT_APP_API_URL=$REACT_APP_API_URL

RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
RUN echo '#!/bin/sh\necho "healthy"' > /usr/share/nginx/html/health && \
    chmod +x /usr/share/nginx/html/health

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"] 