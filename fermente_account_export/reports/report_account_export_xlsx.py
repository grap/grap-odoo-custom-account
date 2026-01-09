# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import xlsxwriter

from odoo import _, models

from ..models import export_type_format


class ReportAccountExportXlsx(models.AbstractModel):
    _name = "report.report_account_export_xlsx.report"
    _inherit = "report.report_xlsx.abstract"
    _description = "Abstract model to export as xlsx account moves and accounts"

    def create_page(
        self,
        export,
        data,
        workbook,
        sheet_name,
        column_names,
        content_function,
        header_specification=None,
        size_specification=None,
        header_format=None,
        line_odd_format=None,
        line_even_format=None,
    ):
        header_specification = header_specification or []
        size_specification = size_specification or {}

        sheet = workbook.add_worksheet(sheet_name)

        # Set column Size
        if size_specification:
            for column_name, size in size_specification.items():
                xls_name = xlsxwriter.utility.xl_col_to_name(
                    column_names.index(column_name)
                )
                sheet.set_column(f"{xls_name}:{xls_name}", size)

        row = 0

        # Write header, if required
        if header_specification:
            col = 0

            for column_name in column_names:
                if column_name not in header_specification:
                    raise Exception(
                        f"{column_name} not in Header: {header_specification.keys()}"
                    )
                value = header_specification[column_name]
                sheet.write(row, col, value, header_format)
                col += 1

            row += 1

        # Write Content
        for line_data in content_function(export, data):
            col = 0
            is_odd = line_data["is_odd"]

            for column_name in column_names:
                if column_name not in line_data:
                    raise Exception(
                        f"{column_name} not in Content: {line_data.keys()}."
                    )
                value = line_data[column_name]
                line_format = is_odd and line_odd_format or line_even_format
                sheet.write(row, col, value, line_format)
                col += 1

            row += 1

    def generate_xlsx_report(self, workbook, data, objects):
        # "num_format": "0.00"
        header_format = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vjustify",
                "fg_color": "#8888CC",
            }
        )
        line_odd_format = workbook.add_format(
            {
                "border": 1,
                "valign": "vjustify",
                "fg_color": "#FFFFFF",
            }
        )
        line_even_format = workbook.add_format(
            {
                "border": 1,
                "valign": "vjustify",
                "fg_color": "#E0E0E0",
            }
        )

        export = objects

        format_tools = getattr(
            export_type_format, f"export_type_format_{objects.export_type}"
        )

        (moves_data, accounts_data) = export._get_moves_and_accounts_data()

        self.create_page(
            export,
            moves_data,
            workbook,
            _("ACCOUNT MOVES"),
            format_tools._MOVES_COLUMNS,
            format_tools._get_formated_moves_data,
            header_specification=format_tools._MOVES_HEADER,
            size_specification=format_tools._MOVES_SIZE,
            header_format=header_format,
            line_odd_format=line_odd_format,
            line_even_format=line_even_format,
        )

        self.create_page(
            export,
            accounts_data,
            workbook,
            _("ACCOUNTS"),
            format_tools._ACCOUNTS_COLUMNS,
            format_tools._get_formated_accounts_data,
            header_specification=format_tools._ACCOUNTS_HEADER,
            size_specification=format_tools._ACCOUNTS_SIZE,
            header_format=header_format,
            line_odd_format=line_odd_format,
            line_even_format=line_even_format,
        )
