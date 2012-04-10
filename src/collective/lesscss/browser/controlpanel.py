# -*- coding: utf-8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.registry.browser import controlpanel
from plone.registry.interfaces import IRegistry

from z3c.form import button

from zope.interface import Interface
from zope.component import queryUtility
from zope import schema

from collective.lesscss import LESSCSSMessageFactory as _

import logging


class ILESSCSSControlPanel(Interface):
    """Global oAuth settings. This describes records stored in the
    configuration registry and obtainable via plone.registry.
    """

    # enable_less_stylesheets = schema.ASCIILine(
    #     title=_(u'label_enable_less_stylesheets', default=u'Enable LESS stylesheets'),
    #     description=_(u'help_enable_less_stylesheets',
    #                     default=u"This setting will enable the LESS stylesheets on a system wide basis."
    #                             u"It's intended to use while in development mode."
    #                             u"In production mode is recommended to static compile them to CSS files."
    #                             u"You can achive this automatically by unsetting this option."),
    #     default=True
    #     )


class LESSCSSEditForm(controlpanel.RegistryEditForm):
    """LESSCSS settings form.
    """
    schema = ILESSCSSControlPanel
    id = "LESSCSSEditForm"
    label = _(u"LESSCSS UI settings")
    description = _(u"help_lesscss_settings_editform",
                    default=u"Settings related to LESSCSS.")

    def updateFields(self):
        super(LESSCSSEditForm, self).updateFields()

    def updateWidgets(self):
        super(LESSCSSEditForm, self).updateWidgets()

    @button.buttonAndHandler(_('Save'), name=None)
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_(u"Changes saved"),
                                                      "info")
        self.context.REQUEST.RESPONSE.redirect("@@lesscss-controlpanel")

    @button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled"),
                                                      "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(),
                                                  self.control_panel_view))

    @button.buttonAndHandler(_(u'Get token'), name='getToken')
    def handleGetToken(self, action):
        data, errors = self.extractData()
        credentials = dict(login=data.get('max_app_username'),
                           password=data.get('max_app_password'))
        from upc.maxui.max import getToken
        logger = logging.getLogger('upc.maxui')

        #Authenticat to max as operations user
        maxcli = MaxClient(data.get('max_server'), auth_method="basic")
        maxcli.setBasicAuth(data.get('max_ops_username'), data.get('max_ops_password'))

        #Add App user to max
        result = maxcli.addUser(credentials['login'], displayName=data.get('max_app_displayname'))
        if not result:
            logger.info('Error creating MAX user for user: %s' % credentials['login'])
            IStatusMessage(self.request).addStatusMessage(_(u"An error occurred during creation of max user"), "info")
        else:
            logger.info('MAX Agent user %s created' % credentials['login'])
            # Request token for app user
            oauth_token = getToken(credentials)
            registry = queryUtility(IRegistry)
            settings = registry.forInterface(ILESSCSSControlPanel, check=False)
            settings.max_app_token = str(oauth_token)

            #Subscribe app user to max
            club_url = getToolByName(self.context, "portal_url").getPortalObject().absolute_url()
            maxcli.setActor(credentials['login'])
            maxcli.subscribe(club_url)

            logger.info('MAX user %s subscribed to %s' % (credentials['login'], club_url))
            IStatusMessage(self.request).addStatusMessage(_(u"Token for MAX application user saved"), "info")


class LESSCSSControlPanel(controlpanel.ControlPanelFormWrapper):
    """LESSCSS settings control panel.
    """
    form = LESSCSSEditForm
    index = ViewPageTemplateFile('controlpanel.pt')
