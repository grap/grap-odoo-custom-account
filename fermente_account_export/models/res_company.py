# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models

from . import export_type_format


class ResCompany(models.Model):
    _inherit = "res.company"

    export_type = fields.Selection(
        selection=export_type_format._SELECTION_EXPORT_TYPE, tracking=True
    )

    max_size_account_code = fields.Integer(tracking=True)

    third_account_add_company_suffix = fields.Boolean(
        string="Add Company Suffix", default=True, tracking=True
    )

    third_account_add_partner_suffix = fields.Boolean(
        string="Add Partner Suffix", default=True, tracking=True
    )
