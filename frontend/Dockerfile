# Base image - NodeJS
FROM node:15

# create destination directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . ./
# Install dependencies (clean install)
RUN npm ci

# Expose port 3000
EXPOSE 3000

# Project runs at port 3000
ENV HOST=0.0.0.0
ENV PORT=3000

# Build the project
RUN npm run build

CMD ["npm", "run", "start"]