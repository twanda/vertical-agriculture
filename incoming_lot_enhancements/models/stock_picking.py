# -*- coding: utf-8 -*-

from odoo import fields, models, api


class Picking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_confirm(self):
        rec = super(Picking, self).action_confirm()
        for line in self.move_line_ids_without_package:
            lot_number = self.env.ref('incoming_lot_enhancements.sequence_operation_product').next_by_id()
            line.write({'lot_name': lot_number})
        return rec
