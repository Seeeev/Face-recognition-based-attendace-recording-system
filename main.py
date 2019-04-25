import cv2
from PyQt5.QtWidgets import QPushButton,QApplication, QWidget, QMessageBox
from PyQt5 import QtWidgets, uic , QtCore
from PyQt5.QtCore import QTimer, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5 import QtGui
import pickle
import datetime as dt
from datetime import datetime, timedelta
import sys
import os,subprocess
import sqlite3
import PySimpleGUI as sg
from PySimpleGUI import SetOptions
from easygui import boolbox,buttonbox
import ctypes
import DTR2


class DisplayCam(QtWidgets.QMainWindow,QPushButton):
    def __init__(self):
        super(DisplayCam,self).__init__()
        uic.loadUi('ui files/display.ui',self)
        self.setWindowIcon(QtGui.QIcon("parsu_logo.png"))
        self.image=None
        self.startButton.clicked.connect(self.start_webcam)
        # For popup message background
        self._popframe = None
        self._popflag = False

        #self.stopButton.clicked.connect(self.stop_webcam)
        #self.face_Enabled=True
        self.name = []
        self.loop = 0
        # Initialiing the time
        self.seconds  = 45
        self.minutes = 46
        self.hours = 13

        self.clock() # Start the clock
        # Add actions to the menubar
        self.actionRegistration.triggered.connect(self.registration)
        self.actionDaily_Time_Record.triggered.connect(self.dtr)

        # Load up the face detector algorithm
        self.faceCascade=cv2.CascadeClassifier('cascades/data/haarcascade_frontalface_default.xml')

        # Load up the recognizer algorithm
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()

        #trained data from the traning module
        self.recognizer.read("trainner.yml")
        #loads the labels from the training modlue
        self.labels = {"person_name": 1}
        with open("labels.pickle", "rb") as f:
            self.og_labels = pickle.load(f)
            self.labels = {v: k for k, v in self.og_labels.items()}
            
    def start_webcam(self):
        self.capture = cv2.VideoCapture(0) # '1' for external webcam '0' for built-in webcam
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH,640)
        self.timer=QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(5)
        self.clock()

    def update_frame(self):
        ret,self.image=self.capture.read()
        self.image=cv2.flip(self.image,1)
        detected_image = self.recognize_face(self.image)
        self.displayImage(detected_image,1)
        

    def recognize_face(self,img):
        gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        faces = self.faceCascade.detectMultiScale(gray, 1.2, 5)
        for(x,y,w,h) in faces:
            
            # Region of Interest/Determine the location of the face
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = self.image[y:y + h, x:x + w]
            # recognize
            id_, conf = self.recognizer.predict(roi_gray)
            if conf >= 45 and conf <= 150:
                print(id_)
                print(self.labels[id_])
                if self.loop < 5:
                    self.name.append(self.labels[id_])
                    self.loop=self.loop+1
                if self.loop == 5:
                    name = self.name
                    self.openWindow(name)
                    self.name=[]
                    self.loop = 0
                    
                font = cv2.FONT_HERSHEY_SIMPLEX
                name = self.labels[id_]
                color = (0,0,255)# White
                stroke = 2
                cv2.putText(img,name,(x,y),font,1,color,stroke,cv2.LINE_AA)
            # Create a rectangle on the face
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,255,255),1)
        return img
        

    def stop_webcam(self):
##        self.capture.release()
##        self.start_webcam().stop()
        self.timer.stop()
        self.clock()
        
        

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
            self.imgLabel.setPixmap(QPixmap.fromImage(outImage))
            self.imgLabel.setScaledContents(True)


    def openWindow(self,name):
        # List of recognized ids
        ids = list(set(name))
        # Open the database connection 
        conn = sqlite3.connect('db_employees.db')
        c = conn.cursor()

        c.execute("""SELECT f_name FROM tb_emp_info WHERE empID = ?""",(ids[0],))
        for x in c:
            name = x[0]
        
        # If morning
        date_t = datetime.strptime(self.update_label(),'%I:%M:%S %p').time() 
        if date_t < dt.time(12):
            SetOptions(background_color='#77A1D3',text_element_background_color='#77A1D3',font='Raleway')
            layout = [[sg.Text("Hi {}, what do you want to do?".format(name))],
                      [sg.Text(" "*10),sg.Button("Time In"), sg.Button("Time Out")]]
            window  = sg.Window('Transaction', auto_size_text=True, default_element_size=(40, 1)).Layout(layout)
            event,choice = window.Read()
        
            if event == "Time In":
                c.execute("""SELECT job_desc FROM tb_emp_info WHERE empID=?""",(ids[0],))
                job_desc = c.fetchall()
                
                # Validate if an employee is within the time period for timing in
                if any(item for item in job_desc if 'Teaching' in item) and date_t < dt.time(8) or any(item for item in job_desc if 'Non-Teaching' in item) and date_t < dt.time(8,30) :
                # Time in
                    # If already timed-in
                    c.execute("""SELECT empID from tb_transaction""")
                    table = c.fetchall()
                    c.execute("""SELECT date from tb_transaction""")
                    date_ = c.fetchall()
                    ids2 = ids[0],
                    ids3 = int(ids2[0]),
                    
                    curr_date = datetime.strftime(datetime.now(), "%Y-%m-%d"),
                    
                    # If timed in today 
                    if ids2 in table and curr_date in date_:
                        ctypes.windll.user32.MessageBoxW(0, "    Already timed in for today", "Ooops!", 1) 
                        c.execute("""SELECT f_name, m_name, l_name FROM tb_emp_info WHERE empID = ?""",(ids[0],))
                        info = c.fetchall()
                        self.idLabel.setText(str(ids[0]))
                        self.nameLabel.setText(str(info[0][0]+" "+info[0][1]+" "+info[0][2]))
                        self.loadImage(ids[0])
                        window.Close()
                        

                    # If not timed in today
                    else:
                        date = str(dt.datetime.now().date())
                        print(date)
                        time = str(self.update_label())
                        c.execute("""INSERT INTO tb_transaction (empID, date, am_in) VALUES (?,?,?)""",(str(ids[0]),date,time))
                        conn.commit()
                        c.execute("""SELECT f_name, m_name, l_name FROM tb_emp_info WHERE empID = ?""",(ids[0],))
                        info = c.fetchall()
                        self.idLabel.setText(str(ids[0]))
                        self.nameLabel.setText(str(info[0][0]+" "+info[0][1]+" "+info[0][2]))
                        self.loadImage(ids[0])

                        # Verify if employee is late or not
                        self.lateChecker(ids[0],date_t,job_desc)
                        self.CheckForConscecutiveLates(ids[0])
                        window.Close()
                else:
                    ctypes.windll.user32.MessageBoxW(0, "    Sorry you're late for today. Transaction disregarded.", "Ooops!", 1)
                    window.Close()
            elif event == "Time Out":
                #Time out
                time = str(self.update_label())
                curr_date = datetime.strftime(datetime.now(), "%Y-%m-%d")
                c.execute("""UPDATE tb_transaction SET am_out = ? WHERE empID =? AND date = ?""",(time,str(ids[0]),curr_date))
                conn.commit()
                c.execute("""SELECT f_name, m_name, l_name FROM tb_emp_info WHERE empID = ?""",(ids[0],))
                info = c.fetchall()
                self.idLabel.setText(str(ids[0]))
                self.nameLabel.setText(str(info[0][0]+" "+info[0][1]+" "+info[0][2]))
                self.loadImage(ids[0])
                window.Close()
                
        # If afternoon
        else:
            # Time In
            SetOptions(background_color='#77A1D3',text_element_background_color='#77A1D3',font='Raleway')
            layout = [[sg.Text("Hi {}, what do you want to do?".format(name))],
                      [sg.Text(" "*10),sg.Button("Time In"), sg.Button("Time Out")]]
            window  = sg.Window('Transaction', auto_size_text=True, default_element_size=(40, 1)).Layout(layout)
            event,choice = window.Read()
            
            if event == "Time In":
                c.execute("""SELECT job_desc FROM tb_emp_info WHERE empID=?""",(ids[0],))
                job_desc = c.fetchall()
                
                # Validate if an employee is within the time period for timing in
                if any(item for item in job_desc if 'Teaching' in item) and date_t > dt.time(12,30) or any(item for item in job_desc if 'Non-Teaching' in item) and date_t > dt.time(12,30) :
                    c.execute("""SELECT empID from tb_transaction""")
                    table = c.fetchall()
                    c.execute("""SELECT date from tb_transaction""")
                    date_ = c.fetchall()
                    ids2 = ids[0],
                    ids3 = int(ids2[0]),
                    
                    curr_date = datetime.strftime(datetime.now(), "%Y-%m-%d"),
                    date = datetime.strftime(datetime.now(), "%Y-%m-%d")
                    id_ = str(ids[0])
            
                    # Time in -  if timed-in in the morning
                    if any(item for item in table if ids[0] in item)  and curr_date in date_ :                  #id_
                        afternoon_in = c.execute("""SELECT pm_in FROM tb_transaction WHERE empID=? and date=?""",(ids[0],date)).fetchall()
                        if afternoon_in[0][0] is None:
                            curr_date = datetime.strftime(datetime.now(), "%Y-%m-%d")
                            time = str(self.update_label())
                            c.execute("""UPDATE tb_transaction SET pm_in = ? WHERE empID = ? and date = ?""",(time,ids[0],curr_date))
                            conn.commit()

                            # Verify if employee is late or not
                            self.lateChecker(ids[0],date_t,job_desc)
                            self.CheckForConscecutiveLates(ids[0])

                            c.execute("""SELECT f_name, m_name, l_name FROM tb_emp_info WHERE empID = ?""",(ids[0],))
                            info = c.fetchall()
                            self.idLabel.setText(str(ids[0]))
                            self.nameLabel.setText(str(info[0][0]+" "+info[0][1]+" "+info[0][2]))
                            self.loadImage(ids[0])
                            window.Close()
                        else:
                            c.execute("""SELECT f_name, m_name, l_name FROM tb_emp_info WHERE empID = ?""",(ids[0],))
                            info = c.fetchall()
                            self.idLabel.setText(str(ids[0]))
                            self.nameLabel.setText(str(info[0][0]+" "+info[0][1]+" "+info[0][2]))
                            ctypes.windll.user32.MessageBoxW(0, "    Already timed in for today", "Ooops!", 1)
                            self.loadImage(ids[0])
                            window.Close()
        
                    else:
                    # Time in -  if not timed-in in the morning
                        date = str(dt.datetime.now().date())
                        time = str(self.update_label())
                        c.execute("""INSERT INTO tb_transaction (empID, date, pm_in) VALUES (?,?,?)""",(ids[0],date,time))
                        conn.commit()
                        
                        # Verify if employee is late or not
                        self.lateChecker(ids[0],date_t,job_desc)
                        self.CheckForConscecutiveLates(ids[0])
                        
                        c.execute("""SELECT f_name, m_name, l_name FROM tb_emp_info WHERE empID = ?""",(ids[0],))
                        info = c.fetchall()
                        self.idLabel.setText(str(ids[0]))
                        self.nameLabel.setText(str(info[0][0]+" "+info[0][1]+" "+info[0][2]))
                        self.loadImage(ids[0])
                        window.Close()
                else:
                    ctypes.windll.user32.MessageBoxW(0, "    Sorry you're too early to time in. Transaction disregarded.", "Ooops!", 0)
                    window.Close()
            elif event == "Time Out":
                #Time out
                time = str(self.update_label())
                c.execute("""UPDATE tb_transaction SET pm_out = ? WHERE empID = ?""",((time),(ids[0])))
                conn.commit()
                c.execute("""SELECT f_name, m_name, l_name FROM tb_emp_info WHERE empID = ?""",(ids[0],))
                info = c.fetchall()
                self.idLabel.setText(str(ids[0]))
                self.nameLabel.setText(str(info[0][0]+" "+info[0][1]+" "+info[0][2]))
                self.loadImage(ids[0])
                window.Close()
        # Viewing data from the Transaction Table
        date = str(dt.datetime.now().date())
        result = c.execute("""SELECT am_in, am_out, pm_in, pm_out FROM tb_transaction WHERE empID=? and date=?""",(ids[0],date))
        self.tableWidget.setRowCount(0)
        conn.commit()
        
        for row_number, row_data in enumerate(result):
            self.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))

        
            

    def registration(self):
        #app=QApplication(sys.argv)
        #self.window=Registration2.Ui_Registration2()
        #self.window.show()
        #sys.exit(app.exec_())
        subprocess.Popen(["python", "Registration2.py"])
        os._exit
        

    def dtr(self):
        #app=QApplication(sys.argv)
        self.window=DTR2.Ui_DTR2()
        self.window.show()
        #sys.exit(app.exec_())
##        subprocess.Popen(["python", "DTR2.py"])
##        os._exit
        

    def clock(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_label)
        self.timer.start(1000)

    def update_label(self):
        # If seconds is 60 add 1 minute and reset seconds to 0
        if self.seconds  == 60:
            self.seconds = 0
            self.minutes = self.minutes + 1
        # If minutes is 60 add 1 hour and reset minutes to 0
        if self.minutes == 60:
            self.hours = self.hours + 1
            self.minutes = 0
        if self.hours == 24 and self.minutes == 0 and self.seconds == 0:
            self.hours = 0
        # Create the time object
        time_ = dt.time(self.hours,self.minutes,self.seconds)
        d = datetime.strptime(str(time_),"%H:%M:%S")
        self.seconds =  self.seconds + 1
        self.cur_time = d.strftime("%I:%M:%S %p")
        cur_date = datetime.strftime(datetime.now(), "%A, %d %B %Y")
        self.pixLabel_2.setText(cur_date)
        self.pixLabel_7.setText(self.cur_time)

        return self.cur_time

    @pyqtSlot()
    def loadImage(self,empID):
        self.EmpImage = cv2.imread('Employee IDs/'+empID+'.PNG')
        self.displayEmp()
    def displayEmp(self):
        qformat=QImage.Format_Indexed8

        if len(self.EmpImage.shape) == 3: # rows[0], cols[1], channel[2]
            if(self.EmpImage.shape[2]) == 4:
                qformat=QImage.Format_RBG8888
            else:
                qformat = QImage.Format_RGB888
        imgID = QImage(self.EmpImage,self.EmpImage.shape[1],self.EmpImage.shape[0],self.EmpImage.strides[0],qformat)

        #BGR to RGB
        imgID = imgID.rgbSwapped()
        self.label.setPixmap(QPixmap.fromImage(imgID))
        self.label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
    
    def lateChecker(self,ID,time_today,job_desc):
        conn = sqlite3.connect('db_employees.db')
        c = conn.cursor()
        year = datetime.strftime(datetime.now(), "%Y")
        month = datetime.strftime(datetime.now(), "%B")
        day = datetime.strftime(datetime.now(), "%d, %A")
        time = str(self.update_label())
        # Else mark 'On Time'. 
        if time_today < dt.time(7,45) and any(item for item in job_desc if 'Teaching' in item) or time_today < dt.time(13,15) and any(item for item in job_desc if 'Non-Teaching' in item):
            c.execute("""INSERT INTO tb_lates (empID, month, day, year,time, note) VALUES (?,?,?,?,?,?)""",(ID,month,day,year,time,'On Time'))
            conn.commit()
        # If late mark 'Late'.
        else:
            c.execute("""INSERT INTO tb_lates (empID, month, day, year, time, note) VALUES (?,?,?,?,?,?)""",(ID,month,day,year,time,'Late'))
            conn.commit()

    def CheckForConscecutiveLates(self,ID):
        conn = sqlite3.connect('db_employees.db')
        c = conn.cursor()
        month = datetime.strftime(datetime.now(), "%B")
        c.execute("""SELECT note FROM tb_lates WHERE empID=? and month=?""",(ID,month))
        lates = c.fetchall()
        lateMeter = 0
        for row_data in lates:
            if row_data[0] == 'Late':
                lateMeter = lateMeter + 1
                if lateMeter == 9:
                    ctypes.windll.user32.MessageBoxW(0, "Warning you have 9 consective lates! One more late and you will be penalized!", "Warning!", 0)

                elif lateMeter == 10:
                    ctypes.windll.user32.MessageBoxW(0, "Warning you have already accumulated 10 consecutive lates! ", "Warning!", 0)
            
if __name__=='__main__':
    import sys
    app=QtWidgets.QApplication(sys.argv)
    window=DisplayCam()
    window.setWindowTitle('Partido State University Biometric System')
    window.show()
    sys.exit(app.exec())
