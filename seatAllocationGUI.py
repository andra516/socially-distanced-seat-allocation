# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 16:17:23 2021
## saveAndThreadDev

@author: henry
"""
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QRect, QRectF, QObject, pyqtSignal, pyqtSlot, QThreadPool, QRunnable
from PyQt5.QtGui import QPixmap, QBitmap, QIcon, QPen, QBrush, QColor, QKeySequence, QCursor, QPainter
import sys
import os
#import time
import numpy as np
from seatAllocationNewSessionHandler import OpenNewSession
from seatAllocationRunHandler import DoneAndRunHandler
import seatAllocationIO


class Communication(QObject):
    
    ginputClickSignal = pyqtSignal(float, float) # will be used to tell MainWindow where seat positions are.

class Worker(QRunnable):
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        
    @pyqtSlot()
    def run(self):
        sceneRect = self.parent.scene.sceneRect()
        planPixmap = QPixmap(sceneRect.width(), sceneRect.height())
        painter = QPainter(planPixmap)
        self.parent.scene.render(painter, sceneRect)
        planPNGFilePath = self.parent.saveDirectory + os.sep + f'Socially Distanced ({self.parent.socialDistancingSeperation}m) Seating Plan.png'
        planPixmap.save(planPNGFilePath, 'PNG')
        

class MyGraphicsView(QtWidgets.QGraphicsView):
    
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setAcceptDrops(True)
#        self.setAcceptHoverEvents(True)
        self.setScene(self.parent.scene)
        
        self.communicator = Communication()
        self.communicator.ginputClickSignal.connect(parent.recordCoord)
    
    def mousePressEvent(self, event):
#        print('mouse press event local pos', event.localPos().toPoint())
        if self.parent.mode == 0:
            pass
        elif self.parent.mode == 1:
            self.handleGinput(event)
        # elif self.parent.mode == 2:
        #     self.handleRemove(event)
        elif self.parent.mode == 3:
            self.handleAddAllocation(event)
        
        
    def handleGinput(self, event):
        scenePressPoint = self.mapToScene(event.localPos().toPoint()) # this is a QPointF
        x = scenePressPoint.x()
        y = scenePressPoint.y()
        self.communicator.ginputClickSignal.emit(x, y)
        
    # def handleRemove(self, event):
    #     pass
    

    def handleAddAllocation(self, event):
        print('adding seat')
        scenePressPoint = self.mapToScene(event.localPos().toPoint())
        print(type(scenePressPoint))
        x = 0
        y = 0
        
        allocatedSeatHighlight = QtWidgets.QGraphicsEllipseItem(x-self.parent.circleDiameter/2, y-self.parent.circleDiameter/2, self.parent.circleDiameter, self.parent.circleDiameter)
        allocatedSeatHighlight.setPen(self.parent.seatPen)
        allocatedSeatHighlight.setBrush(self.parent.opaqueHighlightBrush)
        
        socialCircle = QtWidgets.QGraphicsEllipseItem(x-self.parent.socialCircleDiameter/2, y-self.parent.socialCircleDiameter/2, self.parent.socialCircleDiameter, self.parent.socialCircleDiameter)
        socialCircle.setPen(self.parent.socialDistancePen)
        
        groupIdx = max(self.parent.currentAllocatedSeatGroups.keys())+1
        allocatedSeatGroup = AllocatedSeatItemGroup(self.parent, groupIdx)
        allocatedSeatGroup.addToGroup(allocatedSeatHighlight)
        allocatedSeatGroup.addToGroup(socialCircle)
        
        allocatedSeatGroup.setPos(scenePressPoint)
        
        self.parent.currentAllocatedSeatGroups[groupIdx] = allocatedSeatGroup
        self.parent.currentAllocatedSeatPositions[groupIdx] = np.array([scenePressPoint.x(), scenePressPoint.y()])
        
        self.parent.scene.addItem(allocatedSeatGroup)
        
        self.parent.statusBarModeDetailsLabel.setText(f'{len(self.parent.currentAllocatedSeatGroups.keys())} seats allocated out of {len(self.parent.Xs)}')
        
        # self.parent.checkValid()
        
        
class AllocatedSeatItemGroup(QtWidgets.QGraphicsItemGroup):
    
    def __init__(self, parent, idx):
        super().__init__()
        self.idx = idx
        print(self.idx)
        self.parent = parent
        self.dragMode = False

    def mousePressEvent(self, event):
        if self.parent.mode == 2:
            self.deleteAllocation()
            pass
        else:
            if event.button() == Qt.LeftButton:
                self.dragMode = True
                self.setCursor(QCursor(Qt.CrossCursor))

    def mouseReleaseEvent(self, event):
        if self.dragMode:
            self.dragMode = False
            self.setCursor(QCursor(Qt.ArrowCursor))
            self.update()
        else:
            pass
            
    def mouseMoveEvent(self, event):
        if self.dragMode:
            self.setPos(event.lastScenePos())
            # self.parent.checkValid()
        else:
            pass
        
    def deleteAllocation(self):
        print(self.idx)
        self.parent.currentAllocatedSeatGroups.pop(self.idx)
        self.parent.currentAllocatedSeatPositions.pop(self.idx)
        self.parent.scene.removeItem(self)
        self.parent.statusBarModeDetailsLabel.setText(f'{len(self.parent.currentAllocatedSeatGroups.keys())} seats allocated out of {len(self.parent.Xs)}')

class MyMainWindow(QtWidgets.QMainWindow):
   
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle('Seat Allocation')
        self.setWindowIcon(QIcon(os.getcwd()+os.sep+'images and icon'+os.sep+'init screen.png'))
        
        self.setGeometry(200, 100, 1200, 700)
        self.show()
        
        self.setUpUi()
        
    def setUpUi(self):
        
        self.centralWidget = QtWidgets.QWidget()
        self.mainLayout = QtWidgets.QVBoxLayout()
        
        ### STATUS BAR
        self.statusBar = QtWidgets.QStatusBar()
        self.statusBarModeLabel = QtWidgets.QLabel('Load or Start an Allocation Session')
        self.statusBarModeDetailsLabel = QtWidgets.QLabel()
        self.statusBarOverlapLabel = QtWidgets.QLabel()
        self.statusBar.addPermanentWidget(self.statusBarModeLabel)
        self.statusBar.addWidget(self.statusBarModeDetailsLabel)
        self.statusBar.addWidget(self.statusBarOverlapLabel)
    
        self.setStatusBar(self.statusBar)
        

        ### MENU BAR        
        self.fileMenu = self.menuBar().addMenu('File')
        self.ginputMenu = self.menuBar().addMenu('Ginput')
        self.allocationMenu = self.menuBar().addMenu('Allocation')
        
        ### FILE MENU BAR ACTIONS
        self.newSessionAct = QtWidgets.QAction('Start new allocation session')
        self.loadSessionAct = QtWidgets.QAction('Load previous session') # pixel coordinates from previously found maps
        self.saveSessionAct = QtWidgets.QAction('Save current session')
        self.savePlanAct = QtWidgets.QAction('Save seating plan as .png')
        
        # initially all disabled
        self.loadSessionAct.setEnabled(True)
        self.saveSessionAct.setEnabled(False)
        self.savePlanAct.setEnabled(False)
    
        self.newSessionAct.triggered.connect(self.startNewSession)
        self.loadSessionAct.triggered.connect(self.loadSession)
        self.saveSessionAct.triggered.connect(self.saveSession)
        self.savePlanAct.triggered.connect(self.saveSeatingPlan)
        
        self.newSessionAct.setShortcut(QKeySequence('Ctrl+N'))
        self.loadSessionAct.setShortcut(QKeySequence('Ctrl+O'))
        self.saveSessionAct.setShortcut(QKeySequence('Ctrl+S'))
                
        self.fileMenu.addAction(self.newSessionAct)
        self.fileMenu.addAction(self.loadSessionAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.saveSessionAct)
        self.fileMenu.addAction(self.savePlanAct)
    
        
        ### GINPUT MENU BAR ACTIONS
        self.ginputAct = QtWidgets.QAction('Enable ginput to select seats')
        self.undoSelectAct = QtWidgets.QAction('Undo last selection')
        self.clearAllAct = QtWidgets.QAction('Clear all selections')
        ### initially all disabled
        self.ginputAct.setEnabled(False)
        self.undoSelectAct.setEnabled(False)
        self.clearAllAct.setEnabled(False)
        
        self.ginputAct.triggered.connect(self.ginput)
        self.undoSelectAct.triggered.connect(self.undoSelection)
        self.clearAllAct.triggered.connect(self.clearSelections)
        
        self.ginputAct.setShortcut(QKeySequence('Ctrl+G'))
        self.undoSelectAct.setShortcut(QKeySequence('Ctrl+Z'))
              
        self.ginputMenu.addAction(self.ginputAct)
        self.ginputMenu.addAction(self.undoSelectAct)
        self.ginputMenu.addAction(self.clearAllAct)
        
        ### ALLOCATION MENU BAR ACTIONS
        self.doneAndRunAct = QtWidgets.QAction('Done and run allocator')
        self.addAllocationAct = QtWidgets.QAction('Add an allocation')
        self.removeAllocationAct = QtWidgets.QAction('Remove allocations')
        self.clearAllocationsAct = QtWidgets.QAction('Clear all allocations')
        
        self.doneAndRunAct.setEnabled(False)
        self.addAllocationAct.setEnabled(False)
        self.removeAllocationAct.setEnabled(False)
        self.clearAllocationsAct.setEnabled(False)
        
        self.doneAndRunAct.triggered.connect(self.doneAndRun)
        self.addAllocationAct.triggered.connect(self.addAllocation)
        self.removeAllocationAct.triggered.connect(self.removeAllocation)    
        self.clearAllocationsAct.triggered.connect(self.clearSelections)
        
        self.addAllocationAct.setShortcut(QKeySequence('Ctrl+A'))
        self.removeAllocationAct.setShortcut(QKeySequence('Ctrl+D'))
        
        self.allocationMenu.addAction(self.doneAndRunAct)
        self.allocationMenu.addSeparator()
        self.allocationMenu.addAction(self.addAllocationAct)
        self.allocationMenu.addAction(self.removeAllocationAct)
        self.allocationMenu.addSeparator()
        self.allocationMenu.addAction(self.clearAllocationsAct)


        #### GRAPHICSVIEW WIDGET
        self.scene = QtWidgets.QGraphicsScene()
        self.view = MyGraphicsView(parent=self)
        self.view.setAlignment(Qt.AlignCenter | Qt.AlignLeft)

        #### TOOLBAR LAYOUT AND BUTTONS
        self.toolbarLayout = QtWidgets.QHBoxLayout()
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setOrientation(Qt.Horizontal)
        self.zoomInAct = QtWidgets.QAction(QIcon(os.getcwd() + os.sep+ 'images and icons' + os.sep+ 'zoomIn.png'), 'Zoom In')
        self.zoomOutAct = QtWidgets.QAction(QIcon(os.getcwd() + os.sep+ 'images and icons' + os.sep+ 'zoomOut.png'), 'Zoom Out')
        self.ginputBtnAct = QtWidgets.QAction(QIcon(os.getcwd()+ os.sep+ 'images and icons' + os.sep+ 'ginput.png'),'Ginput')
        self.removeAllocationBtnAct = QtWidgets.QAction(QIcon(os.getcwd()+ os.sep+ 'images and icons' + os.sep+ 'removeAllocationIcon.png'), 'Remove Allocations')
        self.addAllocationBtnAct = QtWidgets.QAction(QIcon(os.getcwd()+ os.sep+ 'images and icons' + os.sep+ 'addAllocationIcon.png'), 'Add Allocations')
        self.doneBtnAct = QtWidgets.QAction('Done\nand Run')
        
        self.zoomInAct.triggered.connect(self.zoomIn)
        self.zoomOutAct.triggered.connect(self.zoomOut)
        self.ginputBtnAct.triggered.connect(self.ginput)
        self.removeAllocationBtnAct.triggered.connect(self.removeAllocation)
        self.addAllocationBtnAct.triggered.connect(self.addAllocation)
        self.doneBtnAct.triggered.connect(self.doneAndRun)
        
        self.zoomInAct.setShortcut(QKeySequence.ZoomIn)
        self.zoomOutAct.setShortcut(QKeySequence.ZoomOut)
        
        self.ginputBtnAct.setEnabled(False)
        self.zoomInAct.setEnabled(False)
        self.zoomOutAct.setEnabled(False)
        self.ginputBtnAct.setEnabled(False)
        self.removeAllocationBtnAct.setEnabled(False)
        self.addAllocationBtnAct.setEnabled(False)
        self.doneBtnAct.setEnabled(False)
        
        self.toolbar.addAction(self.zoomInAct)
        self.toolbar.addAction(self.zoomOutAct)
        self.toolbar.addAction(self.ginputBtnAct)
        self.toolbar.addAction(self.addAllocationBtnAct)
        self.toolbar.addAction(self.removeAllocationBtnAct)
        self.toolbar.addAction(self.doneBtnAct)

        self.toolbarLayout.addWidget(self.toolbar)
        self.toolbarLayout.setAlignment(Qt.AlignRight)
               
        
        ### ADD WIDGETS AND LAYOUT TO MAIN LAYOUT
        self.mainLayout.addLayout(self.toolbarLayout)
        self.mainLayout.addWidget(self.view)
        
        self.centralWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.centralWidget)
        
        
        #### SET INITIAL PIXMAP AND ADD TO SCENE        
        self.initPixmap = QPixmap(os.getcwd()+ os.sep+ 'images and icons' + os.sep+ 'init screen.png')
        self.scene.addPixmap(self.initPixmap)
        self.view.fitInView(QRectF(self.initPixmap.rect()), mode=Qt.KeepAspectRatio)
        self.view.scale(1.2, 1.2)
        
        ## initialise pens and brushes:
        self.opaqueHighlightBrush = QBrush(QColor(238,38,34,255))
        self.transparentHighlightBrush = QBrush(QColor(238,38,34,0))
        self.seatPen = QPen(QColor('#1d59af'))
        self.seatPen.setWidth(3)
        self.socialDistancePen = QPen(QColor('#ee2622'))
        self.socialDistancePen.setWidth(3)
        
        self.mode = 0
        self.moveHighlightIndex = None # varibale that holds index of item currently highlighted for moving
        self.currentSeatGraphicsItems = []
        self.currentAllocatedSeatGroups = {}
        self.currentAllocatedSeatPositions = {}
        
        self.threadpool = QThreadPool()
        
        # self.quickSetup() ## purely for testing to speed up process of opening file
        
    def resetSessionVariables(self):
        '''
        resets seat coordinate variables,
        resets GraphicsItem list
        clears the GraphicsScene
        resets the mode to None: 0
        '''
        self.Xs = []
        self.Ys = []
        self.currentSeatGraphicsItems = []
        self.currentAllocatedSeatGroups = {}
        self.currentAllocatedSeatPositions = {}
        
        self.seatsAllocatedIndices = []
        self.seatPositions = np.array([[]])
#        self.scene.clear()
        self.setMode(0)
        self.saveSessionAct.setEnabled(False)
        
    def enableActions(self, mode):
        if mode == 1:
            self.loadSessionAct.setEnabled(True)
    #        self.saveSessionAct.setEnabled(True)
            # ginput actions
            self.ginputAct.setEnabled(True)
            self.undoSelectAct.setEnabled(True)
            self.clearAllAct.setEnabled(True)
            # allocation
            self.doneAndRunAct.setEnabled(True)
            # toolbar actions
            self.ginputBtnAct.setEnabled(True)
            self.zoomInAct.setEnabled(True)
            self.zoomOutAct.setEnabled(True)
            self.ginputBtnAct.setEnabled(True)
            self.doneBtnAct.setEnabled(True)
            
        elif mode == 0:
            self.loadSessionAct.setEnabled(False)
    #        self.saveSessionAct.setEnabled(False)
            # ginput actions
            self.ginputAct.setEnabled(False)
            self.undoSelectAct.setEnabled(False)
            self.clearAllAct.setEnabled(False)
            self.doneAndRunAct.setEnabled(False)
            # toolbar actions
            self.ginputBtnAct.setEnabled(False)
            self.zoomInAct.setEnabled(False)
            self.zoomOutAct.setEnabled(False)
            self.ginputBtnAct.setEnabled(False)
            self.doneBtnAct.setEnabled(False)
    
    def quickSetup(self):
        '''
        Function to be called when testing to setup the Ui in desired format straight away
        can be customised.
        '''
        
        self.enableActions(mode=1)
        
        self.pngPath, seatPixelCoords, self.magicScale = seatAllocationIO.loadSession(r'C:\Users\henry\Documents\Seat Allocation Project Sum 2021\Seat Allocation Project\GUI\Seat Allocation Session Save Data\Full Seat Selection for Teaching & Learning Building - First Floor Plan')
#        print(seatPixelCoords, self.pngPath, self.magicScale)
        ## Now the PNG and seat coord files have been loaded, set the pixmap and draw coords
        self.updatePixmap(self.pngPath)
        self.view.scale(4,4)
        
        self.seatPositions = np.loadtxt('post allocation seat positions.txt')
        self.seatsAllocatedIndices = np.loadtxt('post allocation allocated indices.txt')
        self.seatsAllocatedIndices = self.seatsAllocatedIndices.astype(np.int64)
        self.socialDistancingSeperation = 2
        self.circleDiameter = 10
        
        self.plotSocialDistancingCircles()
        
             
    def startNewSession(self):
        self.newSessionWindow = OpenNewSession(self)
        
        self.newSessionWindow.show()
        ## updatePixmap() and enableActions() called and self.pngPath assigned in seatAllocationNewSessionHandler when convertPDF() is called.

            
    def updatePixmap(self, pngPath):
        self.planPixmap = QPixmap(pngPath)
        self.resetSessionVariables()
        self.scene.clear()
        self.scene.addPixmap(self.planPixmap)
        self.view.fitInView(QRectF(self.planPixmap.rect()), mode=Qt.KeepAspectRatio)
        self.view.scale(1.2, 1.2)
        self.statusBarModeLabel.setText('Ginput Mode: Select seat positions')
        self.statusBarModeDetailsLabel.setText(f'{len(self.Xs)} seats selected')
    
    def setMode(self, mode_code):
        '''
        sets the mode the app is in
        0 - None
        1 - Ginput Mode
        2 - Post Allocation Mode
        etc.
        '''        
        if mode_code == 0:
            # disable everything
            # ginput mode disable:
            print('changing to mode: None')
            self.ginputBtnAct.setIcon(QIcon(os.getcwd() + os.sep + 'images and icons' + os.sep+ 'ginput.png'))
            self.ginputAct.setText('Enable ginput to select seats')  
            self.addAllocationBtnAct.setIcon(QIcon(os.getcwd() + os.sep + 'images and icons' + os.sep+ 'addAllocationIcon.png'))
            self.removeAllocationBtnAct.setIcon(QIcon(os.getcwd() + os.sep + 'images and icons' + os.sep+ 'removeAllocationIcon.png'))
        elif mode_code == 1:
            # enable ginput and disable others
            print('changing to mode: Ginput')
            # enable ginput
            self.ginputBtnAct.setIcon(QIcon(os.getcwd() + os.sep +  'images and icons' + os.sep + 'ginputOn.png'))
            self.ginputAct.setText('Disable ginput')
        elif mode_code == 2:
            # enable move and disable others
            print('changing to mode: Remove seats and allocations')
            # disable ginput
            self.ginputBtnAct.setIcon(QIcon(os.getcwd() + os.sep + 'images and icons' + os.sep + 'ginput.png'))
            self.ginputAct.setText('Enable ginput to select seats')
            self.addAllocationBtnAct.setIcon(QIcon(os.getcwd() + os.sep + 'images and icons' + os.sep+ 'addAllocationIcon.png'))
            self.removeAllocationBtnAct.setIcon(QIcon(os.getcwd() + os.sep + 'images and icons' + os.sep+ 'removeAllocationIconOn.png'))
            self.removeAllocationAct.setText('Disable remove allocations')
            self.addAllocationAct.setText('Add an allocation')
            
        elif mode_code == 3:
            print('changin to mode: Add Allocations')
            self.addAllocationAct.setText('Disable adding allocation')
            self.removeAllocationAct.setText('Remove allocations')
            
            self.addAllocationBtnAct.setIcon(QIcon(os.getcwd() + os.sep + 'images and icons' + os.sep+ 'addAllocationIconOn.png'))
            self.removeAllocationBtnAct.setIcon(QIcon(os.getcwd() + os.sep + 'images and icons' + os.sep+ 'removeAllocationIcon.png'))
        
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
        
    def undoSelection(self):
        try:
            itemToRemove = self.currentSeatGraphicsItems.pop()
            self.scene.removeItem(itemToRemove)
            self.Xs.pop()
            self.Ys.pop()
        except IndexError:
            pass
        if len(self.Xs)==0:
            self.saveSessionAct.setEnabled(False) # disables saving if no seats selected.
            self.savePlanAct.setEnabled(False)
            self.doneAndRunAct.setEnabled(False)
            self.doneBtnAct.setEnabled(False)
            self.undoSelectAct.setEnabled(False)
            self.clearAllAct.setEnabled(False)
            self.setMode(0)
        
        self.statusBarModeDetailsLabel.setText(f'{len(self.Xs)} seats selected')

    def clearSelections(self):
        ### ADD CAUTIONARY WINDOW TO STOP IF NOT WANTED
        self.setMode(0)
        self.resetSessionVariables()
        self.scene.clear()
        self.scene.addPixmap(self.planPixmap)

        self.saveSessionAct.setEnabled(False)
        self.savePlanAct.setEnabled(False)
        self.undoSelectAct.setEnabled(False)
        self.clearAllAct.setEnabled(False)
        self.ginputBtnAct.setEnabled(True)
        self.doneAndRunAct.setEnabled(False)
        self.doneBtnAct.setEnabled(False)
        
        self.statusBarModeDetailsLabel.setText(f'{len(self.Xs)} seats selected')
        
    @pyqtSlot(float, float)
    def recordCoord(self, x, y):
        self.Xs.append(x)
        self.Ys.append(y)       
        self.circleDiameter = 10 # plots from top left of circle, so adjustments made to plot centre from mouse tip
        ellipse = QtWidgets.QGraphicsEllipseItem(x-self.circleDiameter/2, y-self.circleDiameter/2, self.circleDiameter, self.circleDiameter)
        ellipse.setPen(self.seatPen)
        ellipse.setBrush(self.transparentHighlightBrush)        
        
        self.scene.addItem(ellipse)
        self.currentSeatGraphicsItems.append(ellipse)
        
        ### update number of seats selected
        self.statusBarModeDetailsLabel.setText(f'{len(self.Xs)} seats selected')
        
        if len(self.Xs) > 0:
            self.saveSessionAct.setEnabled(True)
            self.doneAndRunAct.setEnabled(True)
            self.doneBtnAct.setEnabled(True)
            self.undoSelectAct.setEnabled(True)
            self.clearAllAct.setEnabled(True)
        
                                  
    def doneAndRun(self):
        self.seatPixelCoords = np.zeros((len(self.Xs), 2))
        self.seatPixelCoords[:,0] = self.Xs
        self.seatPixelCoords[:,1] = self.Ys
        
        self.saveSession()
        self.seatPositions = np.array([[]])
        self.seatsAllocatedIndices = []
        
        self.enableActions(0)
        self.newSessionAct.setEnabled(False)
        self.saveSessionAct.setEnabled(False)
        self.zoomInAct.setEnabled(True)
        self.zoomOutAct.setEnabled(True)
        
        self.doneAndRunWindow = DoneAndRunHandler(parent=self)
        ## self.seatsAllocated and self.seatPositions assigned within worker in seatAllocationRunHandler
        self.doneAndRunWindow.show()   
        
    @pyqtSlot()
    def plotSocialDistancingCircles(self):
        '''
        Replots all selected seats, highlighting and plotting social distancing circles around allocated seats on the GraphicsScene
        '''
        
        self.enableActions(mode=1)
        self.newSessionAct.setEnabled(True)
        self.ginputBtnAct.setEnabled(False)
        self.ginputAct.setEnabled(False)
        self.undoSelectAct.setEnabled(False)
        self.clearAllAct.setEnabled(False)
        self.addAllocationAct.setEnabled(True)
        self.removeAllocationAct.setEnabled(True)
        self.addAllocationBtnAct.setEnabled(True)
        self.removeAllocationBtnAct.setEnabled(True)
        self.clearAllocationsAct.setEnabled(True)
        self.saveSessionAct.setEnabled(True)
        self.savePlanAct.setEnabled(True)
        
        self.setMode(0)
        
        self.socialCircleDiameter = self.socialDistancingSeperation * self.magicScale
        
        ## GETS RID OF ANY PREVIOUS SEAT SELECTIONS AND ALLOCATION GROUPS:
        if len(self.currentAllocatedSeatGroups)>0:
            for allocatedSeatGroupValue in self.currentAllocatedSeatGroups.values():
                self.scene.removeItem(allocatedSeatGroupValue)
            self.currentAllocatedSeatGroups = {}
            self.currentAllocatedSeatPositions = {}
                
        for seatItem in self.currentSeatGraphicsItems:
            self.scene.removeItem(seatItem)
        self.currentSeatGraphicsItems = []

        ## PLOT HIGHLIGHTS AND SOCIAL CIRCLES ON ALLOCATED SEATS:
        self.allocatedPositions = np.take(self.seatPositions, self.seatsAllocatedIndices, axis=0)
        
        for idx, positions in enumerate(self.allocatedPositions):
            x = 0
            y = 0
            ### create an allocatedSeatGroup instance for each allocated seat
            
            allocatedSeatHighlight = QtWidgets.QGraphicsEllipseItem(x-self.circleDiameter/2, y-self.circleDiameter/2, self.circleDiameter, self.circleDiameter)
            allocatedSeatHighlight.setPen(self.seatPen)
            allocatedSeatHighlight.setBrush(self.opaqueHighlightBrush)
            
            socialCircle = QtWidgets.QGraphicsEllipseItem(x-self.socialCircleDiameter/2, y-self.socialCircleDiameter/2, self.socialCircleDiameter, self.socialCircleDiameter)
            socialCircle.setPen(self.socialDistancePen)
            
            allocatedSeatGroup = AllocatedSeatItemGroup(self, idx)
            allocatedSeatGroup.addToGroup(allocatedSeatHighlight)
            allocatedSeatGroup.addToGroup(socialCircle)
            
            allocatedSeatGroup.setPos(positions[0], positions[1])
            
            self.currentAllocatedSeatGroups[idx] = allocatedSeatGroup
            self.currentAllocatedSeatPositions[idx] = np.array([positions[0], positions[1]])
            
            self.scene.addItem(allocatedSeatGroup)
        
        self.checkValid()
        print(self.magicScale)
        
        # print(self.currentAllocatedSeatPositions)
        
        self.statusBarModeLabel.setText('Post-Allocation Mode: Add, Remove and Adjust Allocations')
        self.statusBarModeDetailsLabel.setText(f'{len(self.currentAllocatedSeatGroups.keys())} seats allocated out of {len(self.Xs)}')
        
    def checkValid(self):
        overlaps = []
        print('running checkValid')
        for seat1idx, pos1 in enumerate(self.currentAllocatedSeatPositions.values()):
            for seat2idx, pos2 in enumerate(self.currentAllocatedSeatPositions.values()):
                if seat1idx == seat2idx:
                    continue
                dist = np.linalg.norm(pos1-pos2)
                if dist < self.socialDistancingSeperation*self.magicScale:
                    overlaps.append([seat1idx, seat2idx])
                    # self.statusBarOverlapLabel.setText(f'seats {seat1idx} and {seat2idx} are less than {self.socialDistancingSeperation}m apart, sep: {dist/self.magicScale} m')
                    print(f'seats {seat1idx} and {seat2idx} are less than {self.socialDistancingSeperation}m apart, sep: {dist/self.magicScale} m')
        print(overlaps)
        
    def removeAllocation(self):
        if self.mode != 2:
            self.setMode(2)
        else:
            self.setMode(0)
            self.removeAllocationAct.setText('Remove allocations')
            self.removeAllocationBtnAct.setIcon(QIcon(os.getcwd() + os.sep + 'images and icons' + os.sep+ 'removeAllocationIcon.png'))
        
    def addAllocation(self):
        if self.mode != 3:
            self.setMode(3)
        else:
            self.setMode(0)
            self.addAllocationAct.setText('Add an allocation')
            self.addAllocationBtnAct.setIcon(QIcon(os.getcwd() + os.sep + 'images and icons' + os.sep+ 'addAllocationIcon.png'))
    
    
    
    def loadSession(self):
        ### when loading in a previous file, need the magic scale pre-calculated - needs to go into json file
        ### need to work out how to save and read from json files
        
        dialog = QtWidgets.QFileDialog()
        dialog.setDirectory(os.getcwd())
        dialog.setWindowTitle('Load in a previous session')
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        if dialog.exec_():
            self.saveDirectory = dialog.selectedFiles()[0].replace('/', os.sep)

            try:
                self.pngPath, seatPixelCoords, self.magicScale = seatAllocationIO.loadSession(self.saveDirectory)
#                print(seatPixelCoords, self.pngPath, self.magicScale)
                ## Now the PNG and seat coord files have been loaded, set the pixmap and draw coords
                self.updatePixmap(self.pngPath)
                for seat in seatPixelCoords:
                    self.recordCoord(seat[0], seat[1])

                self.enableActions(mode=1)   
                
            except Exception as e:
                print(e.__class__.__name__)
                print(e)
                print('Folder didn\'t contain what was expected')
        else:
            pass

    def saveSession(self):
        self.setMode(0)
        seatAllocationIO.saveSession(self.saveDirectory, self.Xs, self.Ys)

    def saveSeatingPlan(self):
        savePlanWorker = Worker(self)
        
        self.threadpool.start(savePlanWorker)
        
        
    
 
app = None
def main():
    global app
    app = QtWidgets.QApplication(sys.argv)
    w = MyMainWindow()

    app.exec_()

if __name__ == '__main__':
    main()     