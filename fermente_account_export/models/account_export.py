# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64
import logging

from odoo import _, api, fields, models

from . import export_type_format

_logger = logging.getLogger(__name__)


class AccountExport(models.Model):
    _name = "account.export"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Account Export"
    _order = "export_date desc"

    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        readonly=True,
    )

    fiscal_year_id = fields.Many2one(
        comodel_name="account.fiscal.year",
        string="Fiscal year",
        required=True,
        readonly=True,
    )

    export_date = fields.Datetime(required=True, readonly=True)

    name = fields.Char(compute="_compute_name", store=True, readonly=True)

    description = fields.Text(
        readonly=True,
        help="Extra Description for Accountant Manager.",
    )

    move_ids = fields.One2many(
        comodel_name="account.move",
        inverse_name="account_export_id",
        string="Moves",
        readonly=True,
    )

    move_qty = fields.Integer(
        compute="_compute_move_qty", string="Moves Quantity", store=True
    )

    data = fields.Binary(string="Main file", readonly=True, attachment=True)

    file_name = fields.Char(compute="_compute_file_names")

    export_type = fields.Selection(
        selection=export_type_format._SELECTION_EXPORT_TYPE, required=True
    )

    # Compute Section
    @api.depends("export_date")
    def _compute_name(self):
        for export in self:
            export.name = _("Export #%(export_id)d", export_id=export.id)

    @api.depends("move_ids.account_export_id")
    def _compute_move_qty(self):
        for export in self:
            export.move_qty = len(export.move_ids)

    def _compute_file_names(self):
        for export in self:
            export.file_name = (
                f"{export.name} - "
                f"{export.export_date.strftime('%Y-%m-%d__%H-%M-%S')}.xlsx"
            )

    def export_xlsx(self):
        self.ensure_one()
        raw_value = self.env["ir.actions.report"]._render(
            "fermente_account_export.report", self.ids, None
        )[0]
        self.data = base64.b64encode(raw_value)

    def _get_moves_and_accounts_data(self):
        self.ensure_one()
        moves_data = []
        accounts_data = {}

        for move in self.move_ids:
            # dictionary to summarize the lines of the move by account
            move_lines_data = {}

            # Ignoring line with null debit and credit
            for line in move.line_ids.filtered(lambda x: x.credit != x.debit).sorted(
                lambda x: (x.account_id.code)
            ):
                account_code = line._export_get_account_code()
                analytic_code = line._export_get_analytic_code()

                # Collect data for the file of move lines
                move_line_key = (
                    move.name,
                    account_code,
                    analytic_code,
                    line.date_maturity,
                    line.credit > 0,
                    line.partner_id,
                )

                if move_line_key not in move_lines_data.keys():
                    move_lines_data[move_line_key] = line
                else:
                    move_lines_data[move_line_key] |= line

                # Collect data for the file of accounts
                account_key = (account_code,)
                if account_key not in accounts_data.keys():
                    accounts_data[account_key] = line
                else:
                    accounts_data[account_key] |= line

            moves_data.append(move_lines_data)

        return (moves_data, accounts_data)
