def parse_stock_excel(filepath: str):
    # Importing Module
    import xlrd
    # Loading Excel file
    wb = xlrd.open_workbook(filepath)
    # Storing the first sheet into a variable
    sheet = wb.sheet_by_index(0)
    # Printing various cell values
    print("Value of 0-0 cell: ",sheet.cell_value(0, 0))
    print("Value of 20-4 cell: ",sheet.cell_value(20, 4))

if __name__ == "__main__":
    print(parse_stock_excel("temp/STOCK_SAMPLE.XLS"))