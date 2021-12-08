# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):
    def setUp(self):
        super().setUp()
        self.WizardEbpExport = self.env["wizard.ebp.export"]
        self.WizardEbpUnexport = self.env["wizard.ebp.unexport"]
        self.WizardResPartnerAddSuffix = self.env["wizard.res.partner.add.suffix"]
        self.move_1 = self.env.ref("grap_account_export_ebp_test.move_1")
        self.customer_1 = self.env.ref("grap_account_export_ebp_test.customer_1")
        self.sale_account = self.env.ref("grap_account_export_ebp_test.sale_account")
        self.fiscal_year = self.env.ref(
            "grap_account_export_ebp_test.curent_fiscal_year"
        )
        self.receivable_account = self.env.ref(
            "grap_account_export_ebp_test.receivable_account"
        )

    # Test Section
    def test_01_export_move_and_unexport(self):
        self.move_1.post()
        wizard = self.WizardEbpExport.with_context(active_ids=[self.move_1.id]).create(
            {"fiscal_year_id": self.fiscal_year.id}
        )
        wizard.button_export()
        self.assertEqual(
            self.move_1.ebp_export_id.id,
            wizard.ebp_export_id.id,
            "Exporting a move should link it to the ebp export created.",
        )

        # check if exported moves are well locked
        with self.assertRaises(ValidationError):
            self.move_1.write({"ref": "write ref should fail"})

        # Check if we can still write on allowed fields
        self.move_1.write({"narration": "Write narration should success"})

        wizard = self.WizardEbpUnexport.with_context(
            active_ids=[self.move_1.id]
        ).create({})
        wizard.button_unexport()
        self.assertEqual(
            self.move_1.ebp_export_id.id,
            False,
            "Cancelling an export should remove the link with the EBP export.",
        )

    def test_02_export_move_without_unposted(self):
        wizard = self.WizardEbpExport.with_context(active_ids=[self.move_1.id]).create(
            {"fiscal_year_id": self.fiscal_year.id}
        )
        self.assertEqual(
            wizard.ignored_draft_move_qty,
            1,
            "It should not be possible to export a unposted move.",
        )

    def test_03_export_move_with_partner_without_suffix(self):
        self.move_1.post()
        self.customer_1.ebp_suffix = False
        wizard = self.WizardEbpExport.with_context(active_ids=[self.move_1.id]).create(
            {"fiscal_year_id": self.fiscal_year.id}
        )
        self.assertEqual(
            wizard.ignored_partner_move_qty,
            1,
            "It should not be possible to export a unposted move.",
        )
