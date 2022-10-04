# Importing Module
import xlrd


def parse_stock_excel(filepath: str):
    # Loading Excel file
    wb = xlrd.open_workbook(filepath)
    # Storing the first sheet into a variable
    sheet: xlrd.sheet.Sheet = wb.sheet_by_index(0)
    ITEM = 0
    QTY = 1
    MRP = 2
    is_data_row = False
    result = list()

    def is_positive_num(cell: xlrd.sheet.Cell):
        v = cell.value
        s = str(cell.value)
        return v and s.strip() and s.replace(".", "", 1).isdigit() and float(v) > 0

    # Iterating over all rows
    for row in sheet.get_rows():
        if is_positive_num(row[QTY]) and is_positive_num(row[MRP]):
            result.append(
                {
                    # "qty": row[QTY].value,
                    # "mrp": row[MRP].value,
                    "item": row[ITEM].value,
                }
            )
    return result


if __name__ == "__main__":
    result = parse_stock_excel("temp/STOCK_SAMPLE.XLS")
    {print(d) for d in result}
    print("Length:", len(result))
