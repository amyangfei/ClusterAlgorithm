'''
Created on Dec 1, 2012

@author: yangfei
'''


import  wx
import  wx.lib.anchors as anchors
import  wx.lib.filebrowsebutton as filebrowse
import time
import os
from threading import Thread
import cluster
from cluster import point
from process import processtool

#----------------------------------------------------------------------

# Nifty little trick here; apply wx.NewId() to generate a series of
# IDs used later on in the app. 

[   ID_ANCHORSDEMOFRAMEHELPSTATICTEXT,
    ID_ANCHORSDEMOFRAMEHELPSTATICTEXT2,
    ID_ANCHORSDEMOFRAMEHELPSTATICTEXT3,
    ID_ANCHORSDEMOFRAMEHELPGAUGE,
    ID_ANCHORSDEMOFRAMEMAINPANEL, 
    ID_ANCHORSDEMOFRAMEBACKGROUNDPANEL,
    ID_ANCHORSDEMOFRAMECLEARBUTTON,
    ID_ANCHORSDEMOFRAMEBACKBUTTON,
    ID_ANCHORSDEMOFRAMEDRAWBUTTON,
    ID_ANCHORSDEMOFRAMEDRAWBUTTON2,
    ID_ANCHORSDEMOFRAMELASTBUTTON,
    ID_ANCHORSDEMOFRAME,
    ID_ANCHORSDEMOPROGRESSFRAME, 
    ID_ANCHORSDEMOFRAMELEFTCHECKBOX,
 ] = map(lambda _init_ctrls: wx.NewId(), range(14))

backgroundHeight = 500
multiplyBy = [17, 18]
pointSize = [3, 1]
colors=['RED','PINK','PURPLE','YELLOW','GREEN','CYAN','NAVY','BLUE','LIGHT MAGENTA','TURQUOISE','PINK','PURPLE','YELLOW','GREEN','CYAN','NAVY','BLUE','LIGHT MAGENTA','TURQUOISE','BLACK']

class AnchorsDemoFrame(wx.Frame):
    
    iterationRecords = []
    iterationNum = -1
    lastpoints = []
    dataFilePath = '.' + os.path.sep + 'Aggregation.txt'
    clusterType = 'kmeans'
    datafileMultiplyIndex = 0
    
    def __init__(self):
        wx.Frame.__init__(
            self, None, size=(900, 640), id=ID_ANCHORSDEMOFRAME, 
            title='DM Cluster', 
            name='AnchorsDemoFrame', 
            style = wx.MINIMIZE_BOX | wx.SYSTEM_MENU | \
            wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN, pos=(200, 60)
            )
        self.mainPanel = wx.Panel(
                            size=(900, 640), parent=self, 
                            id=ID_ANCHORSDEMOFRAMEMAINPANEL, name='panel1', 
                            style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN
                            | wx.FULL_REPAINT_ON_RESIZE, 
                            pos=(0, 0)
                            )
        self.mainPanel.SetAutoLayout(True)        
        
        self.fbbh = filebrowse.FileBrowseButton(
            self.mainPanel, -1, size=(300, 30), changeCallback = self.fbbhCallback, pos=(10,5)
            )
        
        clusterList = ['kmeans', 'dbscan']
        ch = wx.Choice(self.mainPanel, -1, (320, 7), choices = clusterList)
        ch.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.EvtChoice, ch)

        global backgroundHeight
        self.backgroundPanel = wx.Panel(
                                size=(884, 500), parent=self.mainPanel, 
                                id=ID_ANCHORSDEMOFRAMEBACKGROUNDPANEL, 
                                name='backgroundPanel', 
                                style=wx.SIMPLE_BORDER | wx.CLIP_CHILDREN, 
                                pos = (8, 40)
                                )

        self.backgroundPanel.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.backgroundPanel.SetConstraints(
            anchors.LayoutAnchors(self.backgroundPanel, True, True, True, True)
            )

        drawbutton = wx.Button(parent=self.mainPanel, size=(80, 22), label="Cluster", id=ID_ANCHORSDEMOFRAMEDRAWBUTTON)
        drawbutton.SetPosition((420, 10))
        self.Bind(
            wx.EVT_BUTTON, self.OnDrawButton, id=ID_ANCHORSDEMOFRAMEDRAWBUTTON
            )        
        
        lastbutton = wx.Button(parent=self.mainPanel, size=(80, 22), label="Last Result", id=ID_ANCHORSDEMOFRAMELASTBUTTON)
        lastbutton.SetPosition((510, 10))
        self.Bind(
            wx.EVT_BUTTON, self.OnLastButton, id=ID_ANCHORSDEMOFRAMELASTBUTTON
            )
        
        drawbutton2 = wx.Button(parent=self.mainPanel, size=(120, 22), label="Show Iteration", id=ID_ANCHORSDEMOFRAMEDRAWBUTTON2)
        drawbutton2.SetPosition((600, 10))
        self.Bind(
            wx.EVT_BUTTON, self.OnShowButton, id=ID_ANCHORSDEMOFRAMEDRAWBUTTON2
            )
        
        backButton = wx.Button(parent=self.mainPanel, size=(80, 22), label="Back Step", id=ID_ANCHORSDEMOFRAMEBACKBUTTON)
        backButton.SetPosition((730, 10))

        self.Bind(
            wx.EVT_BUTTON, self.OnBackButton, id=ID_ANCHORSDEMOFRAMEBACKBUTTON
            )
        
        clearButton = wx.Button(parent=self.mainPanel, size=(50, 22), label="Clear", id=ID_ANCHORSDEMOFRAMECLEARBUTTON)
        clearButton.SetPosition((830, 10))

        self.Bind(
            wx.EVT_BUTTON, self.OnclearButton, id=ID_ANCHORSDEMOFRAMECLEARBUTTON
            )

        self.helpStaticText = wx.StaticText(
                                label='Since DBSCAN-ALGORITHM doesn\'t have an iteration '+ 
                                'progress, only KMEANS is supported with iteration demonstrating. '
                                'Press button \"Show Iteration\" or \"back step\" and have a try. Enjoy it!', 
                                id=ID_ANCHORSDEMOFRAMEHELPSTATICTEXT, 
                                parent=self.mainPanel, name='helpStaticText', 
                                size=(600, 60), style=wx.ST_NO_AUTORESIZE, 
                                pos=(8, 534)
                                )
        self.helpStaticText.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, 'Courier New'))

        self.helpStaticText2 = wx.StaticText(
                                        label='Iteration times : not defined\nNow: havn\'t started', 
                                        id=ID_ANCHORSDEMOFRAMEHELPSTATICTEXT2, 
                                        parent=self.mainPanel, name='helpStaticText2', 
                                        size=(285, 60), style=wx.ST_NO_AUTORESIZE, 
                                        pos=(610, 534)
                                        )
        self.helpStaticText2.SetFont(wx.Font(11, wx.DECORATIVE, wx.ITALIC, wx.BOLD, False))
        self.helpStaticText2.SetForegroundColour('RED')
        
        #self.Bind(wx.EVT_SIZE, self.ReDrawDots)

    def fbbhCallback(self, evt):
        self.OnclearButton(None)
        fpath = evt.GetString()
        self.dataFilePath = fpath
        if fpath.split(os.path.sep)[-1] == 'datath.txt':
            self.datafileMultiplyIndex = 1
        else:
            self.datafileMultiplyIndex = 0
    
    def EvtChoice(self, event):
        print event.GetString()
        self.clusterType = event.GetString()
    
    def EvtRadioBox(self, event):
        self.clusterType = 'kmeans' if event.GetInt()==0 else 'dbscan'
        
    def ReDrawDots(self, event):
        #self.Update()
        
        #self.backgroundPanel.SetBackgroundColour(wx.Colour(255,255,255))
        #self.backgroundPanel.Update()
        self.Update()
        time.sleep(0.01)
        if len(self.lastpoints) <= 0:
            return
        dc = wx.ClientDC(self.backgroundPanel)
        dc.SetPen(wx.Pen("RED"))
        dc.SetBrush(wx.Brush("RED"))
        for point in self.lastpoints:
            colortype = point.type if point.type != cluster.DBSCAN_NOISETYPE else -1
            #dc.SetPen(wx.Pen(colors[colortype], 1))
            if self.datafileMultiplyIndex == 1:
                colortype = point.type if point.type<=11 else -1
                dc.SetPen(wx.Pen(colors[colortype]))
            else:
                dc.SetPen(wx.Pen('RED', 1, wx.SOLID))
            dc.SetBrush(wx.Brush(colors[colortype]))
            dc.DrawCircle(point.coordinates[0]*multiplyBy[self.datafileMultiplyIndex], \
                          backgroundHeight-point.coordinates[1]*multiplyBy[self.datafileMultiplyIndex], pointSize[self.datafileMultiplyIndex])
        print len(self.lastpoints)

    def OnShowButton(self, event):
        self.DrawFootprint(1)
    
    def OnBackButton(self, event):
        self.DrawFootprint(-1)
    
    def DrawFootprint(self, iterationDelta):
        if self.clusterType != 'kmeans':
            dlg = wx.MessageDialog(self, 'Since DBSCAN-ALGORITHM doesn\'t have an iteration '+ 
                                'progress, only KMEANS is supported with iteration demonstrating!',
                               'We feel Sorry for it',
                               wx.OK | wx.ICON_INFORMATION
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        self.iterationNum += iterationDelta
        if self.iterationNum >= len(self.iterationRecords):
            self.iterationNum = len(self.iterationRecords) - 1
        elif self.iterationNum < 0:
            self.iterationNum = 0
           
        dc = wx.ClientDC(self.backgroundPanel)
        dc.SetPen(wx.Pen("RED"))
        dc.SetBrush(wx.Brush("RED"))
        iternum = 0
        for pointtype in self.iterationRecords[self.iterationNum]:
            '''
            colortype = pointtype if pointtype != cluster.DBSCAN_NOISETYPE else -1
            '''
            if self.datafileMultiplyIndex == 1:
                colortype = pointtype if pointtype<=9 else -1
                dc.SetPen(wx.Pen(colors[colortype]))
            
            if pointtype == -1:
                dc.SetBrush(wx.Brush('WHITE'))
                dc.SetPen(wx.Pen('WHITE'))
            else:
                dc.SetBrush(wx.Brush(colors[pointtype]))
            dc.DrawCircle(self.lastpoints[iternum].coordinates[0]*multiplyBy[self.datafileMultiplyIndex], \
                          backgroundHeight-self.lastpoints[iternum].coordinates[1]*multiplyBy[self.datafileMultiplyIndex], pointSize[self.datafileMultiplyIndex])
            iternum += 1
        numIter = 'undefined' if self.iterationNum==-1 else str(self.iterationNum)
        if self.iterationNum == len(self.iterationRecords)-1:
            numIter += ' End of iteration'
        self.helpStaticText2.SetLabelText('Iteration times : '+str(len(self.iterationRecords)-1)+'\nNow: '+str(numIter))

    def OnclearButton(self, event):
        dc = wx.ClientDC(self.backgroundPanel)
        dc.SetPen(wx.Pen("WHITE"))
        dc.SetBrush(wx.Brush("WHITE"))
        dc.DrawRectangle(0, 0, self.backgroundPanel.GetSize()[0],self.backgroundPanel.GetSize()[1])
    
    def OnLastButton(self, event):
        self.ReDrawDots(event)
    
    def OnDrawButton(self, event):
        progress = progressThread()
        progress.start() 
        handle = handleThread(self, progress)
        handle.start()        
        '''
        self.lastpoints = processtool.generate_clusteredpoints(self.dataFilePath, self.clusterType, self.datafileMultiplyIndex, self.iterationRecords) 
            
        dc = wx.ClientDC(self.backgroundPanel)
        dc.SetPen(wx.Pen("RED"))
        dc.SetBrush(wx.Brush("RED"))
        for point in self.lastpoints:
            colortype = point.type if point.type != cluster.DBSCAN_NOISETYPE else -1
            if self.datafileMultiplyIndex == 1:
                colortype = point.type if point.type<=9 else -1
                dc.SetPen(wx.Pen(colors[colortype]))
            dc.SetBrush(wx.Brush(colors[colortype]))
            dc.DrawCircle(point.coordinates[0]*multiplyBy[self.datafileMultiplyIndex], \
                          backgroundHeight-point.coordinates[1]*multiplyBy[self.datafileMultiplyIndex], pointSize[self.datafileMultiplyIndex])
        
        self.iterationNum = -1
        self.helpStaticText2.SetLabelText('Iteration times : '+str(len(self.iterationRecords)-1)+'\nNow: '+str(len(self.iterationRecords)-1))
        '''
        #progress.Destroy()

class handleThread(Thread):
    def __init__(self, auiframe, ano_thread):
        Thread.__init__(self)
        self.auiframe = auiframe
        self.ano = ano_thread
        
    def run(self):
        self.auiframe.lastpoints = processtool.generate_clusteredpoints(self.auiframe.dataFilePath, self.auiframe.clusterType, self.auiframe.datafileMultiplyIndex, self.auiframe.iterationRecords) 
                    
        dc = wx.ClientDC(self.auiframe.backgroundPanel)
        dc.SetPen(wx.Pen("RED"))
        dc.SetBrush(wx.Brush("RED"))
        for point in self.auiframe.lastpoints:
            colortype = point.type if point.type != cluster.DBSCAN_NOISETYPE else -1
            if self.auiframe.datafileMultiplyIndex == 1:
                colortype = point.type if point.type<=9 else -1
                dc.SetPen(wx.Pen(colors[colortype]))
            dc.SetBrush(wx.Brush(colors[colortype]))
            dc.DrawCircle(point.coordinates[0]*multiplyBy[self.auiframe.datafileMultiplyIndex], \
                          backgroundHeight-point.coordinates[1]*multiplyBy[self.auiframe.datafileMultiplyIndex], pointSize[self.auiframe.datafileMultiplyIndex])
        
        self.auiframe.iterationNum = -1
        self.auiframe.helpStaticText2.SetLabelText('Iteration times : '+str(len(self.auiframe.iterationRecords)-1)+'\nNow: '+str(len(self.auiframe.iterationRecords)-1))
        self.ano.Destroy()
        
        
class progressThread(Thread, wx.Frame):

    def __init__(self):
        
        Thread.__init__(self)
        wx.Frame.__init__(self, None, size=(360, 180), id=ID_ANCHORSDEMOPROGRESSFRAME, 
            title='WAIT WITH PATIENCE', 
            name='progressFrame', 
            style = wx.MINIMIZE_BOX | wx.SYSTEM_MENU | \
            wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN, pos=(400, 300))
        
        self.ptpanel = wx.Panel(size=(360, 180), parent=self,name='ptpanel', 
                                pos = (0,0)
                                )
        self.ptpanel.SetBackgroundColour(wx.Colour(255,255,255))
        
        font = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False)
        self.pttext = wx.StaticText(label="Please wait with patience.", \
            parent=self.ptpanel, id=ID_ANCHORSDEMOFRAMEHELPSTATICTEXT3, \
            name='waittip',pos=(50, 30),size=(160, 60))
        self.pttext.SetForegroundColour('RED')
        self.pttext.SetFont(font)
        
        g2 = wx.Gauge(self.ptpanel, ID_ANCHORSDEMOFRAMEHELPGAUGE, 100, pos=(50, 75), size=(260, 30))
        g2.Pulse()
        
        self.Show(True)
        
    def run(self):
        pass
        
if __name__ == '__main__':
    app = wx.App()
    frame = AnchorsDemoFrame()
    frame.Show(True)
    app.MainLoop()

