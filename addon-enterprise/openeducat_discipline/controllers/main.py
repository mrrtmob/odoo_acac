# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

import base64
import logging

from odoo.http import request

from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal

_logger = logging.getLogger(__name__)


class DisciplinePortal(CustomerPortal):

    @http.route(['/student/apology/letter',
                 '/student/apology/letter/<int:discipline_id>',
                 '/student/apology/letter/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_student_descipline_letter(self, discipline_id, **kw):

        if discipline_id:
            discipline_ids = request.env['op.discipline'].sudo().search([
                ('id', '=', discipline_id)])
        else:
            return request.render('website.404')

        return request.render(
            "openeducat_discipline.portal_student_submit_letter",
            {
                'discipline_ids': discipline_ids,
                'subject_name':
                    discipline_ids.student_id.name + " Apology letter",
                'page_name': 'appology_form'
            }
        )

    @http.route(['/student/apology/letter/submit',
                 '/student/apology/letter/submit/<int:discipline_id>',
                 '/student/apology/letter/submit/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_student_submit_apology_letter(self, discipline_id=None, **kw):

        attechment_list = []
        if 'attachments' in request.params:
            attached_files = request.httprequest.files.getlist('attachments')
            for attachment in attached_files:
                attached_file = attachment.read()
                attachment = request.env['ir.attachment'].sudo().create({
                    'name': attachment.filename,
                    'res_model': 'op.discipline',
                    'res_id': discipline_id,
                    'type': 'binary',
                    # 'name': attachment.filename,
                    'datas': base64.encodestring(attached_file),
                })
                attechment_list.append(attachment.id)

            vals = {
                'subject': kw['list_name'],
                'body_html': kw['content'],
                'email_to': request.httprequest.form.getlist('partner'),
                'email_from': 'nikbhai@gmail.com',
            }

        request.env["mail.mail"].sudo().create(vals)

        template = request.env.ref(
            'openeducat_discipline.email_student_apology_letter_template',
            raise_if_not_found=False)

        discipline = request.env['op.discipline'].sudo().search([
            ('id', '=', discipline_id)])
        if vals.get('email_to'):
            for rec in vals.get('email_to'):
                partner_id = request.env['res.partner'].sudo().search([
                    ('email', '=', rec)])
                if partner_id and template:
                    template.sudo().write({'email_to': rec})
                    template.sudo().write({'body_html': kw['content']})
                    template.sudo().write({'subject': kw['list_name']})
                    template.sudo().write(
                        {'attachment_ids': [(6, 0, attechment_list)]})
                    template.sudo().send_mail(discipline.id,
                                              force_send=True,
                                              raise_exception=True)
        return request.redirect("/student/profile")

    @http.route(['/student/discipline/data/<int:semester_id>',
                 '/student/discipline/data/<int:student_id>/<int:semester_id>', ],
                type='http', auth="user", website=True)
    def portal_student_discipline_form(self, student_id=None, semester_id=None, ):

        user = request.env.user
        student_id = request.env["op.student"].sudo().search(
            [('user_id', '=', user.id)])
        student_discipline = request.env['pm.student.discipline'].sudo().search(
            [('student_id', '=', student_id.id), ('semester_id', '=', semester_id)])

        disciplines = request.env['op.discipline'].sudo().search([('student_discipline_id', '=', student_discipline.id)])

        return request.render(
            "pm_general.pm_student_portal_discipline_detail",
            {'student_discipline': student_discipline,
             'disciplines': disciplines,
             'student': student_id,
             'page_name': 'discipline_detail'})
