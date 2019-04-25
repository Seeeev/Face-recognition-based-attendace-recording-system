from reportlab.platypus import Image,Spacer, BaseDocTemplate, Frame, Paragraph, PageBreak, PageTemplate, Table, TableStyle, FrameBreak
from reportlab.lib.styles import getSampleStyleSheet, StyleSheet1, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape
from reportlab.lib.pagesizes import letter, inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import subprocess
from subprocess import Popen
from calendar import monthrange as mr
import numpy as np
from datetime import datetime,date as ddate
import sqlite3
from time import strptime



def generateForm(data): #data = empID,year,month,day
    employee_id = data[0]
    year = int(data[1])
    month = int(strptime(data[2],'%B').tm_mon)
    days = int(data[3])
    month_ = datetime(year,month,days)
    month_ = month_.strftime("%B %Y")

    conn = sqlite3.connect('db_employees.db')
    c = conn.cursor()
    
    c.execute("""SELECT l_name, f_name, m_name FROM tb_emp_info WHERE empID=?""",(employee_id,))
    full_name = c.fetchall()
    l_name = full_name[0][0]
    f_name = full_name[0][1]
    m_name = full_name[0][2]
    c.execute("""SELECT job_desc FROM tb_emp_info WHERE empID=?""",(employee_id,))
    job_desc = c.fetchall()
    job_desc = job_desc[0][0] 
    
    # FONTS
    pdfmetrics.registerFont(TTFont('Calibri', 'Calibri.ttf'))
    pdfmetrics.registerFont(TTFont('Calibrib', 'Calibrib.ttf'))

    pdfmetrics.registerFont(TTFont('Cambria Math', 'cambria.ttc'))
    pdfmetrics.registerFont(TTFont('Baskerville Old Face', 'BASKVILL.TTF'))

    # STYLES
    stylesheet = StyleSheet1()
    stylesheet.add(ParagraphStyle(name='paragraph1',
                                  fontName='Calibri',
                                  fontSize=13,
                                  leading=12,)
                                  #spaceAfter=12,
                   )
    stylesheet.add(ParagraphStyle(name='paragraph2',
                                  fontName='Cambria Math',
                                  fontSize=16,
                                  leading=15,
                                  leftIndent = 1.3*inch,)
                   )
    stylesheet.add(ParagraphStyle(name='paragraph3',
                                  fontName='Baskerville Old Face',
                                  fontSize=11,
                                  leading = 7,
                                  #spaceAfter=0,
                                  leftIndent = 1.3*inch,)
                   )
    stylesheet.add(ParagraphStyle(name='paragraph4',
                                  fontName='Calibrib',
                                  fontSize=25,
                                  leading = 30,
                                  leftIndent = 1.2*inch,)
                                  #spaceAfter=12,
                   )
    stylesheet.add(ParagraphStyle(name='Credentials',
                                  fontName='Calibrib',
                                  leading=13,
                                  fontSize=12,)
                   )
    # Storage for the flowables
    elements=[]
    
    # Create the document handler
    doc = BaseDocTemplate('generate form.pdf', pagesize=landscape(letter), leftMargin=0.2*inch, topMargin=0.3*inch, bottomMargin=0.3*inch)
    
    # Divide the page into two columns
    frame1 = Frame(doc.leftMargin, doc.bottomMargin, doc.width/2-6, doc.height, id='col1')
    frame2 = Frame(doc.leftMargin+doc.width/2+40, doc.bottomMargin, doc.width/2-6, doc.height, id='col2')

    # Insert the flowables in the 'elements'
    elements.append(Paragraph('Civil Service Form No. 48',stylesheet['paragraph1']))
    logo = Image('parsu_logo.png', width=50,height=50, hAlign = 'LEFT')
    elements.append(logo)
    elements.append(Spacer(0,-50))
    elements.append(Paragraph('PARTIDO STATE UNIVERSITY',stylesheet['paragraph2']))
    elements.append(Paragraph('San Juan Bautista Street, Goa, Camarines Sur',stylesheet['paragraph3']))
    elements.append(Paragraph('DAILY TIME RECORD',stylesheet['paragraph4']))
    elements.append(Paragraph('Employee ID : '+employee_id,stylesheet['Credentials']))
    elements.append(Paragraph('For the month of: '+month_,stylesheet['Credentials']))
    elements.append(Paragraph('Name : '+l_name+', '+f_name+' '+m_name,stylesheet['Credentials']))
    if job_desc == 'Teaching':
        elements.append(Paragraph('Regular Days : '+'07:30-11:30/01:00-05:00',stylesheet['Credentials']))
    elif job_desc == 'Non-Teaching':
        elements.append(Paragraph('Regular Days : '+'08:00-12:00/01:00-05:00',stylesheet['Credentials']))
    elements.append(Paragraph('Saturdays : As required',stylesheet['Credentials']))


    # Storage for the transactions logs (dictionary)
    d = {}

    # Initialize variables or transactions to None
    for i in range (31):
        d['day{0}_in_am'.format(i+1)] = None
        d['day{0}_out_am'.format(i+1)] = None
        d['day{0}_in_pm'.format(i+1)] = None
        d['day{0}_out_pm'.format(i+1)] = None
        d['day{0}_tardy'.format(i+1)] = None
        d['day{0}_undertime'.format(i+1)] = None
        
    # Insert data from transactions
    table_data = np.array([['Day','Morning','','Afternoon','','Tardy','Undertime'],
                  ['','IN','OUT','IN','OUT','hh:mm:ss','hh:mm:ss']])
    # Accepts month and year as input to determine column height
    row_range = mr(year,month)[1]
    rows = np.zeros((row_range,7))
    table_data = np.concatenate((table_data, rows), axis=0)
    # Append data to table
    for i in range(row_range):
        # Number of days in a month
        table_data[i+2][0] = i+1
    # Transform numpy array to list for it can be considered as flowables
    table_data = table_data.tolist()

    # Fill up the DTR form with transactions
    populateForm(employee_id,year,month,days,table_data)
    
    elements.append(Spacer(0,20))
    # Create the table
    table = Table(table_data)
    # Add Styles to the table
    table.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.5,colors.black),
                               ('FONTNAME',(0,0),(-1,-1), 'Times-Roman'),
                               ('FONTSIZE',(0,0),(-1,-1), 8),
                               ('LEFTPADDING',(0,0),(-1,-1),8),
                               ('RIGHTPADDING',(0,0),(-1,-1),8),
                               ('TOPPADDING',(0,0),(-1,-1),0),
                               ('BOTTOMPADDING',(0,0),(-1,-1),0),
                               ('SPAN',(0,0),(0,1)),
                               ('SPAN',(1,0),(2,0)),
                               ('SPAN',(3,0),(4,0)),
                               ('ALIGN',(0,0),(-1,-1),'CENTER'),
                               ]))
    # Append the table in order for it to be viewed in the form
    elements.append(table)
    elements.append(FrameBreak())
    
    # Make copy of column 1
    elements.append(Paragraph('Civil Service Form No. 48',stylesheet['paragraph1']))
    logo = Image('parsu_logo.png', width=50,height=50, hAlign = 'LEFT')
    elements.append(logo)
    elements.append(Spacer(0,-50))
    elements.append(Paragraph('PARTIDO STATE UNIVERSITY',stylesheet['paragraph2']))
    elements.append(Paragraph('San Juan Bautista Street, Goa, Camarines Sur',stylesheet['paragraph3']))
    elements.append(Paragraph('DAILY TIME RECORD',stylesheet['paragraph4']))
    elements.append(Paragraph('Employee ID : '+employee_id,stylesheet['Credentials']))
    elements.append(Paragraph('For the month of : '+month_,stylesheet['Credentials']))
    elements.append(Paragraph('Name : '+l_name+', '+f_name+' '+m_name,stylesheet['Credentials']))
    if job_desc == 'Teaching':
        elements.append(Paragraph('Regular Days : '+'07:30-11:30/01:00-05:00',stylesheet['Credentials']))
    elif job_desc == 'Non-Teaching':
        elements.append(Paragraph('Regular Days : '+'08:00-12:00/01:00-05:00',stylesheet['Credentials']))
    elements.append(Paragraph('Saturdays : As reqired',stylesheet['Credentials']))
    elements.append(Spacer(0,20))
    elements.append(table)

    doc.addPageTemplates([PageTemplate(id='TwoCol',frames=[frame1,frame2]), ])
    
    doc.build(elements)
    
    subprocess.Popen(['generate form.pdf'],shell=True)
def populateForm(employee_id,year, month, days, table_data):
    print(year,month,days)
    #print(employee_id,year, month, days)
    conn = sqlite3.connect('db_employees.db')
    c = conn.cursor()
    c.execute("""SELECT date, am_in, am_out, pm_in, pm_out, Tardy, Undertime FROM tb_transaction WHERE empID=?""",(employee_id,))
    month =str(month).zfill(2)
    date = '%s-%s-'%(year,month)
    # get the number of days in a given month and perform task to each days
    for i in range((len(table_data) - 2)):
        c.execute("""select am_in, am_out, pm_in, pm_out, Tardy, Undertime from tb_transaction where empID=? and date=?""",(employee_id,date+str((i+1)).zfill(2)))
        data = c.fetchall()
        
        # insert the transactions in the cells of the dtr form
        try:
            for x in range (6):
                table_data[2+i][1+x] = data[0][x]
        # if cells is empty, set to None
        except IndexError:
            for x in range (6):
                table_data[2+i][1+x] = None
        # Prints 'Weekend' for saturdays and sundays. If transactions are done during weekends else ignore 
        if ddate(int(year),int(month),i+1).weekday() == 6 or ddate(int(year),int(month),i+1).weekday() == 5:
            if table_data[2+i][5] == None:
                table_data[2+i][5] = 'Weekend'

##data = ['201510381','2019','January','1']
##generateForm(data)





