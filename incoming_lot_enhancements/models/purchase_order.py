# -*- coding: utf-8 -*-

from odoo import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    @api.multi
    def _create_picking(self):
        res = super(PurchaseOrder,self)._create_picking()
        for order in self:
            for picking in order.picking_ids.filtered(lambda pc : pc.picking_type_id.code == 'incoming'):
                for line in picking.move_line_ids_without_package:
                    if not line.lot_name:
                        lot_number = self.env.ref('incoming_lot_enhancements.sequence_operation_product').next_by_id()
                        line.write({'lot_name': lot_number})
                
        return res