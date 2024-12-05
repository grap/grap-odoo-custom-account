# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class WizardAccountExport(models.TransientModel):
    _name = "wizard.account.export"
    _description = "Account Export Wizard"

    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        readonly=True,
        default=lambda s: s._default_company_id(),
    )

    account_export_id = fields.Many2one(
        string="Account Export", comodel_name="account.export", readonly=True
    )

    fiscal_year_id = fields.Many2one(
        comodel_name="account.fiscal.year",
        string="Fiscal Year",
        required=True,
        default=lambda s: s._default_fiscal_year_id(),
        help="Only the moves in this fiscal year will be exported",
        domain="[('company_id', '=', company_id)]",
    )

    description = fields.Text(help="Extra Description for Accountant Manager.")

    ignored_draft_move_qty = fields.Integer(
        compute="_compute_move_selection", store=True
    )

    ignored_fiscal_year_move_qty = fields.Integer(
        compute="_compute_move_selection", store=True
    )

    ignored_journal_code_move_qty = fields.Integer(
        compute="_compute_move_selection", store=True
    )

    ignored_to_check_move_qty = fields.Integer(
        compute="_compute_move_selection", store=True
    )

    ignored_exported_move_qty = fields.Integer(
        compute="_compute_move_selection", store=True
    )

    ignored_partner_move_qty = fields.Integer(
        compute="_compute_move_selection", store=True
    )

    ignored_tax_move_qty = fields.Integer(compute="_compute_move_selection", store=True)

    selected_move_qty = fields.Integer(
        string="Quantity of Selected Moves",
        readonly=True,
        compute="_compute_move_selection",
        store=True,
    )

    exported_move_ids = fields.Many2many(
        string="Exported Moves",
        comodel_name="account.move",
        compute="_compute_move_selection",
        store=True,
    )

    exported_move_qty = fields.Integer(
        string="Quantity of Exported Moves",
        readonly=True,
        compute="_compute_move_selection",
        store=True,
    )

    @api.model
    def _default_company_id(self):
        if self.env.company.fiscal_type == "group":
            raise ValidationError(_("Unable to export account moves at group level"))
        return self.env.company.fiscal_company_id.id

    @api.model
    def _default_fiscal_year_id(self):
        dates = [
            x["date"]
            for x in self.env["account.move"].search_read(
                [("id", "in", self.env.context.get("active_ids"))], ["date"]
            )
        ]
        min_date = min(dates)
        max_date = max(dates)
        for fiscal_year in self.env["account.fiscal.year"].search([]):
            if fiscal_year.date_from <= min_date and max_date <= fiscal_year.date_to:
                return fiscal_year.id

    @api.depends("fiscal_year_id")
    def _compute_move_selection(self):
        AccountMove = self.env["account.move"]
        AccountJournal = self.env["account.journal"]

        for wizard in self:
            selected_moves = AccountMove.browse(self.env.context.get("active_ids", []))
            wizard.selected_move_qty = len(selected_moves)

            selection_domain = [("id", "in", self.env.context.get("active_ids", []))]
            full_domain = selection_domain[:]

            # filter by state (remove draft)
            wizard.ignored_draft_move_qty = len(
                AccountMove.search(selection_domain + [("state", "=", "draft")])
            )
            full_domain += [("state", "!=", "draft")]

            # Filter by partner without export suffix
            incorrect_partner_move_lines = selected_moves.mapped("line_ids").filtered(
                lambda x: x.partner_id and x.partner_id.export_suffix is False
            )
            incorrect_partner_move_ids = incorrect_partner_move_lines.mapped(
                "move_id"
            ).ids
            wizard.ignored_partner_move_qty = len(incorrect_partner_move_ids)
            full_domain += [("id", "not in", incorrect_partner_move_ids)]

            # Filter by tax code without export suffix
            incorrect_tax_move_lines = selected_moves.mapped("line_ids").filtered(
                lambda x: x.account_id.export_suffix_on_tax_required
                and False in x.mapped("tax_ids.export_suffix")
            )
            incorrect_tax_move_ids = incorrect_tax_move_lines.mapped("move_id").ids
            wizard.ignored_tax_move_qty = len(incorrect_tax_move_ids)
            full_domain += [("id", "not in", incorrect_tax_move_ids)]

            # filter by fiscalyear
            if wizard.fiscal_year_id:
                wizard.ignored_fiscal_year_move_qty = len(
                    AccountMove.search(
                        selection_domain
                        + [
                            "|",
                            ("date", "<", wizard.fiscal_year_id.date_from),
                            ("date", ">", wizard.fiscal_year_id.date_to),
                        ]
                    )
                )
                full_domain += [
                    ("date", ">=", wizard.fiscal_year_id.date_from),
                    ("date", "<=", wizard.fiscal_year_id.date_to),
                ]
            else:
                wizard.ignored_fiscal_year_move_qty = 0

            # Filter by journal (export_code should be defined)
            journal_without_export_codes = AccountJournal.search(
                [("export_code", "!=", False)]
            )
            wizard.ignored_journal_code_move_qty = len(
                AccountMove.search(
                    selection_domain
                    + [("journal_id", "not in", journal_without_export_codes.ids)]
                )
            )
            full_domain += [("journal_id", "in", journal_without_export_codes.ids)]

            # filter moves to check
            wizard.ignored_to_check_move_qty = len(
                AccountMove.search(selection_domain + [("to_check", "=", True)])
            )
            full_domain += [("to_check", "=", False)]

            # filter yet exported moves
            wizard.ignored_exported_move_qty = len(
                AccountMove.search(
                    selection_domain + [("account_export_id", "!=", False)]
                )
            )
            full_domain += [("account_export_id", "=", False)]

            wizard.exported_move_ids = AccountMove.search(full_domain)
            wizard.exported_move_qty = len(wizard.exported_move_ids.ids)

    def _prepare_account_export(self):
        self.ensure_one()
        return {
            "fiscal_year_id": self.fiscal_year_id.id,
            "description": self.description,
            "company_id": self.company_id.id,
            "export_date": fields.Datetime.now(),
        }

    def button_export(self):
        self.ensure_one()
        self._compute_move_selection()
        if self.exported_move_qty == 0:
            raise ValidationError(_("No account move can be exported."))
        AccountExport = self.env["account.export"]
        self.account_export_id = AccountExport.create(self._prepare_account_export())
        self.account_export_id.export(self.exported_move_ids)
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.export",
            "view_mode": "form",
            "view_type": "form",
            "res_id": self.account_export_id.id,
            "views": [(False, "form")],
        }
