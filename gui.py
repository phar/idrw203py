import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget,QApplication, QWidget, QPushButton,QGroupBox,QLineEdit,QRadioButton,QHBoxLayout,QVBoxLayout,QCheckBox,QListWidget,QFileDialog
from PyQt5.QtCore import QSize
from idrw203driver import *
from QLed import QLed


class HelloWindow(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)

		self.setMinimumSize(QSize(640, 480))
		self.setWindowTitle("USB-203 GUI")
		self.driver = IDRW203Driver()


		e = QLineEdit()
		fm = e.fontMetrics()
		m = e.textMargins()
		c = e.contentsMargins()
		charwidth = fm.width('x')


		centralWidget = QWidget(self)
		self.setCentralWidget(centralWidget)

		gridLayout = QVBoxLayout(self)
		centralWidget.setLayout(gridLayout)

		statusbox = QGroupBox("status")
		gridLayout.addWidget(statusbox)

		numberbox = QGroupBox("Number Format")
		gridLayout.addWidget(numberbox)

		cgridLayout = QGridLayout(self)
		statusbox.setLayout(cgridLayout)
			
			
		self.connectedled=QLed(self, onColour=QLed.Green, shape=QLed.Circle)
		self.connectedled.value=False
		cgridLayout.addWidget(self.connectedled,0,1)
        
		self.connbutton = QPushButton(self)
		self.connbutton.setText("Connect")
		self.connbutton.clicked.connect(self.do_connect)
		
		cgridLayout.addWidget(self.connbutton, 0, 2)

		self.disbutton = QPushButton(self)
		self.disbutton.setText("Disconnect")
		self.disbutton.setEnabled(False)
		self.disbutton.clicked.connect(self.do_disconnect)

		cgridLayout.addWidget(self.disbutton, 0, 3)

		status = QLabel(self)
		status.setText("Status: ")
		cgridLayout.addWidget(status, 0,4)

		self.statustext = QLabel(self)
		self.statustext.setText("The reader is not connected...")
		cgridLayout.addWidget(self.statustext, 1,4)


		ngridLayout = QGridLayout(self)
		numberbox.setLayout(ngridLayout)

		self.range1 = QRadioButton("10H")
		ngridLayout.addWidget(self.range1, 0,1)
		self.ranget1 = QLineEdit(self)
		self.ranget1.setFixedWidth(charwidth * 12)
		ngridLayout.addWidget(self.ranget1, 0,2)
		self.range1.setChecked(True)

		self.range2 = QRadioButton("8H --> 10D")
		ngridLayout.addWidget(self.range2, 1,1)
		self.ranget2 = QLineEdit(self)
		self.ranget2.setFixedWidth(charwidth * 12)
		ngridLayout.addWidget(self.ranget2, 1,2)

		self.range3 = QRadioButton("6H --> 10D")
		ngridLayout.addWidget(self.range3, 2,1)
		self.ranget3 = QLineEdit(self)
		self.ranget3.setFixedWidth(charwidth * 12)
		ngridLayout.addWidget(self.ranget3, 2,2)

		self.range4 = QRadioButton("2H + 4H")
		ngridLayout.addWidget(self.range4, 3,1)
		self.ranget4 = QLineEdit(self)
		self.ranget4.setFixedWidth(charwidth * 12)
		ngridLayout.addWidget(self.ranget4, 3,2)

		self.range5 = QLabel(",")
		ngridLayout.addWidget(self.range5, 3,3)
		self.ranget5 = QLineEdit(self)
		self.ranget5.setFixedWidth(charwidth * 8)
		ngridLayout.addWidget(self.ranget5, 3,4)


		self.anausbbutton = QCheckBox(self)
		self.anausbbutton.setText("Analog USB Keyboard")
		ngridLayout.addWidget(self.anausbbutton, 0, 5)

		lockbutton = QCheckBox(self)
		lockbutton.setText("Lock Card operation")
		ngridLayout.addWidget(lockbutton, 1, 5)

		incbutton = QCheckBox(self)
		incbutton.setText("Card Number is Incremented")
		ngridLayout.addWidget(incbutton, 2, 5)

		readbutton = QPushButton(self)
		readbutton.setText("Read Card")
		ngridLayout.addWidget(readbutton, 3, 5)
		readbutton.clicked.connect(self.do_read)


		writebutton = QPushButton(self)
		writebutton.setText("Write Card")
		ngridLayout.addWidget(writebutton, 4, 5)


		filebox = QGroupBox("")
		gridLayout.addWidget(filebox)
		bgridLayout = QGridLayout(self)
		filebox.setLayout(bgridLayout)

		filebutton = QPushButton(self)
		filebutton.setText("File...")
		filebutton.clicked.connect(self.do_load_file)
		bgridLayout.addWidget(filebutton, 0, 0)

		delbutton = QPushButton(self)
		delbutton.setText("Delete")
		bgridLayout.addWidget(delbutton, 0, 1)

		autobutton = QPushButton(self)
		autobutton.setText("Auto Write")
		bgridLayout.addWidget(autobutton, 0, 2)

		stopbutton = QPushButton(self)
		stopbutton.setText("Stop Write")
		bgridLayout.addWidget(stopbutton, 0, 3)

		clearbutton = QPushButton(self)
		clearbutton.setText("Clear")
		bgridLayout.addWidget(clearbutton, 0, 4)
		
		cardlist = QGroupBox("")
		cgridLayout = QGridLayout(self)
		gridLayout.addWidget(cardlist)
		cardlist.setLayout(cgridLayout)
		
		self.inlist = QListWidget()
		cgridLayout.addWidget(self.inlist, 0, 0)

		self.outlist = QListWidget()
		cgridLayout.addWidget(self.outlist, 0, 1)


	def do_connect(self):
		self.driver.connect() #just using it for emulation for now
		if self.driver.connected == True:
			self.driver.buzzer()
			self.connectedled.setValue(True)
			self.connbutton.setEnabled(False)
			self.disbutton.setEnabled(True)
			self.statustext.setText("Reader connection is successful")
		else:
			self.statustext.setText("The reader is not connected...")



	def do_disconnect(self):
		if self.driver.connected == True:
			self.driver.disconnect()
			self.connectedled.setValue(False)
			self.connbutton.setEnabled(True)
			self.disbutton.setEnabled(False)
			self.statustext.setText("Failed to connect to reader...")

	def do_read(self):
		if self.driver.connected == True:
			done = True
			while done == True:
				(ret,stat,val) = self.driver.Em4100_read()
				print(val)
				if(val):
					self.driver.buzzer()
					self.ranget1.setText(str(val))
					intval = str(val)
					self.ranget2.setText(str(int(str(intval)[-8:],16)).rjust(8,'0'))
					self.ranget3.setText(str(int(str(intval)[-6:],16)).rjust(6,'0'))
	#				self.ranget4.setText(str(int(str(intval)[-4:-6],16)))
	#				self.ranget5.setText(str(int(str(intval)[-4:],16)))
				if self.anausbbutton.isChecked():
					done = False
	
			else:
				self.driver.buzzer()
				self.driver.buzzer()
				self.driver.buzzer()
				self.statustext.setText("Read Failed")


	def do_load_file(self):
		dlg = QFileDialog()
		dlg.setFileMode(QFileDialog.AnyFile)
		dlg.setNameFilter(str("RFID Tag List (*.txt)"))
#		filenames = QStringList()

		if dlg.exec_():
			filenames = dlg.selectedFiles()
			print(filenames)
			for f in filenames:
#				try:
					ff = open(f)
					ll = ff.readlines()
					ff.close()
#					for l in ll:
					self.inlist.addItems(ll)
#				except:
#					pass

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = HelloWindow()
    mainWin.show()
    sys.exit( app.exec_() )
