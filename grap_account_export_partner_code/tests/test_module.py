# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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

    def test_04_test_wizard_partner_add_suffix(self):
        partner_with_suffix = self.ResPartner.create(
            {"name": "Partner With Suffix", "ebp_suffix": "SUFF"}
        )
        partner_a = self.ResPartner.create({"name": "A"})
        partner_bb = self.ResPartner.create({"name": "BB"})
        partner_ccc = self.ResPartner.create({"name": "CCC"})
        partner_dddd = self.ResPartner.create({"name": "DDDD"})
        partner_duplicate_1 = self.ResPartner.create({"name": "bobleponge"})
        partner_duplicate_2 = self.ResPartner.create({"name": "bobleponge"})

        wizard = self.WizardResPartnerAddSuffix.with_context(
            active_ids=[
                partner_with_suffix.id,
                partner_a.id,
                partner_bb.id,
                partner_ccc.id,
                partner_dddd.id,
                partner_duplicate_1.id,
                partner_duplicate_2.id,
            ]
        ).create({})

        line_partner_with_suffix = wizard.line_ids.filtered(
            lambda x: x.partner_id.id == partner_with_suffix.id
        )
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
        self.assertEqual(line_partner_with_suffix.ebp_suffix, "SUFF")
        self.assertEqual(line_a.ebp_suffix, "A")
        self.assertEqual(line_bb.ebp_suffix, "BB")
        self.assertEqual(line_ccc.ebp_suffix, "CCC")
        self.assertEqual(line_dddd.ebp_suffix, "DDDD")
        self.assertEqual(line_duplicate_1.ebp_suffix, "BOBL")
        self.assertEqual(line_duplicate_2.ebp_suffix, "BOB2")
