'''
Created on Dec 1, 2012

@author: yangfei
'''

from cluster import point, kmeans, dbscan

__kmeansk__ = [7, 6]
'''
epsSelect = [1.8, 0.26]
MinPtsSelect = [11, 17]
'''
epsSelect = [1.8, 0.30]
MinPtsSelect = [11, 18]
clustertypes = ['kmeans', 'dbscan']

class processtool:
    
    @staticmethod
    def read_points_fromfile(fname):
        retlist=[]
        pruningDic = {}
        pruningTimes = 80
        pruningRGB = 230
        try:
            fin = open(fname, 'r')
            for line in fin.readlines():
                strlist = line.split()
                if len(strlist) == 2:
                    retlist.append((strlist[0], strlist[1]))
                elif len(strlist) == 5:
                    if int(strlist[2])<pruningRGB and int(strlist[3])<pruningRGB and int(strlist[4])<pruningRGB:
                        x = round(float(strlist[0])/pruningTimes, 1)
                        y = round(float(strlist[1])/pruningTimes, 1)
                        if not pruningDic.has_key((str(x),str(y))):
                            pruningDic[(str(x),str(y))] = 1
                            retlist.append((x,y))                
        except Exception,ex:
            print Exception,':',ex
        finally:
            fin.close()   
        return retlist
    
    @staticmethod
    def generate_plist(coorlist):
        retlist=[]
        num = 0
        for coors in coorlist:
            retlist.append(point(num, len(coors), coors))
            num += 1
        return retlist
    
    '''
    read points from a file with path filepath
    generate points and do clustering
    then return the cluster result
    '''
    @staticmethod
    def generate_clusteredpoints(filepath, methodType, dataIndex, recordList):
        oripoints = processtool.read_points_fromfile(filepath)
        points = processtool.generate_plist(oripoints)
        if methodType == 'kmeans':
            kmeansfactory = kmeans(__kmeansk__[dataIndex], points)
            kmeansfactory.kmeansClusterWithRecord(recordList)
            #kmeansfactory.printResult()
            return kmeansfactory.points
        elif methodType == 'dbscan':
            #dbscanfactory = dbscan(1.1, 5, points)
            dbscanfactory = dbscan(epsSelect[dataIndex], MinPtsSelect[dataIndex], points)
            dbscanfactory.dbscanCluster()
            #dbscanfactory.printResult()
            return dbscanfactory.points
    