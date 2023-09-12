# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PmIngredientCategory(models.Model):
    _name = "pm.ingredient.category"
    _description = "Ingredient Category"
    _inherit = "mail.thread"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char('Name', index=True, required=True)
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name',
        store=True
    )
    parent_id = fields.Many2one('pm.ingredient.category', 'Parent Category', index=True, ondelete='cascade')
    parent_path = fields.Char(index=True)
    child_id = fields.One2many('pm.ingredient.category', 'parent_id', 'Child Categories')
    product_count = fields.Integer(
        '# Ingredients', compute='_compute_product_count',
        help="The number of ingredients under this category (Does not consider the children categories)")
    code = fields.Char()

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name

    def _compute_product_count(self):
        read_group_res = self.env['product.template'].read_group([('ingredient_categ_id', 'child_of', self.ids)], ['ingredient_categ_id'], ['ingredient_categ_id'])
        group_data = dict((data['ingredient_categ_id'][0], data['ingredient_categ_id_count']) for data in read_group_res)

        for categ in self:
            product_count = 0

            for sub_categ_id in categ.search([('id', 'child_of', categ.ids)]).ids:
                product_count += group_data.get(sub_categ_id, 0)

            categ.product_count = product_count

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive categories.'))

        return True

    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]
