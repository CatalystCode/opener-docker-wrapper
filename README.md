# opener-docker-wrapper

[![Deploy to Azure](https://azuredeploy.net/deploybutton.svg)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fc-w%2Fopener-docker-wrapper%2Fmaster%2Fazuredeploy.json)
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

A test page for the service is available at [https://localhost:9999](http://localhost:9999).

By default the response will be returned as JSON. If the raw OpeNER XML
output in [KAF format](http://kyoto-project.eu/xmlgroup.iit.cnr.it/kyoto/indexdd46.html?option=com_content&view=article&id=141&Itemid=130)
is desired, set the request accept header to `application/xml`. [Sample JSON response](https://github.com/c-w/opener-docker-wrapper/files/2129059/rome.json.txt). [Sample XML response](https://github.com/c-w/opener-docker-wrapper/files/2128722/rome.xml.txt).

If you are looking for additional NLP capabilities beyond the ones listed above, take a look at [@devkws's fork](https://github.com/devkws/opener-docker-wrapper) which adds [constituent-parsing](https://github.com/devkws/opener-docker-constituent-parser), [polarity-tagging](https://github.com/devkws/opener-docker-polarity-tagger) and [opinion-detection](https://github.com/devkws/opener-docker-opinion-detector-basic).
