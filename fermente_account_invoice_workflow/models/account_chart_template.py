# Copyright (C) 2013 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, models


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    @api.model
    def _post_create_demo_data(self, created):
        return super()._post_create_demo_data(
            created.with_context(chart_template_create_demo_data=True)
        )
