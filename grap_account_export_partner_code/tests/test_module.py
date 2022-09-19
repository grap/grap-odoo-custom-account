# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):
    def setUp(self):
        super().setUp()
        self.ResPartner = self.env["res.partner"]
        self.Wizard = self.env["wizard.res.partner.add.export.code"]
        self.AccountAccount = self.env["account.account"]
        self.AccountJournal = self.env["account.journal"]
        self.AccountMove = self.env["account.move"]

        self.customer = self.env.ref("grap_account_export_partner_code.customer_2")
        self.account_type_receivable = self.env.ref(
            "account.data_account_type_receivable"
        )
        self.account_type_revenue = self.env.ref("account.data_account_type_revenue")

        self.account_sale = self.AccountAccount.create(
            {
                "code": "SALET",
                "name": "Revenue (sale)",
                "reconcile": True,
                "user_type_id": self.account_type_revenue.id,
            }
        )
        self.account_receivable = self.AccountAccount.create(
            {
                "code": "RECVT",
                "name": "Receivable (test)",
                "reconcile": True,
                "user_type_id": self.account_type_receivable.id,
            }
        )

        self.journal_sale = self.AccountJournal.create(
            {
                "name": "Sales journal",
                "code": "SAJT",
                "type": "sale",
                "default_credit_account_id": self.account_sale.id,
                "default_debit_account_id": self.account_sale.id,
            }
        )

    def test_01_accounting_export_sanitize(self):
        def _sanitize(name):
            return self.ResPartner._accounting_export_sanitize(name)

        # Check Upper
        self.assertEqual(_sanitize("To Upper"), "TO UPPER")
        self.assertEqual(_sanitize("   To Strip  "), "TO STRIP")
        self.assertEqual(
            _sanitize("Duplicated    Spaces Between       Words  "),
            "DUPLICATED SPACES BETWEEN WORDS",
        )
        self.assertEqual(_sanitize("With accent éèàù"), "WITH ACCENT EEAU")

        self.assertEqual(_sanitize("With Special# Char"), "WITH SPECIAL CHAR")
        self.assertEqual(_sanitize("With Special ! Char"), "WITH SPECIAL CHAR")
        self.assertEqual(_sanitize("With Special ! Char"), "WITH SPECIAL CHAR")
        self.assertEqual(_sanitize("With Number 123"), "WITH NUMBER")

    def test_02_accounting_export_get_base_text(self):
        def _get_base(name):
            return self.ResPartner._accounting_export_get_base_text(name)

        self.assertEqual(_get_base("a Name with a word of many characters"), "CHAR")
        self.assertEqual(_get_base("Mr Baa"), "BAA1")
        self.assertEqual(_get_base("A Bi"), "BI01")
        self.assertEqual(_get_base("A B"), "A001")
        self.assertEqual(_get_base(""), "")

    def test_03_wizard_partner_add_export_code(self):
        partner_with_suffix = self.ResPartner.create(
            {"name": "Partner With Suffix", "accounting_export_code": "SUFF"}
        )
        partner_a = self.ResPartner.create({"name": "A"})
        partner_bb = self.ResPartner.create({"name": "BB"})
        partner_ccc = self.ResPartner.create({"name": "CCC"})
        partner_dddd = self.ResPartner.create({"name": "DDDD"})
        partner_duplicate_1 = self.ResPartner.create({"name": "bobleponge 01"})
        partner_duplicate_2 = self.ResPartner.create({"name": "bobleponge 02"})
        partner_duplicate_3 = self.ResPartner.create({"name": "bobleponge 03"})

        wizard = self.Wizard.with_context(
            active_ids=[
                partner_with_suffix.id,
                partner_a.id,
                partner_bb.id,
                partner_ccc.id,
                partner_dddd.id,
                partner_duplicate_1.id,
                partner_duplicate_2.id,
                partner_duplicate_3.id,
            ]
        ).create({})

        line_duplicate_3 = wizard.line_ids.filtered(
            lambda x: x.partner_id.id == partner_duplicate_3.id
        )
        # Test OnChange
        line_duplicate_3.accounting_export_code = "BOBL"
        line_duplicate_3.onchange_accounting_export_code()
        self.assertEqual(line_duplicate_3.state, "duplicate_new")

        line_duplicate_3.accounting_export_code = "EBPC"
        line_duplicate_3.onchange_accounting_export_code()
        self.assertEqual(line_duplicate_3.state, "duplicate_existing")

        line_duplicate_3.accounting_export_code = "abéc"
        line_duplicate_3.onchange_accounting_export_code()
        self.assertEqual(line_duplicate_3.accounting_export_code, "ABEC")

        line_duplicate_3.accounting_export_code = ""
        line_duplicate_3.onchange_accounting_export_code()
        self.assertEqual(line_duplicate_3.state, "empty")

        # Try to confirm with incorrect value
        with self.assertRaises(ValidationError):
            wizard.button_affect_accounting_export_code()
        line_duplicate_3.unlink()

        wizard.button_affect_accounting_export_code()
        self.assertEqual(partner_with_suffix.accounting_export_code, "SUFF")
        self.assertEqual(partner_a.accounting_export_code, "A001")
        self.assertEqual(partner_bb.accounting_export_code, "BB01")
        self.assertEqual(partner_ccc.accounting_export_code, "CCC1")
        self.assertEqual(partner_dddd.accounting_export_code, "DDDD")
        self.assertEqual(partner_duplicate_1.accounting_export_code, "BOBL")
        self.assertEqual(partner_duplicate_2.accounting_export_code, "BOB2")

    def test_04_search_journal_item_count(self):
        # Check first if partner doesn't requires export code
        partners = self.ResPartner.search([("journal_item_count", ">", 0)])
        # import pdb; pdb.set_trace()
        self.assertNotIn(self.customer.id, partners.ids)

        self.AccountMove.create(
            {
                "journal_id": self.journal_sale.id,
                "partner_id": self.customer.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "line 1",
                            "partner_id": self.customer.id,
                            "account_id": self.account_receivable.id,
                            "debit": 100,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "line 2",
                            "partner_id": self.customer.id,
                            "account_id": self.account_sale.id,
                            "credit": 100,
                        },
                    ),
                ],
            }
        )

        partners = self.ResPartner.search([("journal_item_count", ">", 0)])
        self.assertIn(self.customer.id, partners.ids)
