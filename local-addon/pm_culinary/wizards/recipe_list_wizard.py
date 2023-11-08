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


    def action_print_report(self):

        active_ids = self.env.context.get('active_ids')
        print("list of recipes: " + str(active_ids))
        recipes = self.env['pm.recipe'].search([('id', '=', [5,7])])
        print("========form ======== " + str(self.read()[0]))
        print("========custom_field ======== " + str(self.custom_field))
        print("========print_with_sub ======== " + str(self.print_with_sub))
        print("========number_of_portion ======== " + str(self.number_of_portion))
        print("========recipes ======== " + str(recipes))

        data ={
            'form': self.read()[0],
        }
        print("========data ======== " + str(data))
        return self.env.ref('pm_culinary.report_recipe_list').report_action(self,data=data)