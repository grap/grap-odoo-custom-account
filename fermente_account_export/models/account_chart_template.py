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
                "export_suffix_on_tax_required": account_template.export_suffix_on_tax_required,
                "export_suffix_on_tax_default": account_template.export_suffix_on_tax_default,
            }
        )
        return res
