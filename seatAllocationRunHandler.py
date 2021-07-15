# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 14:07:48 2021

@author: henry
"""

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QRunnable
from seatAllocationAlgorithms import jonsAllocator, richardsAllocator
import sys

class DummyParent():
    
    def __init__(self, seatPixelCoords):
         self.seatPixelCoords = seatPixelCoords
    
class Communication(QObject):
    
    finishedSignal = pyqtSignal(str)
     
class AlgorithmWorker(QRunnable):
    
    def __init__(self, parent, seatPixelCoords, socialDistSep, margin, magicScale, n1, n2, totalReRuns):
        super().__init__()
        self.communicator = Communication()
        self.parent = parent
        self.seatPixelCoords = seatPixelCoords
        self.socialDistSep = socialDistSep
        self.margin = margin
        self.magicScale = magicScale
        self.n1 = n1
        self.n2 = n2
        self.totalReRuns = totalReRuns
    
    @pyqtSlot()
    def run(self):
        self.parent.seatsAllocatedBest, self.parent.positionsBest = richardsAllocator(self.seatPixelCoords, self.socialDistSep, 
                                                                                      margin=self.margin, magicScale=self.magicScale, stageOneLoops=self.n1, 
                                                                                      stageTwoLoops=self.n2, totalReRuns=self.totalReRuns)                
        
        print(f'Number of Seats Allocated: {len(self.parent.seatsAllocatedBest)} out of {self.parent.positionsBest.shape[0]}')
        self.communicator.finishedSignal.emit('r')
        


class doneAndRunHandler(QtWidgets.QWidget):
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setUpUi()
        
        
    def setUpUi(self):
        self.setGeometry(600, 150, 300, 60)
        self.setWindowTitle('Set Allocation Algorithm Parameters')
        
        
        self.mainLayout = QtWidgets.QVBoxLayout()
        
        self.selectAlgoTitle = QtWidgets.QLabel('Select an Allocation Algorithm')
        self.selectAlgoTitle.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.selectAlgoDropDown = QtWidgets.QComboBox()
        self.selectAlgoDropDown.insertItem(0, 'Select an algorithm...')
        self.selectAlgoDropDown.insertItem(1, 'Richard\'s Allocator')
        self.selectAlgoDropDown.insertItem(2, 'Jon\'s Allocator')
        
        self.selectAlgoDropDown.currentIndexChanged.connect(self.changeLayout)
        
        self.socialDistancingSepTitle = QtWidgets.QLabel('Set the Social Distancing Seperation (in metres)')
        self.socialDistancingSepLineEdit = QtWidgets.QLineEdit('2')
         
        
    
        self.mainLayout.addWidget(self.selectAlgoTitle)
        self.mainLayout.addWidget(self.selectAlgoDropDown)
        self.mainLayout.addWidget(self.socialDistancingSepTitle)
        self.mainLayout.addWidget(self.socialDistancingSepLineEdit)
        
        #### CREATE STACKED WIDGET
        self.stackedWidget = QtWidgets.QStackedWidget()
        
        ### DEFAULT WIDGET:
        with open('algorithmDescriptions.html', 'r') as f:
            message = f.read()
        self.defaultWidget = QtWidgets.QLabel()
        self.defaultWidget.setText("This software currently offers two seat allocation algorithms for finding seating solutions.\n- Richard\'s Allocator\n- Jon\'s Allocator")
#        self.defaultWidget = QtWidgets.QLabel(message)
        self.defaultWidget.setAlignment(Qt.AlignCenter)
        
        ## RICHARDS WIDGET:
        self.richardsWidget = QtWidgets.QWidget()
        self.richardsLayout = QtWidgets.QVBoxLayout()
        
        self.rDescription = QtWidgets.QLabel()
        self.rDescription.setText('<html><b>DESCRIPTION OF RICHARD\'S ALGORITHM</b></html>')
        
        
        self.rStage1Layout = QtWidgets.QHBoxLayout()
        self.rStage1LoopsTitle = QtWidgets.QLabel('Set number of Stage One Iterations')
        self.rStage1LoopsLineEdit = QtWidgets.QLineEdit('50')
        self.rStage1LoopsLineEdit.setAlignment(Qt.AlignRight)
        self.rStage1Layout.addWidget(self.rStage1LoopsTitle)
        self.rStage1Layout.addWidget(self.rStage1LoopsLineEdit)
        
        self.rStage2Layout = QtWidgets.QHBoxLayout()       
        self.rStage2LoopsTitle = QtWidgets.QLabel('Set number of Stage Two Iterations')
        self.rStage2LoopsLineEdit = QtWidgets.QLineEdit('200')
        self.rStage2LoopsLineEdit.setAlignment(Qt.AlignRight)
        self.rStage2Layout.addWidget(self.rStage2LoopsTitle)
        self.rStage2Layout.addWidget(self.rStage2LoopsLineEdit)

        self.rMarginLayout = QtWidgets.QHBoxLayout()        
        self.rMarginTitle = QtWidgets.QLabel('Set Margin (in metres)')
        self.rMarginLineEdit = QtWidgets.QLineEdit('0.1')
        self.rMarginLineEdit.setAlignment(Qt.AlignRight)
        self.rMarginLayout.addWidget(self.rMarginTitle)
        self.rMarginLayout.addWidget(self.rMarginLineEdit)
        
        self.rTotalReRunsLayout = QtWidgets.QHBoxLayout()
        self.rTotReRunsTitle = QtWidgets.QLabel('Set Total Number of Re-Runs')
        self.rTotReRunsLineEdit = QtWidgets.QLineEdit('150')
        self.rTotReRunsLineEdit.setAlignment(Qt.AlignRight)
        self.rTotalReRunsLayout.addWidget(self.rTotReRunsTitle)
        self.rTotalReRunsLayout.addWidget(self.rTotReRunsLineEdit)
    
    
        self.richardsLayout.addWidget(self.rDescription)
        self.richardsLayout.addLayout(self.rStage1Layout)
        self.richardsLayout.addLayout(self.rStage2Layout)
        self.richardsLayout.addLayout(self.rMarginLayout)
        self.richardsLayout.addLayout(self.rTotalReRunsLayout)
    
    
        self.richardsWidget.setLayout(self.richardsLayout)
        
        ### JONS WIDGET
        self.jonsWidget = QtWidgets.QLabel()
        self.jonsWidget.setText('<html><b>DESCRIPTION OF JON\'S ALGORITHM</b></html>')
        
        self.stackedWidget.addWidget(self.defaultWidget)
        self.stackedWidget.addWidget(self.richardsWidget)
        self.stackedWidget.addWidget(self.jonsWidget)
        self.stackedWidget.setCurrentWidget(self.defaultWidget)   
        
        self.mainLayout.addWidget(self.stackedWidget)
        
        self.doneAndRunBtn = QtWidgets.QPushButton('Run Allocator')
        self.doneAndRunBtn.clicked.connect(self.runAllocator)
        self.mainLayout.addWidget(self.doneAndRunBtn)      
        
        self.setLayout(self.mainLayout)
        
    def changeLayout(self):
        self.currentIndex = self.selectAlgoDropDown.currentIndex()
        
        if self.currentIndex == 0:
            self.stackedWidget.setCurrentWidget(self.defaultWidget)
            self.doneAndRunBtn.setEnabled(False)
        elif self.currentIndex == 1:
            self.stackedWidget.setCurrentWidget(self.richardsWidget) 
            self.doneAndRunBtn.setEnabled(True)
        elif self.currentIndex == 2:
            self.stackedWidget.setCurrentWidget(self.jonsWidget)          
            self.doneAndRunBtn.setEnabled(True)
        
        ## If it changes to Richard's Allocator, reset layout
        
        ## If it changes to Jon's reset layout/ show the correct stacked widget
        
    def runAllocator(self):
        if self.currentIndex == 1:
            self.runRichards()
        elif self.currentIndex == 2:
            self.runJons()
            
    def runRichards(self):
        self.parent.socialDistancingSeperation = float(self.socialDistancingSepLineEdit.text())
        margin = float(self.rMarginLineEdit.text())
        magicScale = self.parent.magicScale
        n1 = int(self.rStage1LoopsLineEdit.text())
        n2 = int(self.rStage2LoopsLineEdit.text())
        totalReRuns = int(self.rTotReRunsLineEdit.text())
        
        self.hide()

        
        algorithmWorker = AlgorithmWorker(self.parent, self.parent.seatPixelCoords, self.parent.socialDistancingSeperation, margin, magicScale, n1, n2, totalReRuns)
        algorithmWorker.communicator.finishedSignal.connect(self.parent.plotSocialDistancingCircles)
        
        
        self.parent.threadpool.start(algorithmWorker)
        
        
    
    def runJons(self):
        pass
        
        
        
        




def main():
    app = QtWidgets.QApplication(sys.argv)
    doneAndRunWidget = doneAndRunHandler()
    doneAndRunWidget.show()
    sys.exit(app.exec_())
        

if __name__ == '__main__':
    main()