FROM python:3.12-bullseye

WORKDIR /usr/src/app

COPY ./ ./
RUN apt-get update                             \
 && apt-get install -y --no-install-recommends \
    ca-certificates curl firefox-esr           \
 && rm -fr /var/lib/apt/lists/*                \
 && curl -L https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz | tar xz -C /usr/local/bin
RUN pip install -r requirements.txt

COPY . .

ADD start.sh /
RUN chmod +x /start.sh

CMD ["/start.sh"]