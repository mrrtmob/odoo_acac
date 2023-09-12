# -*- coding: utf-8 -*-
# NOTE: adapted from PurchaseOrderLine

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PmMenuLine(models.Model):
    _name = 'pm.menu.line'
    _description = 'Menu Line'
    _order = 'menu_id, sequence, id'

    name = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    menu_id = fields.Many2one('pm.menu', string='Menu', index=True, required=True, ondelete='cascade')
    recipe_id = fields.Many2one('pm.recipe', 'Recipe', domain=[('state', '=', 'approved')])
    display_type = fields.Selection(
        [('line_section', "Section"),
         ('line_note', "Note")],
        default=False,
        help="Technical field for UX purpose."
    )
    number_of_portion = fields.Integer('Yield', required=True, default=10)
    cost_per_portion = fields.Float('Cost per Portion', compute='_compute_cost_per_portion', store=True)
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        default=lambda self: self.env.company.currency_id.id,
        required=True)
    price_per_portion = fields.Float('Selling Price per Portion', compute='_compute_price_per_portion', store=True)
    line_type = fields.Selection(
        [('cold_appetizer', 'Cold Appetizer'),
         ('soup', 'Soup'),
         ('hot_appetizer', 'Hot Appetizer'),
         ('intermediate_course', 'Intermediate course'),
         ('main_course', 'Main Course'),
         ('cheese', 'Cheese'),
         ('entremet', 'Entremet'),
         ('dessert', 'Dessert')]
    )

    @api.constrains('menu_id', 'recipe_id')
    def _check_recipe_id(self):
        for record in self:
            if record.recipe_id:
                count = record.search_count([
                    ('menu_id', '=', record.menu_id.id),
                    ('recipe_id', '=', record.recipe_id.id)
                ])

                if count > 1:
                    raise ValidationError(
                        _("%s must not be duplicated in this menu.") % record.recipe_id.name)

    @api.depends('recipe_id.cost_per_portion')
    def _compute_cost_per_portion(self):
        for record in self:
            record.cost_per_portion = record.recipe_id.cost_per_portion

    @api.depends('recipe_id.price_per_portion')
    def _compute_price_per_portion(self):
        for record in self:
            record.price_per_portion = record.recipe_id.price_per_portion

    @api.model
    def create(self, values):
        if values.get('display_type', self.default_get(['display_type'])['display_type']):
            values.update(recipe_id=False)

        line = super(PmMenuLine, self).create(values)

        return line

    def write(self, values):
        if 'display_type' in values and self.filtered(lambda line: line.display_type != values.get('display_type')):
            raise UserError(_(
                "You cannot change the type of a menu line. Instead you should delete the current line and create a new line of the proper type."))

        return super(PmMenuLine, self).write(values)

    @api.onchange('recipe_id')
    def onchange_recipe_id(self):
        if not self.recipe_id:
            return

        self.name = self.recipe_id.name
