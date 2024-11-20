# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class WizardResPartnerAddExportCodeLine(models.TransientModel):
    _name = "wizard.res.partner.add.export.code.line"
    _description = "Add Suffix for Partners Wizard Line"

    _order = "company_id, partner_id"

    _STATE_SELECTION = [
        ("ok", "OK"),
        ("empty", "Empty"),
        ("duplicate_existing", "Duplicate With Existing Codes"),
        ("duplicate_new", "Duplicate With New Codes"),
    ]

    wizard_id = fields.Many2one(
        comodel_name="wizard.res.partner.add.export.code", delete="cascade"
    )

    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Partner", readonly=True
    )

    company_id = fields.Many2one(
        comodel_name="res.company", string="Company", readonly=True
    )

    accounting_export_code = fields.Char(string="Accounting Export Code", size=4)

    state = fields.Selection(selection=_STATE_SELECTION, string="State", readonly=True)

    @api.onchange("accounting_export_code")
    def onchange_accounting_export_code(self):
        ResPartner = self.env["res.partner"]
        self.accounting_export_code = ResPartner._accounting_export_sanitize(
            self.accounting_export_code
        )
        if not self.accounting_export_code:
            self.state = "empty"
        else:
            existing_suffixes = ResPartner._get_existing_accounting_export_codes(
                company_ids=[self.company_id.id], ignore_partner=self.partner_id
            ).get(self.company_id.id, [])
            if self.accounting_export_code in existing_suffixes:
                self.state = "duplicate_existing"
            else:
                if (
                    self.wizard_id.line_ids.filtered(
                        lambda x: x.company_id == self.company_id
                    )
                    .filtered(lambda x: x.partner_id != self.partner_id)
                    .filtered(
                        lambda x: x.accounting_export_code
                        == self.accounting_export_code
                    )
                ):
                    self.state = "duplicate_new"
                else:
                    self.state = "ok"
