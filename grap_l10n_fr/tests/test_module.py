# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):
    def setUp(self):
        super().setUp()
        self.ResCompany = self.env["res.company"]
        self.french_chart_of_account = self.env.ref(
            "l10n_fr.l10n_fr_pcg_chart_template"
        )
        self.euro = self.env.ref("base.EUR")

    def _get_account(self, company, code):
        return self.env["account.account"].search(
            [("code", "=", code), ("company_id", "=", company.id)]
        )[0]

    def _get_tax(self, company, description):
        return self.env["account.tax"].search(
            [("description", "=", description), ("company_id", "=", company.id)]
        )[0]

    # Test Section
    def test_01_create_new_chart_of_account(self):

        # Create a new company
        company = self.ResCompany.create(
            {"name": "Test Company (GRAP - L10n_fr", "currency_id": self.euro.id}
        )
        self.env.user.company_id = company.id
        self.french_chart_of_account.try_loading_for_current_company()

        # Check that custom fields are correctly applied on expense accounts
        account_601 = self._get_account(company, "601")
        self.assertTrue(account_601.ebp_export_tax)
        self.assertEquals(account_601.ebp_code_no_tax, "9")

        # Check that custom fields are correctly applied on income accounts
        account_707 = self._get_account(company, "707")
        self.assertTrue(account_707.ebp_export_tax)
        self.assertFalse(account_707.ebp_code_no_tax)

        # Check that custom fields are correctly applied on taxes
        tax_sale_20 = self._get_tax(company, "TVA-VT-20.0-HT")
        self.assertTrue(tax_sale_20.ebp_suffix)
