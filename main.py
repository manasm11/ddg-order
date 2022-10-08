# Importing Module
from datetime import datetime
import os
import json
import xlrd
from fastapi import FastAPI, Request, Form, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials

import smtplib

EMAIL_FROM = open("email").read().strip()
PASSWORD = open("password").read().strip()
EMAIL_TO = open("emailto").read().strip()

ADMIN_USERNAME = open("admin_username").read().strip()
ADMIN_PASSWORD = open("admin_password").read().strip()

templates = Jinja2Templates(directory=".")

security = HTTPBasic()

app = FastAPI()


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        context={
            "regions": regions,
            "request": request,
            "products": parse_stock_excel("temp/STOCK_SAMPLE.XLS"),
        },
    )


@app.get("/admin")
async def root(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    if (
        credentials.username == ADMIN_USERNAME
        and credentials.password == ADMIN_PASSWORD
    ):
        if not os.path.exists("orders/"):
            os.mkdir("orders")
        return templates.TemplateResponse(
            "admin.html",
            context={
                "request": request,
                "orders": reversed(os.listdir("orders")),
            },
        )
    else:
        return "WRONG CREDENTIALS !!!"


@app.post("/order")
async def order(
    bg: BackgroundTasks,
    name: str = Form(),
    region: str = Form(),
    contact: str = Form(),
    items: str = Form(),
):
    items: dict = json.loads(items)
    billno: int = datetime.now().timestamp() * 10000 % 16650000000000
    bill = f"ONL{int(billno)}"
    print(
        f"name={name}, region={region}, contact={contact}, items={items}, bill={bill}"
    )
    csv_data = [f"{k},{v},{bill}\n" for k, v in items.items()]
    if not os.path.exists("orders/"):
        os.mkdir("orders")
    date_time = datetime.now().isoformat().replace("T", " ").split(".")[0]
    csv_path = f"orders/{date_time}__{name}__{region}__{contact}__{bill}.csv"
    with open(csv_path, "w") as f:
        f.write("Item Name,Quantity,Bill No.\n")
        f.writelines(csv_data)

    bg.add_task(send_mail, csv_path)
    return FileResponse("order_placed.html")


app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount(
    "/orders",
    StaticFiles(directory="orders", html=True, check_dir=False),
    name="orders",
)


def send_mail(csv_path: str):
    # Create a multipart message
    shop, region, contact, *_ = csv_path.split("__")
    shop = shop.replace("#", " ").split("/")[-1]
    region = region.replace("#", " ")
    subject = f"Order: '{shop}' {region}, {contact}"
    body = open(csv_path).read()
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(EMAIL_FROM, PASSWORD)

        msg = f"Subject: {subject}\n\n{body}"

        smtp.sendmail(EMAIL_FROM, EMAIL_TO, msg)


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
