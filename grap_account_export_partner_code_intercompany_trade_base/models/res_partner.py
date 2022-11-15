# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _intercompany_trade_allowed_fields(self):
        """Allow accountant to set accounting export code
        on intercompany trade partners"""
        res = super()._intercompany_trade_allowed_fields()
        res.append("accounting_export_code")
        return res
