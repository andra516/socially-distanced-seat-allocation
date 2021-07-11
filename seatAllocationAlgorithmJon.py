# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 21:26:28 2021

@author: henry
"""
import numpy as np

def jonsAllocator(points, scale):
    ''' 
    Jon's seat allocation algorithm.
    
    Inputs: 
        points: numpy ndarray containing pixel coordinates of all seats selected.
                columns are X or Y coordinate, rows are different seats
        scale: float indicating the pixel -> real life metre conversion. scale has
                units of pixels per real life metre.
        
    Outputs:
        fpoints: numpy ndarray containing pixel coordinates of optimal seat
    
    '''

    N = len(points)
    
    socialDistancingSeperation = 2 # measured in metres
    rcut = socialDistancingSeperation * scale
#    metres = 78.4
#    rcut = metres*1.5  # 76 pixels per 1m
    
    overlap = True
    cpoints = list(points)
    while overlap == True:
        print(len(cpoints))
        overlap = False
    
        N = len(cpoints)
        counts = np.zeros(N)
    
        for i in np.arange(N):
            for j in np.arange(N):
                if i == j:
                    continue
                a = cpoints[i]
                b = cpoints[j]
                dist = np.linalg.norm(a-b)
                if dist < rcut:
                    counts[i] += 1
                    overlap = True
        if overlap:
            print(counts)
            if N > 150:
                M = 40
            else:
                M = 3
            worstM = np.argpartition(counts, -M)[-M:]
            np.random.shuffle(worstM)
            badp = worstM[0]
            # else:
            #     badp = np.argmax(counts)
            cpoints.pop(badp)
    
    fpoints = np.array(cpoints)
    
    return fpoints

def main():
    points = np.loadtxt(r'C:\Users\henry\Documents\Seat Allocation Project Sum 2021\Seat Allocation Project\GUI\Seat Allocation Save Data.txt')
#    print(points)
    
    ppi = 300
    pdfScale = '1:100'
    scaleVals = pdfScale.split(sep=':')
    
    SCALE = int(scaleVals[0])/int(scaleVals[1]) * ppi * 100/2.54000508 # in pixels per real life metre
    print(SCALE)
    jonsAllocator(points, SCALE)
    
    
    
    
    
    
if __name__ == '__main__':
    main()