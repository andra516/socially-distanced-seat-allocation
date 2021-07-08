# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 16:17:23 2021
## saveAndThreadDev

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
import seatAllocationIO

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
        self.communicator.moveClickSignal.connect(parent.setMoveHighlight)
    
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
        '''
        currently built to return the index of the ellipse item that a click is within
        want it to emit a signal with either: index of graphics item click was within
        or None if the click was outside - returning None is a bit tricky - need to look up how you
        emit multiple datatypes
        '''
        
        seatPixelPositions = np.zeros((len(self.parent.Xs), 2))
        seatPixelPositions[:,0] = self.parent.Xs
        seatPixelPositions[:,1] = self.parent.Ys
        
#        print(seatPixelPositions)
        scenePressPoint = self.mapToScene(event.localPos().toPoint())
        clickPixelPosition = np.zeros(seatPixelPositions.shape)
        clickPixelPosition[:,0] = scenePressPoint.x()
        clickPixelPosition[:,1] = scenePressPoint.y()
        
        pixelDistArray = (abs(seatPixelPositions - clickPixelPosition)**2).sum(axis=1)
        
        indexArray = np.argwhere(pixelDistArray < (self.parent.circleDiameter*1.5/2)**2)
        
        if indexArray.shape != (0, 1):
            print(indexArray.item())
            self.communicator.moveClickSignal.emit(indexArray.item())
        else:
            self.communicator.moveClickSignal.emit()
        
#        try:
#            index = np.argwhere(pixelDistArray < (self.parent.circleDiameter*1.5/2)**2)
#
#
#        except ValueError:
#            print(np.argwhere(pixelDistArray < (self.parent.circleDiameter*1.5/2)**2).shape)
#        
##        
#        try:
#            index = int(np.argwhere(pixelDistArray < (self.parent.circleDiameter*1.2/2)**2)) # return the index of QGraphicsItem where click is at least within 1.2xradius
#            self.communicator.moveClickSignal.emit(index)
#        except Exception as e:
#            print('Error, try again', e.__class__.__name__)
#            print(e)
#            ## probably due to circles overlapping.
#            ## possible errors: 1) click was outside circle circumference: TypeError - only size-1 arrays can be converted to Python scalars
#            ### 2) circles are overlapping and you click at intersection - again TypeError.
#            pass
#        
        
        

class MyMainWindow(QtWidgets.QMainWindow):
   
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle('Seat Allocation')
        
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
        self.loadSessionAct = QtWidgets.QAction('Load previous session data') # pixel coordinates from previously found maps
        self.saveAct = QtWidgets.QAction('Save current seat allocation session')
        
        # initially all disabled
        self.loadSessionAct.setEnabled(True)
        self.saveAct.setEnabled(False)
    
        self.openAct.triggered.connect(self.openPNGFile)
        self.loadSessionAct.triggered.connect(self.loadSession)
        self.saveAct.triggered.connect(self.saveSession)
        
        self.openAct.setShortcut(QKeySequence('Ctrl+O'))
                
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.loadSessionAct)
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
        self.doneAndRunAct.triggered.connect(self.doneAndRun)
        
        self.selectSeatsAct.setShortcut(QKeySequence('Ctrl+G'))
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
        self.doneAct.triggered.connect(self.doneAndRun)
        
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
        
    
        ## initialise brushes:
        self.opaqueHighlightBrush = QBrush(QColor(238,38,34,255))
        self.transparentHighlightBrush = QBrush(QColor(238,38,34,0))
        
        self.mode = 0
        self.moveHighlightIndex = None # varibale that holds index of item currently highlighted for moving
        
        
#        self.quickSetup() ## purely for testing to speed up process of opening file
        
    def resetSessionVariables(self):
        '''
        resets seat coordinate variables,
        resets GraphicsItem list
        clears the GraphicsScene
        resets the mode to None: 0
        '''
        self.Xs = []
        self.Ys = []
        self.currentGraphicsEllipseItems = []
#        self.scene.clear()
        self.setMode(0)
        self.saveAct.setEnabled(False)
        
        
    def enableActions(self):
        self.loadSessionAct.setEnabled(True)
#        self.saveAct.setEnabled(True)
        # ginput actions
        self.selectSeatsAct.setEnabled(True)
        self.undoSelectAct.setEnabled(True)
#        self.movePointAct.setEnabled(True)
        self.clearAllAct.setEnabled(True)
        self.doneAndRunAct.setEnabled(True)
        # toolbar actions
        self.ginputAct.setEnabled(True)
        self.zoomInAct.setEnabled(True)
        self.zoomOutAct.setEnabled(True)
        self.ginputAct.setEnabled(True)
        self.scaleAct.setEnabled(True)
        self.doneAct.setEnabled(True)
    
    def quickSetup(self):
        '''
        Function to be called when testing to setup the Ui in desired format straight away
        can be customised.
        '''
        
        self.enableActions()
#        self.loadSessionAct.setEnabled(True)
##        self.saveAct.setEnabled(True)
#        # ginput actions
#        self.selectSeatsAct.setEnabled(True)
#        self.undoSelectAct.setEnabled(True)
##        self.movePointAct.setEnabled(True)
#        self.clearAllAct.setEnabled(True)
#        self.doneAndRunAct.setEnabled(True)
#        # toolbar actions
#        self.ginputAct.setEnabled(True)
#        self.zoomInAct.setEnabled(True)
#        self.zoomOutAct.setEnabled(True)
#        self.ginputAct.setEnabled(True)
#        self.scaleAct.setEnabled(True)
#        self.doneAct.setEnabled(True)
        
        self.fileName = os.getcwd() + '\\Room Plans\\Aston Webb C Block - Lower Ground Floor Plan.png'
#        print(self.fileName)
        self.updatePixmap(self.fileName)
        self.view.scale(11.5,11.5)
             
    def openPNGFile(self):

        self.fileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Image', os.getcwd(), "PNG Files (*.png)")[0]
        #### NEED TO GET THIS TO OPEN IN 'DOCUMENTS' FOLDER BY DEFAULT
        if self.fileName == '': ## incase filedialog was closed without choosing image
            pass
        else:
            ### ENSURE ALL ACTIONS ARE ENABLED
            self.enableActions()
#            # file actions
#            
#            self.loadSessionAct.setEnabled(True)
##            self.saveAct.setEnabled(True)
#            # ginput actions
#            self.selectSeatsAct.setEnabled(True)
#            self.undoSelectAct.setEnabled(True)
##            self.movePointAct.setEnabled(True)
#            self.clearAllAct.setEnabled(True)
#            self.doneAndRunAct.setEnabled(True)
#            # toolbar actions
#            self.ginputAct.setEnabled(True)
#            self.zoomInAct.setEnabled(True)
#            self.zoomOutAct.setEnabled(True)
#            self.ginputAct.setEnabled(True)
#            self.scaleAct.setEnabled(True)
#            self.doneAct.setEnabled(True)
            
            
            self.updatePixmap(self.fileName)
            
    def updatePixmap(self, fileName):
        self.planPixmap = QPixmap(fileName)
        self.resetSessionVariables()
        self.scene.clear()
        self.scene.addPixmap(self.planPixmap)
        self.view.fitInView(QRectF(self.planPixmap.rect()), mode=Qt.KeepAspectRatio)
        self.view.scale(1.2, 1.2)
    
    def setMode(self, mode_code):
        '''
        sets the mode the app is in
        0 - None
        1 - Ginput Mode
        2 - Move Mode
        etc.
        '''        
        if mode_code == 0:
            # disable everything
            # ginput mode disable:
            print('changing to mode: None')
            self.ginputAct.setIcon(QIcon(os.getcwd() + '\\images and icons\\ginput.png'))
            self.selectSeatsAct.setText('Enable ginput to select seats')
            # disable move mode and setBrushes:
            self.movePointAct.setText('Enable move mode to adjust selections')
        elif mode_code == 1:
            # enable ginput and disable others
            print('changing to mode: Ginput')
            # enable ginput
            self.ginputAct.setIcon(QIcon(os.getcwd() + '\\images and icons\\ginputOn.png'))
            self.selectSeatsAct.setText('Disable ginput')
            # disable move:
            self.movePointAct.setText('Enable move mode to adjust selections')  
        elif mode_code == 2:
            # enable move and disable others
            print('changing to mode: Move')
            # disable ginput
            self.ginputAct.setIcon(QIcon(os.getcwd() + '\\images and icons\\ginput.png'))
            self.selectSeatsAct.setText('Enable ginput to select seats')
            # enable move
            self.movePointAct.setText('Disable move mode')
        
        self.mode = mode_code
  
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
        try:
            itemToRemove = self.currentGraphicsEllipseItems.pop()
            self.scene.removeItem(itemToRemove)
        except IndexError:
            pass
        self.Xs.pop()
        self.Ys.pop()
        if len(self.Xs)==0:
            self.saveAct.setEnabled(False) # disables saving if no seats selected.
            self.setMode(0)

    def clearSelections(self):
        ### ADD CAUTIONARY WINDOW TO STOP IF NOT WANTED
        self.setMode(0)
        self.resetSessionVariables()
        self.scene.clear()
        self.scene.addPixmap(self.planPixmap)

        self.saveAct.setEnabled(False)
        
    @pyqtSlot(float, float)
    def recordCoord(self, x, y):
        self.Xs.append(x)
        self.Ys.append(y)       
        self.circleDiameter = 10 # plots from top left of circle, so adjustments made to plot centre from mouse tip
        ellipse = QtWidgets.QGraphicsEllipseItem(x-self.circleDiameter/2, y-self.circleDiameter/2, self.circleDiameter, self.circleDiameter)
        ellipse.setPen(QPen(QColor('#1d59af')))
        ellipse.setBrush(self.transparentHighlightBrush)        
        
        self.scene.addItem(ellipse)
        self.currentGraphicsEllipseItems.append(ellipse)
        if len(self.Xs) > 0:
            self.saveAct.setEnabled(True)
        
    @pyqtSlot(int)
    def setMoveHighlight(self, index):
        highlightedGraphicsEllipseItem = self.currentGraphicsEllipseItems[index]

#        if self.moveHighlightIndex is None:
            # if no seat is currently highlighted
        highlightedGraphicsEllipseItem.setBrush(self.opaqueHighlightBrush)     
#        elif self.moveHighlightIndex == index:
            # if seat already highlighted is clicked, 
#            highlightedGraphicsEllipseItem.setBrush(self.transparentHighlightBrush)
        
            
            ## if no seat is highlighted
                        
#        else:
#            pass
                                                     

    def doneAndRun(self):
        self.setMode(0)
        self.seatPixelCoords = np.zeros((len(self.currentGraphicsEllipseItems), 2))
        self.seatPixelCoords[:,0] = self.Xs
        self.seatPixelCoords[:,1] = self.Ys
        
        # replace this with saveSession eventually
        self.saveSession()
        self.selectedSeatCoords = jonsAllocator(self.seatPixelCoords)
        
        self.plotSocialDistancingCircles()
        
    def plotSocialDistancingCircles(self):
        socialCircleRadius = 50 # THIS IS NOT TO SCALE!!!!
        for i in range(self.selectedSeatCoords.shape[0]):
            x = self.selectedSeatCoords[i,0]
            y = self.selectedSeatCoords[i, 1]
            self.scene.addEllipse(x-socialCircleRadius/2, y-socialCircleRadius/2, socialCircleRadius, socialCircleRadius, pen=QPen(QColor('red')))
        pass
    
    def loadSession(self):
        dialog = QtWidgets.QFileDialog()
        dialog.setDirectory(os.getcwd())
        dialog.setWindowTitle('Load in a previous session folder')
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        if dialog.exec_():
            directory = dialog.selectedFiles()[0].replace('/', os.sep)
            
#            print('directory at loadSession', directory)
            self.fileName, seatPixelCoords = seatAllocationIO.loadSession(directory)
            ## Now the PNG and seat coord files have been loaded, set the pixmap and draw coords
            self.updatePixmap(self.fileName)
#            print('fileName at loadSession' , self.fileName)
        
            for seat in seatPixelCoords:
                self.recordCoord(seat[0], seat[1])
        
            self.enableActions()    
        else:
            pass

        
        
    def saveSession(self):
        self.setMode(0)
        dialog = QtWidgets.QFileDialog()
        dialog.setWindowTitle('Save Session Data to new Directory')
        dialog.setDirectory(os.getcwd())
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        if dialog.exec_():
            directory = dialog.selectedFiles()[0].replace('/', os.sep)
            ## automatically comes with directory seperators as forward slashes.
            seatAllocationIO.saveSession(directory, self.fileName, self.Xs, self.Ys)
        else:
            pass
        
    
 
app = None
def main():
    global app
    app = QtWidgets.QApplication(sys.argv)
    w = MyMainWindow()

    app.exec_()

if __name__ == '__main__':
    main()     