# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = "account.config.settings"

    export_type = fields.Selection(
        related="company_id.fiscal_company_id.export_type", readonly=False
    )

    max_size_account_code = fields.Integer(
        related="company_id.fiscal_company_id.max_size_account_code", readonly=False
    )

    third_account_add_company_suffix = fields.Boolean(
        related="company_id.fiscal_company_id.third_account_add_company_suffix",
        readonly=False,
    )

    third_account_add_partner_suffix = fields.Boolean(
        related="company_id.fiscal_company_id.third_account_add_partner_suffix",
        readonly=False,
    )
