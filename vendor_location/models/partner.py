# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    picking_type_id = fields.Many2one('stock.picking.type', string="Default Operation Type")
