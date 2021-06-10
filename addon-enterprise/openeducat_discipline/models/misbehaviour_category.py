# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import api, models, fields


class OpMisbehaviourCategory(models.Model):
    _name = "op.misbehaviour.category"
    _description = "Misbehaviour Category Details"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char('Name', required=True)
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name',
        store=True)
    misbehaviour_type = fields.Selection(
        [('major', 'Major'), ('minor', 'Minor')],
        'Category Type', required=True)
    parent_id = fields.Many2one(
        'op.misbehaviour.category', 'Parent Category',
        index=True, ondelete='cascade')
    parent_path = fields.Char(index=True)
    child_id = fields.One2many(
        'op.misbehaviour.category', 'parent_id', 'Child Categories')
    misbehaviour_template_id = fields.Many2one(
        'mail.template', 'Misbehaviour Template', required=True)
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (
                    category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name

    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]
