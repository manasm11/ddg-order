# Importing Module
import xlrd
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory=".")


def parse_stock_excel(filepath: str):
    # Loading Excel file
    wb = xlrd.open_workbook(filepath)
    # Storing the first sheet into a variable
    sheet: xlrd.sheet.Sheet = wb.sheet_by_index(0)
    # Defining column variables
    ITEM = 0
    QTY = 1
    MRP = 2

    def is_positive_num(cell: xlrd.sheet.Cell):
        v = cell.value
        s = str(cell.value)
        return v and s.strip() and s.replace(".", "", 1).isdigit() and float(v) > 0

    # Iterating over all rows
    result = list()
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


app = FastAPI()


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", context={"regions": regions, "request": request, "products": parse_stock_excel("temp/STOCK_SAMPLE.XLS")})


app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn

    # result = parse_stock_excel("temp/STOCK_SAMPLE.XLS")
    # {print(d) for d in result}
    # print("Length:", len(result))
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug", reload=True)


regions = [
    "ACHALGANJ",
    "AGAUS",
    "AKBARPUR",
    "ALLAHABAD",
    "ASALAT GANJ",
    "AUNAHA",
    "AURAIYA",
    "BANDA",
    "BANGARMAU",
    "BARASAROHI",
    "BEEGAHPUR",
    "BHAGHPUR",
    "BHAUPUR",
    "BHITAR GAO",
    "BIGHAPUR",
    "BILINDA",
    "BIRHANA ",
    "BITHOOR",
    "CHAUDAGRA",
    "CHIBRAMAU",
    "DAHI ",
    "DERAPUR",
    "DHATA",
    "DIBIAPUR",
    "ETAWAH",
    "FARIDPUR",
    "FARRUKHABAD",
    "FATEHPUR",
    "FAZALGANJ",
    "GORAKHPUR",
    "GUJANI",
    "GURSAHAYAN",
    "HAIDRABAD",
    "HAMEERPUR",
    "HARDOI",
    "JALLAUN",
    "JHANSI",
    "JUNIHA",
    "KANNAUJ",
    "KANPUR",
    "KARWI",
    "KIDWAI",
    "KONCH",
    "KUDNI",
    "MADHAVGANJ",
    "MAHOBA",
    "MALWA",
    "MANIMAU",
    "MAQSUDABAD",
    "MUNGISAPUR",
    "NOONARI",
    "ORAI",
    "PATAN",
    "PATARA",
    "PUKHRAYAN",
    "PUNJAB",
    "PURWA",
    "RAATH",
    "RAMA ",
    "RAMAIPUR",
    "RASULABAD",
    "REWADI",
    "ROOMA",
    "SAFIPUR",
    "SAHLI",
    "SAJETI",
    "SHAMBHUA",
    "SHANKAR",
    "SWAROOP NAGAR ",
    "TAUS",
    "TIKRA",
    "TIRWA",
    "UMARDA",
    "UNNAO",
    "VISHDHAN",
]
