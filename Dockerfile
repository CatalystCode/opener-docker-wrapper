FROM python:3.6

RUN apt-get update \
  && apt-get install -y ca-certificates python3-virtualenv \
  && rm -rf /var/lib/apt/lists/*

ADD requirements.txt /app/requirements.txt
RUN python3 -m venv /venv \
  && /venv/bin/pip install --no-cache-dir --upgrade pip setuptools \
  && /venv/bin/pip install --no-cache-dir -r /app/requirements.txt

ADD app/ /app/

ENV SANIC_OPENER_IDENTIFY_LANGUAGE_URL="http://opener-language-identifier"
ENV SANIC_OPENER_TOKENIZE_URL="http://opener-tokenizer"
ENV SANIC_OPENER_POS_URL="http://opener-pos-tagger"
ENV SANIC_OPENER_NER_URL="http://opener-ner"
ENV SANIC_OPENER_KAF2JSON_URL="http://opener-kaf2json"

WORKDIR /app
EXPOSE 80
CMD ["/venv/bin/python3", "/app/server.py", "--port", "80"]
