FROM node:20-alpine
WORKDIR /app
RUN npm install -g sirv-cli
COPY dist ./dist
EXPOSE 5000
CMD ["sirv", "dist", "--port", "5000", "--cors", "--single", "--host"]
