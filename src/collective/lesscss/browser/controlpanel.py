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

    enable_less_stylesheets = schema.Bool(
        title=_(u'label_enable_less_stylesheets', default=u'Enable LESS stylesheets'),
        description=_(u'help_enable_less_stylesheets',
                        default=u"This setting will enable the LESS stylesheets on a site wide basis."
                                u"It's intended to use while in (theme) development mode."
                                u"In production mode it is recommended to static compile them to CSS files."
                                u"You can achive this automatically by unsetting this option."),
        default=True
        )


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
        if not data.get('enable_less_stylesheets', None):
            # Compile all enabled LESS resources from portal_less into static CSS resources
            #compileLESSresources(self.context)
            IStatusMessage(self.request).addStatusMessage(_(u"Token for MAX application user saved"), "info")


class LESSCSSControlPanel(controlpanel.ControlPanelFormWrapper):
    """LESSCSS settings control panel.
    """
    form = LESSCSSEditForm
    index = ViewPageTemplateFile('controlpanel.pt')
