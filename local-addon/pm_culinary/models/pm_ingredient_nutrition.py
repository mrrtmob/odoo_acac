# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PmIngredientNutrition(models.Model):
    _name = 'pm.ingredient.nutrition'
    _description = 'Ingredient Nutrition'

    product_id = fields.Many2one('product.product', 'Ingredient', index=True, required=True, ondelete='cascade')
    nutrition_id = fields.Many2one('pm.nutrition', 'Nutrition', index=True, required=True, ondelete='cascade')
    qty = fields.Float('Quantity', required=True)
    measurement_unit = fields.Selection(
        [('mcg', 'Microgram (mcg)'),
         ('mg', 'Milligram (mg)'),
         ('g', 'Gram (g)')],
        required=True
    )

    @api.onchange('nutrition_id')
    def _onchange_nutrition_id(self):
        self.measurement_unit = self.nutrition_id.measurement_unit
