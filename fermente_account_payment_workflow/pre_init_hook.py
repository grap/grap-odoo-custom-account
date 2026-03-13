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
            FROM account_payment ap
                JOIN account_move am ON ap.move_id = am.id
            WHERE ap.payment_type != 'transfer'
            AND am.state != 'draft';
        """,
    ]

    for request in requests:
        logger.info("Execute: %s" % request)
        cr.execute(request)
