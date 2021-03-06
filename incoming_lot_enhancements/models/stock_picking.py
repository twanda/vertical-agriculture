# -*- coding: utf-8 -*-

from odoo import fields, models, api


class Picking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_confirm(self):
        rec = super(Picking, self).action_confirm()
        for picking in self:
            if picking.picking_type_id.code == 'incoming':
                for line in picking.move_line_ids_without_package:
                    if not line.lot_name:
                        lot_number = self.env.ref('incoming_lot_enhancements.sequence_operation_product').next_by_id()
                        line.write({'lot_name': lot_number})
        return rec

    
    @api.multi
    def _create_backorder(self, backorder_moves=[]):
        
        backorders = super(Picking,self)._create_backorder(backorder_moves)
        for picking in backorders:
            if picking.picking_type_id.code == 'incoming':
                for line in picking.move_line_ids_without_package:
                    if not line.lot_name:
                        lot_number = self.env.ref('incoming_lot_enhancements.sequence_operation_product').next_by_id()
                        line.write({'lot_name': lot_number})
        return backorders
