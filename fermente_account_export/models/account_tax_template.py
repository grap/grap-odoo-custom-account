# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class AccountTaxTemplate(models.Model):
    _inherit = "account.tax.template"

    ebp_suffix = fields.Char(
        string="Suffix in EBP",
        help="When exporting Entries to EBP, this suffix will be"
        " appended to the Account Number to make it a new Account.",
    )

    def _get_tax_vals(self, company, tax_template_to_tax):
        res = super()._get_tax_vals(company, tax_template_to_tax)
        res["ebp_suffix"] = self.ebp_suffix
        return res
