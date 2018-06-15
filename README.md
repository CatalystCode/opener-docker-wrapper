# opener-docker-wrapper

[![Deploy to Azure](https://azuredeploy.net/deploybutton.svg)](https://azuredeploy.net/)
[![Docker Pulls](https://img.shields.io/docker/pulls/cwolff/opener-docker-wrapper.svg)](https://hub.docker.com/r/cwolff/opener-docker-wrapper/)

This repository contains a simple service to wrap multiple OpeNER services and expose them via a unified API.

```bash
# start the nlp services and wrapper service
docker-compose up --build -d

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

If you are looking for additional NLP capabilities beyond the ones listed above, take a look at [@devkws's fork](https://github.com/devkws/opener-docker-wrapper) which adds [constituent-parsing](https://github.com/devkws/opener-docker-constituent-parser), [polarity-tagging](https://github.com/devkws/opener-docker-polarity-tagger) and [opinion-detection](https://github.com/devkws/opener-docker-opinion-detector-basic).
