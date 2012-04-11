import os
import subprocess
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.resource.interfaces import IResourceDirectory
from zope.component import getUtility
import logging


class compiledCSSView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        logger = logging.getLogger('collective.lesscss')
        portal_less = getToolByName(self.context, 'portal_less')
        lessc_command_line = os.path.join(os.environ.get('INSTANCE_HOME'), os.path.pardir, os.path.pardir, 'bin', 'lessc')
        less_resources = portal_less.getEvaluatedResources(self.context)

        results = []

        for less_resource in less_resources:
            res_id = less_resource.getId()
            # Just make sure that is a plone.resource object
            if '++' in res_id:
                # Extract its resource directory type and name
                resource_directory_type = res_id.split(os.path.sep)[0]
                resource_file_name = res_id.split(os.path.sep)[1]

                # Get its directoryResource object and extract the full path
                resource_path = getUtility(IResourceDirectory, name=resource_directory_type).directory

                # Call the LESSC executable
                results.append('/*    %s    */\n' % res_id)

                process = subprocess.Popen([lessc_command_line, os.path.join(resource_path, resource_file_name)],
                                   stdout=subprocess.PIPE)
                output, errors = process.communicate()
                results.append(output)
                results.append('\n/*    End  %s    */\n' % res_id)
            else:
                logger.warning("The resource %s is not a valid plone.resource asset, and cannot be server-side compiled." % res_id)

        return ''.join(results)
