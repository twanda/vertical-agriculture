# -*- coding: utf-8 -*-

from odoo import models, api


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.model
    def default_get(self, fields):
        rec = super(StockMoveLine, self).default_get(fields)
        if self._context.get('add_lot_number_name', False):
            picking = self.env['stock.picking'].browse(self._context['add_lot_number_name'])
            if picking.picking_type_id.code == 'incoming':
                for line in picking.move_ids_without_package:
                    if line.product_id.type == 'product':
                        rec['product_id'] = line.product_id.id
                        rec['location_dest_id'] = line.location_dest_id.id
                        break
                lot_number = self.env.ref('incoming_lot_enhancements.sequence_operation_product').next_by_id()
                rec['lot_name'] = lot_number
        return rec
