FROM python:3.11-alpine

RUN apk add --no-cache \
    nodejs \
    npm \
    bash \
    git \
    make \
    g++ \
    libffi-dev \
    musl-dev \
    gcc \
    python3-dev

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install gunicorn \
    && pip install -r requirements.txt

COPY package.json .
COPY package-lock.json .
RUN npm install

COPY . .

RUN npm run build

CMD ["npm", "start"]
