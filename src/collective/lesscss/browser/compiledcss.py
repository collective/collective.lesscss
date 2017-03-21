from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from plone.memoize import ram
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility

import logging
import os
import subprocess

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

    def _get_lessc_cmd(self):
        lessc_command_line = os.path.join(os.environ.get('INSTANCE_HOME'),
                                          os.path.pardir, os.path.pardir,
                                          'bin',
                                          'lessc')
        if not os.path.exists(lessc_command_line):
            self.logger.error("A valid lessc executable cannot be found."
                              "We are assumming that it has been provided by "
                              "buildout and placed in the buildout bin "
                              "directory. If not, you should provide one "
                              "(e.g. symbolic link) and place it there.")
        return lessc_command_line

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

        mustMinify = self.useCleanCss()
        compiled_css = self.compile_less_code(
            self._get_lessc_cmd(),
            ''.join(results),
            mustMinify
        )

        for res_id in less_resources_ids:
            self.logger.info("The resource %s has been server-side compiled." % res_id)
        if mustMinify:
            self.logger.info("Resources have been minified.")

        self.request.response.setHeader('Content-Type', 'text/css')
        return compiled_css

    def compile_less_code(self, lessc_command_line, less_code, minify=False):
        """Compiles less code via the lessc compiler installed in bin/.

        This procedure returns the compiled css code that results of
        the compilation of the code as a string.  Errors are
        discarded and not returned back.
        """

        # Call the LESSC executable
        cmd = [lessc_command_line, '-']
        if minify:
            cmd.append('--compress')
        process = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,
                                   stdin=subprocess.PIPE)
        output, errors = process.communicate(input=less_code)

        # Return the command output
        return output

    def useCleanCss(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(ILESSCSSControlPanel, check=False)
        return settings.use_clean_css
