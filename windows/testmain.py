'''
Created on Nov 30, 2012

@author: yangfei
'''
from cluster import kmeans
from process import processtool

def kmeansTest():
    oriplist = processtool.read_points_fromfile('./Aggregation.txt')

    kmeansfactory = kmeans(7, processtool.generate_plist(oriplist))
    kmeansfactory.kmeansCluster()
    kmeansfactory.printResult()

def dbscanTest():
    points = processtool.generate_clusteredpoints('./Aggregation.txt', 'dbscan')
    print len(points)

def thtest():
    retlist = processtool.read_points_fromfile('./datath.txt')
    print len(retlist)
    
if __name__ == '__main__':
    print 'test testmain.'
    #kmeansTest()
    #dbscanTest()
    #thtest()