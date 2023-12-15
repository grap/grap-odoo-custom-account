# Copyright (C) 2021 - Today: Coop IT Easy (http://coopiteasy.be)
# @author: Rémy TAYMANS (remy@coopiteasy.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    sale_move_policy = fields.Selection(
        selection=[
            ("standard", "Standard"),
            ("groupby_account_tax", "Group by account and tax"),
            ("groupby_account_tax_partner", "Group by account, tax and partner"),
        ],
        default="standard",
        help="Select how PoS account move lines should be aggregated",
    )
