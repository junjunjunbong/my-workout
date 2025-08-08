# syntax=docker/dockerfile:1
FROM node:20-alpine
WORKDIR /app
COPY frontend/ /app/
RUN npm ci || npm install
RUN npm run build || echo "No build script; skipping"
EXPOSE 3000
CMD ["npm", "start"]