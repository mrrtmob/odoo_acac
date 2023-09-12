from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PmTraining(models.Model):
    _name = 'pm.training'
    _description = 'Description'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))

    # look up to employee
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    course_id = fields.Many2one('pm.training.courses', 'Training Course', required=True)
    location = fields.Text('Location')
    remark = fields.Char('Remark')
    approve_date = fields.Date('Approved Date')
    approved_by = fields.Many2one(
        comodel_name="res.users",
        string="Approved By",
        track_visibility="onchange",
        readonly=True,
        index=True,
    )

    @api.constrains('start_date', 'end_date')
    def check_dates(self):
        for record in self:
            start_date = fields.Date.from_string(record.start_date)
            end_date = fields.Date.from_string(record.end_date)
            if start_date > end_date:
                raise ValidationError(
                    _("End Date cannot be set before Start Date."))