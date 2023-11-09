from odoo import models, fields, api
from odoo.exceptions import ValidationError

class WizardRecipeList(models.TransientModel):
    _name = "wizard.recipe.list"
    _description = "Recipe List Wizard"

    custom_field = fields.Selection(
        [('number_of_portion', 'Yield')],
        default='number_of_portion',
        required=True
    )
    print_with_sub = fields.Boolean('Print with Sub Recipes', default=True)
    number_of_portion = fields.Integer('Yield')

    @api.constrains('number_of_portion', 'makes')
    def _check_number_of_portion_and_makes(self):
        if self.custom_field == 'number_of_portion' and self.number_of_portion <= 0:
            raise ValidationError("Yield must be greater than 0")

    @api.onchange('custom_field')
    def _onchange_custom_field(self):
        self.print_with_sub = self.print_with_sub

    def action_print_report(self):
        active_ids = self.env.context.get('active_ids')
        recipes = []

        # get make and uor from here and then pass into data, then pass to ReportRecipeList(models.AbstractModel)
        for recipe_id in active_ids:
            recipe = self.env['pm.recipe'].search([('id', '=', recipe_id)])
            recipes.append({
                'recipe_id': recipe_id,
                'is_sub_recipe':recipe.is_sub_recipe,
                'makes': recipe.makes,
                'uor': recipe.uor
            })
        data ={
            'form': self.read()[0],
            'recipes': recipes
        }
        return self.env.ref('pm_culinary.report_recipe_list').report_action(self,data=data)