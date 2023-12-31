import time
from odoo import fields, models, api, _

import io
import json
from odoo.http import request
from odoo.exceptions import AccessError, UserError, AccessDenied

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

import calendar
from datetime import date

class TrialView(models.TransientModel):
    _inherit = "account.common.report"
    _name = 'account.trial.balance'

    journal_ids = fields.Many2many('account.journal',

                                   string='Journals', required=True,
                                   default=[])
    display_account = fields.Selection(
        [('all', 'All'), ('movement', 'With movements'),
         ('not_zero', 'With balance is not equal to 0')],
        string='Display Accounts', required=True, default='movement')

    @api.model
    def view_report(self, option):
        r = self.env['account.trial.balance'].search([('id', '=', option[0])])

        data = {
            'display_account': r.display_account,
            'model':self,
            'journals': r.journal_ids,
            'target_move': r.target_move,

        }
        if r.date_from:
            data.update({
                'date_from':r.date_from,
            })
        if r.date_to:
            data.update({
                'date_to':r.date_to,
            })

        filters = self.get_filter(option)
        records = self._get_report_values(data)
        currency = self._get_currency()

        return {
            'name': "Trial Balance",
            'type': 'ir.actions.client',
            'tag': 't_b',
            'filters': filters,
            'report_lines': records['Accounts'],
            'debit_total': records['debit_total'],
            'credit_total': records['credit_total'],
            'init_debit_total': records['init_debit_total'],
            'init_credit_total': records['init_credit_total'],
            'final_debit_total': records['final_debit_total'],
            'final_credit_total': records['final_credit_total'],
            'currency': currency,
        }

    def get_filter(self, option):
        data = self.get_filter_data(option)
        filters = {}
        if data.get('journal_ids'):
            filters['journals'] = self.env['account.journal'].browse(data.get('journal_ids')).mapped('code')
        else:
            filters['journals'] = ['All']
        if data.get('target_move'):
            filters['target_move'] = data.get('target_move')
        if data.get('date_from'):
            filters['date_from'] = data.get('date_from')
        if data.get('date_to'):
            filters['date_to'] = data.get('date_to')

        filters['company_id'] = ''
        filters['journals_list'] = data.get('journals_list')
        filters['company_name'] = data.get('company_name')
        filters['target_move'] = data.get('target_move').capitalize()

        return filters

    def get_current_company_value(self):

        cookies_cids = [int(r) for r in request.httprequest.cookies.get('cids').split(",")] \
            if request.httprequest.cookies.get('cids') \
            else [request.env.user.company_id.id]
        for company_id in cookies_cids:
            if company_id not in self.env.user.company_ids.ids:
                cookies_cids.remove(company_id)
        if not cookies_cids:
            cookies_cids = [self.env.company.id]
        if len(cookies_cids) == 1:
            cookies_cids.append(0)
        return cookies_cids

    def get_filter_data(self, option):
        r = self.env['account.trial.balance'].search([('id', '=', option[0])])
        default_filters = {}
        company_id = self.env.companies.ids
        company_domain = [('company_id', 'in', company_id)]
        journal_ids = r.journal_ids if r.journal_ids else self.env['account.journal'].search(company_domain, order="company_id, name")


        journals = []
        o_company = False
        for j in journal_ids:
            if j.company_id != o_company:
                journals.append(('divider', j.company_id.name))
                o_company = j.company_id
            journals.append((j.id, j.name, j.code))

        filter_dict = {
            'journal_ids': r.journal_ids.ids,
            'company_id': company_id,
            'date_from': r.date_from,
            'date_to': r.date_to,
            'target_move': r.target_move,
            'journals_list': journals,
            # 'journals_list': [(j.id, j.name, j.code) for j in journals],

            'company_name': ', '.join(self.env.companies.mapped('name')),
        }
        filter_dict.update(default_filters)
        return filter_dict

    def _get_report_values(self, data):
        docs = data['model']
        display_account = data['display_account']
        journals = data['journals']
        accounts = self.env['account.account'].search([])
        if not accounts:
            raise UserError(_("No Accounts Found! Please Add One"))
        account_res = self._get_accounts(accounts, display_account, data)
        debit_total = 0
        debit_total = sum(x['debit'] for x in account_res)
        credit_total = sum(x['credit'] for x in account_res)
        init_debit_total = 0
        init_debit_total = sum(x['Init_balance']['debit'] for x in account_res if 'Init_balance' in x and x['Init_balance'])
        init_credit_total = sum(x['Init_balance']['credit'] for x in account_res if 'Init_balance' in x and x['Init_balance'])
        final_debit_total = 0
        final_debit_total = sum(x['total_debit_balance'] for x in account_res)
        final_credit_total = sum(x['total_credit_balance'] for x in account_res)
        return {
            'doc_ids': self.ids,
            'debit_total': debit_total,
            'credit_total': credit_total,
            'init_debit_total': init_debit_total,
            'init_credit_total': init_credit_total,
            'final_debit_total': final_debit_total,
            'final_credit_total': final_credit_total,
            'docs': docs,
            'time': time,
            'Accounts': account_res,
        }

    @api.model
    def create(self, vals):
        vals['target_move'] = 'posted'

        # get this month as default date filter
        today = date.today()
        this_month_first_date = today.replace(day=1)
        this_month_last_date = today.replace(day = calendar.monthrange(today.year, today.month)[1])
        vals['date_from'] = this_month_first_date
        vals['date_to'] = this_month_last_date

        res = super(TrialView, self).create(vals)
        return res

    def write(self, vals):
        if vals.get('target_move'):
            vals.update({'target_move': vals.get('target_move').lower()})
        if vals.get('journal_ids'):
            vals.update({'journal_ids': [(6, 0, vals.get('journal_ids'))]})
        if vals.get('journal_ids') == []:
            vals.update({'journal_ids': [(5,)]})

        if vals.get('date_from') and not vals.get('date_to'):
            vals.update({'date_to': ''})
        if vals.get('date_to') and not vals.get('date_from'):
            vals.update({'date_from': ''})
        if not vals.get('date_from') and not vals.get('date_to'):
            vals.update({'date_from': '', 'date_to': ''})

        res = super(TrialView, self).write(vals)
        return res

    def _get_accounts(self, accounts, display_account, data):

        account_result = {}
        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        tables = tables.replace('"', '')
        if not tables:
            tables = 'account_move_line'
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        if data['target_move'] == 'posted':
            filters += " AND account_move_line.parent_state = 'posted'"
        else:
            filters += " AND account_move_line.parent_state in ('draft','posted')"
        if data.get('date_from'):
            filters += " AND account_move_line.date >= '%s'" % data.get('date_from')
        if data.get('date_to'):
            filters += " AND account_move_line.date <= '%s'" % data.get('date_to')

        if data['journals']:
            filters += ' AND jrnl.id IN %s' % str(tuple(data['journals'].ids) + tuple([0]))
        tables += ' JOIN account_journal jrnl ON (account_move_line.journal_id=jrnl.id)'
        # compute the balance, debit and credit for the provided accounts
        request = (
                    "SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" + \
                    " FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
        params = (tuple(accounts.ids),) + tuple(where_params)
        self.env.cr.execute(request, params)
        for row in self.env.cr.dictfetchall():
            account_result[row.pop('id')] = row

        # get accounts to display
        self.env.cr.execute("""SELECT DISTINCT(account_id) FROM account_move_line""")
        display_account_ids = self.env.cr.fetchall()
        # convert list of tuples to list
        display_account_ids = [id for t in display_account_ids for id in t]

        account_res = []
        for account in accounts:
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance', 'total_debit_balance', 'total_credit_balance'])
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res['code'] = account.code
            res['name'] = account.name
            res['id'] = account.id
            if data.get('date_from'):

                res['Init_balance'] = self.get_init_bal(account, display_account, data)

            if account.id in account_result:
                res['debit'] = account_result[account.id].get('debit')
                res['credit'] = account_result[account.id].get('credit')
                res['balance'] = account_result[account.id].get('balance')

            total_balance = res['balance'] + res['Init_balance']['balance'] if 'Init_balance' in res and res['Init_balance'] else res['balance']
            if total_balance > 0:
                res['total_debit_balance'] = total_balance
            if total_balance < 0:
                res['total_credit_balance'] = total_balance * -1

            # if display_account == 'all':
            #     account_res.append(res)
            # if display_account == 'not_zero' and not currency.is_zero(
            #         res['balance']):
            #     account_res.append(res)
            # if display_account == 'movement' and (
            #         not currency.is_zero(res['debit']) or not currency.is_zero(
            #         res['credit'])):
            #     account_res.append(res)
            
            if res['id'] in display_account_ids:
                account_res.append(res)
                
        return account_res

    def get_init_bal(self, account, display_account, data):
        if data.get('date_from'):

            tables, where_clause, where_params = self.env[
                'account.move.line']._query_get()
            tables = tables.replace('"', '')
            if not tables:
                tables = 'account_move_line'
            wheres = [""]
            if where_clause.strip():
                wheres.append(where_clause.strip())
            filters = " AND ".join(wheres)
            if data['target_move'] == 'posted':
                filters += " AND account_move_line.parent_state = 'posted'"
            else:
                filters += " AND account_move_line.parent_state in ('draft','posted')"
            if data.get('date_from'):
                filters += " AND account_move_line.date < '%s'" % data.get('date_from')

            if data['journals']:
                filters += ' AND jrnl.id IN %s' % str(tuple(data['journals'].ids) + tuple([0]))
            tables += ' JOIN account_journal jrnl ON (account_move_line.journal_id=jrnl.id)'

            # compute the balance, debit and credit for the provided accounts
            request = (
                    "SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" + \
                    " FROM " + tables + " WHERE account_id = %s" % account.id + filters + " GROUP BY account_id")
            params = tuple(where_params)
            self.env.cr.execute(request, params)
            for row in self.env.cr.dictfetchall():
                return row

    @api.model
    def _get_currency(self):
        journal = self.env['account.journal'].browse(
            self.env.context.get('default_journal_id', False))
        if journal.currency_id:
            return journal.currency_id.id
        lang = self.env.user.lang
        if not lang:
            lang = 'en_US'
        lang = lang.replace("_", '-')
        currency_array = [self.env.company.currency_id.symbol,
                          self.env.company.currency_id.position,
                          lang]
        return currency_array

    def get_dynamic_xlsx_report(self, data, response ,report_data, dfr_data):
        report_data_main = json.loads(report_data)
        output = io.BytesIO()
        total = json.loads(dfr_data)
        filters = json.loads(data)
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        head = workbook.add_format({'bold': True,
                                    'font_size': 15})
        head.set_align('center')
        head.set_align('vcenter')
        sub_heading = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': 14,
             'border': 1,
             'border_color': 'black'})
        txt = workbook.add_format({'font_size': 14, 'border': 1})
        txt_account = workbook.add_format({'font_size': 14, 'border': 1, 'font_color': '#00A09D'})
        txt_l = workbook.add_format({'font_size': 14, 'border': 1, 'bold': True})
        sheet.merge_range('A2:H3', filters.get('company_name') + ':' + ' Trial Balance', head)
        date_head = workbook.add_format({'align': 'center', 'bold': True,
                                         'font_size': 11})
        date_head.set_align('center')
        date_head.set_align('vcenter')
        date_style = workbook.add_format({'align': 'center',
                                          'font_size': 14})
        if filters.get('date_from'):
            sheet.merge_range('C4:D4', 'From: '+filters.get('date_from') , date_head)
        if filters.get('date_to'):
            sheet.merge_range('E4:F4', 'To: '+ filters.get('date_to'), date_head)
        sheet.merge_range('A5:H6', 'Journals: ' + ', '.join([ lt or '' for lt in filters['journals'] ]) + '  Target Moves: '+ filters.get('target_move'), date_head)
        sheet.write('A7', 'Code', sub_heading)
        sheet.write('B7', 'Account', sub_heading)
        if filters.get('date_from'):
            sheet.write('C7', 'Initial Debit', sub_heading)
            sheet.write('D7', 'Initial Credit', sub_heading)
            sheet.write('E7', 'Current Debit', sub_heading)
            sheet.write('F7', 'Current Credit', sub_heading)
            sheet.write('G7', 'Total Debit', sub_heading)
            sheet.write('H7', 'Total Credit', sub_heading)
        else:
            sheet.write('C7', 'Debit', sub_heading)
            sheet.write('D7', 'Credit', sub_heading)

        row = 6
        col = 0
        sheet.set_column(5, 0, 10)
        sheet.set_column(6, 1, 50)
        sheet.set_column(7, 2, 15)
        if filters.get('date_from'):
            sheet.set_column(8, 3, 15)
            sheet.set_column(9, 4, 15)
            sheet.set_column(10, 5, 15)
            sheet.set_column(11, 6, 15)
            sheet.set_column(12, 7, 15)
            sheet.set_column(13, 8, 15)
        else:

            sheet.set_column(8, 3, 15)
            sheet.set_column(9, 4, 15)
        for rec_data in report_data_main:

            row += 1
            sheet.write(row, col, rec_data['code'], txt_account)
            sheet.write(row, col + 1, rec_data['name'], txt_account)
            if filters.get('date_from'):
                if rec_data.get('Init_balance'):
                    sheet.write(row, col + 2, rec_data['Init_balance']['debit'], txt)
                    sheet.write(row, col + 3, rec_data['Init_balance']['credit'], txt)
                else:
                    sheet.write(row, col + 2, 0, txt)
                    sheet.write(row, col + 3, 0, txt)

                sheet.write(row, col + 4, rec_data['debit'], txt)
                sheet.write(row, col + 5, rec_data['credit'], txt)
                sheet.write(row, col + 6, rec_data['total_debit_balance'], txt)
                sheet.write(row, col + 7, rec_data['total_credit_balance'], txt)

            else:
                sheet.write(row, col + 2, rec_data['debit'], txt)
                sheet.write(row, col + 3, rec_data['credit'], txt)
        sheet.write(row+1, col, 'Total', sub_heading)
        if filters.get('date_from'):
            sheet.write(row + 1, col + 2, total.get('init_debit_total'), txt_l)
            sheet.write(row + 1, col + 3, total.get('init_credit_total'), txt_l)
            sheet.write(row + 1, col + 4, total.get('debit_total'), txt_l)
            sheet.write(row + 1, col + 5, total.get('credit_total'), txt_l)
            sheet.write(row + 1, col + 6, total.get('final_debit_total'), txt_l)
            sheet.write(row + 1, col + 7, total.get('final_credit_total'), txt_l)
        else:
            sheet.write(row + 1, col + 2, total.get('debit_total'), txt_l)
            sheet.write(row + 1, col + 3, total.get('credit_total'), txt_l)

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
