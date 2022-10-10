# Importing Module
from datetime import datetime
import os
import json
import xlrd
from fastapi import FastAPI, Request, Form, Depends, BackgroundTasks, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from tempfile import NamedTemporaryFile

import shutil
import os
import smtplib
from email.message import EmailMessage

EMAIL_FROM = open("conf/email").read().strip()
PASSWORD = open("conf/password").read().strip()
EMAIL_TO = open("conf/emailto").read().strip()

ADMIN_USERNAME = open("conf/admin_username").read().strip()
ADMIN_PASSWORD = open("conf/admin_password").read().strip()

CURRENT_STOCK = json.load(open("stock.json")) if os.path.exists("stock.json") else []

templates = Jinja2Templates(directory="html")

security = HTTPBasic()

app = FastAPI()


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        "html/index.html",
        context={
            "regions": regions,
            "request": request,
            "products": CURRENT_STOCK,
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
            "html/admin.html",
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
    name = name.upper()
    region = region.upper()
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
    return FileResponse("html/order_placed.html")


@app.post("/uploadstock/")
async def create_upload_file(stock: UploadFile):
    global CURRENT_STOCK
    temp_file_path = save_uploaded_file(stock)
    CURRENT_STOCK = parse_stock_excel(temp_file_path)
    with open("stock.json", "w") as f:
        json.dump(CURRENT_STOCK, f)
    return RedirectResponse("/admin", 301)


app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount(
    "/orders",
    StaticFiles(directory="orders", html=True, check_dir=False),
    name="orders",
)


def save_uploaded_file(file: UploadFile):
    with NamedTemporaryFile(delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        file.file.close()
        return tmp.name


def send_mail(csv_path: str):
    # orders/2022-10-09 00:12:04__SOME SHOP__HAIDRABAD__8400640404__ONL2545244043.csv
    _, shopname, region, contact, _ = csv_path.split("__")
    msg = EmailMessage()
    msg["Subject"] = f"Order: {shopname} {region}"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_FROM

    msg.set_content(
        f"Order from {shopname} {region}, contact {contact} for more detail."
    )

    msg.add_attachment(open(csv_path).read(), filename=csv_path.split("/")[-1])

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_FROM, PASSWORD)
        smtp.send_message(msg)


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

    uvicorn.run("main:app", port=8001, log_level="debug", reload=True)


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
