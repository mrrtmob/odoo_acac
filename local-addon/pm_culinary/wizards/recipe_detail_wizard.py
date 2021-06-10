from odoo import models, fields, api
from odoo.exceptions import ValidationError


class WizardRecipeDetail(models.TransientModel):
    _name = "wizard.recipe.detail"
    _description = "Recipe Detail Wizard"

    recipe_id = fields.Many2one('pm.recipe', default=lambda self: self.env.context.get('active_id'))
    is_sub_recipe = fields.Boolean(related='recipe_id.is_sub_recipe')
    custom_field = fields.Selection(
        [('number_of_portion', 'Yield'),
         ('makes', 'Makes')],
        default='number_of_portion',
        required=True
    )
    number_of_portion = fields.Integer('Yield')
    makes = fields.Float()
    uor = fields.Selection(
        [('kg', 'kg'),
         ('l', 'l')],
        'UoR',
        related='recipe_id.uor'
    )

    @api.constrains('number_of_portion', 'makes')
    def _check_number_of_portion_and_makes(self):
        if self.custom_field == 'number_of_portion' and self.number_of_portion <= 0:
            raise ValidationError("Yield must be greater than 0")

        if self.custom_field == 'makes' and self.makes <= 0:
            raise ValidationError("Makes must be greater than 0")

    @api.onchange('recipe_id')
    def _onchange_recipe_id(self):
        self.number_of_portion = self.recipe_id.number_of_portion
        self.makes = self.recipe_id.makes

    @api.onchange('custom_field')
    def _onchange_custom_field(self):
        self.number_of_portion = self.recipe_id.number_of_portion
        self.makes = self.recipe_id.makes

    def print_report(self):
        res = {
            'recipe_id': self.recipe_id.id,
            'custom_field': self.custom_field,
            'number_of_portion': self.number_of_portion,
            'makes': self.makes
        }

        return self.env.ref('pm_culinary.report_recipe_detail').report_action(self, data=res)
