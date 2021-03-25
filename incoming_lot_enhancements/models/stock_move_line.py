# -*- coding: utf-8 -*-

from odoo import models, api


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.model
    def default_get(self, fields):
        rec = super(StockMoveLine, self).default_get(fields)
        if self._context.get('add_lot_number_name', False):
            lot_number = self.env.ref('incoming_lot_enhancements.sequence_operation_product').next_by_id()
            rec['lot_name'] = lot_number
        return rec
