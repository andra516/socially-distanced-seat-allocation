# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 16:17:23 2021
JonathanWatkins

@author: henry
"""
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QRect, QRectF, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPixmap, QBitmap, QIcon, QPen, QBrush, QColor, QKeySequence, QCursor
import sys
import os
#import time
import numpy as np
from seatAllocationAlgorithmJon import jonsAllocator

class Communication(QObject):
    
    ginputClickSignal = pyqtSignal(float, float) # will be used to tell MainWindow where seat positions are.
    moveClickSignal = pyqtSignal(int)

class MyGraphicsView(QtWidgets.QGraphicsView):
    
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.scene = parent.scene
        self.setScene(self.scene)
        
        self.communicator = Communication()
        self.communicator.ginputClickSignal.connect(parent.recordCoord)
        self.communicator.moveClickSignal.connect(parent.highlightMove)
    
    def mousePressEvent(self, event):
        print('mouse press event local pos', event.localPos().toPoint())
        if self.parent.mode == 0:
            pass
        elif self.parent.mode == 1:
            self.handleGinput(event)
        elif self.parent.mode == 2:
            self.handleMove(event)
        
    def handleGinput(self, event):
        scenePressPoint = self.mapToScene(event.localPos().toPoint()) # this is a QPointF
        x = scenePressPoint.x()
        y = scenePressPoint.y()
        self.communicator.ginputClickSignal.emit(x, y)
        
    def handleMove(self, event):
        seatPixelPositions = np.zeros((len(self.parent.Xs), 2))
        seatPixelPositions[:,0] = self.parent.Xs
        seatPixelPositions[:,1] = self.parent.Ys
        
#        print(seatPixelPositions)
        scenePressPoint = self.mapToScene(event.localPos().toPoint())
        clickPixelPosition = np.zeros(seatPixelPositions.shape)
        clickPixelPosition[:,0] = scenePressPoint.x()
        clickPixelPosition[:,1] = scenePressPoint.y()
        
        pixelDistArray = (abs(seatPixelPositions - clickPixelPosition)**2).sum(axis=1)
        print('min dist', np.min(pixelDistArray), 'circle #', np.argmin(pixelDistArray))
        print(self.parent.circleDiameter/2)
           
        try:
            index = int(np.argwhere(pixelDistArray < (self.parent.circleDiameter*1.2/2)**2)) # return the index of QGraphicsItem where click is at least within 1.2xradius
            self.communicator.moveClickSignal.emit(index)
        except Exception as e:
            print('Error, try again', e.__class__.__name__)
            print(e)
            ## probably due to circles overlapping.
            ## possible errors: 1) click was outside circle circumference: TypeError - only size-1 arrays can be converted to Python scalars
            ### 2) circles are overlapping and you click at intersection - again TypeError.
            pass
        
        
        

class MyMainWindow(QtWidgets.QMainWindow):
   
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle('Seat Allocation')
#        self.resize(1500, 800)
        self.setGeometry(200, 100, 1200, 700)
        self.show()
        
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
        
        self.openAct.setShortcut(QKeySequence('Ctrl+O'))
                
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
        self.movePointAct.triggered.connect(self.movePoint)
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
        self.zoomInAct = QtWidgets.QAction(QIcon(os.getcwd() + '\\images and icons\\zoomIn.png'), 'Zoom In')
        self.zoomOutAct = QtWidgets.QAction(QIcon(os.getcwd() + '\\images and icons\\zoomOut.png'), 'Zoom Out')
        self.ginputAct = QtWidgets.QAction(QIcon(os.getcwd() + '\\images and icons\\ginput.png'),'Ginput')     
        self.scaleAct = QtWidgets.QAction(QIcon(os.getcwd() + '\\images and icons\\scale.png'), 'Scale')
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
        self.initPixmap = QPixmap(os.getcwd() + '\\images and icons\\uob logo.png')
        self.scene.addPixmap(self.initPixmap)
        self.view.fitInView(QRectF(self.initPixmap.rect()), mode=Qt.KeepAspectRatio)
        
        self.Xs = []
        self.Ys = []
        self.currentGraphicsEllipseItems = []
        
        self.mode = None
        
        self.quickSetup() ## purely for testing to speed up process of opening file
        
    def quickSetup(self):
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
        
        print(os.getcwd() + '\\Room Plans\\Aston Webb C Block - Lower Ground Floor Plan.pdf-Page1.png')
        self.updatePixmap(os.getcwd() + '\\Room Plans\\Aston Webb C Block - Lower Ground Floor Plan.pdf-Page1.png')
        self.view.scale(10,10)
        
        
    def openPNGFile(self):

        fileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Image', os.getcwd(), "PNG Files (*.png)")[0]
        #### NEED TO GET THIS TO OPEN IN 'DOCUMENTS' FOLDER BY DEFAULT
        if fileName == '': ## incase filedialog was closed without choosing image
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
            
            self.updatePixmap(fileName)
            
    def updatePixmap(self, fileName):
        self.planPixmap = QPixmap(fileName)
        self.scene.clear()
        self.scene.addPixmap(self.planPixmap)
        self.view.fitInView(QRectF(self.planPixmap.rect()), mode=Qt.KeepAspectRatio)
    
    def setMode(self, mode_code):
        '''
        sets the mode the app is in
        0 - None
        1 - ginput
        2 - move
        3 -        
        '''        
        if mode_code == 0:
            # disable everything
            # ginput mode disable:
            print('changing to mode: None')
            self.ginputAct.setIcon(QIcon(os.getcwd() + '\\images and icons\\ginput.png'))
            self.selectSeatsAct.setText('Enable ginput to select seats')
            # disable move mode:
            self.movePointAct.setText('Enable move mode to adjust selections')
        elif mode_code == 1:
            # enable ginput and disable others
            print('changing to mode: Ginput')
            print('disabling move mode')
            # enable ginput
            self.ginputAct.setIcon(QIcon(os.getcwd() + '\\images and icons\\ginputOn.png'))
            self.selectSeatsAct.setText('Disable ginput')
            # disable move:
            self.movePointAct.setText('Enable move mode to adjust selections')  
        elif mode_code == 2:
            # enable move and disable others
            print('changing to mode: Move')
            print('disabling ginput mode')
            # disable ginput
            self.ginputAct.setIcon(QIcon(os.getcwd() + '\\images and icons\\ginput.png'))
            self.selectSeatsAct.setText('Enable ginput to select seats')
            # enable move
            self.movePointAct.setText('Disable move mode')
            
        self.mode = mode_code
    
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
            self.ginputAct.setIcon(QIcon(os.getcwd() + '\\images and icons\\ginputOn.png'))
            self.selectSeatsAct.setText('Disable ginput')
        else:
            self.ginputAct.setIcon(QIcon(os.getcwd() + '\\images and icons\\ginput.png'))
            self.selectSeatsAct.setText('Enable ginput to select seats')
            
    def setMove(self, permission):
        '''
        Similar to setGinput() - changes the movePermission to 'permission'
        '''
        print('changing movePermission to', permission)
        self.movePermission = permission
        if self.movePermission:
            self.movePointAct.setText('Disable move mode')
        else:
            self.movePointAct.setText('Enable move mode to adjust selections')  
  
    def zoomIn(self):
        if self.mode != 0:
            self.setMode(0)
        else:
            pass
            
        self.view.scale(1.4, 1.4)
        return
        
    def zoomOut(self):
        # if not in None mode, disable all
        if self.mode != 0:
            self.setMode(0)
        else:
            pass
            
        self.view.scale(0.6, 0.6)
        return

    def ginput(self):
        # if its already enabled, disable
        if self.mode == 1:
            self.setMode(0)
        else:         # if in any other mode is enabled, set to ginput mode
            self.setMode(1)
            
    def movePoint(self):
        # if already enabled, disable
        if self.mode == 2:
            self.setMode(0)
        else:       # if any other mode is enabled, set to move mode
            self.setMode(2)
        
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
        self.circleDiameter = 10 # plots from top left of circle, so adjustments made to plot centre from mouse tip
        ellipse = QtWidgets.QGraphicsEllipseItem(x-self.circleDiameter/2, y-self.circleDiameter/2, self.circleDiameter, self.circleDiameter)
        ellipse.setPen(QPen(QColor('#1d59af')))                    
        self.scene.addItem(ellipse)
        self.currentGraphicsEllipseItems.append(ellipse)
        
    @pyqtSlot(int)
    def highlightMove(self, index):
        highlightedGraphicsEllipseItem = self.currentGraphicsEllipseItems[index]
        highlightedGraphicsEllipseItem.setBrush(QBrush(QColor('#ee2622')))
        
                                                        

    def saveSeats(self):
        self.seatPixelCoords = np.zeros((len(self.currentGraphicsEllipseItems), 2))
        self.seatPixelCoords[:,0] = self.Xs
        self.seatPixelCoords[:,1] = self.Ys
        
        np.savetxt('seatPixelCoords.txt', self.seatPixelCoords)        
        self.selectedSeatCoords = jonsAllocator(self.seatPixelCoords)
        
        self.plotSocialDistancingCircles()
        
    def plotSocialDistancingCircles(self):
        socialCircleRadius = 50 # THIS IS NOT TO SCALE!!!!
        for i in range(self.selectedSeatCoords.shape[0]):
            x = self.selectedSeatCoords[i,0]
            y = self.selectedSeatCoords[i, 1]
            self.scene.addEllipse(x-socialCircleRadius/2, y-socialCircleRadius/2, socialCircleRadius, socialCircleRadius, pen=QPen(QColor('red')))
            
    def saveAsPNGFile(self):
        pass
           
 
app = None
def main():
    global app
    app = QtWidgets.QApplication(sys.argv)
    w = MyMainWindow()

    app.exec_()

if __name__ == '__main__':
    main()     