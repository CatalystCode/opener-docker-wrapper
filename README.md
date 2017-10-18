[![Docker status](https://img.shields.io/docker/pulls/cwolff/opener-docker-wrapper.svg)](https://hub.docker.com/r/cwolff/opener-docker-wrapper/)

# opener-docker-wrapper

This repository contains a simple service to wrap multiple OpeNER services that run on the same Docker host and expose them via a unified API.

```bash
# start the nlp services
docker network create opener
docker run -d --net opener --name opener-language-identifier cwolff/opener-docker-language-identifier
docker run -d --net opener --name opener-tokenizer cwolff/opener-docker-tokenizer
docker run -d --net opener --name opener-pos-tagger cwolff/opener-docker-pos-tagger
docker run -d --net opener --name opener-ner cwolff/opener-docker-ner

# start the wrapper service
docker run -d --net opener -p 9999:80 cwolff/opener-docker-wrapper

# call the wrapper service
curl 'http://localhost:9999/opener' \
  -H 'Content-Type: application/json' \
  -d '{"text": "I went to Rome last year. It was fantastic.",
       "steps": [
         "identify_language",
         "tokenize",
         "pos",
         "ner"
       ]}'
```
