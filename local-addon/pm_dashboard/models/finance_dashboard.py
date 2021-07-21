from odoo import models, api
from datetime import date,datetime,timedelta
import pandas as pd
from dateutil.relativedelta import relativedelta
from odoo.http import request
from itertools import groupby
from operator import itemgetter

class FinanceDashboard(models.AbstractModel):
    _name = 'finance.dashboard'

    @api.model
    def get_finance_data(self):
        result = {
            'budgets' : [],
            'vendors' : [] 
        }
        starting_day_of_current_year = datetime.now().date().replace(month=1, day=1)    
        ending_day_of_current_year = datetime.now().date().replace(month=12, day=31)
        accounts = self.env['crossovered.budget'].search([
            ('date_from', '>=', starting_day_of_current_year) , 
            ('date_to', '<=', ending_day_of_current_year),
            ('state', 'in', ['confirm', 'validate', 'done'])
            ])
        for ac in accounts: 
            planned_amount = 0
            actual_amount = 0
            variance = 0
            for bl in  ac.crossovered_budget_line: 
                #print(bl.planned_amount)
                planned_amount += bl.planned_amount
                #print(bl.practical_amount)
                actual_amount += abs(bl.practical_amount)
                variance = planned_amount - actual_amount
            data = { 
                'name': ac.name,
                'planned_amount': planned_amount,
                'actual_amount': actual_amount,
                'variance': variance
            }
            result['budgets'].append(data)
        
        #top 5 vendors
 
        first_day_of_this_month = date.today().replace(day=1)
        last_day_of_this_month = (date.today() + relativedelta(months=1, day=1)) - timedelta(1)

        query = """
                SELECT SUM(amount_total) as amount, partner_id, invoice_partner_display_name as vendor
                FROM account_move where move_type IN ('in_invoice', 'in_refund') AND date >= DATE ('%s') AND date <= DATE ('%s')  
                GROUP BY invoice_partner_display_name,partner_id ORDER BY amount DESC LIMIT 5"""  %(starting_day_of_current_year, ending_day_of_current_year)
        self.env.cr.execute(query)
        top_accounts = self.env.cr.dictfetchall()
        #total billed amount
        query3 = """
            SELECT SUM(amount_total) as amount
            FROM account_move where move_type IN ('in_invoice', 'in_refund') AND date >= DATE ('%s') AND date <= DATE ('%s')"""  %(first_day_of_this_month, last_day_of_this_month)
        self.env.cr.execute(query3)
        total_bill = self.env.cr.dictfetchall()

        print(total_bill)

        for item in top_accounts: 
            query2 = """
            SELECT SUM(amount_total) as amount,partner_id,invoice_partner_display_name as vendor
            FROM account_move where move_type IN ('in_invoice', 'in_refund') AND date >= DATE ('%s') AND date <= DATE ('%s') AND partner_id = '%s'
            GROUP BY invoice_partner_display_name, partner_id LIMIT 1"""  %(first_day_of_this_month, last_day_of_this_month,item['partner_id']) 
            self.env.cr.execute(query2)
            this_month = self.env.cr.dictfetchall()
            if len(this_month): 
                item['this_month'] = this_month[0]['amount']
            else: 
                item['this_month'] = 0

            if total_bill[0]['amount']:
                item['avg_12'] = round(item['amount'] / 12,  2)
                item['total_p'] = round(item['amount'] / total_bill[0]['amount'] * 100 , 2)
           
        result['vendors'] = top_accounts
        print('vendors', result['vendors'])
                
        return result

    @api.model
    def get_ytd_vs_budget(self):
        result = [] 
        starting_day_of_current_year = datetime.now().date().replace(month=1, day=1)    
        ending_day_of_current_year = datetime.now().date().replace(month=12, day=31)
        accounts = self.env['crossovered.budget'].search([
            ('date_from', '>=', starting_day_of_current_year) , 
            ('date_to', '<=', ending_day_of_current_year),
            ('state', 'in', ['confirm', 'validate', 'done'])
            ])
        total_buget = 0
        total_actual = 0
        for ac in accounts: 
            planned_amount = 0
            actual_amount = 0
            for bl in  ac.crossovered_budget_line: 
                planned_amount += bl.planned_amount
                actual_amount += abs(bl.practical_amount)
            total_buget += planned_amount
            total_actual += actual_amount
        total_actual_p = 0
        if total_actual > 0:
            total_actual_p = round(total_actual / total_buget * 100 , 2)
        total_buget_p = round(100 - total_actual_p, 2)
        result.append(total_actual_p)
        result.append(total_buget_p)
        
        print ('ytd_budget',result)
        return result