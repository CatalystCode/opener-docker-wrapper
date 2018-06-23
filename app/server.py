#!/usr/bin/env python3
"""A simple webservice to wrap OpeNER services.

"""
from functools import lru_cache
from os.path import dirname
from os.path import join
from typing import Dict
from typing import Iterable
from typing import Text
from typing import Tuple
from urllib.parse import urlparse

from aiohttp import ClientError
from aiohttp import ClientSession
from asyncio_extras import async_contextmanager
from sanic import Sanic
from sanic import response
from sanic.exceptions import InvalidUsage
from sanic.exceptions import ServerError
from sanic.request import Request
from sanic.response import HTTPResponse
from sanic_cors import CORS

Texts = Iterable[Text]


app = Sanic(__name__)

app.static('/favicon.ico', join(dirname(__file__), 'static', 'favicon.ico'))
app.static('/', join(dirname(__file__), 'static', 'test_page.html'))

CORS(app, automatic_options=True)


@app.route('/ping/', methods=['GET'])
async def ping(request: Request) -> HTTPResponse:
    return response.text('OK')


@app.route('/status/', methods=['GET'])
async def status(request: Request) -> HTTPResponse:
    urls = {key: value for key, value in app.config.items()
            if key.startswith('OPENER_') and key.endswith('_URL')}

    return response.json({
        'config': {
            'accept': _get_all_accept_values(),
            'steps': _all_steps(),
            'urls': urls
        }
    })


@app.route('/opener/', methods=['POST'])
async def opener(request: Request) -> HTTPResponse:
    nlp, steps, accept = _parse_request(request)

    for endpoint in _build_opener_urls(steps, accept):
        nlp = await _call_opener_service(endpoint, nlp)

    return HTTPResponse(nlp, content_type=accept)


def _parse_request(request: Request) -> Tuple[Text, Texts, Text]:
    nlp = (request.json or {}).get('text')
    if not nlp:
        raise InvalidUsage('no input defined to process, please '
                           'specify "text" request property')

    steps = (request.json or {}).get('steps')
    if not steps:
        raise InvalidUsage('no steps specified for nlp processing, '
                           'please specify at least one step, all '
                           'steps are: {}'.format(', '.join(_all_steps())))

    accept_values = _get_all_accept_values()
    accept = request.headers.get('Accept', accept_values[0])
    if accept == '*/*':
        accept = accept_values[0]
    if accept not in accept_values:
        raise InvalidUsage('unknown accept header {}, '
                           'please specify one of: {}'
                           .format(accept, ', '.join(accept_values)))

    return nlp, steps, accept


@lru_cache(maxsize=1)
def _get_client_cache() -> Dict[Text, ClientSession]:
    return {}


@async_contextmanager
async def _get_client_session(url: Text) -> ClientSession:
    netloc = urlparse(url).netloc

    if not netloc:
        client = ClientSession()
        yield client
        await client.close()
    else:
        cache = _get_client_cache()
        try:
            client = cache[netloc]
        except KeyError:
            client = ClientSession()
            cache[netloc] = client
        yield client


def _build_opener_urls(steps: Texts, accept: Text) -> Texts:
    try:
        steps = [app.config['OPENER_{}_URL'.format(step).upper()]
                 for step in steps]
    except KeyError as ex:
        raise InvalidUsage('unknown step {}, all steps are: {}'
                           .format(ex, ', '.join(_all_steps())))

    if accept == 'application/json' and steps[-1].lower() != 'kaf2json':
        try:
            steps.append(app.config['OPENER_KAF2JSON_URL'])
        except KeyError as ex:
            raise InvalidUsage('application/json requested but '
                               '{} is not set'.format(ex))

    return steps


def _all_steps() -> Texts:
    return (key[len('OPENER_'):-len('_URL')] for key in app.config
            if key.startswith('OPENER_') and key.endswith('_URL'))


def _get_all_accept_values() -> Tuple[Text]:
    return 'application/json', 'application/xml'


async def _call_opener_service(endpoint: Text, data: Text) -> Text:
    async with _get_client_session(endpoint) as session:
        async with session.post(endpoint, data={'input': data}) as response:
            try:
                response.raise_for_status()
            except ClientError as ex:
                raise ServerError('unable to call {} {}'.format(endpoint, ex))
            else:
                return await response.text()


if __name__ == '__main__':
    from argparse import ArgumentParser
    from multiprocessing import cpu_count

    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=80)
    parser.add_argument('--workers', type=int, default=cpu_count())
    args = parser.parse_args()

    app.run(host=args.host, port=args.port, workers=args.workers)
