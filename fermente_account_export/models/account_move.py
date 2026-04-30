# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    _ALLOWED_FIELDS_WRITE_EXPORT = [
        # Allow to send to partner after export
        "is_move_sent",
        # Allow to generate access token to public visualization
        "access_token",
        # Allow to write a free text
        "narration",
        # Allow to mark a move as to check again
        "to_check",
        # Allow to set a credit note on an exported invoice
        "reverse_entry_id",
        # Technical field that is frequently written by the ORM
        "needed_terms_dirty",
        # Allow to create/delete attachment
        "message_attachment_count",
        "message_main_attachment_id",
    ]

    account_export_id = fields.Many2one(
        comodel_name="account.export",
        copy=False,
        readonly=True,
        tracking=True,
        help="Indicates whether the move has already been exported"
        " in an accounting Software. It is changed automatically.",
    )

    def write(self, vals):
        self._check_exported_moves(vals, mode="write")
        return super().write(vals)

    def unlink(self):
        self._check_exported_moves(False, mode="unlink")
        return super().unlink()

    def _check_exported_moves(self, vals, mode="write"):
        if self.env.context.get("ignore_account_move_exported", False):
            return

        exported_moves = self.filtered(lambda x: x.account_export_id)
        if not exported_moves:
            return

        if mode == "write":
            if not vals:
                return

            # we check if the all the keys are allowed in vals
            forbidden_fields = [
                x for x in vals.keys() if x not in self._ALLOWED_FIELDS_WRITE_EXPORT
            ]
            if not forbidden_fields:
                return
            raise ValidationError(
                _(
                    "You cannot modify exported moves: %(move_names)s."
                    " Forbidden fields: %(field_names)s",
                    move_names=", ".join([m.name for m in exported_moves]),
                    field_names=forbidden_fields,
                )
            )
        elif mode == "unlink":
            raise ValidationError(
                _(
                    "You cannot delete exported moves: %(move_names)s.",
                    move_names=", ".join([m.name for m in exported_moves]),
                )
            )
