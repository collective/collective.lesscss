.. contents::

Introduction
============

This package allow theme developers to add LESS stylesheets into a Plone site.

LESS
====

LESS extends CSS with dynamic behavior such as variables, mixins, operations and functions. LESS runs on both the client-side (Chrome, Safari, Firefox) and server-side.

You can find more information about LESS at http://lesscss.org/

Integration with Plone
======================

This package clone the portal_css behavior, extending it to meet both client-side and server-side LESS resources compiling methods.

It adds a *portal_less* tool to the portal, enables an import/export GS profile *lessregistry.xml*, overrides the default *Products.ResourceRegistries* viewlet by adding the LESS resources part for the <head> tag.

Adding LESS resources
=====================

This package is intended to be used in conjunction with an user defined Plone Theme package. As a developer, you can include as many LESS resources as you may need to build your theme. You can add LESS resources using a GS profile named *lessregistry.xml*. The syntax is cloned from *cssregistry.xml* profile::

    <?xml version="1.0"?>
    <object name="portal_less" meta_type="LESS Stylesheets Registry">
      <stylesheet title="++bootstrap++less/bootstrap.less" authenticated="False"
        enabled="on" id="++bootstrap++less/bootstrap.less" rendering="link"/>
    </object>


Control Panel
=============

You can manage the way the LESS resources compile by accessing the LESS resources configlet located at the site setup. By default, client-side LESS resources compile mode and minification are enabled.

Client side compiling
=====================

Client-side compiling is intended to use while in (theme) development mode.

collective.lesscss will use the standard method for compiling client-side by using the *less.js* (v1.3, at the time of this writting) and exposing the LESS resources after the portal_css ones::

    <link rel="stylesheet/less" type="text/css" href="styles.less">
    <!-- Here goes the rest of portal_javascript resources -->
    <script src="less.js" type="text/javascript"></script>

Server side compiling
=====================

Server-side compiled LESS resources are recommended in production mode. By unsetting this option, the site will server-side compile them into CSS resources and enable a volatile cache on them. 

IMPORTANT NOTE: Server-side compiling requires to have declared the resources via plone.resource package in your theme package! Example::

    <plone:static
      directory="resources/less"
      type="bootstrap"
      name="less"
      />

And furthermore, if you aren't using plone.app.theming for develop your theme you should declare the type you are using for your resources by creating this class somewhere in your theme (e.g. traversal.py)::

    from plone.resource.traversal import ResourceTraverser

    class BootstrapTraverser(ResourceTraverser):
    """The theme traverser.

    Allows traveral to /++bootstrap++<name> using ``plone.resource`` to fetch
    things stored either on the filesystem or in the ZODB.
    """
    name = 'bootstrap'

and later on, declare the adapter via zcml::

    <adapter
    name="bootstrap"
    for="* zope.publisher.interfaces.IRequest"
    provides="zope.traversing.interfaces.ITraversable"
    factory=".traversal.BootstrapTraverser"
    />

So, you should now be able to access to the resources inside the resources directory by accessing::

    http://localhost/Plone/++bootstrap++less/

Twitter bootstrap integration
=============================

You can check out the package https://github.com/sneridagh/example.bootstrap for a full example on how to integrate LESS resources in your theme package.
