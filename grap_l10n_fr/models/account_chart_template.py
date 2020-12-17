# Copyright (C) 2020 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.http import request


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    def load_for_current_company(self, sale_tax_rate, purchase_tax_rate):
        res = super().load_for_current_company(sale_tax_rate, purchase_tax_rate)

        # <Copy:odoo>
        # do not use `request.env` here, it can cause deadlocks
        if request and request.session.uid:
            current_user = self.env['res.users'].browse(request.uid)
            company = current_user.company_id
        else:
            # fallback to company of current user, most likely __system__
            # (won't work well for multi-company)
            company = self.env.user.company_id
        # </EndCopy>

        company.account_sale_tax_id = False
        company.account_purchase_tax_id = False
        return res
