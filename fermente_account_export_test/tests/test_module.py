# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.AccountExport = cls.env["account.export"]
        cls.WizardAccountExport = cls.env["wizard.account.export"]
        cls.move_1 = cls.env.ref("account.1_demo_invoice_followup").copy()
        cls.move_1.journal_id.export_code = cls.move_1.journal_id.code
        cls.fiscal_year = cls.env.ref("fermente_account_export_test.curent_fiscal_year")

    # Test Section

    def _export_move(self):
        self.move_1.action_post()
        wizard = self.WizardAccountExport.with_context(
            active_ids=[self.move_1.id]
        ).create({"fiscal_year_id": self.fiscal_year.id})
        self.assertEqual(wizard.ignored_draft_move_qty, 0)
        self.assertEqual(wizard.ignored_fiscal_year_move_qty, 0)
        self.assertEqual(wizard.ignored_journal_code_move_qty, 0)
        self.assertEqual(wizard.ignored_to_check_move_qty, 0)
        self.assertEqual(wizard.ignored_exported_move_qty, 0)
        self.assertEqual(wizard.ignored_partner_move_qty, 0)
        self.assertEqual(wizard.ignored_tax_move_qty, 0)
        result = wizard.button_export()

        export = self.AccountExport.browse(result["res_id"])

        self.assertEqual(
            self.move_1.account_export_id,
            export,
            "Exporting a move should link it to the export created.",
        )

        # check if exported moves are well locked
        with self.assertRaises(ValidationError):
            self.move_1.write({"ref": "write ref should fail"})

        # Check if we can still write on allowed fields
        self.move_1.write({"narration": "Write narration should success"})

    def test_01_export_move_ebp(self):
        self.env.company.export_type = "ebp"
        self._export_move()

    def test_02_export_move_sage(self):
        self.env.company.export_type = "sage"
        self._export_move()

    def test_10_export_move_without_unposted(self):
        wizard = self.WizardAccountExport.with_context(
            active_ids=[self.move_1.id]
        ).create({"fiscal_year_id": self.fiscal_year.id})
        self.assertEqual(
            wizard.ignored_draft_move_qty,
            1,
            "It should not be possible to export a unposted move.",
        )

    def test_20_export_move_with_partner_without_code(self):
        self.env.company.third_account_add_partner_suffix = True
        self.move_1.action_post()
        self.move_1.partner_id.export_suffix = False
        wizard = self.WizardAccountExport.with_context(
            active_ids=[self.move_1.id]
        ).create({"fiscal_year_id": self.fiscal_year.id})
        self.assertEqual(
            wizard.ignored_partner_move_qty,
            1,
            "It should not be possible to export a move for partner without code",
        )

    def test_21_export_move_with_partner_without_code_non_blocking(self):
        self.env.company.third_account_add_partner_suffix = False
        self.move_1.action_post()
        self.move_1.partner_id.export_suffix = False
        wizard = self.WizardAccountExport.with_context(
            active_ids=[self.move_1.id]
        ).create({"fiscal_year_id": self.fiscal_year.id})
        self.assertEqual(
            wizard.ignored_partner_move_qty,
            0,
            "It should be possible to export a move for partner without code"
            " if it is not required.",
        )
