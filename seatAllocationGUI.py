# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 16:17:23 2021

@author: henry
"""
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QRect, QRectF, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPixmap, QBitmap, QIcon, QPen, QColor, QKeySequence, QCursor
import sys
import os
#import time
import numpy as np
from seatAllocationAlgorithmJon import jonsAllocator

class Communication(QObject):
    
    ginputClickSignal = pyqtSignal(float, float) # will be used to tell MainWindow where seat positions are.


class MyGraphicsView(QtWidgets.QGraphicsView):
    
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.scene = parent.scene
        self.setScene(self.scene)
        
        self.communicator = Communication()
        self.communicator.ginputClickSignal.connect(parent.recordCoord)
    
    def mousePressEvent(self, event):
        print('mouse press event local pos', event.localPos().toPoint())
        if self.parent.ginputPermission == True:
            scenePressPoint = self.mapToScene(event.localPos().toPoint()) # this is a QPointF
            x = scenePressPoint.x()
            y = scenePressPoint.y()
            self.communicator.ginputClickSignal.emit(x, y)
        else:
            pass

class MyMainWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle('Seat Allocation')
#        self.resize(1500, 800)
        self.setGeometry(200, 100, 1200, 700)
        self.show()
        print('why son')
        print('wow thats grape')
        
        self.setUpUi()
        
    def setUpUi(self):
        
        self.centralWidget = QtWidgets.QWidget()
        self.mainLayout = QtWidgets.QVBoxLayout()
        
        ### MENU BAR        
        self.fileMenu = self.menuBar().addMenu('File')
        self.ginputMenu = self.menuBar().addMenu('Ginput')
        
        
        ### FILE MENU BAR ACTIONS
        self.openAct = QtWidgets.QAction('Open')
        self.loadSeatsAct = QtWidgets.QAction('Load seats') # pixel coordinates from previously found maps
        self.saveAct = QtWidgets.QAction('Save seating plan')
        # initially all disabled
        self.loadSeatsAct.setEnabled(False)
        self.saveAct.setEnabled(False)
    
        self.openAct.triggered.connect(self.openPNGFile)
        self.saveAct.triggered.connect(self.saveAsPNGFile)
                
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.loadSeatsAct)
        self.fileMenu.addAction(self.saveAct)
    
        
        ### GINPUT MENU BAR ACTIONS
        self.selectSeatsAct = QtWidgets.QAction('Enable ginput to select seats')
        self.undoSelectAct = QtWidgets.QAction('Undo last selection')
        self.movePointAct = QtWidgets.QAction('Move selections')
        self.clearAllAct = QtWidgets.QAction('Clear all selections')
        self.doneAndRunAct = QtWidgets.QAction('Done and run allocator')
        ### initially all disabled
        self.selectSeatsAct.setEnabled(False)
        self.undoSelectAct.setEnabled(False)
        self.movePointAct.setEnabled(False)
        self.clearAllAct.setEnabled(False)
        self.doneAndRunAct.setEnabled(False)
        
        self.selectSeatsAct.triggered.connect(self.ginput)
        self.undoSelectAct.triggered.connect(self.undoSelection)
        self.clearAllAct.triggered.connect(self.clearSelections)
        self.doneAndRunAct.triggered.connect(self.saveSeats)
        
        self.undoSelectAct.setShortcut(QKeySequence('Ctrl+Z'))
              
        self.ginputMenu.addAction(self.selectSeatsAct)
        self.ginputMenu.addAction(self.undoSelectAct)
        self.ginputMenu.addAction(self.movePointAct)
        self.ginputMenu.addAction(self.clearAllAct)
        self.ginputMenu.addAction(self.doneAndRunAct)


        #### GRAPHICSVIEW WIDGET
        self.scene = QtWidgets.QGraphicsScene()
        self.view = MyGraphicsView(parent=self)
#        self.view.setCursor(QCursor(QBitmap('cursor.bmp')))
        self.view.setAlignment(Qt.AlignCenter | Qt.AlignLeft)


        #### TOOLBAR LAYOUT AND BUTTONS
        self.toolbarLayout = QtWidgets.QHBoxLayout()
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setOrientation(Qt.Horizontal)
        self.zoomInAct = QtWidgets.QAction(QIcon(os.getcwd() + '\\icon logos\\zoomIn.png'), 'Zoom In')
        self.zoomOutAct = QtWidgets.QAction(QIcon(os.getcwd() + '\\icon logos\\zoomOut.png'), 'Zoom Out')
        self.ginputAct = QtWidgets.QAction(QIcon(os.getcwd() + '\\icon logos\\ginput.png'),'Ginput')
        self.ginputPermission = False # ginputPermission will initially be False        
        self.scaleAct = QtWidgets.QAction(QIcon(os.getcwd() + '\\icon logos\\scale.png'), 'Scale')
        self.doneAct = QtWidgets.QAction('Done')
        
        self.zoomInAct.triggered.connect(self.zoomIn)
        self.zoomOutAct.triggered.connect(self.zoomOut)
        self.ginputAct.triggered.connect(self.ginput)
        self.doneAct.triggered.connect(self.saveSeats)
        
        self.ginputAct.setEnabled(False)
        self.zoomInAct.setEnabled(False)
        self.zoomOutAct.setEnabled(False)
        self.ginputAct.setEnabled(False)
        self.scaleAct.setEnabled(False)
        self.doneAct.setEnabled(False)
        
        self.toolbar.addAction(self.zoomInAct)
        self.toolbar.addAction(self.zoomOutAct)
        self.toolbar.addAction(self.scaleAct)
        self.toolbar.addAction(self.ginputAct)
        self.toolbar.addAction(self.doneAct)

        self.toolbarLayout.addWidget(self.toolbar)
        self.toolbarLayout.setAlignment(Qt.AlignRight)
               
        
        ### ADD WIDGETS AND LAYOUT TO MAIN LAYOUT
        self.mainLayout.addLayout(self.toolbarLayout)
        self.mainLayout.addWidget(self.view)
        
        self.centralWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.centralWidget)
        
        
        #### SET INITIAL PIXMAP AND ADD TO SCENE        
        self.initPixmap = QPixmap(os.getcwd() + '\\icon logos\\uob logo.png')
        self.scene.addPixmap(self.initPixmap)
        self.view.fitInView(QRectF(self.initPixmap.rect()), mode=Qt.KeepAspectRatio)
        
        
        self.Xs = []
        self.Ys = []
        self.currentGraphicsEllipseItems = []
        
    def openPNGFile(self):

        self.fileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Image', os.getcwd(), "PNG Files (*.png)")[0]
        if self.fileName == '': ## incase filedialog was closed without choosing image
            pass
        else:
            ### ENSURE ALL ACTIONS ARE ENABLED
            # file actions
            self.loadSeatsAct.setEnabled(True)
#            self.saveAct.setEnabled(True)
            # ginput actions
            self.selectSeatsAct.setEnabled(True)
            self.undoSelectAct.setEnabled(True)
            self.movePointAct.setEnabled(True)
            self.clearAllAct.setEnabled(True)
            self.doneAndRunAct.setEnabled(True)
            # toolbar actions
            self.ginputAct.setEnabled(True)
            self.zoomInAct.setEnabled(True)
            self.zoomOutAct.setEnabled(True)
            self.ginputAct.setEnabled(True)
            self.scaleAct.setEnabled(True)
            self.doneAct.setEnabled(True)
            
            #### NEED TO GET THIS TO OPEN IN 'DOCUMENTS' FOLDER
            self.updatePixmap()
            
    def updatePixmap(self):
        self.planPixmap = QPixmap(self.fileName)
        self.scene.clear()
        self.scene.addPixmap(self.planPixmap)
        self.view.fitInView(QRectF(self.planPixmap.rect()), mode=Qt.KeepAspectRatio)
        
    
    def saveAsPNGFile(self):
        pass
    
    
    
    def zoomIn(self):
        if self.ginputPermission:
            self.setGinput(False)
            
        self.view.scale(1.4, 1.4)
        return
        
    def zoomOut(self):
        if self.ginputPermission:
            self.setGinput(False)
            
        self.view.scale(0.6, 0.6)
        return
       
    def setGinput(self, permission):
        '''
        Method to change the ginputAct QIcon, and change 
        ginputPermission attribute to 'permission'
        Inputs
            permission : bool - what ginputPermission should be set to.
        '''
        print('changing ginputPermission to', permission)
        self.ginputPermission = permission
        if self.ginputPermission:
            self.ginputAct.setIcon(QIcon(os.getcwd() + '\\icon logos\\ginputOn.png'))
            self.selectSeatsAct.setText('Disable ginput')
        else:
            self.ginputAct.setIcon(QIcon(os.getcwd() + '\\icon logos\\ginput.png'))
            self.selectSeatsAct.setText('Enable ginput to select seats')
            
    def ginput(self):
        # if ginput isn't already enabled, allow it to be
        if not self.ginputPermission:
            self.setGinput(True)
        # if its already enabled, disable it
        else:
            self.setGinput(False)
            
    def undoSelection(self):
        itemToRemove = self.currentGraphicsEllipseItems.pop()
        self.scene.removeItem(itemToRemove)
        self.Xs.pop()
        self.Ys.pop()
        
    def clearSelections(self):
        ### ADD CAUTIONARY WINDOW TO STOP IF NOT WANTED
        self.scene.clear()
        self.scene.addPixmap(self.planPixmap)
        self.currentGraphicsEllipseItems = []
        self.Xs = []
        self.Ys = []
        
    @pyqtSlot(float, float)
    def recordCoord(self, x, y):
        self.Xs.append(x)
        self.Ys.append(y)
        circleRadius = 10 # plots from top left of circle, so adjustments made to plot centre from mouse tip
        ellipse = QtWidgets.QGraphicsEllipseItem(x-circleRadius/2, y-circleRadius/2, circleRadius, circleRadius)
        self.scene.addItem(ellipse)
        self.currentGraphicsEllipseItems.append(ellipse)

    def saveSeats(self):
        self.seatPixelCoords = np.zeros((len(self.currentGraphicsEllipseItems), 2))
        self.seatPixelCoords[:,0] = self.Xs
        self.seatPixelCoords[:,1] = self.Ys
        
        np.savetxt('seatPixelCoords.txt', self.seatPixelCoords)        
        self.selectedSeatCoords = jonsAllocator(self.seatPixelCoords)
        
        self.plotSocialDistancingCircles()
        
    def plotSocialDistancingCircles(self):
        circleRadius = 50 # THIS IS NOT TO SCALE!!!!
        for i in range(self.selectedSeatCoords.shape[0]):
            x = self.selectedSeatCoords[i,0]
            y = self.selectedSeatCoords[i, 1]
            self.scene.addEllipse(x-circleRadius/2, y-circleRadius/2, circleRadius, circleRadius, pen=QPen(QColor('red')))
        
 
app = None
def main():
    global app
    app = QtWidgets.QApplication(sys.argv)
    w = MyMainWindow()

    app.exec_()

if __name__ == '__main__':
    main()     