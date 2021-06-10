from odoo import models, fields, api
from odoo.exceptions import ValidationError


class WizardRecipeSchedule(models.TransientModel):
    _name = "wizard.recipe.schedule"
    _description = "Recipe Schedule Wizard"

    from_date = fields.Date('From Date', required=True)
    to_date = fields.Date('To Date', required=True)

    @api.constrains('from_date', 'to_date')
    def _check_from_date_and_to_date(self):
        if self.from_date > self.to_date:
            raise ValidationError("To Date must be after From Date")

    def print_report(self):
        res = {
            'from_date': self.from_date,
            'to_date': self.to_date
        }

        return self.env.ref('pm_culinary.report_recipe_schedule').report_action(self, data=res)
