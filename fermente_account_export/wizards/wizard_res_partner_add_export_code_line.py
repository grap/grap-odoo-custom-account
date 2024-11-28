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
        comodel_name="wizard.res.partner.add.export.code", ondelete="cascade"
    )

    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Partner", readonly=True
    )

    company_id = fields.Many2one(
        comodel_name="res.company", string="Company", readonly=True
    )

    export_suffix = fields.Char(size=4)

    state = fields.Selection(selection=_STATE_SELECTION, readonly=True)

    @api.onchange("export_suffix")
    def onchange_export_suffix(self):
        ResPartner = self.env["res.partner"]
        self.export_suffix = ResPartner._accounting_export_sanitize(self.export_suffix)
        if not self.export_suffix:
            self.state = "empty"
        else:
            existing_suffixes = ResPartner._get_existing_export_suffixs(
                company_ids=[self.company_id.id], ignore_partner=self.partner_id
            ).get(self.company_id.id, [])
            if self.export_suffix in existing_suffixes:
                self.state = "duplicate_existing"
            else:
                if (
                    self.wizard_id.line_ids.filtered(
                        lambda x: x.company_id == self.company_id
                    )
                    .filtered(lambda x: x.partner_id != self.partner_id)
                    .filtered(lambda x: x.export_suffix == self.export_suffix)
                ):
                    self.state = "duplicate_new"
                else:
                    self.state = "ok"
