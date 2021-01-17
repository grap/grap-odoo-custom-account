# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, models


class WizardEbpUnexport(models.TransientModel):
    _name = "wizard.ebp.unexport"
    _description = "EBP Unexport Wizard"

    @api.multi
    def button_unexport(self):
        AccountMove = self.env["account.move"]
        moves = AccountMove.browse(self.env.context.get("active_ids", False))
        # We use sudo, because in a CAE context, if we cancel an export done
        # in GRP context, it will not be accessible in 3PP context.
        moves.sudo().with_context(force_write_ebp_exported=True).write(
            {"ebp_export_id": False}
        )
