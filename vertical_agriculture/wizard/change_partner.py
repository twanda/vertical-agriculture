# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ChangePartnerWizard(models.TransientModel):
    _name = 'change.partner.wizard'

    farmer_id = fields.Many2one('res.partner', string="Farmer", domain=[('is_farmer', '=', True)], required=True)
    date_from = fields.Date(string='Farming Since', required=True)

    def update_history(self, plant):
        if plant.current_order_id:
            plant.current_order_id.write({'date_to': fields.Date.today()})
        vals = {
            'plant_id': plant.id,
            'farmer_id': self.farmer_id.id,
            'date_from': plant.date_from,
        }
        new_order = self.env['agri.plantation.history'].create(vals)
        plant.current_order_id = new_order.id
        return

    def action_change_partner(self):
        plant = self.env['agri.plantation'].browse(self.env.context.get('active_ids'))
        plant.write({'farmer_id': self.farmer_id.id, 'date_from': self.date_from})
        self.update_history(plant)
        return
