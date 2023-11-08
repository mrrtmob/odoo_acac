from odoo import models, fields, api
from odoo.exceptions import ValidationError

# class WizardRecipeList(models.TransientModel):
#     _name = "wizard.recipe.list"
#     _description = "Recipe List Wizard"

#     recipe_id = fields.Many2one('pm.recipe', default=lambda self: self.env.context.get('active_id'))
#     # recipe_id = fields.Many2one('pm.recipe', default=lambda self: 5)

#     is_sub_recipe = fields.Boolean(related='recipe_id.is_sub_recipe')
#     custom_field = fields.Selection(
#         [('number_of_portion', 'Yield'),
#          ('makes', 'Makes')],
#         default='number_of_portion',
#         required=True
#     )
#     print_with_sub = fields.Boolean('Print with Sub Recipes', default=True)
#     number_of_portion = fields.Integer('Yield')
#     makes = fields.Float()
#     uor = fields.Selection(
#         [('kg', 'kg'),
#          ('l', 'l')],
#         'UoR',
#         related='recipe_id.uor'
#     )

#     @api.constrains('number_of_portion', 'makes')
#     def _check_number_of_portion_and_makes(self):
#         if self.custom_field == 'number_of_portion' and self.number_of_portion <= 0:
#             raise ValidationError("Yield must be greater than 0")

#         if self.custom_field == 'makes' and self.makes <= 0:
#             raise ValidationError("Makes must be greater than 0")

#     @api.onchange('recipe_id')
#     def _onchange_recipe_id(self):
#         self.number_of_portion = self.recipe_id.number_of_portion
#         self.makes = self.recipe_id.makes

#     @api.onchange('custom_field')
#     def _onchange_custom_field(self):
#         print("yo")
#         self.number_of_portion = self.recipe_id.number_of_portion
#         self.makes = self.recipe_id.makes
#         self.print_with_sub = self.print_with_sub

#     def action_print_report(self):
#         data ={
#             'recipe_id': self.recipe_id,
#             'custom_field': self.custom_field,
#             'print_with_sub': self.print_with_sub,
#             'number_of_portion': self.number_of_portion,
#             'makes': self.makes
#         }

#         print("data recipe id "+str(data))
#         return self.env.ref('pm_culinary.action_report_recipe_list').report_action(self,data=data)


class WizardRecipeList(models.TransientModel):
    _name = "wizard.recipe.list"
    _description = "Recipe List Wizard"

    recipe_id = fields.Many2one('pm.recipe', string='Recipe')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')

    def action_print_report(self):

        # recipes = self.env['pm.recipe'].search_read([])
        print("========form ======== " + str(self.read()[0]))
        print("========recipe ======== " + str(self.recipe_id))
        data ={
            'form': self.read()[0],
        }
        print("========data ======== " + str(data))
        return self.env.ref('pm_culinary.report_recipe_list').report_action(self,data=data)