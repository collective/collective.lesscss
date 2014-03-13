import os
import subprocess
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone.resource.interfaces import IResourceDirectory
from zope.component import getUtility
from plone.memoize import ram
import logging
import re


def render_cachekey(method, self, lessc_command_line, resource_path, resource_file_name):
    """Cache by resource_path and resource_file_name"""
    return (resource_path, resource_file_name)


class compiledCSSView(BrowserView):
    """ View for server-side compiling of the LESS resources in portal_less
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.logger = logging.getLogger('collective.lesscss')

    def __call__(self):
        portal_less = getToolByName(self.context, 'portal_less')
        lessc_command_line = os.path.join(os.environ.get('INSTANCE_HOME'), os.path.pardir, os.path.pardir, 'bin', 'lessc')
        if not os.path.exists(lessc_command_line):
            self.logger.error("A valid lessc executable cannot be found."
                         "We are assumming that it has been provided by buildout"
                         "and placed in the buildout bin directory."
                         "If not, you should provide one (e.g. symbolic link) and place it there.")

        less_resources = portal_less.getEvaluatedResources(self.context)
        regex = r'^(\+\+[\w_-]+\+\+[\w_-\.]+)\/(.*)$'

        results = []

        for less_resource in less_resources:
            res_id = less_resource.getId()
            find = re.search(regex, res_id)

            # Just make sure that is a plone.resource object
            if find:
                # Extract its resource directory type and name
                resource_directory_type, resource_file_name = find.groups()

                # Get its directoryResource object and extract the full path
                resource_path = getUtility(IResourceDirectory, name=resource_directory_type).directory

                results.append('/*    %s    */\n' % res_id)

                results.append(self.renderLESS(lessc_command_line, resource_path, resource_file_name))

                results.append('\n/*    End  %s    */\n' % res_id)
            else:
                self.logger.warning("The resource %s is not a valid plone.resource asset, and cannot be server-side compiled." % res_id)

        self.request.response.setHeader('Content-Type', 'text/css')
        return ''.join(results)

    @ram.cache(render_cachekey)
    def renderLESS(self, lessc_command_line, resource_path, resource_file_name):
        self.logger.info("The resource %s has been server-side compiled." % resource_file_name)

        # Call the LESSC executable
        process = subprocess.Popen([lessc_command_line, os.path.join(resource_path, resource_file_name)],
                           stdout=subprocess.PIPE)
        output, errors = process.communicate()
        # Return the command output
        return output
