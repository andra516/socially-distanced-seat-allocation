# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 12:46:32 2021

@author: henry

module containing functions that will handle file I/O when saving/loading seat
allocation sessions
"""

import numpy as np
import os
import json

def savePlanDetails(saveDirectory, ppi, pdfScale, magicScale):
    '''
    Saves a .json file containing details of the plan including:
        - ppi: int, the pixels per inch for the PNG file of plan converted from original PDF
        - pdfScale: str,  defining the scale of the plan drawing
        - magicScale: float, defines the pixel to real life metre conversion (measured in pixels per real life metre)
    '''
    
    planDetails = {"planDetails":{"ppi": ppi, 
                                  "pdfScale": pdfScale, 
                                  "magicScale" : magicScale}
                    }
    
    planDetailsPath = saveDirectory + os.sep + 'planDetails.json'
    
    with open(planDetailsPath, 'w') as f:
        json.dump(planDetails, f)
        
    pass
    


def saveSession(saveDirectory, Xs, Ys):
    '''
    Function that saves the progress made in selecting seats in a given room plan.
    
    - Saves a numpy array of seat coordinates (in pixels on the .png) to a .txt file named : 'Seat Allocation Save Data.txt'
    - Eventually will also save indices of selected seats which have been chosen for the allocation to a seperate .txt file
    
    (or everything is saved to a .json file)
    
    Inputs:\n
        > directory, str of directory path that data should save to.\n
        > Xs - list of floats of all X coordinates (in pixel space) of selected seats to be saved.\n
        > Ys - list of floats of all Y coords.\n
    
    '''     
    ## SAVE SELECTED SEAT PIXEL COORDINATES
    seatPixelCoords = np.zeros(shape=(len(Xs),2))
    seatPixelCoords[:,0] = Xs
    seatPixelCoords[:,1] = Ys

    seatCoordFilePath = saveDirectory + os.sep + 'Seat Allocation Save Data.txt'
    np.savetxt(seatCoordFilePath, seatPixelCoords)

    # (eventually) SAVE ALLOCATED SEAT COORDS/INDICES and replace with .json file

def loadSession(directory):
    '''
    Function that loads the seatPixelCoords, the room plan .png (and eventually allocated seats)
    from given directory.
    
    Inputs:
        > directory: file path for directory previous session was saved in.
        
    Returns:
        if folder contains what is expected:
        > PNGFilePath: file path of .png of room plan
        > seatPixelCoords: numpy ndarray of seat coordinates.
        > magicScale: pixel to real space conversion in pixels per real life metre
        if not:
        returns None indicating there was an error
    '''
    ### CHECK EXACTLY ONE .PNG AND ONE .TXT FILE - png will be image of lecture hall
    # txt will be seatPixelCoords
    numTXTs = 0
    numPNGs = 0
    numPDFs = 0
    numJSONs = 0
    numElse = 0
    for file in os.listdir(directory):
        if os.path.splitext(file)[1] == '.txt':
            numTXTs += 1
            sessionDataFile = file
        elif os.path.splitext(file)[1] == '.png':
            numPNGs += 1
            PNGFile = file
        elif os.path.splitext(file)[1] == '.pdf':
            numPDFs += 1
            PDFFile = file
        elif os.path.splitext(file)[1] == '.json':
            numJSONs += 1
            JSONFile = file
        else:
            numElse += 1
        
            
    if numTXTs != 1 or numPNGs != 1 or numPDFs != 1 or numJSONs != 1 or numElse != 0:
        print('File should only contain exactly one .png, one .pdf, one .txt and one .json file')
        return None
    
    ## find PNGFilePath
    sessionSaveDataPath = directory + os.sep + sessionDataFile
    PNGFilePath = directory + os.sep + PNGFile
    ## load the seat coords
    seatPixelCoords = np.loadtxt(sessionSaveDataPath)
    ## load the magicScale
    with open((directory+os.sep+JSONFile), 'r') as f:
        planDetails = json.load(f)['planDetails']
    
    magicScale = planDetails['magicScale']
    
    return (PNGFilePath, seatPixelCoords, magicScale)




if __name__ == '__main__':
    directory = r'C:\Users\henry\Documents\Seat Allocation Project Sum 2021\Seat Allocation Project\GUI\Seat Allocation Session Save Data'
#    emptyFolder = r'C:\Users\henry\Documents\Seat Allocation Project Sum 2021\Seat Allocation Project\GUI\Seat Allocation Session Save Data\New Folder'

#    PNGFilePath = r'C:\Users\henry\Documents\Seat Allocation Project Sum 2021\Seat Allocation Project\GUI\Seat Allocation Session Save Data\Full Seat Selection for Aston Webb Lower GFloor\Aston Webb C Block - Lower Ground Floor Plan.png'
    Xs = [10, 20, 30, 40, 50]
    Ys = [5, 10, 15, 20, 25]
    
    
    d = saveSession(directory, Xs, Ys)
    