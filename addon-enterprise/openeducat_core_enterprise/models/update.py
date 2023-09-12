# -*- coding: utf-8 -*-
###############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech-Receptives(<http://www.techreceptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################


from odoo import api
from odoo.models import AbstractModel


class PublisherWarrantyContract(AbstractModel):
    _inherit = "publisher_warranty.contract"

    @api.model
    def _get_message_logs(self):

        res = super(PublisherWarrantyContract, self)._get_message_logs()
        IrParamSudo = self.env['ir.config_parameter'].sudo()
        openeducat_instance_key = IrParamSudo.get_param(
            'database.openeducat_instance_key')
        openeducat_instance_hash_key = IrParamSudo.get_param(
            'database.openeducat_instance_hash_key')
        openeducat_hash_validate_date = IrParamSudo.get_param(
            'database.hash_validated_date')
        openeducat_expiration_date = IrParamSudo.get_param(
            'database.openeducat_expire_date')

        res.update({
            "openeducat_hash_validate_date": openeducat_hash_validate_date,
            "enterprise_code": str(openeducat_instance_key
                                   ) + "," + str(openeducat_instance_hash_key),
            "openeducat_expire_date": openeducat_expiration_date,
        })
        return res
