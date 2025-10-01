# Use Node.js 18 alpine image
FROM node:18-alpine AS base

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Development target
FROM base AS development

# Expose port for development server
EXPOSE 3000

# Start development server with hot reloading
CMD ["npm", "start"]

# Production target
FROM base AS production

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Use nginx to serve the built app
FROM nginx:alpine AS production-serve
COPY --from=production /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
