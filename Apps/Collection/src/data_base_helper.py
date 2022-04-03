#You are connected to database "central_db" as user "postgres" via socket in "/var/run/postgresql" at port "5432".
#todo make funvtions that allow for easy transfer of csv's to psql table
#works just need to install 'pip install psycopg2'
#python3.10 -m pip install --upgrade setuptools
#python3.10 -m Apps.Collection.src.data_base_helper
#sudo -u postgres -i
#CREATE USER max WITH PASSWORD 'password';

import psycopg2

conn = psycopg2.connect(database="dummy", user = "max", password = "password", host = "127.0.0.1", port = "5432")

print(conn)


conn.autocommit = True
cursor = conn.cursor()
  
#ARGENX SE,04016X101,9766,27889,SH,,DFND,1,2,3,4,27889,0,0
sql = '''CREATE TABLE TEMPTEST(company_name varchar(63),\
    filling_date varchar(30),\
    num1 int, num2 int, cmp_ticker varchar(30), varnum varchar(30) ,\
    cmp_ticker2 varchar(30),num11 int, num12 int, num13 int, num14 int,\
    num15 int, num16 int, num17 int);'''
  
  
#cursor.execute(sql)
  
sql2 = '''COPY details(employee_id,employee_name,\
employee_email,employee_salary)
FROM 'resources/13F-HR-parsed-data.csv'
DELIMITER ','
CSV HEADER;'''
  
cursor.execute(sql2)
  
sql3 = '''select * from details;'''
cursor.execute(sql3)
for i in cursor.fetchall():
    print(i)
  
conn.commit()
conn.close()




def csv_to_psql_data_table(csv_file, data_base="dummy", 
                           user="max", password = "password", 
                           host = "127.0.0.1", port = "5432"):
    pass

