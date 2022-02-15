from odoo import models, fields, _, api, SUPERUSER_ID
from datetime import datetime
import werkzeug
from odoo.exceptions import UserError, ValidationError



class PmLeave(models.Model):
    _inherit = 'hr.leave'
    is_special_leave = fields.Boolean("Special Leave")
    employee_remaining_paid_leave = fields.Float(related="employee_id.remaining_leaves")

    def send_email_to_reviewer(self):
        print("*******************")
        appraisal_ids = self.env['hr.appraisal'].search(
            [('appraisal_start', '=', datetime.today()), ('state', '=', 1)])
        if appraisal_ids:
            for appraisal in appraisal_ids:
                appraisal.action_start_appraisal()

    @api.constrains('date_from', 'date_to', 'employee_id')
    def _check_date_state(self):
        if self.env.context.get('leave_skip_state_check'):
            return
        for holiday in self:
            if holiday.state in ['cancel', 'refuse', 'validate1', 'validate'] and not self.user_has_groups('hr_holidays.group_hr_holidays_manager'):
                raise ValidationError(_("This modification is not allowed in the current state."))




    # def _check_approval_update(self, state):
    #     print("hit me the fake one")

    #     """ Check if target state is achievable. """
    #     if self.env.is_superuser():
    #         return

    #     current_employee = self.env.user.employee_id
    #     is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
    #     is_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')


    #     for holiday in self:
    #         val_type = holiday.holiday_status_id.leave_validation_type
    #         responsible = holiday.holiday_status_id.responsible_id
    #         print(state)
    #         print(responsible.name)
    #         print(self.env.user.name)

    #         if state == 'validate' and val_type == 'both' and self.env.user != responsible:
    #             raise UserError(
    #                 _('You are not authorized to approve this final leave'))

    #         if not is_manager and state != 'confirm':
    #             if state == 'draft':
    #                 if holiday.state == 'refuse':
    #                     raise UserError(_('Only a Leave Manager can reset a refused leave.'))
    #                 if holiday.date_from and holiday.date_from.date() <= fields.Date.today():
    #                     raise UserError(_('Only a Leave Manager can reset a started leave.'))
    #                 if holiday.employee_id != current_employee:
    #                     raise UserError(_('Only a Leave Manager can reset other people leaves.'))
    #             else:
    #                 if val_type == 'no_validation' and current_employee == holiday.employee_id:
    #                     continue
    #                 # use ir.rule based first access check: department, members, ... (see security.xml)
    #                 holiday.check_access_rule('write')

    #                 # This handles states validate1 validate and refuse
    #                 if holiday.employee_id == current_employee:
    #                     raise UserError(_('Only a Leave Manager can approve/refuse its own requests.'))

    #                 if (state == 'validate' and val_type == 'manager') and holiday.holiday_type == 'employee':
    #                     if not is_officer and self.env.user != holiday.employee_id.leave_manager_id:
    #                         raise UserError(
    #                             _('You must be either %s\'s manager or Leave manager to approve this leave') % (
    #                                 holiday.employee_id.name))







class PmSurvey(models.Model):
    _inherit = 'survey.survey'
    # category = fields.Selection(selection_add=[('appraisal', "Appraisal")])
    department_id = fields.Many2one('hr.department', 'Department')
    job_id = fields.Many2one('hr.job')


    @api.depends('session_code')
    def _compute_session_link(self):
        print("I'm Child")
        for survey in self:
            survey.session_link = werkzeug.urls.url_join(
                survey.get_base_url(),
                survey.get_start_url())

    def write(self, vals):
      # Temporarily fixing image issue when update a record
      if vals['background_image']:
          self.env.cr.execute("""DELETE FROM ir_attachment WHERE res_model = '%s' AND res_field = '%s' AND res_id = %d""" % (self._name, 'background_image', self.id))

      return super(PmSurvey, self).write(vals)



class PmSurveyUserInputInherit(models.Model):
    _inherit = 'survey.user_input'
    emp_id = fields.Many2one('hr.employee', related='appraisal_id.emp_id', store=True)
    # survey_answer_link = fields.Char( compute="_compute_survey_answer_link", store=True)

    # def _compute_survey_answer_link(self):
    #     for rec in self:
    #         base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #         survey_link = '/survey/print/%s?answer_token=%s' % (rec.survey_id.access_token, rec.token)
    #         rec.survey_answer_link = base_url + survey_link

    def action_share_survey(self):
        '''
        This function opens a window to compose an email, with the edi purchase template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = self.env.ref('pm_hr.pm_mail_template_user_input_answer', raise_if_not_found=False)
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'survey.user_input',
            'active_model': 'survey.user_input',
            'active_id': self.ids[0],
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id and template_id.id or False,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_light",
            'force_email': True,
            'mark_rfq_as_sent': True,
        })

        ctx['model_description'] = _('Survey Answers')

        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }



    def action_share_survey1(self):
        print('hit me')

        template = self.env.ref('pm_hr.pm_mail_template_user_input_answer', raise_if_not_found=False)
        print(template)

        local_context = dict(
            self.env.context,
            default_survey_id=self.survey_id.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            notif_layout='mail.mail_notification_light',
        )
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'survey.invite',
            'target': 'new',
            'context': local_context,
        }


    # def write(self, vals):
    #     print("**************************")
    #     print(vals)
    #
    #     if vals['state'] == 'done':
    #         appraisal = self.appraisal_id
    #         partner = self.partner_id
    #
    #         if appraisal and partner:
    #             appraisal.message_post_with_view(
    #                 'pm_hr.pm_appraisal_template',
    #                 values={'obj': self, 'partner_name': partner.name})
    #
    #     return super(PmSurveyUserInputInherit, self).write(vals)



class Channel(models.Model):
    _inherit = 'slide.channel'

    def write(self, vals):
      # Temporarily fixing image issue when update a record
      if vals['image_1920']:
          # print(self._name)
          # print(self.id)
          self.env.cr.execute("""DELETE FROM ir_attachment WHERE res_model = '%s' AND res_id = %d""" % (self._name, self.id))

      return super(Channel, self).write(vals)



class Slide(models.Model):
    _inherit = 'slide.slide'

    def write(self, vals):
      # Temporarily fixing image issue when update a record
      if vals['image_1920']:
          # print(self._name)
          # print(self.id)
          self.env.cr.execute("""DELETE FROM ir_attachment WHERE res_model = '%s' AND res_id = %d""" % (self._name, self.id))

      return super(Slide, self).write(vals)