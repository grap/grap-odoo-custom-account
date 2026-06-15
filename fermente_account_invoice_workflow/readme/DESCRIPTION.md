This module extends the functionality of account moves to changes
default behaviour that doesn't fit with GRAP (Fermente!) needs.

Add a 'Verified' state on `account.move` (supplier and supplier
refund invoices)

- Only the users member of 'Accounting / Accountant' can
  validate supplier account invoices
- Member of 'Accounting / Billing' can only verify invoices.

Add a constraint, when verifying supplier invoices. check if the following fields
are correctly set:

- Bill Date (`invoice_date`)
- Due Date (`invoice_date_due`)
- Vendor Invoice Number (`supplier_invoice_number`)

Note:
This check is not done on account moves that are generated from `hr_expense`.
