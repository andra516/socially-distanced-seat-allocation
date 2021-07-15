# -*- coding: utf-8 -*-
"""
Created on Sat Jul 10 16:50:43 2021

@author: henry
"""

import numpy as np
import os
import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QRunnable, QThreadPool, pyqtSignal, pyqtSlot, QObject, QThread
from PyPDF2 import PdfFileReader
from pdf2image import convert_from_path
from seatAllocationIO import savePlanDetails
import shutil

### create QRunnable that will convert pdf and all that sexy stuff
### need a QThreadPool too 

class DummyParent():
    
    def __init__(self):
        self.threadpool = QThreadPool()
        

    def updatePixmap(self, pngPath):
        pass
    
    def enableActions(self, mode):
        pass     
        


class WorkerSignals(QObject):
    
    finishedSignal = pyqtSignal()

class Worker(QRunnable):
    
    def __init__(self, parent, pdfPath, ppi, pngPath):
        super().__init__()
        self.parentWidget = parent
        self.pdfPath = pdfPath
        self.ppi = ppi
        self.pngPath = pngPath
        self.workerSignals = WorkerSignals()
        
    @pyqtSlot()
    def run(self):
        print('starting conversion')
        image = convert_from_path(self.pdfPath, self.ppi)[0]
        image.save(self.pngPath, 'PNG')
        print('finished conversion and saved')
        
        self.workerSignals.finishedSignal.emit()

class OpenNewSession(QtWidgets.QWidget):
    
    def __init__(self, parent):
        super().__init__()
        
        self.parent = parent       
        
        self.setUpUi()
        
    def setUpUi(self):
        self.setGeometry(600, 150, 500, 180)        
        self.setWindowTitle('Start New Allocation Session')
        
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.pdfPathLineEdit = QtWidgets.QLineEdit()
        self.planScaleLineEdit = QtWidgets.QLineEdit('1:100')
        self.pngResolutionLineEdit = QtWidgets.QLineEdit('300')
        self.newDirectoryLineEdit = QtWidgets.QLineEdit()
        
        self.pdfPathTitle = QtWidgets.QLabel('Select Room Plan PDF File')
        self.planScaleTitle = QtWidgets.QLabel('Input the Plan Scale (Default 1:100)')
        self.pngResolutionTitle = QtWidgets.QLabel('Set PNG Display Resolution (Default: 300 ppi)')
        self.newDirectoryTitle = QtWidgets.QLabel('Select Session Save Location')
        
        self.browsePDFButton = QtWidgets.QPushButton('Browse')
        self.browsePDFButton.clicked.connect(self.browsePDFButtonPush)
        self.newDirectoryButton = QtWidgets.QPushButton('Browse')
        self.newDirectoryButton.setEnabled(False)
        self.newDirectoryButton.clicked.connect(self.newDirectoryButtonPush)
        self.doneButton = QtWidgets.QPushButton('Open Room Plan')
        self.doneButton.setEnabled(False)
        self.doneButton.clicked.connect(self.convertPDF)
        
        self.pdfPathLayout = QtWidgets.QHBoxLayout()
        self.pdfPathLayout.addWidget(self.pdfPathLineEdit)
        self.pdfPathLayout.addWidget(self.browsePDFButton)
        
        self.newDirectoryLayout = QtWidgets.QHBoxLayout()
        self.newDirectoryLayout.addWidget(self.newDirectoryLineEdit)
        self.newDirectoryLayout.addWidget(self.newDirectoryButton)
        
        self.mainLayout.addWidget(self.pdfPathTitle)
        self.mainLayout.addLayout(self.pdfPathLayout)
        self.mainLayout.addWidget(self.planScaleTitle)
        self.mainLayout.addWidget(self.planScaleLineEdit)
        self.mainLayout.addWidget(self.pngResolutionTitle)
        self.mainLayout.addWidget(self.pngResolutionLineEdit)
        self.mainLayout.addWidget(self.newDirectoryTitle)
        self.mainLayout.addLayout(self.newDirectoryLayout)
        self.mainLayout.addWidget(self.doneButton)
        
        self.setLayout(self.mainLayout)
        
        self.ppi = 300
    
        
    def browsePDFButtonPush(self):

        self.pdfPath = QtWidgets.QFileDialog.getOpenFileName(self, 'Select PDF', os.getcwd(), "PDF Files (*.pdf)")[0]
        if self.pdfPath == '':
            pass
        else:
#            print(self.pdfPath)
            self.pdfPathLineEdit.setText(self.pdfPath) 
            self.newDirectoryButton.setEnabled(True)
            
    def newDirectoryButtonPush(self):
        dialog = QtWidgets.QFileDialog()
        dialog.setWindowTitle('Select Session Save Location')
        dialog.setDirectory(os.getcwd())
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        
        if dialog.exec_():
            self.sessionSavePath = dialog.selectedFiles()[0].replace('/', os.sep)            
            
            sessionNum = 1
            
            while True:
                saveDirectory = self.sessionSavePath + os.sep + 'Seat Allocation Session #' + str(sessionNum) + ' - ' + os.path.splitext(os.path.basename(self.pdfPath))[0]
                if os.path.basename(saveDirectory) in os.listdir(self.sessionSavePath):
                    sessionNum += 1
                else:
                    self.parent.saveDirectory = saveDirectory
                    break
             
            self.newDirectoryLineEdit.setText(self.parent.saveDirectory)       

            self.doneButton.setEnabled(True)
        else:
            pass
        

    def convertPDF(self):
        ## disable buttons and LineEdits
        self.browsePDFButton.setEnabled(False)
        self.newDirectoryButton.setEnabled(False)
        self.doneButton.setEnabled(False)
        self.pdfPathLineEdit.setEnabled(False)
        self.pngResolutionLineEdit.setEnabled(False)
        self.planScaleLineEdit.setEnabled(False)
        self.newDirectoryLineEdit.setEnabled(False)
        
        
        ## read off whats in the lineEdits
        self.ppi = int(self.pngResolutionLineEdit.text())
        self.pdfScale = self.planScaleLineEdit.text().split(sep=':')
        self.pdfPath = self.pdfPathLineEdit.text()

        ### Create session save directory
        try:
            os.mkdir(self.parent.saveDirectory)
            ## copy pdf room plan to session save directory
            pdfCopyPath = self.parent.saveDirectory + os.sep + os.path.basename(self.pdfPath)
            shutil.copy(self.pdfPath, pdfCopyPath)
        except Exception as e:
            print(e.__class__.__name__)
            print(e)
            

        self.parent.pngPath = self.parent.saveDirectory + os.sep + os.path.splitext(os.path.basename(self.pdfPath))[0] + '.png'
            
        self.worker = Worker(self, self.pdfPath, self.ppi, self.parent.pngPath)
        self.worker.workerSignals.finishedSignal.connect(self.close)
        self.parent.threadpool.start(self.worker)

#        self.close()
            
        
#            # convert the pdf to a png at the desired ppi and save to saveDirectory
#        try:
#            image = convert_from_path(self.pdfPath, self.ppi)[0]
#            self.parent.pngPath = self.parent.saveDirectory + os.sep + os.path.splitext(os.path.basename(self.pdfPath))[0] + '.png'
#            image.save(self.parent.pngPath, 'PNG')
#
#            ## close the window and call parent functions/set variables          
#            self.close()
#        except Exception as e:
#            print(e.__name__)
#            print(e)
#            pass
#        
    def close(self):
        self.parent.magicScale = int(self.pdfScale[0])/int(self.pdfScale[1]) * self.ppi * 100 / 2.54000508
        self.parent.updatePixmap(self.parent.pngPath)
        self.parent.enableActions(1)
        
        savePlanDetails(self.parent.saveDirectory, self.ppi, self.pdfScale, self.parent.magicScale)
#        print(r'saved plan details :)')
        
        self.hide()



def main():
    app = QtWidgets.QApplication(sys.argv)
    openNewSessionWidget = OpenNewSession(DummyParent())
    openNewSessionWidget.show()
    sys.exit(app.exec_())
        

if __name__ == '__main__':
    main()