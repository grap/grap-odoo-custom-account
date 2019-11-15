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

    # Test Section
    def test_01_create_new_chart_of_account(self):

        # Create a new company
        company = self.ResCompany.create(
            {"name": "Test Company (GRAP - L10n_fr", "currency_id": self.euro.id}
        )
        self.env.user.company_id = company.id
        self.french_chart_of_account.try_loading_for_current_company()
