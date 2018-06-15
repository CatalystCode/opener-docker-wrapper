FROM alpine:3.6

ENV BUILD_DEPENDENCIES "build-base python3-dev"

RUN apk add --update --no-cache ${BUILD_DEPENDENCIES}

# Install Python 3.6
RUN apk add --no-cache python3 libstdc++ \
  && python3 -m ensurepip \
  && rm -r /usr/lib/python*/ensurepip \
  && pip3 install --no-cache-dir --upgrade pip setuptools \
  && if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip; fi

# Set up tokenizer server
ADD requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt
ADD run_server.py /server.py

# Cleanup
RUN apk del ${BUILD_DEPENDENCIES} \
  && rm /app/requirements.txt

ENV SANIC_OPENER_IDENTIFY_LANGUAGE_URL "http://opener-language-identifier"
ENV SANIC_OPENER_TOKENIZE_URL "http://opener-tokenizer"
ENV SANIC_OPENER_POS_URL "http://opener-pos-tagger"
ENV SANIC_OPENER_NER_URL "http://opener-ner"

EXPOSE 80
CMD ["python3.6", "/server.py", "--port", "80"]
