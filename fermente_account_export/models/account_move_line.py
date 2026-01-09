# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _export_get_analytic_code(self):
        self.ensure_one()
        if self.move_id.company_id.fiscal_type == "fiscal_child":
            return self.move_id.company_id.code
        return ""

    def _export_get_account_code(self):
        self.ensure_one()
        return self.account_id._get_account_code(self)
