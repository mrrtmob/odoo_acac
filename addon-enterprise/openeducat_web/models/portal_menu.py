# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import api, fields, models


class PortalMenu(models.Model):
    _name = "openeducat.portal.menu"
    _description = "Portal Menu"
    _order = "sequence, id"

    def _default_sequence(self):
        menu = self.search([], limit=1, order="sequence DESC")
        return menu.sequence or 0

    website_id = fields.Many2one('website', 'Website', ondelete='cascade')
    sequence = fields.Integer('Sequence', default=_default_sequence)
    name = fields.Char('Menu', required=True, translate=True)
    link = fields.Char('Link', default='')
    icon_code = fields.Char('Icon-Code')
    active = fields.Boolean('Visible On The Portal')
    is_visible_to_student = fields.Boolean('Visible On The Student', default=True)
    is_visible_to_parent = fields.Boolean('Visible On The Parent', default=True)
    is_visible = fields.Boolean(compute='_compute_visible', string='Is Visible')
    group_ids = fields.Many2many('res.groups', string='Visible Groups')
    background_color = fields.Char(string="Background Color",
                                   default="#02b0e0")
    icon_image = fields.Image('Icon Image')

    @api.model
    def create(self, vals):
        self.clear_caches()
        for website in self.env['website'].search([], limit=1):
            w_vals = dict(vals, **{
                'website_id': website.id,
            })
            res = super(PortalMenu, self).create(w_vals)
        return res

    def _compute_visible(self):
        for menu in self:
            visible = True
            if menu.user_has_groups('base.group_user'):
                visible = False

            menu.is_visible = visible
