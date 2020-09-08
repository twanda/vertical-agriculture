# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AgriculturePlantation(models.Model):
    _name = 'agri.plantation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(index=True, required=True)
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    comment = fields.Text(string='Notes')
    date_from = fields.Date(string='Farming since:')
    the_geom = fields.GeoMultiPolygon('NPA Shape')
    farmer_id = fields.Many2one('res.partner', string="Farmer", domain=[('is_farmer', '=', True)])



