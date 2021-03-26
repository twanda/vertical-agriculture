# -*- coding: utf-8 -*-

from odoo.osv import expression

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_farmer = fields.Boolean(string="Is Farmer ?")
    farmer_code = fields.Char('Farmer Code')
    plantation_ids = fields.Many2many('agri.plantation', 'farmer_plantation_rel', 'farmer_id',
                                      'plant_id', string="Plantations")
    history_ids = fields.One2many('agri.plantation.history', 'farmer_id', string="History")
    plantation_count = fields.Char('Plantation Count', compute='_compute_plantation_count')

    def create_location(self, vals):
        values = {
            'usage': 'supplier',
            'name': vals.get('name'),
            'location_id': self.env.ref('stock.stock_location_suppliers').id
        }
        location = self.env['stock.location'].create(values)
        return location

    @api.model
    def create(self, vals):
        if vals.get('is_farmer'):
            location = self.create_location(vals)
            vals.update({'location_id': location.id})
        result = super(ResPartner, self).create(vals)
        return result

    def _compute_plantation_count(self):
        for rec in self:
            count =len(rec.history_ids.ids)
            rec.plantation_count = count

    def action_view_plantations(self):
        for rec in self:
            history_ids = rec.history_ids.ids
            return {
                'name': 'History',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'res_model': 'agri.plantation.history',
                'domain': [('id', 'in', history_ids)],
            }



