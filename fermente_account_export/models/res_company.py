# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    # Column Section
    ebp_analytic_enabled = fields.Boolean(
        string="Enable Analytic in EBP",
        default=False,
        help="Check this box if you want to enable the analytic when"
        " exporting in EBP.",
    )

    ebp_default_analytic_account_id = fields.Many2one(
        string="Default Analytic Account for EBP",
        comodel_name="account.analytic.account",
    )

    @api.constrains("ebp_analytic_enabled", "fiscal_type")
    def _ebp_check_analytic_mode_fiscal_type(self):
        companies = self.filtered(
            lambda x: x.fiscal_type in ["fiscal_child", "fiscal_mother"]
            and x.ebp_analytic_enabled
        )
        if companies:
            raise ValidationError(
                _(
                    "Unable to enable analytic for the following companies"
                    " that are CAE or Integrated companies %s"
                    % (", ".join([x.name for x in companies]))
                )
            )
