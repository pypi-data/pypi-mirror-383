# -*- coding: utf-8 -*-

from collective.eeafaceted.z3ctable.columns import ActionsColumn as DashboardActionsColumn
from collective.eeafaceted.z3ctable.columns import BaseColumn
from collective.eeafaceted.z3ctable.columns import DateColumn
from collective.eeafaceted.z3ctable.columns import MemberIdColumn
from collective.eeafaceted.z3ctable.columns import PrettyLinkColumn as DashboardPrettyLinkColumn
from collective.iconifiedcategory.browser.tabview import AuthorColumn as IconifiedAuthorColumn
from collective.iconifiedcategory.browser.tabview import CategoryColumn as IconifiedCategoryColumn
from collective.iconifiedcategory.browser.tabview import CreationDateColumn as IconifiedCreationDateColumn
from collective.iconifiedcategory.browser.tabview import FilesizeColumn as IconifiedFilesizeColumn
from collective.iconifiedcategory.browser.tabview import LastModificationColumn as IconifiedLastModificationColumn
from collective.iconifiedcategory.interfaces import IIconifiedCategorySettings
from imio.annex import _
from plone import api
from Products.CMFPlone.utils import safe_unicode
from zope.i18n import translate

import html


class PrettyLinkColumn(DashboardPrettyLinkColumn):
    header = _(u'Title')
    weight = 20

    # link to a file, open in new tab
    params = {'target': '_blank'}

    def getPrettyLink(self, obj):
        """Display the description just under the pretty link."""
        pl = super(PrettyLinkColumn, self).getPrettyLink(obj)

        # simple blank space
        blank = u'<p class="discreet"></p>'

        # display description if any
        description = safe_unicode(html.escape(obj.Description() or u'')).replace('\n', '<br/>')
        if description:
            description = u'<p class="discreet">{0}</p>'.format(description)

        # display filename if any
        filename = html.escape(obj.file.filename or '')
        field_name = translate(
            'File',
            domain='imio.annex',
            context=obj.REQUEST)
        filename = u'<div class="discreet"><label class="horizontal">{0}</label>' \
            '<div class="type-text-widget">{1}</div></div>'.format(
                field_name, filename)

        # display scan_id if any
        scan_id = html.escape(getattr(obj, "scan_id", '') or '')
        if scan_id:
            field_name = translate(
                'scan_id',
                domain='collective.dms.scanbehavior',
                context=obj.REQUEST)
            scan_id = u'<div class="discreet"><label class="horizontal">{0}</label>' \
                '<div class="type-textarea-widget">{1}</div></div>'.format(
                    field_name, scan_id)
        return pl + blank + description + filename + scan_id


class AuthorColumn(MemberIdColumn):
    """ """
    weight = IconifiedAuthorColumn.weight
    header = IconifiedAuthorColumn.header


class CategoryColumn(IconifiedCategoryColumn, BaseColumn):
    """ """


class CreationDateColumn(IconifiedCreationDateColumn, DateColumn):
    """ """


class LastModificationColumn(IconifiedLastModificationColumn, DateColumn):
    """ """


class FilesizeColumn(IconifiedFilesizeColumn, BaseColumn):
    """ """


class ActionsColumn(DashboardActionsColumn):
    header = _(u'Actions')
    weight = 100
    params = {'showHistory': True, 'showActions': True, 'showArrows': True}

    def _showArrows(self):
        sort_categorized_tab = api.portal.get_registry_record(
            'sort_categorized_tab',
            interface=IIconifiedCategorySettings,
        )
        return not (bool(sort_categorized_tab))

    def renderCell(self, item):
        """ """
        self.params['showArrows'] = self._showArrows()
        return super(ActionsColumn, self).renderCell(item)
