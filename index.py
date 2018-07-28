from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import xlsxwriter
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
import sqlite3
import schedule
conn = sqlite3.connect('db.sqlite3')
c=conn.cursor()
def product_link(content,driver,j):
    if content.find('ul',attrs={'class':'product-list group'}):
        products=content.find('ul',attrs={'class':'product-list group'}).findAll('li')
        for product in products:
            product_url='https://www.takealot.com'+product.find('p',attrs={'class':'p-title fn'}).find('a')['href']
            driver.get(product_url)
            time.sleep(5)
            html = driver.execute_script("return document.body.innerHTML;")
            content = BeautifulSoup(html, "html.parser")
            if content.find('h1',attrs={'class':'fn'}):
                title=content.find('h1').get_text().strip()
                print(j)

                print(title)
                seller1=''
                price1=''
                seller2 = ''
                price2 = ''
                if content.find('span',attrs={'class':'sold-by'}):
                    seller1=content.find('span',attrs={'class':'sold-by'}).find('a').get_text().strip()
                if content.find('div',attrs={'class':'product-wrap product'}):
                    if content.find('div',attrs={'class':'product-wrap product'}).find('span',attrs={'class':'amount'}):
                        price1=content.find('div',attrs={'class':'product-wrap product'}).find('span',attrs={'class':'amount'}).get_text().strip()
                if content.find('div', attrs={'class': 'more-choices group buybox-bordered'}):
                    if content.find('div', attrs={'class': 'more-choices group buybox-bordered'}).find('span', attrs={'class': 'alt-seller'}):
                        seller2=content.find('div', attrs={'class': 'more-choices group buybox-bordered'}).find('span', attrs={'class': 'alt-seller'}).get_text().strip()
                        price2=content.find('div', attrs={'class': 'more-choices group buybox-bordered'}).find('span',attrs={'class':'amount'}).get_text().strip()

                print(seller1)
                c.execute("INSERT INTO result  VALUES (?,?,?,?,?,?,?)",(j,title,seller1,price1,seller2,price2,product_url))
                # Save (commit) the changes
                conn.commit()
                j = j + 1
    return j
def scrape(url,j):
    # opts = Options()
    # opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64)")
    # opts.add_argument('--headless')
    # driver = webdriver.Chrome('/home/admin1987/Python-project/scraper/chromedriver', chrome_options=opts)
    driver = webdriver.PhantomJS(executable_path="/home/admin1987/Python-project/scraper/phantomjs")

    workbook = xlsxwriter.Workbook('result.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', 'Product Title')
    worksheet.write('B1', 'Seller 1')
    worksheet.write('C1', 'Price')
    worksheet.write('D1', 'Seller 2')
    worksheet.write('E1', 'Price')
    worksheet.write('F1', 'Link')
    driver.get(url)
    time.sleep(10)
    html=driver.execute_script("return document.body.innerHTML;")
    content=BeautifulSoup(html,"html.parser")
    total=product_link(content,driver,j)
    page= content.find('div',attrs={'class':'filter-paginator pagination'}).findAll('a')
    pagenum=len(page)
    for i in range(pagenum):
        if (i>0 and i<pagenum-1):
            link='https://www.takealot.com'+page[i]['href']
            driver.get(link)
            time.sleep(10)
            html = driver.execute_script("return document.body.innerHTML;")
            content = BeautifulSoup(html, "html.parser")
            total=product_link(content,driver,total)

    driver.close()
    k=1
    for row in c.execute("SELECT * FROM result ORDER BY seller1 "):
        k=k+1
        worksheet.write('A' + str(k), row[1])
        worksheet.write('B' + str(k), row[2])
        worksheet.write('C' + str(k), row[3])
        worksheet.write('D' + str(k), row[4])
        worksheet.write('E' + str(k), row[5])
        worksheet.write('F' + str(k), row[6])
    workbook.close()
def start():
    print("running Start function !")
    c.execute("DELETE FROM result")
    conn.commit()
    scrape('https://www.takealot.com/seller/monthly-madness?sort=BestSelling%20Descending&rows=120&start=0&backend=arj-fbye-zz-fla-fcenax&filter=Available:true&sellers=785161',1)
    send_from='weidongjackzhang@outlook.com'
    #send_to='Matthew@thirdwavesa.co.za'
    send_to = 'star1987lei@gmail.com'
    subject='Hello, your csv!'
    text='Your csv file was updated'
    username = 'weidongjackzhang@outlook.com'
    password = 'admin1987'
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach(MIMEText(text))

    part = MIMEBase('application', "octet-stream")
    part.set_payload(open("result.xlsx", "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="result.csv"')
    msg.attach(part)

    # context = ssl.SSLContext(ssl.PROTOCOL_SSLv3)
    # SSL connection only working on Python 3+
    smtp = smtplib.SMTP('smtp.live.com', 587)

    smtp.starttls()
    smtp.login(username, password)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.quit()

start()
# schedule.every().hour.do(start)
# schedule.every().day.at('08:10').do(start)
# schedule.every().day.at('15:10').do(start)
# schedule.every().day.at('13:20').do(start)
# schedule.every().day.at('13:50').do(start)
# schedule.every().day.at('15:25').do(start)
# schedule.every().day.at('16:00').do(start)
# schedule.every().day.at('16:30').do(start)

# while True:
#   #Run pending scheduler events
#   schedule.run_pending()
#   #Wait 60 seconds to check the trigger again
#   time.sleep(60)
