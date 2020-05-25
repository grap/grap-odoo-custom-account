# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):
    def setUp(self):
        super().setUp()
        self.invoice = self.env.ref(
            "l10n_generic_coa.demo_invoice_equipment_purchase"
        ).copy()
        self.user_demo = self.env.ref("base.user_demo")
        self.user_admin = self.env.ref("base.user_admin")

    # Test Section
    def test_check_supplier_invoice_check_data(self):
        with self.assertRaises(UserError):
            self.invoice.action_invoice_open()

        # Set required values and try again
        self._set_correct_value()
        self.invoice.action_invoice_open()

    def test_check_supplier_invoice_access_no_manager(self):
        self._set_correct_value()
        with self.assertRaises(UserError):
            self.invoice.sudo(self.user_demo).action_invoice_open()

        # a basic user should have the possibility to verify an invoice
        self.invoice.sudo(self.user_demo).action_invoice_verify()

    def test_check_supplier_invoice_access_manager(self):
        self._set_correct_value()
        self.invoice.sudo(self.user_admin).action_invoice_open()

    def _set_correct_value(self):
        self.invoice.supplier_invoice_number = "#42"
        self.invoice.date_due = self.invoice.create_date.date()
        self.invoice.date_invoice = self.invoice.create_date.date()
