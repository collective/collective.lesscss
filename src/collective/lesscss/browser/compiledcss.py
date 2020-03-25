# -*- coding: utf-8 -*-
from collective.lesscss.browser.controlpanel import ILESSCSSControlPanel
from plone import api
from plone.memoize import ram
from plone.memoize.volatile import DontCache
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from six import StringIO
from zope.component import queryUtility

import lesscpy
import logging


def render_cachekey(method, self):
    """Cache for compiled resources"""
    portal_less = api.portal.get_tool('portal_less')
    if portal_less.getDebugMode():
        raise DontCache
    return 'collective.lesscss.browser.compiledcss.compiledCSSView.__call__'


class compiledCSSView(BrowserView):
    """ View for server-side compiling of the LESS resources in portal_less
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.logger = logging.getLogger('collective.lesscss')

    def portal_less(self):
        return getToolByName(self.context, 'portal_less')

    def getInlineLess(self, item_id):
        """ Get the less code of a registered resource as a string

        item_id: This is the id of the resource that we want to get
        the content from.

        return: The actual content of the stored resource is returned
        in a string"""
        portal_less = self.portal_less()
        inline_code = portal_less.getInlineResource(item_id, self.context)
        return inline_code

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'text/css')
        portal_less = api.portal.get_tool('portal_less')
        if portal_less.getDebugMode():
            self.request.response.setHeader('Cache-Control', 'no-cache')
        else:
            self.request.response.setHeader('Cache-Control', 'public, max-age=31536000')
        return self.get_compiled_less_ressources()

    @ram.cache(render_cachekey)
    def get_compiled_less_ressources(self):
        portal_less = self.portal_less()

        less_resources = portal_less.getEvaluatedResources(self.context)
        less_resources_ids = [l.getId() for l in less_resources]

        results = []
        for res_id in less_resources_ids:
            resource_inline = self.getInlineLess(res_id)
            results.append('/*    %s    */\n' % res_id)
            results.append(resource_inline)
            results.append('\n/*    End  %s    */\n' % res_id)

        mustMinify = self.shouldMinify()
        compiled_css = self.compile_less_code(
            ''.join(results),
            mustMinify
        )
        if compiled_css is None:
            return ''

        for res_id in less_resources_ids:
            self.logger.info('The resource %s has been server-side compiled.' % res_id)
        if mustMinify and less_resources_ids:
            self.logger.info('Resources have been minified.')

        return compiled_css

    def compile_less_code(self, less_code, minify=False):
        """Compiles less code via the lesscpy compiler.

        This procedure returns the compiled css code that results of
        the compilation of the code as a string.  Errors are
        discarded and not returned back.
        """
        output = ''
        try:
            less_code = less_code.encode('utf-8')
            output = lesscpy.compile(
                StringIO(less_code),
                xminify=minify
            )
        except Exception as e:
            self.logger.error(e)
            return None
        return output

    def shouldMinify(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(ILESSCSSControlPanel, check=False)
        return settings.use_clean_css
