# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 14:07:48 2021

@author: henry
"""

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QRunnable
from PyQt5.QtGui import QKeySequence
from seatAllocationAlgorithms import eliminationAllocator, additionAllocator
import sys

class DummyParent():
    
    def __init__(self, seatPixelCoords):
         self.seatPixelCoords = seatPixelCoords
         self.magicScale = 'deeznuts'
    
class Communication(QObject):
    
    finishedSignal = pyqtSignal()
     
class AlgorithmWorker(QRunnable):
    
    def __init__(self, parent, algorithm, seatPixelCoords, socialDistSep, magicScale, **kwargs):
        super().__init__()
        self.communicator = Communication()
        self.parent = parent
        self.algorithm = algorithm
        self.seatPixelCoords = seatPixelCoords
        self.socialDistSep = socialDistSep
        self.magicScale = magicScale
        self.kwargs = kwargs
        
    @pyqtSlot()
    def run(self):

        self.parent.seatsAllocatedIndices, self.parent.seatPositions = self.algorithm(seatPixelCoords=self.seatPixelCoords, kwargs=self.kwargs,
                                                                                          socialDistancingSeperation=self.socialDistSep, 
                                                                                          magicScale=self.magicScale)
   
        print(f'Number of Seats Allocated: {len(self.parent.seatsAllocatedIndices)} out of {self.parent.seatPositions.shape[0]}')
        self.communicator.finishedSignal.emit()

class DoneAndRunHandler(QtWidgets.QWidget):
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setUpUi()
        
        
    def setUpUi(self):
        self.setGeometry(600, 150, 600, 100)
        self.setWindowTitle('Set Allocation Algorithm Parameters')
        
        
        self.mainLayout = QtWidgets.QVBoxLayout()
        
        self.selectAlgoTitle = QtWidgets.QLabel('Select an Allocation Algorithm')
        self.selectAlgoTitle.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.selectAlgoDropDown = QtWidgets.QComboBox()
        self.selectAlgoDropDown.insertItem(0, 'Select an algorithm...')
        self.selectAlgoDropDown.insertItem(1, 'Richard\'s Algorithm: Allocation by Addition')
        self.selectAlgoDropDown.insertItem(2, 'Jon\'s Algorithm: Allocation by Elimination')
        
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
        self.defaultWidget.setWordWrap(True)
        self.defaultWidget.setText(message)
#        self.defaultWidget = QtWidgets.QLabel(message)
        self.defaultWidget.setAlignment(Qt.AlignCenter)
        
        ## ADDITION WIDGET:
        self.additionWidget = QtWidgets.QWidget()
        self.additionLayout = QtWidgets.QVBoxLayout()
        
        self.aDescription = QtWidgets.QLabel()
        self.aDescription.setText("<html><b>Allocation by Addition</b><p><small>Thanks to Richard Mason for letting me use his original MATLAB algorithm, translated to Python here!</small></p></html>")
        self.aDescription.setAlignment(Qt.AlignLeft)
        
        
        self.aStage1Layout = QtWidgets.QHBoxLayout()
        self.aStage1LoopsTitle = QtWidgets.QLabel('Set number of Stage One Iterations')
        self.aStage1LoopsLineEdit = QtWidgets.QLineEdit('50')
        self.aStage1LoopsLineEdit.setAlignment(Qt.AlignRight)
        self.aStage1Layout.addWidget(self.aStage1LoopsTitle)
        self.aStage1Layout.addWidget(self.aStage1LoopsLineEdit)
        
        self.aStage2Layout = QtWidgets.QHBoxLayout()       
        self.aStage2LoopsTitle = QtWidgets.QLabel('Set number of Stage Two Iterations')
        self.aStage2LoopsLineEdit = QtWidgets.QLineEdit('200')
        self.aStage2LoopsLineEdit.setAlignment(Qt.AlignRight)
        self.aStage2Layout.addWidget(self.aStage2LoopsTitle)
        self.aStage2Layout.addWidget(self.aStage2LoopsLineEdit)

        self.aMarginLayout = QtWidgets.QHBoxLayout()        
        self.aMarginTitle = QtWidgets.QLabel('Set Margin (in metres)')
        self.aMarginLineEdit = QtWidgets.QLineEdit('0.1')
        self.aMarginLineEdit.setAlignment(Qt.AlignRight)
        self.aMarginLayout.addWidget(self.aMarginTitle)
        self.aMarginLayout.addWidget(self.aMarginLineEdit)
        
        self.aTotalReRunsLayout = QtWidgets.QHBoxLayout()
        self.aTotReRunsTitle = QtWidgets.QLabel('Set Total Number of Re-Runs')
        self.aTotReRunsLineEdit = QtWidgets.QLineEdit('150')
        self.aTotReRunsLineEdit.setAlignment(Qt.AlignRight)
        self.aTotalReRunsLayout.addWidget(self.aTotReRunsTitle)
        self.aTotalReRunsLayout.addWidget(self.aTotReRunsLineEdit)
    
    
        self.additionLayout.addWidget(self.aDescription)
        self.additionLayout.addLayout(self.aStage1Layout)
        self.additionLayout.addLayout(self.aStage2Layout)
        self.additionLayout.addLayout(self.aMarginLayout)
        self.additionLayout.addLayout(self.aTotalReRunsLayout)
    
    
        self.additionWidget.setLayout(self.additionLayout)
        
        ### ELIMINATION WIDGET
        self.elimWidget = QtWidgets.QLabel()
        self.elimWidget.setWordWrap(True)
        self.elimWidget.setText('<html><b>Allocation by Elimination</b><p><small>Thanks to Jonathan Watkins for letting me use his algorithm!</small></p></html>')
        self.elimWidget.setAlignment(Qt.AlignCenter)
        
        self.stackedWidget.addWidget(self.defaultWidget)
        self.stackedWidget.addWidget(self.additionWidget)
        self.stackedWidget.addWidget(self.elimWidget)
        self.stackedWidget.setCurrentWidget(self.defaultWidget)
        
        self.mainLayout.addWidget(self.stackedWidget)
        
        self.doneAndRunBtn = QtWidgets.QPushButton('Run Allocator')
        self.doneAndRunBtn.clicked.connect(self.runAllocator)
        self.doneAndRunBtn.setAutoDefault(True)
        self.doneAndRunBtn.setEnabled(False)
        self.mainLayout.addWidget(self.doneAndRunBtn)      
        
        self.setLayout(self.mainLayout)
        
    def changeLayout(self):
        self.currentIndex = self.selectAlgoDropDown.currentIndex()
        
        if self.currentIndex == 0:
            self.stackedWidget.setCurrentWidget(self.defaultWidget)
            self.doneAndRunBtn.setEnabled(False)
        elif self.currentIndex == 1:
            self.stackedWidget.setCurrentWidget(self.additionWidget) 
            self.doneAndRunBtn.setEnabled(True)
        elif self.currentIndex == 2:
            self.stackedWidget.setCurrentWidget(self.elimWidget)          
            self.doneAndRunBtn.setEnabled(True)
        
    def runAllocator(self):
        if self.currentIndex == 1:
            self.runAdd()
        elif self.currentIndex == 2:
            self.runElim()
            
    def runAdd(self):
        self.parent.socialDistancingSeperation = float(self.socialDistancingSepLineEdit.text())
        margin = float(self.aMarginLineEdit.text())
        n1 = int(self.aStage1LoopsLineEdit.text())
        n2 = int(self.aStage2LoopsLineEdit.text())
        totalReRuns = int(self.aTotReRunsLineEdit.text())
        
        self.hide()
        
        algorithmWorker = AlgorithmWorker(parent=self.parent, algorithm=additionAllocator, seatPixelCoords=self.parent.seatPixelCoords, 
                                          socialDistSep=self.parent.socialDistancingSeperation, magicScale=self.parent.magicScale, 
                                          margin=margin, stageOneLoops=n1, stageTwoLoops=n2, totalReRuns=totalReRuns)
        
        algorithmWorker.communicator.finishedSignal.connect(self.parent.plotSocialDistancingCircles)
        
        self.parent.threadpool.start(algorithmWorker)
        
        
    
    def runElim(self):
        self.parent.socialDistancingSeperation = float(self.socialDistancingSepLineEdit.text())

        self.hide()
        
        algorithmWorker = AlgorithmWorker(parent=self.parent, algorithm=eliminationAllocator, seatPixelCoords=self.parent.seatPixelCoords, 
                                          socialDistSep=self.parent.socialDistancingSeperation, magicScale=self.parent.magicScale)
        
        algorithmWorker.communicator.finishedSignal.connect(self.parent.plotSocialDistancingCircles)
        
        self.parent.threadpool.start(algorithmWorker)        
        
        




def main():
    app = QtWidgets.QApplication(sys.argv)
    doneAndRunWidget = DoneAndRunHandler(DummyParent('your mum'))
    doneAndRunWidget.show()
    sys.exit(app.exec_())
        

if __name__ == '__main__':
    main()