# -*- coding: utf-8 -*-

from odoo import models, api


class ReportRecipeDetail(models.AbstractModel):
    _name = 'report.pm_culinary.report_recipe_detail_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        custom_data = {
            'custom_field': data['custom_field'],
            'custom_number_of_portion': data['number_of_portion'],
            'custom_makes': data['makes']
        }
        print(custom_data)

        return {
            'doc_ids': docids,
            'doc_model': self.env['pm.recipe'],
            'docs': self.env['pm.recipe'].browse(self.env.context.get('active_id')),
            'custom_data': custom_data
        }


class ReportRecipeSchedule(models.AbstractModel):
    _name = 'report.pm_culinary.report_recipe_schedule_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        result = {}
        dates = []

        schedules = self.env['pm.schedule'].search(
            [('state', '=', 'approved'), ('event_date', '>=', data['from_date']), ('event_date', '<=', data['to_date'])],
            order='event_date asc'
        )

        for schedule in schedules:
            formatted_event_date = schedule.event_date.strftime('%A, %B %d, %Y')
            is_date_already_exist = formatted_event_date in dates

            if not is_date_already_exist:
                dates.append(formatted_event_date)

            if formatted_event_date not in result:
                result[formatted_event_date] = []

            for recipe in schedule.schedule_menu_ids.menu_id.menu_line_ids.recipe_id:
                is_recipe_already_exist = recipe.name in result[formatted_event_date]

                if not is_recipe_already_exist:
                    result[formatted_event_date].append(recipe.name)

        return {
            'doc_ids': docids,
            'doc_model': self.env['pm.recipe'],
            'result': result,
            'dates': dates,
            'from_date': data['from_date'],
            'to_date': data['to_date']
        }
