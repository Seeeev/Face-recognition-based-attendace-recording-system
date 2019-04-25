from PyQt5.QtWidgets import QPushButton,QApplication, QWidget, QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
import cv2
import DTR2
import os, subprocess
import ctypes
import sqlite3
import PySimpleGUI as sg
from PySimpleGUI import SetOptions
import TrainFaces
from easygui import enterbox
class Ui_Registration2(QtWidgets.QMainWindow,QPushButton):
    def __init__(self):
        super(Ui_Registration2,self).__init__()
        uic.loadUi('ui files/Registration.ui',self)
        self.id_saved = None
        # Run the database
        self.run_database()
        # View data from database
        self.view_data()
        self.x = []
        # Start Webcam -----------------------------------------------
        self.startButton.clicked.connect(self.start_cam)
        # ------------------------------------------------------------

        # Add actions to the menubar
        self.actionHome.triggered.connect(self.home)
        self.actionDaily_Time_Record.triggered.connect(self.dtr)

        # Get the data from the form
        self.pushButton_5.clicked.connect(self.get_data)

        # Train images
        self.trainButton.clicked.connect(self.train_data)
        
        self.clicked  =  True
        # Face Registration (used for recognizing an employee)
        self.faceRegister.clicked.connect(self.face_register)
        # Below are disabled fields until payrol system is implemented
        self.salary = self.lineEdit_12.setEnabled(False)
        self.ratio = self.lineEdit_13.setEnabled(False)
        self.acc_no = self.lineEdit_14.setEnabled(False)
        self.pagibig_no = self.lineEdit_15.setEnabled(False)
        self.phil_health_no = self.lineEdit_16.setEnabled(False)
        self.gsis_no = self.lineEdit_17.setEnabled(False)
        
        self.salary = self.lineEdit_12.setText("Disabled for now")
        self.ratio = self.lineEdit_13.setText("Disabled for now")
        self.acc_no = self.lineEdit_14.setText("Disabled for now")
        self.pagibig_no = self.lineEdit_15.setText("Disabled for now")
        self.phil_health_no = self.lineEdit_16.setText("Disabled for now")
        self.gsis_no = self.lineEdit_17.setText("Disabled for now")
        # Take a picture of the employee
        self.save_idButton.clicked.connect(self.capture_image)

        # Search Employee
        self.pushButton_10.clicked.connect(self.searchEmployee)
        # Delete Employee
        self.pushButton_7.clicked.connect(self.deleteEmployee)
        # Edit Employee
        self.pushButton_8.clicked.connect(self.editEmployee)
        # View data from database
        self.view_data()
        # Lock an employee
        self.inactiveButton.clicked.connect(self.lockEmployee)
        # List of locked employee
        self.inactiveEmployees.clicked.connect(self.inactive_emp_list)

        # Close Window
        self.closeButton.clicked.connect(self.closeWindow)

    def start_cam(self):
        self.capture=cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT,180)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH,316)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(5)
        
    def update_frame(self):
        ret,self.image=self.capture.read()
        self.image=cv2.flip(self.image,1)   
        # Display Image Function
        self.displayImage(self.image,1)
        return self.image
        
        
        
    def displayImage(self,img,window=1):
        qformat=QImage.Format_Indexed8
        if len(img.shape)==3: #[0]=rows, [1]=cols [2]=channels
            if img.shape[2]==4:
                qformat=QImage.Format_RGBA8888
                
            else:
                qformat=QImage.Format_RGB888
                
        outImage=QImage(img,img.shape[1],img.shape[0],img.strides[0],qformat)
        #BRG to RGB
        outImage=outImage.rgbSwapped()
        if window==1:
            self.frame_2.setPixmap(QPixmap.fromImage(outImage))
            self.frame_2.setScaledContents(True)
            

    def capture_image(self):
        conn = sqlite3.connect('db_employees.db')
        c = conn.cursor()
        c.execute("""SELECT empID FROM tb_emp_info""")
        id_list = c.fetchall()
        
        while True:
            current_id = enterbox(msg='Please enter your ID.', title=' ', default='', strip=True)
            if any(item for item in id_list if current_id in item):
                cv2.imwrite("Employee IDs/"+current_id+".png",self.update_frame())
                ctypes.windll.user32.MessageBoxW(0, "      ID Saved Successfuly", "Success", 0)
                break
            elif current_id ==  None:
                break
            
            else:
                ctypes.windll.user32.MessageBoxW(0, "        Invalid ID!", "Error", 0)
    
    def dtr(self):
##        subprocess.Popen(["python", "DTR2.py"])
##        os._exit
        self.ui = DTR2.Ui_DTR2()
        self.ui.show()

    def home(self):
        subprocess.Popen(["python", "main.py"])
        os._exit
        #self.window=main.DisplayCam()
        #self.window.show()
        
    def get_data(self):
        conn = sqlite3.connect('db_employees.db')
        c = conn.cursor()
        c.execute("""SELECT empID from tb_emp_info""")
        id_list = c.fetchall()
        current_id = self.lineEdit.text()
        if self.lineEdit.text().isdigit():
            if any(item for item in id_list if current_id in item):
                ctypes.windll.user32.MessageBoxW(0, "    ID already exists", "Error", 0)
            else:
                self.empID = self.lineEdit.text()
                if len(self.lineEdit_2.text()) == 0:
                    ctypes.windll.user32.MessageBoxW(0, "    Empty field in Last Name", "Error", 0)
                elif len(self.lineEdit_3.text()) == 0:
                    ctypes.windll.user32.MessageBoxW(0, "    Empty field in First Name", "Error", 0)
                elif len(self.lineEdit_4.text()) == 0:
                    ctypes.windll.user32.MessageBoxW(0, "    Empty field in Middle Name", "Error", 0)
                elif len(self.lineEdit_5.text()) == 0:
                    ctypes.windll.user32.MessageBoxW(0, "    Empty field in Address ", "Error", 0)
        else:
            ctypes.windll.user32.MessageBoxW(0, "    Enter a valid Employee ID", "Error", 0)
 
         
        if (self.lineEdit.text().isdigit() and len(self.lineEdit_2.text())>0 and len(self.lineEdit_3.text())>0 and len(self.lineEdit_4.text()) > 0 and len(self.lineEdit_5.text())>0):
            # Get the inputs from the user and store it in variables
            self.l_name = self.lineEdit_2.text()
            self.f_name= self.lineEdit_3.text()
            self.m_name = self.lineEdit_4.text()
            self.gender = self.comboBox.currentText()
            self.civil_status = self.comboBox_2.currentText()
            self.job_desc = self.comboBox_3.currentText()
            self.position = self.comboBox_4.currentText()
            self.campus = self.comboBox_5.currentText()
            self.dept = self.comboBox_6.currentText()
            self.address = self.lineEdit_5.text()
            self.dependent_type = self.comboBox_7.currentText()
            self.soa = self.comboBox_8.currentText()
            self.emp_status = self.comboBox_9.currentText()
            self.date_hired = self.dateEdit.date().toPyDate() 
            self.date_of_birth = self.dateEdit_2.date().toPyDate()

            # Pull the data from the registration form and it in the database
            c.execute("""INSERT INTO tb_emp_info VALUES (:empID, :l_name, :f_name, :m_name, :gender,
                      :civil_status, :job_desc, :position, :campus, :dept, :address, :dependent_type,
                      :soa,:emp_status, :date_hired, :date_of_birth)""",
                      {'empID':self.empID, 'l_name':str(self.l_name), 'f_name':str(self.f_name),
                       'm_name':str(self.m_name), 'gender':str(self.gender),
                       'civil_status':str(self.civil_status), 'job_desc':str(self.job_desc),
                       'position':str(self.position), 'campus':str(self.campus), 'dept':str(self.dept),
                       'address':str(self.address),'dependent_type':str(self.dependent_type), 'soa':str(self.soa),
                       'emp_status':str(self.emp_status),'date_hired':str(self.date_hired),
                       'date_of_birth':str(self.date_of_birth)})
            conn.commit()
            self.view_data()
            

            # Clear form
            c.close()
            conn.close()
            self.lineEdit.setText(None)
            self.lineEdit_2.setText(None)
            self.lineEdit_3.setText(None)
            self.lineEdit_4.setText(None)
            self.lineEdit_5.setText(None)

            # Confirmation Message
            ctypes.windll.user32.MessageBoxW(0, "    You are now registered. Please move to the Face Registration", "Success", 0)            

    def run_database(self):
        # Create the database and insert the data from the form
        conn = sqlite3.connect('db_employees.db')
        c = conn.cursor()
        # Employee's Information Table
        c.execute("""CREATE TABLE IF NOT EXISTS tb_emp_info(empID TEXT,
                                                          l_name TEXT,
                                                          f_name TEXT,
                                                          m_name TEXT,
                                                          gender TEXT,
                                                          civil_status TEXT,
                                                          job_desc TEXT,
                                                          position TEXT,
                                                          campus TEXT,
                                                          dept TEXT,
                                                          address TEXT,
                                                          dependent_type TEXT,
                                                          soa TEXT,
                                                          emp_status TEXT,
                                                          date_hired TEXT,
                                                          date_of_birth TEXT)""")
      
        conn.commit()
        # Transaction Table
        c.execute("""CREATE TABLE IF NOT EXISTS tb_transaction(empID TEXT,
                                                            date TEXT,
                                                            am_in TEXT,
                                                            am_out TEXT,
                                                            pm_in TEXT,
                                                            pm_out TEXT,
                                                            Tardy TEXT,
                                                            Undertime TEXT)""")
        conn.commit()
        # Database for number of lates
        c.execute("""CREATE TABLE IF NOT EXISTS tb_lates(empID TEXT,
                                                        month TEXT,
                                                        day TEXT,
                                                        year TEXT,
                                                        time TEXT,
                                                        note TEXT)""")
        # Table for inactive employees
        c.execute("""CREATE TABLE IF NOT EXISTS tb_emp_inactive(empID TEXT,
                                                          l_name TEXT,
                                                          f_name TEXT,
                                                          m_name TEXT,
                                                          gender TEXT,
                                                          civil_status TEXT,
                                                          job_desc TEXT,
                                                          position TEXT,
                                                          campus TEXT,
                                                          dept TEXT,
                                                          address TEXT,
                                                          dependent_type TEXT,
                                                          soa TEXT,
                                                          emp_status TEXT,
                                                          date_hired TEXT,
                                                          date_of_birth TEXT)""")
        
            
    def view_data(self):
        conn = sqlite3.connect('db_employees.db')
        query = "SELECT empID, l_name, f_name, m_name, gender, civil_status, job_desc, position,  campus, dept, address  FROM tb_emp_info"
        result = conn.execute(query)
        self.tableWidget.setRowCount(0)
        
        for row_number, row_data in enumerate(result):
            self.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))


    def train_data(self):
        TrainFaces.train()
##        subprocess.Popen(["python", "TrainFaces.py"])
##        os._exit
    def face_register(self):
        #FaceRegister.registerFace()
        subprocess.Popen(["python", "FaceRegister.py"])
        os._exit
    def searchEmployee(self):
        searchOption = self.comboBox_10.currentText()
        searchInput = self.lineEdit_6.text()
        conn = sqlite3.connect('db_employees.db')
        c = conn.cursor()
        if searchOption == 'Employee ID':
            c.execute("""SELECT empID, l_name, f_name, m_name, gender, civil_status, job_desc, position,  campus, dept, address  FROM tb_emp_info WHERE empID=?""",(searchInput,))
            result = c.fetchall()
            if searchInput != "":
                self.tableWidget.setRowCount(0)
                for row_number, row_data in enumerate(result):
                    self.tableWidget.insertRow(row_number)
                    for column_number, data in enumerate(row_data):
                        self.tableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))
            else:
                self.view_data()
        elif SearchOption == 'First Name':
            c.execute("""SELECT empID, l_name, f_name, m_name, gender, civil_status, job_desc, position,  campus, dept, address  FROM tb_emp_info WHERE f_name=?""",(searchInput,))
            result = c.fetchall()
            if searchInput != "":
                self.tableWidget.setRowCount(0)
                for row_number, row_data in enumerate(result):
                    self.tableWidget.insertRow(row_number)
                    for column_number, data in enumerate(row_data):
                        self.tableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))
            else:
                self.view_data()
            
        elif SearchOption == 'Last Name':
            c.execute("""SELECT empID, l_name, f_name, m_name, gender, civil_status, job_desc, position,  campus, dept, address  FROM tb_emp_info WHERE l_name=?""",(searchInput,))
            result = c.fetchall()
            if searchInput != "":
                self.tableWidget.setRowCount(0)
                for row_number, row_data in enumerate(result):
                    self.tableWidget.insertRow(row_number)
                    for column_number, data in enumerate(row_data):
                        self.tableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))
            else:
                self.view_data()
        elif SearchOption == 'Department':
            c.execute("""SELECT empID, l_name, f_name, m_name, gender, civil_status, job_desc, position,  campus, dept, address  FROM tb_emp_info WHERE dept=?""",(searchInput,))
            result = c.fetchall()
            if searchInput != "":
                self.tableWidget.setRowCount(0)
                for row_number, row_data in enumerate(result):
                    self.tableWidget.insertRow(row_number)
                    for column_number, data in enumerate(row_data):
                        self.tableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))
            else:
                self.view_data()
        elif SearchOption == 'Position':
            c.execute("""SELECT empID, l_name, f_name, m_name, gender, civil_status, job_desc, position,  campus, dept, address  FROM tb_emp_info WHERE position=?""",(searchInput,))
            result = c.fetchall()
            if searchInput != "":
                self.tableWidget.setRowCount(0)
                for row_number, row_data in enumerate(result):
                    self.tableWidget.insertRow(row_number)
                    for column_number, data in enumerate(row_data):
                        self.tableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))
            else:
                self.view_data()

    def deleteEmployee(self):
        #data = self.tableWidget.selectedItems()[0].text()
        try:
            data = self.tableWidget.selectedItems()
            empID = data[0].text()
            count = self.tableWidget.currentRow()
            print(count)
            data_ = self.tableWidget.selectedRanges()
            for i in range(len(data)):
                print(data[i].text())
            choice = ctypes.windll.user32.MessageBoxW(0, "Are you sure you want to delete this employee? All his/her data will be lost.", "Confirmation", 1)
            if choice == 1:
                conn = sqlite3.connect('db_employees.db')
                c = conn.cursor()
                c.execute("""DELETE FROM tb_emp_info WHERE empID=?""",(empID,))
                conn.commit()
                ctypes.windll.user32.MessageBoxW(0, "    Employee successfuly deleted!", "Success!", 0)
                self.view_data()
        except IndexError:
            ctypes.windll.user32.MessageBoxW(0, "    No employee selected!", "Error!", 0)
    def editEmployee(self):
        # Execute if row is selected in the list of employees
        if len(self.tableWidget.selectedItems()) != 0:
            data = self.tableWidget.selectedItems()
            empID = data[0].text()
            
            conn = sqlite3.connect('db_employees.db')
            c = conn.cursor()
            empInfo=c.execute("""SELECT * FROM tb_emp_info WHERE empID=?""",(empID,)).fetchall()
            
            empID = empInfo[0][0]
            l_name = empInfo[0][1]
            f_name = empInfo[0][2]
            m_name = empInfo[0][3]
            gender = empInfo[0][4]

            civil_status = empInfo[0][5]
            job_desc = empInfo[0][6]
            position = empInfo[0][7]
            campus = empInfo[0][8]
            dept = empInfo[0][9]
            address = empInfo[0][10]
            dependent_type = empInfo[0][11]
            soa = empInfo[0][12]
            emp_status = empInfo[0][13]
            date_hired = empInfo[0][14]
            date_of_birth = empInfo[0][15]
            
            # Create a GUI for editing an employee
            while (True):
                SetOptions(background_color='#77A1D3',text_element_background_color='#77A1D3',font='Raleway')
                
                layout = [      
                [sg.Text('Employee ID', size=(15, 1), auto_size_text=False, justification='right'), sg.InputText(empID),
                 sg.Text('Campus', size=(15, 1), auto_size_text=False, justification='right'),
                 sg.InputCombo(['Goa Campus', 'Caramoan Campus','Tinambac Campus','San Jose Campus','Lagonoy Campus','Salogon Campus','Sagnay Campus'], size=(38, 3),default_value=campus)],      
                [sg.Text('Last Name', size=(15, 1), auto_size_text=False, justification='right'), sg.InputText(l_name),
                 sg.Text('Department', size=(15, 1), auto_size_text=False, justification='right'),sg.InputCombo(['College of Arts and Sciences', 'College of Education','College of Engineering and Technology','College of Business Management','None'], size=(38, 3), default_value=dept)],
                [sg.Text('First Name', size=(15, 1), auto_size_text=False, justification='right'), sg.InputText(f_name),
                 sg.Text('Address', size=(15, 1), auto_size_text=False, justification='right'), sg.InputText(address)],
                [sg.Text('Middle Name', size=(15, 1), auto_size_text=False, justification='right'), sg.InputText(m_name),
                 sg.Text('Dependent Type', size=(15, 1), auto_size_text=False, justification='right'),
                 sg.InputCombo(['-------'], size=(38, 3), default_value=dependent_type)],
                [sg.Text('Gender', size=(15, 1), auto_size_text=False, justification='right'),sg.InputCombo(['Male', 'Female'], size=(38, 3), default_value = gender),
                 sg.Text('Status of Appt.', size=(15, 1), auto_size_text=False, justification='right'),sg.InputCombo(['Permanent', 'Job Order','Contract of Service','Casual','Temporary'], size=(38, 3),default_value=soa)],
                [sg.Text('Civil Status', size=(15, 1), auto_size_text=False, justification='right'),sg.InputCombo(['Single', 'Married','Divorced','Widowed','Separated'], size=(38, 3),default_value=civil_status),
                 sg.Text('Employee Status', size=(15, 1), auto_size_text=False, justification='right'),sg.InputCombo(['Active', 'Inactive'], size=(38, 3),default_value=emp_status)],
                [sg.Text('Job Description', size=(15, 1), auto_size_text=False, justification='right'),sg.InputCombo(['Teaching', 'Non-Teaching'], size=(38, 3), default_value=job_desc),
                 sg.Text('Date Hired', size=(15, 1), auto_size_text=False, justification='right'), sg.InputText(date_hired)],
                [sg.Text('Position', size=(15, 1), auto_size_text=False, justification='right'),sg.InputCombo(['Position-Instructor 1, 2, & 3', 'Assistant-Professor 1& 2','Associate-Professor 1-5','Professor 1-6','University Professor','University President'], size=(38, 3),default_value=position),
                 sg.Text('Date of Birth', size=(15, 1), auto_size_text=False, justification='right'), sg.InputText(date_of_birth)],
                [sg.Text(" "*110),sg.Submit(), sg.Cancel()]]
                window  = sg.Window('Edit Employee', auto_size_text=True, default_element_size=(40, 1)).Layout(layout)
                event,values = window.Read()
                if event == 'Submit' and '' in values:
                    window.Close()
                    ctypes.windll.user32.MessageBoxW(0, "Oops! Don't leave a field empty", "Errror!", 0)
                elif event == 'Cancel':
                    window.Close()
                    break
                elif event == 'Submit' and '' not in values:
                    
                    c.execute("""UPDATE tb_emp_info SET empID=?,campus=?,l_name=?,dept=?,f_name=?,address=?,m_name=?,
                        dependent_type=?,gender=?,soa=?,civil_status=?,emp_status=?,job_desc=?,date_hired=?,position=?,
                        date_of_birth=? WHERE empID=?""",(values[0],values[1],values[2],values[3],values[4],values[5],values[6],values[7],values[8],
                                                          values[9],values[10],values[11],values[12],values[13],values[14],values[15],values[0]))
                    conn.commit()
                    #['201510381', 'Goa Campus', 'Abante', 'College of Arts and Sciences', 'Seven', 'San Francisco, Lagonoy, Camarines Sur', 'Faura', '-------', 'Male', 'Permanent', 'Single', 'Active', 'Teaching', '2000-01-01', 'Position-Instructor 1, 2, & 3', '2000-01-01']
                    window.Close()
                    self.view_data()
                    ctypes.windll.user32.MessageBoxW(0, 'Employee succesfully edited!', "Success!", 0)
                    break
                
        else:
            ctypes.windll.user32.MessageBoxW(0, "No employee selected!", "Error!", 0)

    def lockEmployee(self):
        conn =  sqlite3.connect('db_employees.db')
        c = conn.cursor()
        try:
            data = self.tableWidget.selectedItems()
            empID = data[0].text()
            c.execute ("""INSERT INTO tb_emp_inactive SELECT * FROM tb_emp_info WHERE empID =?""",(empID,))
            conn.commit()
            c.execute ("""DELETE from tb_emp_info WHERE empID=?""",(empID,))
            conn.commit()

            c.execute("""SELECT *  FROM tb_emp_info """)
            result = c.fetchall()
            
            self.tableWidget.setRowCount(0)
            for row_number, row_data in enumerate(result):
                self.tableWidget.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.tableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))
            ctypes.windll.user32.MessageBoxW(0, "    Employee successfuly disabled!", "Success", 0)
        except IndexError:
            ctypes.windll.user32.MessageBoxW(0, "    No employee selected!", "Error", 0)

    def inactive_emp_list(self):
        conn = sqlite3.connect('db_employees.db')
        c = conn.cursor()
        
        
        while (True):
            c.execute("""SELECT empID, (l_name||\", \"||f_name||\" \"||m_name) as name FROM tb_emp_inactive""")
            list_of_disabled_emp = c.fetchall()
            names = []
            
            for list_number,list_names in enumerate(list_of_disabled_emp):
                dict_of_names = {'empID':list_names[0], 'names': list_names[1]}
                
                empDetails = dict_of_names['empID'] +" - " + dict_of_names['names']
                names.append(empDetails)
            SetOptions(background_color='#77A1D3',text_element_background_color='#77A1D3',font='Raleway')
            layout = [[sg.Listbox(values=(names), size=(30,8))],
                      [sg.Text(" "*15),sg.Button('Enable'), sg.Cancel()]]
            window  = sg.Window('Disabled Employees', auto_size_text=True, default_element_size=(40, 1)).Layout(layout)
            event,values = window.Read()
           
            if event == 'Enable':
                try:
                    empID = values[0][0].split()[0]
                    c.execute ("""INSERT INTO tb_emp_info SELECT * FROM tb_emp_inactive WHERE empID =?""",(str(empID),))
                    conn.commit()
                    c.execute ("""DELETE FROM tb_emp_inactive WHERE empID=?""",(str(empID),))
                    conn.commit()
                    window.Close()
                    c.execute("""SELECT *  FROM tb_emp_info """)
                    result = c.fetchall()
            
                    self.tableWidget.setRowCount(0)
                    for row_number, row_data in enumerate(result):
                        self.tableWidget.insertRow(row_number)
                        for column_number, data in enumerate(row_data):
                            self.tableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))
                except IndexError:
                    sg.Popup('Select an employee!')
                    window.Close()
            else:
                window.Close()
                break

    def closeWindow(self):
        window.close()
        
        
if __name__=='__main__':
    import sys
    app=QtWidgets.QApplication(sys.argv)
    window=Ui_Registration2()
    window.show()
    sys.exit(app.exec_())
