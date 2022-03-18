# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):
    def setUp(self):
        super().setUp()
        self.ResPartner = self.env["res.partner"]
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

    def test_04_test_wizard_partner_add_suffix(self):
        partner_a = self.ResPartner.create({"name": "A"})
        partner_bb = self.ResPartner.create({"name": "BB"})
        partner_ccc = self.ResPartner.create({"name": "CCC"})
        partner_dddd = self.ResPartner.create({"name": "DDDD"})
        partner_duplicate_1 = self.ResPartner.create({"name": "bobleponge"})
        partner_duplicate_2 = self.ResPartner.create({"name": "bobleponge"})

        wizard = self.WizardResPartnerAddSuffix.with_context(
            active_ids=[
                partner_a.id,
                partner_bb.id,
                partner_ccc.id,
                partner_dddd.id,
                partner_duplicate_1.id,
                partner_duplicate_2.id,
            ]
        ).create({})

        line_a = wizard.line_ids.filtered(lambda x: x.partner_id.id == partner_a.id)
        line_bb = wizard.line_ids.filtered(lambda x: x.partner_id.id == partner_bb.id)
        line_ccc = wizard.line_ids.filtered(lambda x: x.partner_id.id == partner_ccc.id)
        line_dddd = wizard.line_ids.filtered(
            lambda x: x.partner_id.id == partner_dddd.id
        )
        line_duplicate_1 = wizard.line_ids.filtered(
            lambda x: x.partner_id.id == partner_duplicate_1.id
        )
        line_duplicate_2 = wizard.line_ids.filtered(
            lambda x: x.partner_id.id == partner_duplicate_2.id
        )
        self.assertEqual(line_a.ebp_suffix, "A")
        self.assertEqual(line_bb.ebp_suffix, "BB")
        self.assertEqual(line_ccc.ebp_suffix, "CCC")
        self.assertEqual(line_dddd.ebp_suffix, "DDDD")
        self.assertEqual(line_duplicate_1.ebp_suffix, "BOBL")
        self.assertEqual(line_duplicate_2.ebp_suffix, "BOB2")
