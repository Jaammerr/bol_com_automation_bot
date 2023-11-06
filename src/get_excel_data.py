import os
import sys

import xlwings as xw
from loguru import logger


def get_excel_data() -> list[tuple[str, str]]:
    excel_file_path = os.path.join(os.getcwd(), "input.xlsx")

    if not os.path.exists(excel_file_path):
        logger.error(
            f"Excel file not found at {excel_file_path} | Please create an excel file with name 'input.xlsx' and add the search terms in column C and the link in column D"
        )
        sys.exit(1)

    wb = xw.Book(excel_file_path)
    ws = wb.sheets["Sheet1"]

    if (
        ws.range("C1").value is None
        or ws.range("C1").value.lower() != "Search term".lower()
    ):
        logger.error(
            f"Invalid column name at B1. Expected 'Search Item' but found {ws.range('C1').value}"
        )
        sys.exit(1)

    if ws.range("D1").value is None or ws.range("D1").value.lower() != "Link".lower():
        logger.error(
            f"Invalid column name at D1. Expected 'Link' but found {ws.range('D1').value}"
        )
        sys.exit(1)

    values_list: list[tuple[str, str]] = ws["C1"].expand().value
    values_list.pop(0)  # remove header row
    return values_list
