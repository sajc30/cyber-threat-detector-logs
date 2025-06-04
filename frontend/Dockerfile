# Multi-stage build for React frontend
FROM node:18-alpine as base

# Set working directory
WORKDIR /app

# Copy package files
COPY frontend/threat-detector-dashboard/package*.json ./

# Install dependencies with cache optimization
RUN npm ci --only=production && npm cache clean --force

# Development stage
FROM node:18-alpine as development
WORKDIR /app
COPY frontend/threat-detector-dashboard/package*.json ./
RUN npm ci
COPY frontend/threat-detector-dashboard/ .
EXPOSE 3000
CMD ["npm", "start"]

# Build stage
FROM base as build
COPY frontend/threat-detector-dashboard/ .
RUN npm ci --include=dev && \
    npm run build && \
    npm prune --production

# Production stage with Nginx
FROM nginx:alpine as production

# Install security updates
RUN apk --no-cache add ca-certificates && \
    apk update && apk upgrade

# Create non-root user
RUN addgroup -g 1000 -S appuser && \
    adduser -u 1000 -S appuser -G appuser

# Copy custom nginx configuration
COPY frontend/nginx.conf /etc/nginx/nginx.conf
COPY frontend/default.conf /etc/nginx/conf.d/default.conf

# Copy built application
COPY --from=build /app/build /usr/share/nginx/html

# Create necessary directories and set permissions
RUN mkdir -p /var/cache/nginx /var/log/nginx /var/run && \
    chown -R appuser:appuser /var/cache/nginx /var/log/nginx /var/run /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"] 