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
    print_with_sub = fields.Boolean('Print with Sub Recipes', default=True)
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
        print("yo")
        self.number_of_portion = self.recipe_id.number_of_portion
        self.makes = self.recipe_id.makes
        self.print_with_sub = self.print_with_sub

    def print_report(self):
        res = {
            'recipe_id': self.recipe_id.id,
            'custom_field': self.custom_field,
            'print_with_sub': self.print_with_sub,
            'number_of_portion': self.number_of_portion,
            'makes': self.makes
        }

        return self.env.ref('pm_culinary.report_recipe_detail').report_action(self, data=res)

class WizardMenuPrinting(models.TransientModel):
    _name = "wizard.menu.line"
    _description = "Menus Line"
    menu_wizard_id = fields.Many2one('wizard.menu.detail')
    recipe_id = fields.Many2one('pm.recipe', 'Recipe')
    number_of_portion = fields.Integer('Yield')
    print_with_sub = fields.Boolean('Print with Sub Recipes', default=True)

class WizardMenuPrinting(models.TransientModel):
    _name = "wizard.menu.detail"
    _description = "Menus Printing Wizard"
    menu_line_ids = fields.One2many('wizard.menu.line', 'menu_wizard_id')



    @api.model
    def default_get(self, fields):
        res = super(WizardMenuPrinting, self).default_get(fields)
        active_id = self.env.context.get('active_id', False)
        line_data = []
        menu_lines = self.env['pm.menu.line'].search([('menu_id', '=', active_id)])
        for line in menu_lines:
            line_data.append((0, 0, {'recipe_id': line.recipe_id.id, 'number_of_portion': line.number_of_portion}))
        res.update({'menu_line_ids': line_data})
        return res

    def print_report(self):
        res = {
            'menu_line_ids': self.menu_line_ids.ids,
        }
        return self.env.ref('pm_culinary.report_menu_detail').report_action(self, data=res)

