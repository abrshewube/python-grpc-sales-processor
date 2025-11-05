FROM node:18-alpine

WORKDIR /app

# copy package files
COPY frontend/package*.json ./

# install dependencies
RUN npm install

# copy app files
COPY frontend/ ./

EXPOSE 3000

ENV NEXT_PUBLIC_API_URL=http://localhost:8000

CMD ["npm", "run", "dev"]

