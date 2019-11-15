# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):
    def setUp(self):
        super().setUp()

        self.sale_journal = self.env["account.journal"].search(
            [("type", "=", "sale"), ("code", "=", "INV")]
        )[0]

        self.invoice = self.env.ref("grap_account_change_invoice_move.demo_invoice")

    # Test Section
    def test_01_confirm_non_grouped(self):
        self.sale_journal.group_invoice_lines = False
        self.invoice.action_invoice_open()

        self.assertEquals(
            len(self.invoice.move_id.line_ids),
            5,
            "In a non grouped mode, an invoice with 4 lines"
            " (3 products / 2 account) should generate"
            " an account move with 4 lines (4 sale lines + 1 counterpart)",
        )

    # Test Section
    def test_01_confirm_grouped(self):
        self.sale_journal.group_invoice_lines = True
        self.invoice.action_invoice_open()

        self.assertEquals(
            len(self.invoice.move_id.line_ids),
            3,
            "In a grouped mode, an invoice with 4 lines"
            " (3 products / 2 account) should generate"
            " an account move with 3 lines (2 sale line + 1 counterpart)",
        )
