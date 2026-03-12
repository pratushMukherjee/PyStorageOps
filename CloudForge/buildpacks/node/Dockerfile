FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --production

COPY . .

EXPOSE ${PORT:-3000}

CMD ["node", "index.js"]
