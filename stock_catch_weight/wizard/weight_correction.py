# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError
import time


class WeightCorrection(models.TransientModel):
    _name = 'weight.correction'

    actual_weight = fields.Float(string="Actual Weight", required=True)

    def action_weight_correction(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            picking = self.env['stock.picking'].browse(active_id)
            if picking.exists():
                picking_weight = sum(picking.move_line_ids_without_package.mapped('qty_done'))
                actual_weight = self.actual_weight
                return self.create_catch_weight(picking, actual_weight, picking_weight)

    def _prepare_move_default_values(self, line, picking, new_picking, quantity, location_id, location_dest_id):
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

    def _prepare_move_line_values(self, line, picking, new_picking, quantity):
        vals = {
            'product_id': line.product_id.id,
            'qty_done': quantity,
            'product_uom_id': line.product_uom_id.id,
            'picking_id': new_picking.id,
            'state': 'draft',
            'date_expected': fields.Datetime.now(),
            'location_id': line.location_dest_id.id,
            'location_dest_id': line.location_id.id,
            'picking_type_id': new_picking.picking_type_id.id,
            'warehouse_id': picking.picking_type_id.warehouse_id.id,
            'origin_returned_move_id': line.id,
            'move_id': line.move_id.id,
            'lot_id': line.lot_id.id if line.lot_id else False,
            'procure_method': 'make_to_stock',
            'to_refund': True,
        }
        return vals
    
    def _prepare_backorder_move_line_values(self, line, picking, new_picking, quantity):
        vals = {
            'product_id': line.product_id.id,
            'product_uom_qty': quantity,
            'product_uom_id': line.product_uom_id.id,
            'picking_id': new_picking.id,
            'state': 'draft',
            'date_expected': fields.Datetime.now(),
            'location_id': line.location_id.id,
            'location_dest_id': line.location_dest_id.id,
            'picking_type_id': picking.picking_type_id.id,
            'warehouse_id': picking.picking_type_id.warehouse_id.id,
            'lot_id': line.lot_id.id if line.lot_id else False,
            'procure_method': 'make_to_stock',
            'to_refund': True,
            'lot_name' : line.lot_id.name if line.lot_id else False
        }
        return vals
    
    def _prepare_extra_weight_move_line_values(self,line,picking,new_picking,quantity):
        vals = {
            'product_id': line.product_id.id,
            'qty_done': quantity,
            'product_uom_id': line.product_uom_id.id,
            'picking_id': new_picking.id,
            'state': 'draft',
            'date_expected': fields.Datetime.now(),
            'location_id': line.location_id.id,
            'location_dest_id': line.location_dest_id.id ,
            'picking_type_id': new_picking.picking_type_id.id,
            'warehouse_id': picking.picking_type_id.warehouse_id.id,
            'origin_returned_move_id': line.id,
            'move_id': line.move_id.id,
            'lot_id': line.lot_id.id if line.lot_id else False,
            'procure_method': 'make_to_stock',
            'to_refund': True,
        }
        return vals
        

    def get_original_qty(self, move_line_ids, product_id, location_id, lot_id):
        if lot_id:
            filtered_lines = move_line_ids.filtered(lambda ml: ml.product_id.id == product_id.id
                                                  and ml.location_dest_id.id == location_id.id and ml.lot_id.id == lot_id.id)
            move_line_ids -= filtered_lines
            return filtered_lines.qty_done, move_line_ids
        else:
            filtered_lines = move_line_ids.filtered(lambda ml: ml.product_id.id == product_id.id
                                                               and ml.location_dest_id.id == location_id.id)
            move_line_ids -= filtered_lines
            return filtered_lines.qty_done, move_line_ids

    def _create_catch_weight(self, picking, actual_weight, picking_weight):
        for catch_weight_move in picking.move_line_ids_without_package.mapped('move_id'):
            catch_weight_move.move_dest_ids.filtered(lambda m: m.state not in ('done', 'cancel'))._do_unreserve()

        weight_difference = actual_weight - picking_weight
        
        picking_type_id = False
        
        if weight_difference > 0:
            location_id = picking.location_id.id
            location_dest_id = picking.location_dest_id.id
            picking_type_id = picking.picking_type_id.id
        
        elif weight_difference < 0:
            location_id = picking.location_dest_id.id
            location_dest_id = picking.location_id.id
            picking_type_id = picking.picking_type_id.return_picking_type_id.id

        new_picking = picking.copy({
            'move_lines': [],
            'picking_type_id': picking_type_id,
            'state': 'draft',
            'origin': _("Catch Weight of %s") % picking.name,
            'location_id': location_id,
            'location_dest_id': location_dest_id})
        new_picking.message_post_with_view('mail.message_origin_link',
                                           values={'self': new_picking, 'origin': picking},
                                           subtype_id=self.env.ref('mail.mt_note').id)
        lines = 0
        mv_list = []
        for line in picking.move_lines:
            if line.quantity_done != 0:
                lines += 1
                quantity = abs(line.quantity_done / picking_weight * weight_difference)
                vals = self._prepare_move_default_values(line, picking, new_picking, quantity, location_id, location_dest_id)
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
        if not lines:
            raise UserError(_("Please specify at least one non-zero quantity."))
        new_picking.action_confirm()
        new_picking.action_assign()
        
        picking_backorder_id = self.env['stock.picking'].search([('backorder_id','=',picking.id),('state','not in',['done','cancel'])])
        
        if weight_difference < 0:
            move_line_ids = picking.move_line_ids
            backorder_mv_lines = []
            
            for mv_line in new_picking.move_ids_without_package:
                # for l_line in mv_line.move_line_ids:
                    # qty, move_line_ids = self.get_original_qty(move_line_ids, l_line.product_id, l_line.location_id, l_line.lot_id)
                    # quantity = abs(qty / picking_weight * weight_difference)
                    # l_line.qty_done = quantity
                    
                mv_list = []
                for o_line in move_line_ids.filtered(lambda ml : ml.move_id  ==  mv_line.origin_returned_move_id):
                    
                    catch_parent_move_line_ref = str(time.time())
                    quantity = abs(o_line.qty_done / picking_weight * weight_difference)
                    o_vals = self._prepare_move_line_values(o_line, picking, new_picking, quantity)
                    o_vals.update({'catch_parent_move_line_ref':catch_parent_move_line_ref})
                    mv_list.append((0, 0, o_vals))
                    
                    if picking_backorder_id:
                        back_vals = self._prepare_backorder_move_line_values(o_line, picking, picking_backorder_id, quantity)
                        back_vals.update({'catch_parent_move_line_ref':catch_parent_move_line_ref})
                        backorder_mv_lines.append((0, 0, back_vals))
                        
                mv_line.move_line_ids.unlink()
                mv_line.move_line_ids = mv_list
                
            if picking_backorder_id:
                backorder_move_ids_without_package_list = []
                for miwp_id in new_picking.move_ids_without_package:
                    move_id_vals = {
                        'product_id' : miwp_id.product_id.id,'product_uom' : miwp_id.product_uom.id,
                        'product_uom_qty' : miwp_id.product_uom_qty,'name' : miwp_id.name,
                        'location_id' : miwp_id.location_dest_id.id,'location_dest_id' : miwp_id.location_id.id,
                        'procure_method': 'make_to_stock', 'picking_id' : picking_backorder_id.id,
                        'catch_parent_move_id' : miwp_id.id,'picking_type_id' : picking.picking_type_id.id,
                    }
                    backorder_move_ids_without_package_list.append((0,0,move_id_vals))
                    
                picking_backorder_id.write({'move_ids_without_package':backorder_move_ids_without_package_list})
                backorder_move_ids = picking_backorder_id.move_ids_without_package.sorted('id',reverse=True)
                
                for ml in range(0,len(backorder_move_ids_without_package_list)):
                    current_move_id = backorder_move_ids[ml]
                    parent_catch_move_id = current_move_id.catch_parent_move_id
                    for pml in parent_catch_move_id.move_line_ids:
                        for bmvl in backorder_mv_lines:
                            if pml.catch_parent_move_line_ref == bmvl[2]['catch_parent_move_line_ref']:
                                bmvl[2]['move_id'] = current_move_id.id                
                picking_backorder_id.write({'move_line_ids':backorder_mv_lines})
        
        if weight_difference > 0:
            move_line_ids = picking.move_line_ids
            for mv_line in new_picking.move_ids_without_package:
                mv_list = []
                for o_line in move_line_ids.filtered(lambda ml : ml.move_id  ==  mv_line.origin_returned_move_id):
                    quantity = abs(o_line.qty_done / picking_weight * weight_difference)
                    o_vals = self._prepare_extra_weight_move_line_values(o_line, picking, new_picking, quantity)
                    mv_list.append((0, 0, o_vals))
                
                mv_line.move_line_ids.unlink()
                mv_line.move_line_ids = mv_list
                
            if picking_backorder_id:
                total_backorder_qty = picking_backorder_id.move_ids_without_package.mapped('product_uom_qty')[0]
                divided_qty = weight_difference / len(picking_backorder_id.move_ids_without_package)
                
                if total_backorder_qty - weight_difference > 0:
                    for mviwp_id in picking_backorder_id.move_ids_without_package:
                        if mviwp_id.product_uom_qty - divided_qty > 0:
                            mviwp_id.write({'product_uom_qty':mviwp_id.product_uom_qty - divided_qty})
                        else:
                            mviwp_id.write({'product_uom_qty':0.0})
                else:
                    for mviwp_id in picking_backorder_id.move_ids_without_package:
                        mviwp_id.write({'product_uom_qty':0.0})
                        
                    self.create_reverse_picking_for_extra_weight(picking_backorder_id,picking,total_backorder_qty,weight_difference)
        return new_picking.id, picking_type_id
    
    
    
    def create_reverse_picking_for_extra_weight(self,backorder_id,picking,total_backorder_qty,weight):        
        location_id = picking.location_dest_id.id
        location_dest_id = picking.location_id.id
        picking_type_id = picking.picking_type_id.return_picking_type_id.id
        
        new_picking = backorder_id.copy({
            'move_lines': [],
            'picking_type_id': picking_type_id,
            'state': 'draft',
            'origin': _("Reverse Transfer for extra weight of %s") % backorder_id.name,
            'location_id': location_id,
            'location_dest_id': location_dest_id})
        new_picking.message_post_with_view('mail.message_origin_link',
                                           values={'self': new_picking, 'origin': picking},
                                           subtype_id=self.env.ref('mail.mt_note').id)
        
        lines = 0
        mv_list = []
        
        total_return_qty = abs(total_backorder_qty - weight)
        divided_qty = total_return_qty / len(picking.move_lines)
        
        for line in picking.move_lines:
            if line.quantity_done != 0:
                lines += 1
                vals = self._prepare_move_default_values(line, picking, new_picking, divided_qty, location_id, location_dest_id)
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
        

    def create_catch_weight(self, picking, actual_weight, picking_weight):
        for rec in self:
            new_picking_id, pick_type_id = rec._create_catch_weight(picking, actual_weight, picking_weight)
        ctx = dict(self.env.context)
        ctx.update({
            'search_default_picking_type_id': pick_type_id,
            'search_default_draft': False,
            'search_default_assigned': False,
            'search_default_confirmed': False,
            'search_default_ready': False,
            'search_default_late': False,
            'search_default_available': False,
        })
        return {
            'name': _('Catch Weight Picking'),
            'view_type': 'form',
            'view_mode': 'form,tree,calendar',
            'res_model': 'stock.picking',
            'res_id': new_picking_id,
            'type': 'ir.actions.act_window',
            'context': ctx,
        }
