# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_farmer = fields.Boolean(string="Is Farmer ?")
    plantation_ids = fields.Many2many('agri.plantation', 'farmer_plantation_rel', 'farmer_id',
                                      'plant_id', string="Plantations")

