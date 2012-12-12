'''
Created on Nov 30, 2012

@author: yangfei
'''

from __future__ import division
import sys
import copy
from random import shuffle
from kdtree import KDTree

DBSCAN_NOISETYPE = 99
KDTREE_DELTA = 40
KDTREE_INIT = 40

class kmeans(object):
    def __init__(self, k, pointlist):
        self.k = k
        self.points = pointlist
        
    def kmeansClusterWithRecord(self, recordList):
        centrePoints = [None] * self.k

        self.randomCreate(centrePoints)
        
        recordList[:] = []
        tempList = []
        for point in self.points:
            tempList.append(point.type)
        recordList.append(tempList)
            
        self.partition(centrePoints)
        self.resetCentre(centrePoints)
        lastCriterion = self.calcCriterion(centrePoints)
        counts = 1
        
        times = 0
        while(True):
            
            tempList = []
            for point in self.points:
                tempList.append(point.type)
            recordList.append(tempList)
            
            self.partition(centrePoints)
            self.resetCentre(centrePoints)
            criterion = self.calcCriterion(centrePoints)
            if abs(criterion-lastCriterion) < 0.1 :
                times += 1
                if times >= 2:
                    break
            else:
                times = 0
            lastCriterion = criterion
            counts += 1
        print counts, ' times iteration.'
            
    # generate random central points      
    def randomCreate(self, centrePoints):
        templist = [i for i in range(len(self.points))]
        shuffle(templist)
        for i in range(0, self.k):
            centrePoints[i] = copy.deepcopy(self.points[templist[i]])
            centrePoints[i].type = i
            self.points[templist[i]].type = i
    
    # an iterative division based on central points
    def partition(self, centrePoints):
        for point in self.points:
            index = -1
            minDist = 0.0 + sys.maxint
            for i in range(len(centrePoints)):
                dist = point.distance(centrePoints[i])
                if dist < minDist:
                    index = i
                    minDist = dist
            point.type = centrePoints[index].type
    
    # reset central points
    def resetCentre(self, centrePoints):
        centreIndex = [0]*len(centrePoints)
        typecounts = [0]*len(centrePoints)
        for i in range(len(centrePoints)):
            centreIndex[centrePoints[i].type] = i
            centrePoints[i].coor_reset()
        for point in self.points:
            centrePoints[centreIndex[point.type]].point_add(point)
            typecounts[point.type] += 1
        #print typecounts
        for centrePoint in centrePoints:
            centrePoint.point_mean(typecounts[centrePoint.type])
    
    # calculate square error
    def calcCriterion(self, centrePoints):
        criterion = 0.0
        centreIndex = [0]*len(centrePoints)
        for i in range(len(centrePoints)):
            centreIndex[centrePoints[i].type] = i
        for point in self.points:
            criterion += (point.distance(centrePoints[centreIndex[point.type]])) ** 2
        return criterion    
        
    # print method
    def printResult(self):
        for point in self.points:
            point.print_coor()
            print
  
class dbscan(object):
    global DBSCAN_NOISETYPE
    
    def __init__(self, eps, MinPts, pointlist):
        self.eps = eps
        self.MinPts = MinPts
        self.points = pointlist
        self.unvisited = [i for i in range(len(pointlist))]
        self.kdtree = KDTree.construct_from_data(self.formatpoints())
        self.pointidmap = {}
        for point in pointlist:
            self.pointidmap[tuple(point.coordinates)] = point.id
        
    def dbscanCluster(self):
        ClusterType = -1
        for unid in self.unvisited:
            self.points[unid].visited = True
            self.unvisited.remove(unid)
            NeighborPts = self.regionQuery(self.points[unid])
            if len(NeighborPts) < self.MinPts:
                self.points[unid].type = DBSCAN_NOISETYPE
            else:
                ClusterType += 1
                self.expandCluster(self.points[unid], NeighborPts, ClusterType)
                
    def expandCluster(self, P, NeighborPts, ClusterType):
        P.type = ClusterType
        self.visitNeighbor(NeighborPts, ClusterType)
    
    def visitNeighbor(self, NeighborPts, ClusterType):
        continue_recursion = False
        for pid in NeighborPts:
            if self.points[pid].type == -1:
                self.points[pid].type = ClusterType
            if not self.points[pid].visited:
                self.points[pid].visited = True
                self.unvisited.remove(pid)
                NeighborPts2 = self.regionQuery(self.points[pid])           
                # NeighborPts joined with NeighborPts2
                if len(NeighborPts2) >= self.MinPts:
                    NeighborPts = list(set(NeighborPts) | set(NeighborPts2))
                    continue_recursion = True
                    #break
        if continue_recursion:
            self.visitNeighbor(NeighborPts, ClusterType) 
                             
    # return all points within P's eps-neighborhood
    def regionQuery(self, P):
        '''
        retplist=[]
        for point in self.points:
            if point.distance(P) <= self.eps:
                retplist.append(point.id)
        return retplist
        '''
        return self.kdRadiusQuery(P)
    
    def kdRadiusQuery(self, P):
        global KDTREE_DELTA
        global KDTREE_INIT
        querynum = KDTREE_DELTA
        retplist = []
        while True:
            nearest = self.kdtree.query(query_point=P.coordinates, t=querynum)
            for i in range(len(nearest)-KDTREE_DELTA, len(nearest)):
                pid = self.pointidmap[tuple(nearest[i])]
                if P.distance(self.points[pid]) < self.eps:
                    retplist.append(pid)
                else:
                    return retplist
            querynum += KDTREE_DELTA
        
    # print method
    def printResult(self):
        for point in self.points:
            point.print_coor()
            print
            
    # generate point with format of (x,y,z,...)
    def formatpoints(self):
        ret = []
        for point in self.points:
            ret.append(point.coordinates)
        return ret
            
class point():
    def __init__(self, pid, dimension, coordinatelist):
        self.type = -1
        self.visited = False
        self.id = pid
        self.dim = dimension
        self.coordinates = [0] * dimension
        for i in range(0, min(dimension, len(coordinatelist))):
            self.coordinates[i] = (float)(coordinatelist[i])
    
    def print_coor(self):
        print 'pointid ', self.id, ' dimension ',self.dim,'; type ', self.type, '; coordinates ',
        for coor in self.coordinates:
            print str(coor)+' ',
    
    def distance(self, ano_point):
        dist = 0
        for i in range(0, min(self.dim, ano_point.dim)):
            dist += (self.coordinates[i] - ano_point.coordinates[i])**2
        if self.dim > ano_point.dim:
            for i in range(ano_point.dim, self.dim):
                dist += self.coordinates[i]**2
        return dist**0.5
    
    def coor_reset(self):
        self.coordinates = [0] * len(self.coordinates)
        
    def point_add(self, newPoint):
        for i in range(len(self.coordinates)):
            self.coordinates[i] += newPoint.coordinates[i]
            
    def point_mean(self, num):
        for i in range(len(self.coordinates)):
            self.coordinates[i] /= num 
        
    def equal(self, ano_point):
        retbool = True
        for i in range(len(self.coordinates)):
            if self.coordinates[i] != ano_point.coordinates[i]:
                retbool = False
                break
        return retbool