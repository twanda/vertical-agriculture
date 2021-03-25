# -*- coding: utf-8 -*-

from odoo import fields, models, api


class Picking(models.Model):
    _inherit = 'stock.picking'

    operation_product_id = fields.Many2one('product.product', 'Operation Product', compute="_compute_product_operation")

    @api.depends('move_ids_without_package.product_id')
    def _compute_product_operation(self):
        for line in self.move_ids_without_package:
            if line.product_id.type == 'product':
                self.operation_product_id = line.product_id.id
                break

    @api.multi
    def action_confirm(self):
        rec = super(Picking, self).action_confirm()
        for line in self.move_line_ids_without_package:
            lot_number = self.env.ref('incoming_lot_enhancements.sequence_operation_product').next_by_id()
            line.write({'lot_name': lot_number})
        return rec
