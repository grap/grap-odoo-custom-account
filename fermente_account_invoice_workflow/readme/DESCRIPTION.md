This module extends the functionality of account moves to changes
default behaviour that doesn't fit with GRAP (Fermente!) needs.

Add a 'Verified' state on `account.move` (supplier and supplier
refund invoices)

- Only the users member of 'Accounting / Accountant' can
  validate supplier account invoices
- Member of 'Accounting / Billing' can only verify invoices.

Add a constraint, when verifying supplier invoices.
