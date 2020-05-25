This module extends the functionality of account invoices to
changes default behaviour that doesn't fit with GRAP needs.

Add a 'Verified' state on ``account.invoice`` (supplier and supplier
refund invoices)

* Only the users member of 'Accounting & Finance / Billing Manager'
  can validate supplier account invoices
* Member of 'Accounting & Finance / Billing' can only verify invoices.

Add a constraint, when verifying supplier invoices.
