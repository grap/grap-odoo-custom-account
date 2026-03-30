# Copyright (C) 2026 - Today: GRAP (http://www.grap.coop)
# Copyright 2022 Tecnativa - Ernesto Tejeda
# @author: Quentin DUPONT
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests.common import Form, TransactionCase


# Inspired by account_move_reconcile_forbid_cancel tests (Tecnativa)
class TestFermenteAccountPaymentWorkflow(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env = cls.env(
            context={
                **cls.env.context,
                "mail_create_nolog": True,
                "mail_create_nosubscribe": True,
                "mail_notrack": True,
                "no_reset_password": True,
                "tracking_disable": True,
            }
        )

        # Models
        cls.AccountPayment = cls.env["account.payment"]

        # Create datas
        cls.user_non_account_manager = cls.env["res.users"].create(
            {
                "name": "Emmanuel Macron Mozart de la Finance",
                "login": "macrotte",
                "groups_id": [(6, 0, cls.env.ref("account.group_account_user").ids)],
                "email": "macron@oligarchie.fr",
            }
        )
        cls.user_account_manager = cls.env["res.users"].create(
            {
                "name": "Sibylle",
                "login": "sibylle",
                "groups_id": [(6, 0, cls.env.ref("account.group_account_manager").ids)],
                "email": "sibylle@notedefrais.fr",
            }
        )

        cls.receivable_account = cls._create_account(
            "Receivable", "REC", "asset_receivable", True
        )
        cls.payable_account = cls._create_account(
            "Payable", "PAY", "liability_payable", True
        )
        cls.income_account = cls._create_account("Income", "INC", "income")
        cls.expense_account = cls._create_account("Expense", "EXP", "expense")

        cls.journal_bank = cls.env["account.journal"].create(
            {
                "name": "Bank Journal Test",
                "code": "BNKTEST",
                "type": "bank",
            }
        )

        cls.journal_cash = cls.env["account.journal"].create(
            {
                "name": "Cash Journal Test",
                "code": "CASHTEST",
                "type": "cash",
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Partner test",
                "property_account_receivable_id": cls.receivable_account.id,
                "property_account_payable_id": cls.payable_account.id,
            }
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "property_account_income_id": cls.income_account.id,
                "property_account_expense_id": cls.expense_account.id,
            }
        )

    # -------------------------
    # CLASS METHODS
    # -------------------------

    @classmethod
    def _create_account(cls, name, code, account_type, reconcile=False):
        return cls.env["account.account"].create(
            {
                "name": name,
                "code": code,
                "account_type": account_type,
                "reconcile": reconcile,
            }
        )

    @classmethod
    def _create_invoice(cls, move_type):
        with Form(
            cls.env["account.move"].with_context(default_move_type=move_type)
        ) as move_form:
            move_form.invoice_date = fields.Date.today()
            move_form.partner_id = cls.partner

            with move_form.invoice_line_ids.new() as line:
                line.product_id = cls.product
                line.price_unit = 100.0

        return move_form.save()

    @classmethod
    def _create_payment_from_invoice_with_user(cls, invoice, journal, user):
        action = invoice.action_register_payment()
        action["context"]["default_journal_id"] = journal.id

        with Form(
            cls.env[action["res_model"]].with_context(**action["context"])
        ) as form:
            payment_register = form.save()

        payment_register = payment_register.with_user(user)
        payments = payment_register._create_payments()

        return payments

    # -------------------------
    # TEST
    # -------------------------

    # Non accountant AND Bank journal → False
    def test_01_non_account_manager_journal_bank(self):
        sale_invoice1 = self._create_invoice("out_invoice")
        sale_invoice1.action_post()

        payment = self._create_payment_from_invoice_with_user(
            sale_invoice1,
            self.journal_bank,
            self.user_non_account_manager,
        )

        self.assertEqual(sale_invoice1.payment_state, "paid")
        self.assertFalse(payment.is_checked)
        self.assertFalse(payment.move_id.is_payment_checked)

    # Non accountant BUT Cash journal → True
    def test_02_non_account_manager_journal_cash(self):
        sale_invoice2 = self._create_invoice("out_invoice")
        sale_invoice2.action_post()

        payment2 = self._create_payment_from_invoice_with_user(
            sale_invoice2,
            self.journal_cash,
            self.user_non_account_manager,
        )

        self.assertEqual(sale_invoice2.payment_state, "paid")
        self.assertTrue(payment2.is_checked)
        self.assertTrue(payment2.move_id.is_payment_checked)

    # Accountant and Bank journal → True
    def test_03_account_manager_journal_bank(self):
        sale_invoice3 = self._create_invoice("out_invoice")
        sale_invoice3.action_post()

        payment3 = self._create_payment_from_invoice_with_user(
            sale_invoice3,
            self.journal_bank,
            self.user_account_manager,
        )

        self.assertEqual(sale_invoice3.payment_state, "paid")
        self.assertTrue(payment3.is_checked)
        self.assertTrue(payment3.move_id.is_payment_checked)

    # Accountant and Cash journal → True
    def test_04_account_manager_journal_cash(self):
        sale_invoice4 = self._create_invoice("out_invoice")
        sale_invoice4.action_post()

        payment4 = self._create_payment_from_invoice_with_user(
            sale_invoice4,
            self.journal_cash,
            self.user_account_manager,
        )

        self.assertEqual(sale_invoice4.payment_state, "paid")
        self.assertTrue(payment4.is_checked)
        self.assertTrue(payment4.move_id.is_payment_checked)
