FROM node:20-slim

# Install Python + system Chrome (for the SPA-rendering probe fallback).
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 python3-pip python3-venv \
        wget gnupg ca-certificates \
        fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst fonts-freefont-ttf \
        libxss1 \
    && wget -q -O /usr/share/keyrings/google-chrome.asc https://dl-ssl.google.com/linux/linux_signing_key.pub \
    && sh -c 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.asc] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list' \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

ENV BROWSER_PATH=/usr/bin/google-chrome-stable \
    PORT=8080 \
    NODE_ENV=production \
    PYTHON_BIN=/usr/src/app/venv/bin/python

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN python3 -m venv /usr/src/app/venv \
    && /usr/src/app/venv/bin/pip install --no-cache-dir -r requirements.txt

COPY scans/ ./scans/
COPY utils/ ./utils/
COPY server/ ./server/

WORKDIR /usr/src/app/server
RUN npm install --omit=dev

EXPOSE 8080
CMD ["npm", "start"]
