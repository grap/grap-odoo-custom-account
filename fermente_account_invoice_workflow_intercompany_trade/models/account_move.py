# Copyright (C) 2026 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _check_before_mark_as_verified(self):
        self._check_all_intercompany_trade()
        return super()._check_before_mark_as_verified()
