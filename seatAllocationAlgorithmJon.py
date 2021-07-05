# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 21:26:28 2021

@author: henry
"""
import numpy as np

def jonsAllocator(points):
    ''' 
    Jon's seat allocation algorithm.
    
    Inputs: 
        points: numpy ndarray containing pixel coordinates of all seats selected.
                columns are X or Y coordinate, rows are different seats
        ***scale: yet to be implemented
        
    Outputs:
        fpoints: numpy ndarray containing pixel coordinates of optimal seat
    
    '''

    N = len(points)
    metres = 78.4
    rcut = metres*1.5  # 76 pixels per 1m
    
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
    pass
    
if __name__ == '__main__':
    main()