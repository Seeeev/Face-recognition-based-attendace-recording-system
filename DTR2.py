from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
import cv2
import sqlite3
from datetime import datetime, date
import ctypes
from GenerateForm import generateForm
from computations import tardy, undertime
import os
import subprocess

class Ui_DTR2(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui_DTR2,self).__init__()
        uic.loadUi('ui files/dtr.ui',self) # Load GUI design
        
        tardy() # Compute for tardy
        undertime() # Compute for undertime
       
        # When buttons are clicked do something....
        self.pushButton_2.clicked.connect(self.viewLogs) # view transactions
        self.pushButton.clicked.connect(self.printDTR) # Pint DTR button
        self.pushButton_3.clicked.connect(self.searchEmp) # search an employee

        # Add actions to the menubar
        self.actionHome.triggered.connect(self.home)
        self.actionRegistration.triggered.connect(self.registration)

    def home(self):
        subprocess.Popen(["python", "main.py"])
        os._exit
    def registration(self):
        subprocess.Popen(["python", "Registration2.py"])
        os._exit
    def printDTR(self):
        year = self.comboBox.currentText()
        month = self.comboBox_2.currentText()
        days  = self.comboBox_3.currentText()
        try:
            empID = self.tableWidget.selectedItems()[0].text()
            data = empID,year,month,days
            generateForm(data)
        except IndexError:
            ctypes.windll.user32.MessageBoxW(0, "       Please select an employee ID!" , "Error!", 0)
        

    def searchEmp(self):
        conn = sqlite3.connect('db_employees.db')
        c = conn.cursor()

        
        empID = {}# Get it for comparison
        if self.radioButton_1.isChecked(): # Search by all
            #data = self.tableWidget.selectedItems()[0].text(),self.comboBox.currentText(),self.comboBox_2.currentText(),self.comboBox_3.currentText()
            data = str(self.lineEdit.text())
            c.execute("SELECT empID,(l_name||\", \"||f_name) as name FROM tb_emp_info WHERE empID=? or l_name=? or f_name=? or m_name=? or gender=? or job_desc=? or dept=?",(data,data,data,data,data,data,data))
            result = c.fetchall()
            
            if data != "":
                self.tableWidget.setRowCount(0)
                for row_number, row_data in enumerate(result):
                    self.tableWidget.insertRow(row_number)
                    for column_number, data in enumerate(row_data):
                        self.tableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))
            else:
                self.view_employees()
                
        elif self.radioButton_2.isChecked():
            data = str(self.lineEdit.text())
            c.execute("SELECT empID,(l_name||\", \"||f_name) as name FROM tb_emp_info WHERE empID=?",(data,))
            result = c.fetchall()
            
            if data != "":
                self.tableWidget.setRowCount(0)
                for row_number, row_data in enumerate(result):
                    self.tableWidget.insertRow(row_number)
                    for column_number, data in enumerate(row_data):
                        self.tableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))
            else:
                self.view_employees()
        elif self.radioButton_3.isChecked():
            data = str(self.lineEdit.text())
            c.execute("SELECT empID,(l_name||\", \"||f_name) as name FROM tb_emp_info WHERE dept=?",(data,))
            result = c.fetchall()
            
            if data != "":
                self.tableWidget.setRowCount(0)
                for row_number, row_data in enumerate(result):
                    self.tableWidget.insertRow(row_number)
                    for column_number, data in enumerate(row_data):
                        self.tableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))
            else:
                self.view_employees()
        elif self.radioButton_4.isChecked():
            data = str(self.lineEdit.text())
            c.execute("SELECT empID,(l_name||\", \"||f_name) as name FROM tb_emp_info WHERE l_name=?",(data,))
            result = c.fetchall()
            
            if data != "":
                self.tableWidget.setRowCount(0)
                for row_number, row_data in enumerate(result):
                    self.tableWidget.insertRow(row_number)
                    for column_number, data in enumerate(row_data):
                        self.tableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))
            else:
                self.view_employees()

    
        
        
    def view_employees(self):
        conn = sqlite3.connect('db_employees.db')
        c = conn.cursor()
        query = "SELECT empID, (l_name||\", \"||f_name) as name  FROM tb_emp_info"
        result = c.execute(query)
        # update here
##        if self.tableWidget.selectedItems()[0].text() != "":
##            data = self.tableWidget.selectedItems()[0].text(),self.comboBox.currentText(),self.comboBox_2.currentText(),self.comboBox_3.currentText()
        self.tableWidget.setRowCount(0)
    
        for row_number, row_data in enumerate(result):
            self.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))
        
    def viewLogs(self):
        try:
            # Get the employee id of the selected row of employee
            y = self.tableWidget.selectedItems()[0].text()
            print(type(y) , " id")
            empID = self.tableWidget.selectedItems()[0].text(),self.comboBox.currentText(),self.comboBox_2.currentText(),self.comboBox_3.currentText()
            date =  self.comboBox.currentText()+'-'+self.comboBox_2.currentText()+'-'+self.comboBox_3.currentText()
            date_ = datetime.strptime(date,'%Y-%B-%d').strftime('%m/%d/%y')
            year=datetime.strptime(date,'%Y-%B-%d').strftime('%Y')
            month=datetime.strptime(date,'%Y-%B-%d').strftime('%m')
            days = datetime.strptime(date,'%Y-%B-%d').strftime('%d')
            
            conn = sqlite3.connect('db_employees.db')
            c = conn.cursor()
            
            result = []
            for i in range(int(days)):
                c.execute("""SELECT date, am_in, am_out, pm_in, pm_out, tardy, undertime FROM tb_transaction WHERE empID=? and date=?""",(y,year+'-'+month+'-'+str(i+1).zfill(2)))
                data = c.fetchall()
                if data == []: 
                    result.append([])
                else:
                    result.extend(data)
                    
            self.tableDTR.setRowCount(0)
            
            for row_number, row_data in enumerate(result):
                self.tableDTR.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.tableDTR.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))
        except IndexError:
            ctypes.windll.user32.MessageBoxW(0, "       Please select an employee!" , "Error!", 0)
                

if __name__=='__main__':
    import sys
    app=QtWidgets.QApplication(sys.argv)
    window=Ui_DTR2()
    window.show()
    sys.exit(app.exec_())
