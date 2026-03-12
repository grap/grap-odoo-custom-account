# Copyright (C) 2026 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestFermenteAccountInvoiceWorkflow(TransactionCase):
    def setUp(self):
        super().setUp()
        self.ResPartner = self.env["res.partner"]
        self.AccountAccount = self.env["account.account"]
        self.AccountJournal = self.env["account.journal"]
        self.AccountMove = self.env["account.move"]
        self.main_company = self.env.ref("base.main_company")
        # Create user
        group_account_user = self.env.ref("account.group_account_user").ids
        self.user_demo_account_user = self.env["res.users"].create(
            {
                "name": "John",
                "login": "test1",
                "groups_id": [(6, 0, group_account_user)],
                "email": "john@yourcompany.example.com",
            }
        )

        self.vendor = self.env.ref("base.res_partner_12")

        self.account_expenses = self.AccountAccount.create(
            {
                "code": "600001",
                "name": "Expenses (test)",
                "account_type": "expense",
            }
        )

        self.account_payable = self.AccountAccount.create(
            {
                "code": "211001",
                "name": "Account Payable (test)",
                "account_type": "liability_payable",
            }
        )

        self.journal_purchase = self.AccountJournal.create(
            {
                "name": "Vendors Bills TEST",
                "code": "HA-BILL",
                "type": "purchase",
            }
        )

        # MOVE 1 missing fields
        self.move1 = self.AccountMove.create(
            {
                "journal_id": self.journal_purchase.id,
                "partner_id": self.vendor.id,
                "line_ids": [
                    Command.create(
                        {
                            "name": "line 1",
                            "partner_id": self.vendor.id,
                            "account_id": self.account_expenses.id,
                            "debit": 100,
                        },
                    ),
                    Command.create(
                        {
                            "name": "line 2",
                            "partner_id": self.vendor.id,
                            "account_id": self.account_payable.id,
                            "credit": 100,
                        },
                    ),
                ],
            }
        )

        # MOVE 2 no missing fields
        self.move2 = self.AccountMove.create(
            {
                "journal_id": self.journal_purchase.id,
                "partner_id": self.vendor.id,
                "invoice_date": "1789-07-14",
                "invoice_date_due": "1789-07-14",
                "supplier_invoice_number": "OSS-double-117",
                "line_ids": [
                    Command.create(
                        {
                            "name": "line 1",
                            "partner_id": self.vendor.id,
                            "account_id": self.account_expenses.id,
                            "debit": 117,
                        },
                    ),
                    Command.create(
                        {
                            "name": "line 2",
                            "partner_id": self.vendor.id,
                            "account_id": self.account_payable.id,
                            "credit": 117,
                        },
                    ),
                ],
            }
        )

    def test_01_account_move_verify_missing_fields(self):
        with self.assertRaises(UserError):
            self.move1.action_invoice_verify()
        self.move1.invoice_date = "1789-07-14"
        self.move1.invoice_date_due = "1789-07-14"
        self.move1.supplier_invoice_number = "OSS117"

        # It should pass now
        self.move1.action_invoice_verify()
        self.assertEqual(self.move1.state, "verified")

        self.move1.button_draft()
        self.assertEqual(self.move1.state, "draft")

    def test_02_account_move_post(self):
        # With base user
        with self.assertRaises(UserError):
            self.move2.with_user(self.user_demo_account_user).action_post()

        # With admin
        self.move2.action_post()
        self.assertEqual(self.move2.state, "posted")
