#!/usr/bin/env python3
"""A simple webservice to wrap OpeNER services.

"""
from typing import Iterable
from typing import Text
from typing import Tuple

from requests import RequestException
from requests import post
from sanic import Sanic
from sanic.exceptions import InvalidUsage
from sanic.exceptions import ServerError
from sanic.request import Request
from sanic.response import HTTPResponse


app = Sanic(__name__)


@app.route('/opener/', methods=['POST'])
async def opener(request: Request) -> HTTPResponse:
    nlp, steps = _parse_request(request)
    for endpoint in _build_opener_urls(steps):
        nlp = _call_opener_service(endpoint, nlp)
    return HTTPResponse(nlp, content_type='application/xml')


def _parse_request(request: Request) -> Tuple[Text, Iterable[Text]]:
    nlp = (request.json or {}).get('text')
    if not nlp:
        raise InvalidUsage('no input defined to process, please '
                           'specify "text" request property')
    steps = (request.json or {}).get('steps')
    if not steps:
        raise InvalidUsage('no steps specified for nlp processing, '
                           'please specify at least one step, all '
                           'steps are: {}'.format(', '.join(_all_steps())))
    return nlp, steps


def _build_opener_urls(steps: Iterable[Text]) -> Iterable[Text]:
    try:
        return [app.config['OPENER_{}_URL'.format(step).upper()]
                for step in steps]
    except KeyError as ex:
        raise InvalidUsage('unknown step {}, all steps are: {}'
                           .format(ex, ', '.join(_all_steps())))


def _all_steps():
    return (key[len('OPENER_'):-len('_URL')] for key in app.config
            if key.startswith('OPENER_') and key.endswith('_URL'))


def _call_opener_service(endpoint: Text, data: Text) -> Text:
    try:
        response = post(endpoint, data={'input': data})
        response.raise_for_status()
    except RequestException as ex:
        raise ServerError('unable to call {} {}'.format(endpoint, ex))
    return response.text


if __name__ == '__main__':
    from argparse import ArgumentParser
    from multiprocessing import cpu_count

    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=80)
    args = parser.parse_args()

    app.run(host=args.host, port=args.port, workers=cpu_count())
