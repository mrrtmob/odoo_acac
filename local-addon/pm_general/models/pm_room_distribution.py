
from odoo import models, api, fields, exceptions, _


class OpRoomDistributionCustom(models.TransientModel):
    _inherit = "op.room.distribution"
    class_id = fields.Many2one('op.classroom', 'Class')


class OpHeldExam(models.TransientModel):
    _inherit = "op.held.exam"
    class_id = fields.Many2one('op.classroom', 'Class')

