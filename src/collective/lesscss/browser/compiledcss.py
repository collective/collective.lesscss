from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from plone.memoize import ram
from plone.registry.interfaces import IRegistry
from six import StringIO
from zope.component import queryUtility

import lesscpy
import logging

from collective.lesscss.browser.controlpanel import ILESSCSSControlPanel


def render_cachekey(method, self):
    """Cache for compiled resources"""
    return "collective.lesscss.browser.compiledcss.compiledCSSView.__call__"


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

    @ram.cache(render_cachekey)
    def __call__(self):
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

        for res_id in less_resources_ids:
            self.logger.info("The resource %s has been server-side compiled." % res_id)
        if mustMinify:
            self.logger.info("Resources have been minified.")

        self.request.response.setHeader('Content-Type', 'text/css')
        return compiled_css

    def compile_less_code(self, less_code, minify=False):
        """Compiles less code via the lesscpy compiler.

        This procedure returns the compiled css code that results of
        the compilation of the code as a string.  Errors are
        discarded and not returned back.
        """
        output = ''
        try:
            output = lesscpy.compile(
                StringIO(less_code),
                xminify=minify
            )
        except Exception as e:
            self.logger.error(e)
        return output

    def shouldMinify(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(ILESSCSSControlPanel, check=False)
        return settings.use_clean_css
