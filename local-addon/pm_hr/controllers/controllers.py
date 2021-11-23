# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.survey.controllers.main import Survey
from odoo.http import request
import werkzeug
from odoo.exceptions import UserError

class CustomSurveyController(Survey):  # Inherit in your custom class

    @http.route('/survey/<string:survey_token>/<string:answer_token>/<string:appraisal_id>', type='http', auth='public', website=True)
    def custom_survey_display_page(self, survey_token, answer_token, appraisal_id = None, **post):
        access_data = self._get_access_data(survey_token, answer_token, ensure_token=True)
        if access_data['validity_code'] is not True:
            return self._redirect_with_error(access_data, access_data['validity_code'])

        answer_sudo = access_data['answer_sudo']
        if answer_sudo.state != 'done' and answer_sudo.survey_time_limit_reached:
            answer_sudo._mark_done()

        return request.render('survey.survey_page_fill',
                              self._prepare_survey_data(access_data['survey_sudo'], answer_sudo, appraisal_id, **post))

    def _prepare_survey_data(self, survey_sudo, answer_sudo, appraisal_id=None, **post):
        if appraisal_id:
            answer_sudo.appraisal_id = int(appraisal_id)
        res = super(CustomSurveyController, self)._prepare_survey_data(survey_sudo, answer_sudo, **post)
        return res

    @http.route('/survey/start/<string:survey_token>/<string:appraisal_id>', type='http', auth='public', website=True)
    def survey_start_custom(self, survey_token, answer_token=None, email=False, appraisal_id=None, **post):
        """ Start a survey by providing
         * a token linked to a survey;
         * a token linked to an answer or generate a new token if access is allowed;
        """
        # Get the current answer token from cookie
        if not answer_token:
            answer_token = request.httprequest.cookies.get('survey_%s' % survey_token)

        access_data = self._get_access_data(survey_token, answer_token, ensure_token=False)
        if access_data['validity_code'] is not True:
            return self._redirect_with_error(access_data, access_data['validity_code'])

        survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']
        if not answer_sudo:
            try:
                answer_sudo = survey_sudo._create_answer(user=request.env.user, email=email)
            except UserError:
                answer_sudo = False

        if not answer_sudo:
            try:
                survey_sudo.with_user(request.env.user).check_access_rights('read')
                survey_sudo.with_user(request.env.user).check_access_rule('read')
            except:
                return werkzeug.utils.redirect("/")
            else:
                return request.render("survey.survey_403_page", {'survey': survey_sudo})

        return request.redirect('/survey/%s/%s/%s' % (survey_sudo.access_token, answer_sudo.access_token, appraisal_id))

