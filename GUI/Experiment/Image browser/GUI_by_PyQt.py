#using Qthread
from PyQt4 import QtCore, QtGui, uic
import re,os,sys
import itertools as itool
import requests as req
qtCreatorFile = "untitled.ui" # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
times=0
inpagenum=20
class GetThumb(QtCore.QThread):
    Listofthumb = QtCore.pyqtSignal(list)
    def __init__(self,tag):  
        super(GetThumb,self).__init__()
        self.tag=tag
    def run(self):
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/48.0.2564.116'}
        r=req.get('http://danbooru.donmai.us/',params=self.tag,headers=headers)
        thumbid=re.compile(r'<article.*?<a href="(.*?)">',re.S)
        thumbsrc=re.compile(r'<img itemprop="thumbnailUrl" src="(.*?)".*?>',re.S)
        idlist=re.findall(thumbid,r.text)
        thumblist = re.findall(thumbsrc,r.text)
        for thumbimg,img in itool.zip_longest(thumblist,idlist):
            if(thumbimg!=None):
                thumb="http://danbooru.donmai.us"+thumbimg
                img="http://danbooru.donmai.us"+img
                self.Listofthumb.emit([thumb,img])
            else if(img!=None):
                thumb="alt.png"
                img="http://danbooru.donmai.us"+img
                self.Listofthumb.emit([thumb,img])
            else:
                self.Listofthumb.emit(["alt.png","False"])
class WorkThread(QtCore.QThread):
    finishSignal = QtCore.pyqtSignal(int)
    finishname = QtCore.pyqtSignal(list)
    def __init__(self,imgid,filepath,serial):  
        super(WorkThread,self).__init__()
        self.imgid=imgid
        self.filepath=filepath
        self.serial=serial
    def run(self):
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/48.0.2564.116'}
        imgid=self.imgid
        url='http://danbooru.donmai.us/'+imgid
        r2=req.get(url,headers=headers)
        imgre=re.compile(r'Original:.*?<a href="(.*?)"')
        orilist=re.findall(imgre,r2.text)
        img,ida=orilist[0].split('/')[-1].split('?')
        filename=filepath+'/'+ida+'.'+img.split('.')[-1]
        oriurl='https:'+orilist[0]
        if not (os.filepath.exists(filename)):
            r3=req.get(oriurl,headers=headers,stream=True)
            filesize=int(r3.headers['Content-Length'])
            size=1024
            with open(filename,'wb') as code:
                for chunk in r3.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        percent=size/filesize*100
                        code.write(chunk)
                        size += len(chunk)
                        code.flush()
                        self.finishSignal.emit(percent)
            okmess=ida+" Download already"
            self.finishname.emit([okmess,filesize])
        else:
            okmess="Existed"
            self.finishname.emit([okmess,filesize])
class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.initialize()
        # self.Pause.clicked.connect(self.stop)
        # self.createContextMenu()
        self.workpool=[]
    def initialize(self):
        self.setupUi(self)
        self.filepath="."
        self.Tag.selectAll()
        self.GetUrl.clicked.connect(self.getthumb)             #
        self.dlall.clicked.connect(self.DownloadAll)        #  This monitor the action done
        self.actionSavepath.triggered.connect(self.SetPath) #
        self.imgframe.clicked.connect(self.AddThread)
        # for i in range(0,inpagenum+1):
        # self.Prog
        self.ImageWidgetList = {}
    def AddThread(self):
        self.work.append(WorkThread(imgid,self.filepath,serial))# get id is diffcu
        self.work[serial].start()
    def SetPath(self):
        self.filepath= QtGui.QFileDialog.getExistingDirectory(self, 'Open file','.')
    def getthumb(self):
        self.GetUrl.setDisabled(True)# no else press
        tag={'tags':'scenery','page':'1'}
        if(self.Popular.checkState==2):
            tag['tags']=self.Tag.text()+" order:popular"
        else:
            tag['tags']=self.Tag.text()
        tag['page']=int(self.Page.currentText())
        self.work=GetThumb(tag)
        self.work.Listofthumb.connect(self.Putonthumb)
        self.work.start()
        #self.Pause.setDisabled(False)
    def Putonthumb(self,ls):
        img=ImageWidget(ls[1])
        thumblabel=img.setThumb(ls)
        img_area=ImageContainer(self.imagecontainer)
        img_area.addWidget(img)
    def Workname(self,ls):
        fileid=ls[0]
        filesize="Filesize="+str(int(ls[1]/1024))+"KBytes"
        self.idgot.appendPlainText(fileid)
        self.idgot.appendPlainText(filesize)
    def stop(self):
        self.work.quit()
        self.GetUrl.setDisabled(False)
class ImageContainer(QtGui.QFrame):
    def __init__(self,widgets):
        super(ImageContainer, self).__init__()
        self.area=widgets
        self.ImageWidgetList = {}
    def addWidget(self, widget):
        widget.setParent(self.area)
        # widget.resize(self.widget_w, self.widget_h)
        widget.show()
        self.ImageWidgetList[str(widget.id)] = widget
    def clearAll(self):
        widgets = self.area.children()
        if widgets:
            for widget in widgets:
                widget.setParent(None)
        self.ImageWidgetList.clear()
class ImageWidget(QtGui.QWidget):
    """
    put thumb into this widget
    """
    prevSelected = None
    def __init__(self,imageid):
        super(ImageWidget, self).__init__()
        self.id = imageid
        self.displayText = ''      #text showed
        self.status = 0
        self.showStatus = True
        self.selected = False
        self.isHightlight = False
     def setThumb(self, thumb = None):
        print(thumb[1])
        thumblabel = QtGui.QLabel()
        res=QtGui.QPixmap(thumb[0]).scaled(300,200,QtCore.Qt.KeepAspectRatio)
        thumblabel.setPixmap(res)
        thumblabel.show()
        return thumblabel
     
            
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    app.exec_()