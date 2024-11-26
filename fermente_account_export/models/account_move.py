# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    _ALLOWED_FIELDS_WRITE_EXPORT = [
        "narration",
        "reverse_entry_id",
    ]

    account_export_id = fields.Many2one(
        comodel_name="account.export",
        copy=False,
        readonly=True,
        help="Indicates whether the move has already been exported"
        " in an accounting Software. It is changed automatically.",
    )

    def write(self, vals):
        self._check_exported_moves(vals)
        return super().write(vals)

    def unlink(self):
        self._check_exported_moves()
        return super().unlink()

    def _check_exported_moves(self, vals=False):
        if vals:
            # it is an update, we check if the all the keys
            #  are allowed in vals
            forbidden_fields = [
                x for x in vals.keys() if x not in self._ALLOWED_FIELDS_WRITE_EXPORT
            ]
            if not forbidden_fields:
                return

        if not self.env.context.get("ignore_account_move_exported", False):
            exported_moves = self.filtered(
                lambda x: x.account_export_id.id is not False
            )
            if exported_moves:
                raise ValidationError(
                    _("You cannot modify or delete exported moves: %s!")
                    % ", ".join([m.name for m in exported_moves])
                )
