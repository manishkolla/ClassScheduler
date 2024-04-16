from selenium import webdriver
from selenium.webdriver.common.by import By
import mysql.connector
import sys

driver = webdriver.Chrome(executable_path='DRIVER_HERE')

#Connecting to DataBase. we need to change Database name here.
try:
    connection = mysql.connector.connect(
        user="root",
        password="PASSWORD_HERE",
        host="localhost",
        port=3306,
        database="courses",
        use_unicode=True, 
        charset="utf8mb3"

    )
#except mysql.Error as e:
except:
    print("Error connecting to Mysql Platform:")
    #print(f"Error connecting to Mysql Platform: {e}")
    sys.exit(1)

#Getting DB cursor
cursor=connection.cursor()
#Creating two Database tables.
command1="""CREATE TABLE IF NOT EXISTS classes(Department TEXT,Number TEXT,CourseName LONGTEXT,URL LONGTEXT) DEFAULT CHARSET=utf8 ROW_FORMAT=COMPACT"""


cursor.execute(command1)
driver.get("https://catalogs.gsu.edu/content.php?catoid=25&navoid=3037")


def pageiter():
    try:
        pages=driver.find_element(By.XPATH, '//*[@id="gateway-page"]/body/table/tbody/tr[3]/td[2]/table/tbody/tr[2]/td[2]/table/tbody/tr/td/table[2]/tbody/tr[108]/td')
        page_urls=pages.find_elements(By.TAG_NAME,'a' )
    except:
        return "Classes Retrived!!!!!!!!!!!!!!"
    
    page_numbers=[]
    for urls in page_urls:
        page_numbers.append(urls.get_attribute('href'))
    
    for p in page_numbers:
        driver.get(p)
        table=driver.find_elements(By.XPATH, '//*[@id="gateway-page"]/body/table/tbody/tr[3]/td[2]/table/tbody/tr[2]/td[2]/table/tbody/tr/td/table[2]/tbody/tr/td[2]/a')
        table=table[2:-1]
        department=[]
        number=[]
        for classes in table:
            try:
                class_name=classes.text
                class_url=classes.get_attribute('href')
                print(class_name,class_url)
                department=class_name.split(" ")[0]
                number=class_name.split(" ")[1]
                name=class_name.split("-")[-1].strip()
                cursor.execute("INSERT INTO classes(Department,Number,CourseName,URL ) VALUES (%s,%s,%s,%s)", (department,number,name,class_url))
                connection.commit()
                print("inserted")
                
            except:
                continue

    print("Pages",len(page_numbers), "DONE!!!!!!!!!!!")

i=0
while i<3:
    pageiter()
    
    
    













