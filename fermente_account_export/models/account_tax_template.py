# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class AccountTaxTemplate(models.Model):
    _inherit = "account.tax.template"

    export_suffix = fields.Char(
        help="When exporting Entries, this suffix will be"
        " appended to the Account Number to make it a new Account.",
    )

    def _get_tax_vals(self, company, tax_template_to_tax):
        res = super()._get_tax_vals(company, tax_template_to_tax)
        res["export_suffix"] = self.export_suffix
        return res
