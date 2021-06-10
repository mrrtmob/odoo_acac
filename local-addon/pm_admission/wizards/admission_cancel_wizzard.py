# -*- coding: utf-8 -*-


from odoo import models, fields

class WizardPMApplicantCancel(models.TransientModel):
    _name = 'wizard.pm.admission.cancel'
    _description = "Cancel Admission to Lead"
    reason = fields.Text('Cancel Reason', required=True)
    return_date = fields.Date("Return Date")
    cancel_date = fields.Date(default=lambda self: fields.Datetime.now())

    def cancel_admission(self):
        active_id = self.env.context.get('active_ids', []) or []
        admission = self.env['op.admission'].browse(active_id)
        lead = self.env['crm.lead'].browse(admission.lead_id)
        lead.write({
            'cancel_reason': self.reason,
            'return_date': self.return_date,
            'cancel_date': self.cancel_date,
            'type': 'lead'
        })
        admission.unlink()
        action = self.env.ref("openeducat_admission.act_open_op_admission_view").read()[0]
        return action







