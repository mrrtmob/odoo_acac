from odoo import api, fields, models, _
from datetime import datetime
import time
from odoo.exceptions import ValidationError


class EmployeeRecommendation(models.TransientModel):
    _name = 'employee.recommendation'
    _description = 'Employee Recommendation'

    # date_from = fields.Date(string='From', required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    # date_to = fields.Date(string='To', required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    approver = fields.Many2one("hr.employee" ,required=True, string="Approver", help="The person who signs on the certificate")
   
    def _get_default_note(self):
        employee_id = self.env.context.get('active_id')
        employee = self.env['hr.employee'].search([('id', '=', employee_id)])
        subjective =  "HIS/HER"
        title = "MR/MS"
        employee_name = ""
        if employee.gender == "female":
            subjective = "her"
            title = "Ms"
        elif employee.gender == 'male':
            subjective = "his"
            title = "Mr"
        employee_name = str(title) + " " + str(employee.name)
        subjective = str(subjective)
        print('employee', employee)
        hired_date = employee.joining_date
        hired_date = hired_date.strftime('%d/%m/%Y')
        today =  datetime.today() 
        today = today.strftime('%d/%m/%Y')

        result = """
            <div>
                <p>""" + employee_name + """ has been employed by the Academy of Culinary Arts Cambodia as """ + str(employee.job_id.name) + """ from """ + str(hired_date) + """ until """ + str(today) + """.</p>
                <br/>
                <p>During """ + subjective + """ employment """  + employee_name  + """ was responsible for: </p>
                <div><ul><li><p>LIST KEY RESPONSIBILITIES</p></li><ul/></div>  
                <br/>
                <p> ADD YOUR RECOMMENDATION HERE </p>
                <br/>
                <p style="clear:both;text-allign:left;margin: 0;padding:0">""" + employee_name + """ is self-motivated and driven to do his work to a (high, good, satisfactory) standard of execution and is (well) equipped to grow from challenges that """ +  subjective + """ is presented with. In summary I can (highly) recommend  """ + employee_name  + """ to any institution and wish  """ + subjective + """ all the best and success in the future endeavors.</p>
                <br/>
                <p> Sincerely, </p>
            </div>
            """
        return result

    recommendation = fields.Html(string='Recommendation', default=_get_default_note)
    @api.constrains('date_from', 'date_to')
    def check_dates(self):
        for record in self:
            start_date = fields.Date.from_string(record.date_from)
            end_date = fields.Date.from_string(record.date_to)
            if start_date > end_date:
                raise ValidationError(
                    _("End Date cannot be set before Start Date."))


    def print_report(self):
        employee_id = self.env.context.get('active_id')
        employee = self.env['hr.employee'].search([('id', '=', employee_id)])
        print('employee id', employee.identification_id)
        data = {
            'employee': employee,
            'active_id': employee_id,
            'passport_id': employee.passport_id,
            'identification_id': employee.identification_id,
            'job_position': employee.job_id.name,
            'approver': self.approver.name,
            'approver_position': self.approver.job_id.name,
            'recommendation': self.recommendation
        }

        return self.env.ref('pm_hr.act_get_employee_recommendation').report_action(self, data=data)



