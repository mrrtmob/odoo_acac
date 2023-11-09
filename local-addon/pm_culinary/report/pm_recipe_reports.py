# -*- coding: utf-8 -*-

from odoo import models, api


class ReportRecipeDetail(models.AbstractModel):
    _name = 'report.pm_culinary.report_recipe_detail_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        custom_data = {
            'custom_field': data['custom_field'],
            'custom_number_of_portion': data['number_of_portion'],
            'custom_makes': data['makes'],
            'print_with_sub': data['print_with_sub']
        }

        return {
            'doc_ids': docids,
            'doc_model': self.env['pm.recipe'],
            'docs': self.env['pm.recipe'].browse(self.env.context.get('active_id')),
            'custom_data': custom_data
        }

class ReportRecipeList(models.AbstractModel):
    _name = 'report.pm_culinary.report_recipe_list_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        
        custom_field = data['form']['custom_field']
        custom_number_of_portion = data['form']['number_of_portion']
        print_with_sub = data['form']['print_with_sub']

        recipe_list_print = []

        for rec in data['recipes']:
            print("====rec===="+ str(rec))
            print("=====rec_id====="+ str(self.env['pm.recipe'].browse(rec['recipe_id'])))
            custom_data = {
                'custom_field': custom_field,
                'custom_number_of_portion': custom_number_of_portion,
                'custom_makes': rec['makes'],
                'print_with_sub': print_with_sub
            }
            
            recipe_list_print.append({
                'doc_ids': docids,
                'doc_model': self.env['pm.recipe'],
                'docs': self.env['pm.recipe'].browse(rec['recipe_id']),
                'custom_data': custom_data
            })

        print("====recipe_list_print===="+ str(recipe_list_print))

        return {
            'data_list':recipe_list_print
        }

class ReportMenuDetail(models.AbstractModel):
    _name = 'report.pm_culinary.report_menu_detail_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        print(data)
        lines = self.env['wizard.menu.line'].search([('id', 'in', data['menu_line_ids'])])
        print(lines)
        print(type(lines))
        for d in lines:
            print("****")
            print(d.recipe_id.name)

        return {
            'doc_ids': docids,
            'doc_model': self.env['wizard.menu.detail'],
            'docs': lines,
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
