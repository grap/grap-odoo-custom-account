# Copyright (C) 2020 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.http import request

_REPLACEMENT_JOURNAL_CODE = {"FAC": "VT", "FACTURE": "AC"}

_DELETED_JOURNAL_CODE = ["EXCH", "CABA", "STJ"]


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    def load_for_current_company(self, sale_tax_rate, purchase_tax_rate):
        res = super().load_for_current_company(sale_tax_rate, purchase_tax_rate)

        # <Copy:odoo>
        # do not use `request.env` here, it can cause deadlocks
        if request and request.session.uid:
            current_user = self.env["res.users"].browse(request.uid)
            company = current_user.company_id
        else:
            # fallback to company of current user, most likely __system__
            # (won't work well for multi-company)
            company = self.env.user.company_id
        # </EndCopy>

        company.account_sale_tax_id = False
        company.account_purchase_tax_id = False
        return res

    def _prepare_all_journals(self, acc_template_ref, company, journals_dict=None):
        all_journals = super()._prepare_all_journals(
            acc_template_ref, company, journals_dict
        )

        # Remove undesired journals
        journals = []
        for journal in all_journals:
            if journal["code"] not in _DELETED_JOURNAL_CODE:
                journals.append(journal)

        for journal in journals:
            # rename incorrect code
            if journal["code"] in _REPLACEMENT_JOURNAL_CODE:
                journal["code"] = _REPLACEMENT_JOURNAL_CODE[journal["code"]]

            # set correctly sale and purchase journal
            if journal["type"] in ["sale", "purchase"]:
                journal["update_posted"] = True
        return journals
