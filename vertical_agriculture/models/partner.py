# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_farmer = fields.Boolean(string="Is Farmer ?")
    plantation_ids = fields.Many2many('agri.plantation', 'farmer_plantation_rel', 'farmer_id',
                                      'plant_id', string="Plantations")
    history_ids = fields.One2many('agri.plantation.history', 'farmer_id', string="History")
    plantation_count = fields.Char('Plantation Count', compute='_compute_plantation_count')

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



