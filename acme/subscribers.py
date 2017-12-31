import logging
import sys
from acme.lib.helpers import histoire
from pyramid.threadlocal import get_current_request
from pyramid.events import subscriber
from pyramid.events import BeforeRender
from acme.lib.helpers import RPCHost

log = logging.getLogger(__name__)


class Cleanup:
    def __init__(self, request):
        self.request = request

    def __del__(self):
        pass


def isforstatic(request):
    return [f for f in request.registry.settings['staticfiles']
            if request.path_info.startswith('/' + f)]


def handle_setup(event):
    """
    Do basic request setup
    """

    request = event.request
    if request is None:
        request = get_current_request()

    if request and not isforstatic(request):
        # Retrieve the coin settings from the registry 
        # Create and parameterise an RPCHost instance, store in tmpl_context
        request.tmpl_context.net = 'test' if 'test' in request.path_info else 'main'
        request.tmpl_context.pp = 'back'
        coin = request.registry.settings.get('coins').get('coin')
        request.tmpl_context.coin = coin
        request.tmpl_context.scheme = list(filter(None, coin['scheme'].split('\n'))) 
        if request.tmpl_context.net == 'test':
            request.tmpl_context.acmerpc = RPCHost('http://{}:{}@localhost:{}/'.format(
                coin.get('testnetrpcuser'), coin.get('testnetrpcpass'), coin.get('testnetrpcport')))
            request.tmpl_context.dataset = coin.get('testnetdataset')
        else:
            request.tmpl_context.acmerpc = RPCHost('http://{}:{}@localhost:{}/'.format(
                coin.get('rpcuser'), coin.get('rpcpass'), coin.get('rpcport')))
            request.tmpl_context.dataset = coin.get('dataset')
        request.tmpl_context.endpoint = coin.get('endpoint')
        request.tmpl_context.nbpp = int(coin.get('nbpp'))
        request.tmpl_context.histoire = histoire
        request.tmpl_context.coin['binfo'] = request.tmpl_context.acmerpc.call('getinfo')
        request.tmpl_context.coin['binfo']['moneysupply'] = 0
        request.tmpl_context.coin['addrs'] = [
            'addnode={}\n'.format(node.get('addr')).replace(',', '')
            for node in request.tmpl_context.acmerpc.call('getpeerinfo')]

    log.debug("{}".format(request.registry.settings['staticfiles']))


def handle_teardown(event):
    request = event.request
    if request is None:
        request = get_current_request()
    if request is not None and not isforstatic(request):
        Cleanup(request)


@subscriber(BeforeRender)
def add_global(event):
    request = event['request']
    if request is None:
        request = get_current_request()
    pass
