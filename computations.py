import sqlite3
import datetime as dt
from datetime import datetime, date, timedelta, time
import ctypes

# Teaching -- Official Time
official_time_am_in = datetime.strptime('7:30:00 AM',"%I:%M:%S %p").time()
official_time_am_out = datetime.strptime('11:30:00 AM',"%I:%M:%S %p").time()
official_time_pm_in = datetime.strptime('1:00:00 PM',"%I:%M:%S %p").time()
official_time_pm_out = datetime.strptime('5:00:00 PM',"%I:%M:%S %p").time()

# Non-Teaching --  Official Time
official_time_am_in_ = datetime.strptime('8:00:00 AM',"%I:%M:%S %p").time()
official_time_am_out_ = datetime.strptime('12:00:00 PM',"%I:%M:%S %p").time()
official_time_pm_in_ = datetime.strptime('1:00:00 PM',"%I:%M:%S %p").time()
official_time_pm_out_ = datetime.strptime('5:00:00 PM',"%I:%M:%S %p").time()


def tardy():
    # Connect or start database
    conn = sqlite3.connect('db_employees.db')
    c = conn.cursor()
    c.execute("""UPDATE tb_transaction set  job_desc = (select job_desc from tb_emp_info where tb_transaction.empID = tb_emp_info.empID)""")
    
    # Row Count
    rowid = 1
    # Iterate through the list of employee trasacations
    for row in c.execute("""SELECT * FROM tb_transaction""").fetchall():
        pm_in = c.execute("""SELECT pm_in from tb_transaction WHERE rowid=?""",(rowid,)).fetchall()
        am_in = c.execute("""SELECT am_in from tb_transaction where rowid=?""",(rowid,)).fetchall()
        
        # Compute for tardiness if timed-in in the morning and afternoon
        if pm_in[0][0] != None and am_in[0][0] != None:
            # Compute for tardy
            a = c.execute("""SELECT am_in from tb_transaction where rowid=?""",(rowid,)).fetchall()
            #b = c.execute("""SELECT am_out from tb_transaction WHERE rowid=?""",(rowid,)).fetchall()
            
            a_ = datetime.strptime(a[0][0],"%I:%M:%S %p").time()
            #b_ = datetime.strptime(b[0][0],"%I:%M:%S %p").time()

            d = c.execute("""SELECT pm_in from tb_transaction WHERE rowid=?""",(rowid,)).fetchall()
            #e = c.execute("""SELECT pm_out from tb_transaction WHERE rowid=?""",(rowid,)).fetchall()
            d_ = datetime.strptime(d[0][0],"%I:%M:%S %p").time()
            #e_ = datetime.strptime(e[0][0],"%I:%M:%S %p").time()

            
            job_desc = c.execute("""SELECT job_desc FROM tb_transaction WHERE rowid = ?""",(rowid,)).fetchall()
            # If an employee is teaching....
            if job_desc[0][0] == 'Teaching':
                tardy_am = datetime.combine(date.today(), a_) - datetime.combine(date.today(), official_time_am_in)
                tardy_pm = datetime.combine(date.today(), d_) - datetime.combine(date.today(), official_time_pm_in)
            # If an employee is non-teaching.... 
            else:
                tardy_am = datetime.combine(date.today(), a_) - datetime.combine(date.today(), official_time_am_in_)
                tardy_pm = datetime.combine(date.today(), d_) - datetime.combine(date.today(), official_time_pm_in_)

            # If not late initialize as 0
            if tardy_am < timedelta(0):
                tardy_am = timedelta(0)
            if tardy_pm < timedelta(0):
                tardy_pm = timedelta(0)

            # Combine tardy in am and pm
            total_tardy_ = str(tardy_am + tardy_pm).zfill(8)
            c.execute("""UPDATE tb_transaction SET tardy = ? WHERE rowid = ?""",(str(total_tardy_),rowid))
            conn.commit()
        rowid = rowid + 1
        
        
def undertime():
    conn = sqlite3.connect('db_employees.db')
    c = conn.cursor()
    
    # Row Count
    rowid = 1
    
    # Iterate through the list of employee trasacations
    for row in c.execute("""SELECT * FROM tb_transaction""").fetchall():
        d = c.execute("""SELECT pm_out from tb_transaction WHERE rowid=?""",(rowid,)).fetchall()
        a = c.execute("""SELECT am_out from tb_transaction where rowid=?""",(rowid,)).fetchall()
        
        # Check if timed out both am and pm if not, computation for undertime is ignored
        if a[0][0] != None and d[0][0] != None:
            # Compute for undertime
            am_out = c.execute("""SELECT am_out from tb_transaction where rowid=?""",(rowid,)).fetchall()
            pm_out = c.execute("""SELECT pm_out from tb_transaction WHERE rowid=?""",(rowid,)).fetchall()
            am_out_ = datetime.strptime(am_out[0][0],"%I:%M:%S %p").time()
            pm_out_ = datetime.strptime(pm_out[0][0],"%I:%M:%S %p").time()

            job_desc = c.execute("""SELECT job_desc FROM tb_transaction WHERE rowid = ?""",(rowid,)).fetchall()

            # If an employee is teaching....
            if job_desc[0][0] == 'Teaching':
                undertime_am = datetime.combine(date.today(), official_time_am_out) - datetime.combine(date.today(), am_out_)
                undertime_pm = datetime.combine(date.today(), official_time_pm_out) - datetime.combine(date.today(), pm_out_)
            # If an employee is non-teaching
            else:
                undertime_am = datetime.combine(date.today(), official_time_am_out_) - datetime.combine(date.today(), am_out_)
                undertime_pm = datetime.combine(date.today(), official_time_pm_out_) - datetime.combine(date.today(), pm_out_)

            # If employee is not undertimed initialize as 0 undertime
            if undertime_am < timedelta(0):
                undertime_am = timedelta(0)
            if undertime_pm < timedelta(0):
                undertime_pm = timedelta(0)
            total_undertime = str(undertime_am + undertime_pm).zfill(8)
            # Set the undertime of an employee
            c.execute("""UPDATE tb_transaction SET undertime = ? WHERE rowid = ?""",(str(total_undertime),rowid))
            conn.commit()
        # Row Count + 1  
        rowid = rowid + 1

