# Copyright (C) 2018-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    @api.model
    def _get_tax_group_by_amount(self, amount):
        xml_id = {
            -20: "l10n_fr.tax_group_intra_20",
            -8.5: "l10n_fr.tax_group_intra_85",
            -10: "l10n_fr.tax_group_intra_10",
            -5.5: "l10n_fr.tax_group_intra_55",
            -2.1: "l10n_fr.tax_group_intra_21",
            0: "l10n_fr.tax_group_tva_0",
            2.1: "l10n_fr.tax_group_tva_21",
            5.5: "l10n_fr.tax_group_tva_55",
            8.5: "l10n_fr.tax_group_tva_85",
            10: "l10n_fr.tax_group_tva_10",
            20: "l10n_fr.tax_group_tva_20",
        }.get(amount, "account.tax_group_taxes")
        return self.env.ref(xml_id)

    @api.onchange("amount")
    def onchange_amount(self):
        res = super().onchange_amount()
        self.tax_group_id = self._get_tax_group_by_amount(self.amount).id
        return res

    @api.model
    def create(self, vals):
        vals["tax_group_id"] = self._get_tax_group_by_amount(vals["amount"]).id
        return super().create(vals)
