# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.registry.browser import controlpanel
from zope.ramcache.interfaces.ram import IRAMCache

from z3c.form import button

from zope.interface import Interface
from zope.component import getUtility
from zope import schema

from collective.lesscss import LESSCSSMessageFactory as _


class ILESSCSSControlPanel(Interface):
    """Global oAuth settings. This describes records stored in the
    configuration registry and obtainable via plone.registry.
    """

    enable_less_stylesheets = schema.Bool(
        title=_(u'label_enable_less_stylesheets',
                default=u'Enable client-side compiling LESS stylesheets'),
        description=_(u'help_enable_less_stylesheets',
                      default=u"This setting will control the way LESS "
                              u"stylesheets are compiled for this site. "
                              u"Client-side compiling is intended to use "
                              u"while in (theme) development mode. "
                              u"Server-side compiled LESS resources are "
                              u"recommended in production mode. "
                              u"By unsetting this option, this site will "
                              u"server-side compile them into CSS "
                              u"resources and enable cache on them."),
        default=True
        )

    use_clean_css = schema.Bool(
        title=_(u'label_use_clean_css',
                default=u'Enable CSS compression'),
        description=_(u'description_use_clean_css',
                      default=u"This setting controls whether the compiled CSS"
                              u" code will be compressed (minified)."),
        default=True
    )


class LESSCSSEditForm(controlpanel.RegistryEditForm):
    """LESSCSS settings form.
    """
    schema = ILESSCSSControlPanel
    id = "LESSCSSEditForm"
    label = _(u"LESS resources settings")
    description = _(u"help_lesscss_settings_editform",
                    default=u"Settings related to site LESS resources.")

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
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_(u"Changes saved"),
                                                      "info")
        self.context.REQUEST.RESPONSE.redirect("@@lesscss-controlpanel")

    @button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled"),
                                                      "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(),
                                                  self.control_panel_view))

    @button.buttonAndHandler(_(u'Invalidate LESS cache'), name='refreshLESSCache')
    def handleRefreshLESSCache(self, action):
        getUtility(IRAMCache).invalidateAll()
        IStatusMessage(self.request).addStatusMessage(_(u"Static compiled LESS resources cache refreshed."), "info")
        self.context.REQUEST.RESPONSE.redirect("@@lesscss-controlpanel")


class LESSCSSControlPanel(controlpanel.ControlPanelFormWrapper):
    """LESSCSS settings control panel.
    """
    form = LESSCSSEditForm
    index = ViewPageTemplateFile('controlpanel.pt')
