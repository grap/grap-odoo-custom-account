# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models

from . import export_type_format


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    export_type = fields.Selection(
        selection=export_type_format._SELECTION_EXPORT_TYPE,
    )

    max_size_account_code = fields.Integer()

    third_account_add_company_suffix = fields.Boolean(string="Add Company Suffix")

    third_account_add_partner_suffix = fields.Boolean(string="Add Partner Suffix")

    def _get_account_vals(self, company, account_template, code_acc, tax_template_ref):
        res = super()._get_account_vals(
            company, account_template, code_acc, tax_template_ref
        )
        res[
            "export_suffix_on_tax_required"
        ] = account_template.export_suffix_on_tax_required
        res[
            "export_suffix_on_tax_default"
        ] = account_template.export_suffix_on_tax_default
        return res
