from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os
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
os.remove("result.csv")
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
    # opts.add_argument("--headless")
    # driver = webdriver.Chrome('/home/ec2-user/python/scraper/chromedriver', chrome_options=opts)
    # driver = webdriver.Chrome('chromedriver.exe')
    driver = webdriver.PhantomJS(executable_path="/home/ubuntu/python/scraper/phantomjs")
    csvFileName = 'result.csv'
    csvfile = open(csvFileName, "a+")
    csvfile.write("Product Title,Seller 1,Price,Seller 2,Price,Link\n")

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


        csvfile.write(str(row[1])+','+str(row[2])+','+str(row[3])+','+str(row[4])+','+str(row[5])+','+str(row[6])+'\n')
    csvfile.close()

def start():
    c.execute("DELETE FROM result")
    conn.commit()
    scrape('https://www.takealot.com/seller/monthly-madness?sort=BestSelling%20Descending&rows=120&start=0&backend=arj-fbye-zz-fla-fcenax&filter=Available:true&sellers=785161',1)
    send_from='weidongjackzhang@outlook.com'
    send_to='Matthew@thirdwavesa.co.za'
    # send_to = 'star1987lei@gmail.com'
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
    part.set_payload(open("result.csv", "rb").read())
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

# start()

schedule.every().day.at('06:10').do(start)
schedule.every().day.at('13:10').do(start)
while True:
  #Run pending scheduler events
  schedule.run_pending()
  #Wait 60 seconds to check the trigger again
  time.sleep(60)
