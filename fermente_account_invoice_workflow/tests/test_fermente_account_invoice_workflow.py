# Copyright (C) 2026 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestFermenteAccountInvoiceWorkflow(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResPartner = cls.env["res.partner"]
        cls.AccountAccount = cls.env["account.account"]
        cls.AccountJournal = cls.env["account.journal"]
        cls.AccountMove = cls.env["account.move"]
        cls.main_company = cls.env.ref("base.main_company")
        # Create user
        group_account_user = cls.env.ref("account.group_account_user").ids
        cls.user_demo_account_user = cls.env["res.users"].create(
            {
                "name": "John",
                "login": "test1",
                "groups_id": [(6, 0, group_account_user)],
                "email": "john@yourcompany.example.com",
            }
        )

        cls.vendor = cls.env.ref("base.res_partner_12")

        cls.account_expenses = cls.AccountAccount.create(
            {
                "code": "600001",
                "name": "Expenses (test)",
                "account_type": "expense",
            }
        )

        cls.account_payable = cls.AccountAccount.create(
            {
                "code": "211001",
                "name": "Account Payable (test)",
                "account_type": "liability_payable",
            }
        )

        cls.journal_purchase = cls.AccountJournal.create(
            {
                "name": "Vendors Bills TEST",
                "code": "HA-BILL",
                "type": "purchase",
            }
        )

        # MOVE 1 missing fields
        cls.move1 = cls.AccountMove.create(
            {
                "journal_id": cls.journal_purchase.id,
                "partner_id": cls.vendor.id,
                "move_type": "in_invoice",
                "line_ids": [
                    Command.create(
                        {
                            "name": "line 1",
                            "partner_id": cls.vendor.id,
                            "account_id": cls.account_expenses.id,
                            "debit": 100,
                        },
                    ),
                    Command.create(
                        {
                            "name": "line 2",
                            "partner_id": cls.vendor.id,
                            "account_id": cls.account_payable.id,
                            "credit": 100,
                        },
                    ),
                ],
            }
        )

        # MOVE 2 no missing fields
        cls.move2 = cls.AccountMove.create(
            {
                "journal_id": cls.journal_purchase.id,
                "move_type": "in_invoice",
                "partner_id": cls.vendor.id,
                "invoice_date": "1789-07-14",
                "invoice_date_due": "1789-07-14",
                "supplier_invoice_number": "OSS-double-117",
                "line_ids": [
                    Command.create(
                        {
                            "name": "line 1",
                            "partner_id": cls.vendor.id,
                            "account_id": cls.account_expenses.id,
                            "debit": 117,
                        },
                    ),
                    Command.create(
                        {
                            "name": "line 2",
                            "partner_id": cls.vendor.id,
                            "account_id": cls.account_payable.id,
                            "credit": 117,
                        },
                    ),
                ],
            }
        )

    def test_01_account_move_verify_missing_fields(self):
        self.assertEqual(self.move1.is_verified, False)
        self.assertEqual(self.move1.is_verified_toggle, False)
        self.assertEqual(self.move1.state, "draft")

        with self.assertRaises(UserError):
            self.move1.action_move_verify()
        self.move1.invoice_date = "1789-07-14"
        self.move1.invoice_date_due = "1789-07-14"
        self.move1.supplier_invoice_number = "OSS117"

        # It should pass now
        self.move1.action_move_verify()
        self.assertEqual(self.move1.is_verified, True)
        self.assertEqual(self.move1.is_verified_toggle, True)
        self.assertEqual(self.move1.state, "draft")

        self.move1.action_move_unverify()
        self.assertEqual(self.move1.is_verified, False)
        self.assertEqual(self.move1.is_verified_toggle, False)
        self.assertEqual(self.move1.state, "draft")

        self.move1.action_post()
        self.assertEqual(self.move1.is_verified, True)
        self.assertEqual(self.move1.is_verified_toggle, True)
        self.assertEqual(self.move1.state, "posted")

        self.move1.button_draft()
        self.assertEqual(self.move1.is_verified, False)
        self.assertEqual(self.move1.is_verified_toggle, False)
        self.assertEqual(self.move1.state, "draft")

        # use alternative toggle_field
        self.move1.is_verified_toggle = False
        self.assertEqual(self.move1.is_verified, False)
        self.assertEqual(self.move1.state, "draft")

        self.move1.is_verified_toggle = True
        self.assertEqual(self.move1.is_verified, True)
        self.assertEqual(self.move1.state, "draft")

    def test_02_account_move_post(self):
        # With base user
        with self.assertRaises(UserError):
            self.move2.with_user(self.user_demo_account_user).action_post()

        # With admin
        self.move2.action_post()
        self.assertEqual(self.move2.state, "posted")
