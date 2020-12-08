# Copyright (C) 2021 - Today: Coop IT Easy (http://coopiteasy.be)
# @author: Rémy TAYMANS (remy@coopiteasy.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    pos_sale_move_policy = fields.Selection(
        selection=[
            ("groupby_account_tax", "Group by Account and tax"),
            ("groupby_account_tax_partner", "Group by account, tax and partner"),
        ],
        default="groupby_account_tax",
        help="Select how PoS account moves should be aggregated",
    )
