"""Dicstring."""
import os
from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from pyramid.httpexceptions import default_exceptionresponse_view, HTTPFound
from pyramid.interfaces import IRoutesMapper
from pyramid.settings import asbool


__version__ = "0.1"


class RemoveSlashNotFoundViewFactory(object):
    """Dicstring."""

    def __init__(self, notfound_view=None):
        """Dicstring."""
        if notfound_view is None:
            notfound_view = default_exceptionresponse_view
        self.notfound_view = notfound_view

    def __call__(self, context, request):
        """Dicstring."""
        if not isinstance(context, Exception):
            # backwards compat for an append_notslash_view registered via
            # config.set_notfound_view instead of as a proper exception view
            context = getattr(request, 'exception', None) or context
        path = request.path
        registry = request.registry
        mapper = registry.queryUtility(IRoutesMapper)
        if mapper is not None and path.endswith('/'):
            noslash_path = path.rstrip('/')
            for route in mapper.get_routes():
                if route.match(noslash_path) is not None:
                    qs = request.query_string
                    if qs:
                        noslash_path += '?' + qs
                    return HTTPFound(location=noslash_path)
        return self.notfound_view(context, request)


class HttpMethodOverrideMiddleware(object):
    """WSGI middleware for overriding HTTP Request Method for RESTful support."""

    def __init__(self, application):
        """Dicstring."""
        self.application = application

    def __call__(self, environ, start_response):
        """Dicstring."""
        if 'POST' == environ['REQUEST_METHOD']:
            override_method = ''

            # First check the "_method" form parameter
            # if 'form-urlencoded' in environ['CONTENT_TYPE']:
            if 'form-urlencoded' in environ.get('CONTENT_TYPE', ''):
                from webob import Request
                request = Request(environ)
                override_method = request.POST.get('_method', '').upper()

            # If not found, then look for "X-HTTP-Method-Override" header
            if not override_method:
                override_method = environ.get(
                    'HTTP_X_HTTP_METHOD_OVERRIDE', '').upper()

            if override_method in ('PUT', 'DELETE', 'OPTIONS', 'PATCH'):
                # Save the original HTTP method
                environ['http_method_override.original_method'] = \
                                            environ['REQUEST_METHOD']
                # Override HTTP method
                environ['REQUEST_METHOD'] = override_method

        return self.application(environ, start_response)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings['coins'] = {}
    for k, val in settings.items():
        if k.startswith('coins.'):
            d, c, v = k.split('.')
            try:
                settings['coins'][c][v] = asbool(val) if val in ['false', 'true'] else val
            except KeyError:
                settings['coins'][c] = {}
                settings['coins'][c][v] = asbool(val) if val in ['false', 'true'] else val

    settings['staticfiles'] = os.listdir(
        os.getcwd() + '/acme/static') + ['/favicon.ico', '/robots.txt']

    settings['nodes'] = {}

    config = Configurator(settings=settings)

    config.include('pyramid_mako')

    config.add_static_view(
        name='static', path='acme:static/', cache_max_age=3600)
    config.add_static_view(
        name='css', path='acme:static/css/', cache_max_age=3600)
    config.add_static_view(
        name='fonts', path='acme:static/fonts/', cache_max_age=3600)
    config.add_static_view(
        name='js', path='acme:static/js/', cache_max_age=3600)
    config.add_static_view(
        name='img', path='acme:static/img/', cache_max_age=3600)

    config.add_route('home', '/')
    config.add_route('index', '/{net}/')
    config.add_route('blocks', '/{net}/blk/')
    config.add_route('blocklist', '/{net}/blk/list/{arg}')
    config.add_route('block', '/{net}/blk/{arg}')
    config.add_route('transactions', '/{net}/tx/')
    config.add_route('transaction', '/{net}/tx/{arg}')
    config.add_route('nodes', '/{net}/node/')
    config.add_route('node', '/{net}/node/{arg}')
    config.add_route('publications', '/{net}/pb/')
    config.add_route('publication', '/{net}/pb/{arg}')
    config.add_route('address', '/{net}/addr/{arg}')
    config.add_route('network', '/{net}/net/')
    config.add_route('sparql', '/{net}/sparql')
    config.add_route('search', '/{net}/search/{arg}')
    config.add_route('blockbrowser', '/{net}/blockbrowser/')
    config.add_route('test', '/{net}/test/')

    _session_factory = SignedCookieSessionFactory('roadrunner')
    config.set_session_factory(_session_factory)

    config.add_subscriber('acme.subscribers.handle_setup', 'pyramid.events.NewRequest')

    config.add_translation_dirs('acme:locale')

    config.add_notfound_view(RemoveSlashNotFoundViewFactory())

    config.scan()

    app = config.make_wsgi_app()

    app = HttpMethodOverrideMiddleware(app)

    return app

