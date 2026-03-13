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
        cls.user_demo = cls.env["res.users"].create(
            {
                "name": "John",
                "login": "test1",
                "groups_id": [(6, 0, cls.env.ref("account.group_account_user").ids)],
                "email": "john@yourcompany.example.com",
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

        cls.env["account.journal"].create(
            {
                "name": "Bank Journal",
                "code": "BNKTEST",
                "type": "bank",
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

        cls.sale_invoice = cls._create_invoice("out_invoice")
        cls.sale_invoice.action_post()
        # WIth user demo that don't have account manager rights
        cls.payment = cls._create_payment_from_invoice_with_user(
            cls.sale_invoice,
            cls.user_demo,
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
    def _create_payment_from_invoice_with_user(cls, invoice, user):
        action = invoice.action_register_payment()

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

    def test_01_account_move_check_booleans(self):
        self.assertEqual(self.sale_invoice.payment_state, "paid")
        payment = self.payment
        self.assertFalse(payment.is_checked)
        self.assertFalse(payment.move_id.is_payment_checked)
