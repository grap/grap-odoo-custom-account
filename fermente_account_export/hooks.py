import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("[default Export Code] Initialize journal export code")
    env.cr.execute(
        """
        UPDATE account_journal
        SET export_code = code;
        """
    )
