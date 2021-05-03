# -*- coding: utf-8 -*-

from odoo.osv import expression
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


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
    date_from = fields.Date(string='Farming Since:')
    the_geom = fields.GeoMultiPolygon('NPA Shape')
    farmer_id = fields.Many2one('res.partner', string="Farmer", domain=[('is_farmer', '=', True)])
    current_order_id = fields.Many2one('agri.plantation.history', string="Farmer", domain=[('is_farmer', '=', True)])
    location_id = fields.Many2one('stock.location', string="Location")
    history_ids = fields.One2many('agri.plantation.history', 'plant_id', string="History")
    plantation_count = fields.Char('Plantation Count', compute='_compute_plantation_count')
    plantation_code = fields.Char('Plantation Code',related='name',store=True)
    
    _sql_constraints = [('plantation_code_uniq', 'unique (name)', "Plantation Code must be unique !")]
    

    # def create_location(self, vals):
    #     values = {
    #         'usage': 'supplier',
    #         'name': vals.get('name'),
    #         'location_id': self.env.ref('stock.stock_location_suppliers').id
    #     }
    #     location = self.env['stock.location'].create(values)
    #     return location
    #
    # @api.model
    # def create(self, vals):
    #     location = self.create_location(vals)
    #     vals.update({'location_id': location.id})
    #     result = super(AgriculturePlantation, self).create(vals)
    #     return result

    def _compute_plantation_count(self):
        for rec in self:
            count = len(rec.history_ids.ids)
            rec.plantation_count = count

    def action_view_plantations(self):
        for rec in self:
            history_ids = rec.history_ids.ids
            return {
                'name': 'History',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'agri.plantation.history',
                'domain': [('id', 'in', history_ids)],
            }

    