from odoo.http import request
from datetime import datetime
import logging
import requests
from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.openeducat_rest.controllers.main import ObjectEncoder
from odoo.http import Response
from odoo.addons.pm_rest_api.controllers.aba_payway import ABAPayWay
import json
from user_agents import parse

_logger = logging.getLogger(__name__)

class PaymentPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(PaymentPortal, self)._prepare_portal_layout_values()
        user = request.env.user
        student_id = request.env["op.student"].sudo().search(
            [('user_id', '=', user.id)])
        payment_count = request.env['op.student.fees.details'].sudo().search_count(
            [('student_id', '=', student_id.id)])
        values['payment_count'] = payment_count
        return values



    @http.route(['/student/payment/',
                 '/student/payment/<int:tran_id>'],
                type='http', auth="user", website=True)
    def portal_student_payment_list(self):
        user = request.env.user
        student = request.env["op.student"].sudo().search(
            [('user_id', '=', user.id)])

        val = self._prepare_portal_layout_values()

        payments = request.env['op.student.fees.details'].sudo().search(
            [('student_id', '=', student.id)])

        val['payment_ids'] = payments
        print(val)

        return request.render("pm_rest_api.pm_student_portal_apyment_detail", val)

    @http.route(['/student/payment/create/<string:type>/<int:payment_id>'],
                type='http', auth="user", website=True)
    def portal_create_payment(self, payment_id, type):
        PayWay = ABAPayWay()

        object = 'op.student.fees.details'
        tran_id = ''
        if type == "installment":
            tran_id = 'PP-' + str(payment_id)
            object = 'pm.student.installment'
        elif type == "normal":
            tran_id = 'FP-' + str(payment_id)

        merchant_id = PayWay.get_merchant_id()
        payment_obj = request.env[object].sudo().browse(payment_id)
        getItems = PayWay.get_transaction_items(payment_obj)
        hash_data = PayWay.get_hash(str(merchant_id), str(tran_id), str(payment_obj.amount), str(getItems['items']))
        api_url = PayWay.get_api_url()
        push_back_url = PayWay.get_push_back_url()
        student = payment_obj.student_id or payment_obj.fee_id.student_id
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        success_url = base_url + '/student/aba/success'
        print("*******-*********")
        print(success_url)

        val = {
            'hash': hash_data,
            'amount': str(payment_obj.amount),
            'amount_display': str(payment_obj.amount)+'$',
            'firstname': student.first_name,
            'lastname': student.last_name,
            'continue_success_url': success_url,
            'email': student.email,
            'phone': student.mobile,
            'tran_id': tran_id,
            'url': api_url,
            'push_back_url': push_back_url,
            'items': getItems['items']
        }
        print(val)
        return request.render("pm_rest_api.pm_payment_form_custom", val)

    @http.route(['/student/payment/generate/<string:type>/<int:payment_id>'],
                type='http', auth="user", website=True)
    def portal_generate_payment(self, payment_id, type):
        PayWay = ABAPayWay()
        merchant_id = PayWay.get_merchant_id()
        object = 'op.student.fees.details'
        tran_id = ''
        if type == "installment":
            tran_id = 'PP-' + str(payment_id)
            object = 'pm.student.installment'
        elif type == "normal":
            tran_id = 'FP-' + str(payment_id)
        payment_obj = request.env[object].sudo().browse(payment_id)
        getItems = PayWay.get_transaction_items(payment_obj)
        print(getItems)
        hash_data = PayWay.get_hash(str(merchant_id), str(tran_id), str(payment_obj.amount), str(getItems['items']))
        api_url = PayWay.get_api_url()
        push_back_url = PayWay.get_push_back_url()
        student = payment_obj.student_id or payment_obj.fee_id.student_id
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        success_url = base_url + '/student/aba/success'
        print("*******-*********")
        print(success_url)

        val = {
            'hash': hash_data,
            'amount': str(payment_obj.amount),
            'amount_display': str(payment_obj.amount)+'$',
            'firstname': student.first_name,
            'lastname': student.last_name,
            'continue_success_url': success_url,
            'email': student.email,
            'phone': student.mobile,
            'tran_id': tran_id,
            'url': api_url,
            'payment_option': 'abapay_deeplink',
            'push_back_url': push_back_url,
            'items': getItems['items'],
            'display_items': getItems['raw_items'],
        }
        print(val)
        return Response(json.dumps(val, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=200)

    

    @http.route(['/student/aba/success'],
                type='http', auth='public', website=True)
    def student_payment_success(self):
        environ = request.httprequest.headers.environ
        agent_string = environ.get("HTTP_USER_AGENT")
        user_agent = parse(agent_string)
        if user_agent.is_mobile:
            print("I am from Mobile")
            return request.redirect('acac://payment')
        else:
            print("I am from PC!!")
            return request.render("pm_rest_api.pm_payment_success_form")

    @http.route(['/student/aba/check/transaction/<string:id>'],
                type='http', auth='public', website=True)
    def check_transaction_status(self, id):
        PayWay = ABAPayWay()
        merchant_id = PayWay.get_merchant_id()
        api_url = PayWay.get_api_url()+'check/transaction/'
        hash = PayWay.get_hash_check(str(merchant_id), str(id))
        params = {
            'tran_id': id,
            'hash': hash
        }
        req = requests.post(api_url, data=params)
        data = req.json()
        return Response(req, content_type='application/json;charset=utf-8', status=200)

    @http.route(['/student/aba/pushback'],
                type='http', methods=['POST'], auth='public', csrf=False)
    def student_payment_push_back(self, **post):
        response = post.get('response')
        _logger.info("***************tran_id %s " % (post))
        _logger.info("***************type %s " % (type(post)))
        data = json.loads(response)
        _logger.info("***************type %s " % (data))
        _logger.info("***************type %s " % (type(data)))
        tran_id = data['tran_id']
        status = data['status']
        _logger.info(
            "***************tran_id %s " % (tran_id)
        )
        _logger.info(
            "**************status %s " % (status)
        )

        # tran_id = 'FP-268'
        tran_split = tran_id.split('-')
        tran_code = tran_split[0]
        id = tran_split[1]
        obj = ''
        if tran_code == 'PP':
            obj = 'pm.student.installment'
        elif tran_code == 'FP':
            obj = 'op.student.fees.details'

        transaction_obj = request.env['pm.aba.transaction'].sudo()
        transaction_obj.create({
            'transaction_number': tran_id,
            'status': 'approved'
        })
        student_fee = request.env[obj].sudo().search([('id', '=', id)])

        invoice = student_fee.invoice_id
        print(invoice)
        payment_method = 3
        journal_id = 7
        invoice.action_post()
        payment_data = {
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': invoice.partner_id.id,
            'amount': invoice.amount_total,
            'create_date': datetime.today(),
            'payment_method_id': payment_method,
            'journal_id': journal_id,
            'payment_reference': invoice.name
        }
        account_payment = request.env['account.payment'].sudo().create(payment_data)
        account_payment.action_post()
        print(account_payment)










