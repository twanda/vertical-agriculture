# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AgriculturePlantationHistory(models.Model):
    _name = 'agri.plantation.history'

    plant_id = fields.Many2one('agri.plantation', string="Plantation", required=True)
    farmer_id = fields.Many2one('res.partner', string="Farmer", domain=[('is_farmer', '=', True)], required=True)
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To')





