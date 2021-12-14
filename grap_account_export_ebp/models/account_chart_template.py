# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    def _get_account_vals(self, company, account_template, code_acc, tax_template_ref):
        res = super()._get_account_vals(
            company, account_template, code_acc, tax_template_ref
        )
        res.update(
            {
                "ebp_export_tax": account_template.ebp_export_tax,
                "ebp_code_no_tax": account_template.ebp_code_no_tax,
            }
        )
        return res
