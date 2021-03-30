# -*- coding: utf-8 -*-

from odoo import models,fields,api,_


class StockPicking(models.Model):
    
    _inherit = "stock.picking"
    
    def _prepare_catch_weight_move_default_values(self, line, picking, new_picking, quantity, location_id, location_dest_id):
        vals = {
            'product_id': line.product_id.id,
            'product_uom_qty': quantity,
            'product_uom': line.product_id.uom_id.id,
            'picking_id': new_picking.id,
            'state': 'draft',
            'date_expected': fields.Datetime.now(),
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'picking_type_id': new_picking.picking_type_id.id,
            'warehouse_id': picking.picking_type_id.warehouse_id.id,
            'origin_returned_move_id': line.id,
            'procure_method': 'make_to_stock',
            'to_refund': True,
        }
        return vals
    
    
    @api.multi
    def _create_catch_weight_backorder(self, backorder_quantity_to_add,picking_weight,weight_difference):
        """ Move all non-done lines into a new backorder picking.
        """
        backorders = self.env['stock.picking']
        for picking in self:
            moves_to_backorder = picking.move_ids_without_package.filtered(lambda x: x.state in ('done'))
            if moves_to_backorder:
                backorder_picking = picking.copy({
                    'name': '/',
                    'move_lines': [],
                    'move_line_ids': [],
                    'backorder_id': picking.id,
                    'state': 'draft',
                })
                picking.message_post(
                    body=_('The backorder <a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a> has been created.') % (
                        backorder_picking.id, backorder_picking.name))
                
                lines = 0
                mv_list = []
                for line in picking.move_lines:
                    if line.quantity_done != 0:
                        lines += 1
                        quantity = abs(line.quantity_done / picking_weight * weight_difference)
                        vals = self._prepare_catch_weight_move_default_values(line, picking, backorder_picking, quantity, picking.location_id.id, picking.location_dest_id.id)
                        mv_list.append((0, 0, vals))
                        r = line.copy(vals)
                        vals = {}
                        move_orig_to_link = line.move_dest_ids.mapped('returned_move_ids')
                        move_orig_to_link |= line
                        move_orig_to_link |= line.mapped('move_dest_ids').filtered(lambda m: m.state not in ('cancel')) \
                            .mapped('move_orig_ids').filtered(lambda m: m.state not in ('cancel'))
                        move_dest_to_link = line.move_orig_ids.mapped('returned_move_ids')
                        move_dest_to_link |= line.move_orig_ids.mapped('returned_move_ids') \
                            .mapped('move_orig_ids').filtered(lambda m: m.state not in ('cancel')) \
                            .mapped('move_dest_ids').filtered(lambda m: m.state not in ('cancel'))
                        vals['move_orig_ids'] = [(4, m.id) for m in move_orig_to_link]
                        vals['move_dest_ids'] = [(4, m.id) for m in move_dest_to_link]
                        r.write(vals)
                
                for mv_line in backorder_picking.move_ids_without_package:
                    if mv_line.product_id.id in backorder_quantity_to_add:
                        mv_line.product_uom_qty = backorder_quantity_to_add[mv_line.product_id.id]
                backorder_picking.action_assign()
                
                if backorder_picking.picking_type_id.code == 'incoming':
                    for line in backorder_picking.move_line_ids_without_package:
                        if not line.lot_name:
                            lot_number = self.env.ref('incoming_lot_enhancements.sequence_operation_product').next_by_id()
                            line.write({'lot_name': lot_number})
                backorders |= backorder_picking
                
class StockMove(models.Model):
    
    _inherit = 'stock.move'
    
    
    catch_parent_move_id = fields.Many2one('stock.move',string='Parent Catch Move')
    is_catch_weight_move = fields.Boolean(string='Is Catch Weight Move',default=False)
    
    
class StockMoveLine(models.Model):
    
    _inherit="stock.move.line"
    
    catch_parent_move_line_ref = fields.Char(string='Parent Move Line Ref')
    