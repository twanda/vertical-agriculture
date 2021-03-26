# -*- coding: utf-8 -*-

from odoo import models,fields,api,_


class StockMove(models.Model):
    
    _inherit = 'stock.move'
    
    
    catch_parent_move_id = fields.Many2one('stock.move',string='Parent Catch Move')
    
    
class StockMoveLine(models.Model):
    
    _inherit="stock.move.line"
    
    
    
    catch_parent_move_line_ref = fields.Char(string='Parent Move Line Ref')
    