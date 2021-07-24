# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 21:26:28 2021

@author: henry
"""
import numpy as np
from scipy.spatial.distance import cdist

def eliminationAllocator(seatPixelCoords, kwargs, socialDistancingSeperation=2, magicScale=(300/2.54000508)):
    ''' 
    Jonathan Watkins' algorithm for seat allocation. Works by randomly eliminating the seats that 
    are the most 'violating' - i.e. that have the most overlap, until you are left with a seating
    plan with no overlaps.
    
    Inputs: 
        seatPixelCoords: numpy ndarray containing pixel coordinates of all seats selected.
                columns are X or Y coordinate, rows are different seats
        socialDistancingSeperation: float representing the required seperation between people in metres.
        magicScale: float indicating the pixel -> real life metre conversion. scale has
                units of pixels per real life metre.
        
    Outputs:
        fpoints: numpy ndarray containing pixel coordinates of optimal seat
    
    '''
    N = len(seatPixelCoords)
    rcut = socialDistancingSeperation * magicScale
    
    overlap = True
    cpoints = list(seatPixelCoords)
    seatIndices = [i for i in range(N)]
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

            seatIndices.pop(badp)
            cpoints.pop(badp)
    
    allocatedPositions = np.array(cpoints)
    
    seatsAllocatedIndices = seatIndices
    
    return seatsAllocatedIndices, seatPixelCoords


def additionAllocator(seatPixelCoords, kwargs, socialDistancingSeperation=2, magicScale=(300/2.54000508)):
    '''
    Translation of Richard Mason's SeatAllocation.m MATLAB function for seat allocation.\n
    Works by iteratively generating many seating plans by adding seats around an initial 'seed'.
    Stage One produces a 'good' seating solution, Stage Two takes this solution and uses the seats
    it allocates as the seeds for new seating plans. This process is repeated totalReRuns times.
    
    Inputs:
    ----------------------
    > seatPixelCoords: numpy ndarray of seat pixel positions\n
    > socialDistancingSeperation: float or int defining social distancing seperation in METRES. Defaults to 2m\n
    > magicScale: float defining the pixel space to real space conversiom, measured in pixels per real life metre\n
    THEN KWARGS CONTAINTS:
    > margin: float defining how much seat locations can vary from user's input. Default to 0.1m worth of deviation in any direction\n
            indicates how far (in metres) you are happy for your inputs to change positions during stage 1 (and 2) iterations.
    > stageOneLoops: int defines how many stage one iterations to perform\n
    > stageTwoLoops: int defines how many stage two iterations to perform\n
    > totalReRuns: int defining how many times to repeat stage 1 and stage 2.\n
    
    Returns:
    --------------------
    > seatsAllocatedBest: list of seat indices making up the optimal solution\n
    > positionsBest: array of optimal seat pixel positions.    
    '''
    margin = kwargs['margin']
    

    minSpacing = socialDistancingSeperation*magicScale
    totalNumReRuns = kwargs['totalReRuns']
    
    
    ## number of stage one iterations in a rerun
    n1 = kwargs['stageOneLoops']
    ## number of stage two iterations in a rerun
    n2 = kwargs['stageTwoLoops']
    
    # Array to store the number of seats allocated on a given stage 1 run
    L = np.zeros((n1, 1))
    ## max number of seats that can be allocated in a stage 1 rerun - will likely break before reaching K iterations
    K = 100 ##### maybe make this a fraction of total number of seats?
    ## max number of closest seat positions used
    p = 10

    numberAllocated = np.zeros(shape=(totalNumReRuns, 1))
    
    for reRun in np.arange(totalNumReRuns):

        ##### STAGE 1:
        for s in np.arange(n1):
            seeds = -1*np.ones((K, 1))
            numClosestPositions = np.random.randint(2, p+1)
            
            ## generate new seat coordinates, slightly displaced from original
            # with margin=0, seats are maximally displaced by about 5cm
            # increase margin to create positions that deviate further than this
#            X = seatPixelCoords + margin * (np.random.randn(seatPixelCoords.shape[0], seatPixelCoords.shape[1]))
            #                        \/ 5cm on png  \/ max of normal dist is approx 3, 1.4142 is equal root 2
            X = seatPixelCoords + (margin*magicScale/1.4142135623) * 1/3 * np.random.randn(seatPixelCoords.shape[0], seatPixelCoords.shape[1])

            ## distance matrix for the shifted seat coordinates
            D = cdist(X, X)
            # total number of seats in hall/selected
            m = D.shape[0]
            ## set the self distance i.e. diagonal, to infinity
            D += np.diagflat(np.inf * np.ones((m,1)))
            ## first seat or 'seed' will be 
            seeds[0] = np.random.randint(m)
            
            ## Disallow any seats that are too close to the first seed
            D[:,(D[int(seeds[0]),:]<minSpacing)] = np.inf
            
            for c in np.arange(1, K):
                ## find the 'numberClosestPositions' number of seats to the previous seed
                I = np.argsort(D[int(seeds[c-1]),:])[:numClosestPositions]
                ## and index the distance matrix to get the distance from them to the previous seed
                d = D[int(seeds[c-1]),:][I]
                ## remove any seat indices where distance is infinite - i.e. is not allowed
                I = np.delete(I, np.argwhere(d==np.inf))
                ltemp = len(I)
                if ltemp == 0:
                    break # no seats were grabbed by argsort - i.e. room is full
                else:
                    # get rid of any infinite values
                    d = np.delete(d, np.argwhere(d==np.inf))
                    # pick one of the closest seats to be the next seed
#                    seeds[c] = np.random.choice(I, 1)

                    ## OR randomly choose a seat which is more likely to be the furthest:
                    seeds[c] = np.random.choice(I[d/max(d)>np.random.rand(1)],1)

                if (d == np.inf).all(): ## if the room is full
                    break
                # set previous seed/seat to infinity and disallow any neighbours.
                D[:,(D[int(seeds[c]),:]<minSpacing)] = np.inf
                D[:,int(seeds[c-1])] = np.inf
            
            L[s] = np.count_nonzero(seeds>0) # count number of seats allocated in that stage 1 iteration
            if L[s] == max(L): # if this is the best yet, save indices to seatsAllocatedInit
                seatsAllocatedInit = seeds[seeds>0]
                seatsAllocated = seeds[seeds>0]
                positionsInit = X # slightly altered seat positions
                positions = X
        
        maxFoundSoFar = max(L)
        
#        print(f'Max found after stage 1: {maxFoundSoFar}')
        L = np.zeros((n2, 1))
        
        
        #### STAGE 2:
        for s in np.arange(n2):
            count2 = maxFoundSoFar//5 + np.random.randint(maxFoundSoFar//4+1)
            numClosestPositions = np.random.randint(p+1)
           ## generate new seat coordinates, slightly displaced from original
           
           ## MARGIN MUST BE LESS THAN 1!!!!!!!!!!!!!!!!
#            X = positionsInit + margin**2 * (np.random.randn(seatPixelCoords.shape[0], seatPixelCoords.shape[1]))
            X = positionsInit + ((margin**1.5)*magicScale/1.4142135623) * 1/3 *  np.random.randn(seatPixelCoords.shape[0], seatPixelCoords.shape[1])

            ## Generate a random permutation of the previous best solution - essentially
            # shuffling. If c < count2 then this acts to place a new seed at any previous 
            # seat allocated in the best solution from stage 1 - not necessarily very close
            # to previous seed.
            aSeeds = np.random.choice(seatsAllocatedInit, len(seatsAllocatedInit), replace=False)
            seeds = -1*np.ones((K, 1), dtype=np.int64)
        
            D = cdist(X, X)
            m = D.shape[0]   
            D += np.diagflat(np.inf * np.ones((m,1)))
            seeds[0] = aSeeds[0] ## set first seed in stage2 rerun to random seat in previous best solution
            
            ## Set neighbours now disallowed to be inf far away
            D[:,(D[int(seeds[0]),:] < minSpacing)] = np.inf
            
            for c in np.arange(1, K):
                I = np.argsort(D[int(seeds[c-1]),:])[:numClosestPositions]
                d = D[int(seeds[c-1]),:][I]
                
                I = np.delete(I, np.argwhere(d==np.inf))
                ltemp = len(I)
                if ltemp == 0:
                    break
                else:
                    d = np.delete(d, np.argwhere(d==np.inf))
                    # pick one of the closest seats to be the next seed by default unless c<count2
#                    seeds[c] = np.random.choice(I, 1)
                    ## OR randomly choose a seat which is more likely to be the furthest:
                    seeds[c] = np.random.choice(I[d/max(d)>np.random.rand(1)],1)
                if c < count2:
#                    # if below this variable, set next seed to be a random previously allocated seat (from stage1)
#                    ## BUTTTT
#                    # Only if this aSeeds seat if futher than 2m away from original seat - not a problem if margin=0
                    if D[int(seeds[c-1]), int(aSeeds[c])] != np.inf:
                        seeds[c] = aSeeds[c]
#                        print('seat at aSeeds[c] disallowed by previous seats')

                    
                if (d==np.inf).all(): ## if the room is full
                    break
                # set this seed and all in perimeter to infinity
                D[:,(D[int(seeds[c]),:] < minSpacing)] = np.inf
                D[:,int(seeds[c-1])] = np.inf
        
            L[s] = np.count_nonzero(seeds>0) # count number of seats allocated

            if L[s] >= max(L):
                seatsAllocated = seeds[seeds>0]
                positions = X
        
        
        
        numberAllocated[reRun] = len(seatsAllocated)
        
        print(f'max found during rerun: {numberAllocated[reRun]}')
        if numberAllocated[reRun] == max(numberAllocated):
            seatsAllocatedBest = seatsAllocated
            positionsBest = positions
    
    
    print(f'max number of seat found after all reruns: {max(numberAllocated)}')
    seatsAllocatedBest = seatsAllocatedBest.astype(np.int64)
    
    ### change so it just returns
    
    return seatsAllocatedBest, positionsBest


def main():
    global seatsAllocatedBestBest, positionsBestBest, seatsAllocatedIndices, seatPositions, allocatedPositions
    from seatAllocationIO import loadSession
#    
    directory = r'C:\Users\henry\Documents\Seat Allocation Project Sum 2021\Seat Allocation Project\GUI\Seat Allocation Session Save Data\Full Seat Selection for Teaching & Learning Building - First Floor Plan'
    PNGFilePath, seatPixelCoords, magicScale = loadSession(directory)
    kwargs = {'margin':0.1, 'stageOneLoops':50, 'stageTwoLoops':150, 'totalReRuns':10}
    
    seatsAllocatedIndices, seatPositions = additionAllocator(seatPixelCoords, kwargs)
    
    np.savetxt('post allocation allocated indices.txt', seatsAllocatedIndices.tolist())
    np.savetxt('post allocation seat positions.txt', seatPositions)
    
#    overlapCount = 0
#    maxFound = 0
#    for _ in range(100):
##    eliminationAllocator(seatPixelCoords, magicScale)
#        seatsAllocated, positions = additionAllocator(seatPixelCoords, stageOneLoops=n1, stageTwoLoops=n2, margin=margin, totalReRuns=1)
#        allocatedPositions = np.take(positions, seatsAllocated, axis=0)
#        
#        
#        overlapCount += checkOverlap(allocatedPositions)
#        if len(seatsAllocated) > maxFound:
#            maxFound = len(seatsAllocated)
#            seatsAllocatedBestBest = seatsAllocated
#            positionsBestBest = positions
#
#    print(f'total number of overlaps with margin: {margin} over 100 reruns: {overlapCount} overlaps\nTotal seats allocated: {maxFound}')
    
#    seatsAllocatedIndices, seatPositions = eliminationAllocator(seatPixelCoords, socialDistancingSeperation=2, magicScale=magicScale)
    
def checkOverlap(allocatedPositions):
    allocatedDMatrix = cdist(allocatedPositions, allocatedPositions)
    m = len(seatsAllocatedIndices)
    allocatedDMatrix += np.diagflat(np.inf * np.ones((m,1)))
    
    
    print(f'overlap detected at: {np.argwhere(allocatedDMatrix < 2*300/2.54000508)}')
    
    return len(list(np.argwhere(allocatedDMatrix<2*300/2.54000508)))
    

    

    
if __name__ == '__main__':
    main()