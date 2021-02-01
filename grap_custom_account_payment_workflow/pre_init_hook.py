import logging

logger = logging.getLogger(__name__)


def pre_init_populate_data(cr):
    requests = [
        """
        ALTER TABLE account_move
            ADD COLUMN is_payment_checked bool;
        """,
        """
        ALTER TABLE account_payment
            ADD COLUMN is_checked bool;
        """,
        """
        UPDATE account_move
            SET is_payment_checked = true;
        """,
        """
        UPDATE account_payment
            SET is_checked = true
            WHERE payment_type != 'transfer'
            AND state != 'draft';
        """,
    ]

    for request in requests:
        logger.info("Execute: %s" % request)
        cr.execute(request)
