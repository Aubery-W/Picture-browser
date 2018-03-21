from PyQt4 import QtCore, QtGui, uic
import re,os,sys
from tempfile import NamedTemporaryFile
import itertools as itool
import requests as req
pos=0
qtCreatorFile = "viewerofmine.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
class GetThumb(QtCore.QThread):
    Listofthumb = QtCore.pyqtSignal(list)
    def __init__(self,tag):
        global pos
        pos=0
        super(GetThumb,self).__init__()
        self.tag=tag
    def run(self):
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'}
        r=req.get('http://',params=self.tag,headers=headers)
        thumbid=re.compile(r'<article.*?<a href="(.*?)">',re.S)
        thumbsrc=re.compile(r'<img itemprop="thumbnailUrl" src="(.*?)".*?>',re.S)
        idlist=re.findall(thumbid,r.text)
        thumblist = re.findall(thumbsrc,r.text)
        for thumbimg,imgurl in itool.zip_longest(thumblist,idlist):
            if(thumbimg!=None):
                # print("find thumb")
                thumb="http://danbooru.donmai.us"+thumbimg
                img="http://danbooru.donmai.us"+imgurl
                thumb=req.get(thumb,headers=headers).content
                self.Listofthumb.emit([thumb,img])
            else:
                print("not found")
                thumb=open("alt.png",'rb')
                self.Listofthumb.emit([thumb,'False'])
class GetImage(QtCore.QThread):
    progress=QtCore.pyqtSignal(int)
    def __init__(self,url):
        super(GetImage,self).__init__()
        self.url=url
    def run(self):
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/48.0.2564.116'}
        resp=req.get(self.url,headers=headers)
        imgre=re.compile(r'Information.*?Size.*?<a href="(.*?)">',re.S)
        imgurl=re.findall(imgre,resp.text)
        img="http://danbooru.donmai.us/"+imgurl[0]
        print("123")
        # self.progress.emit(1)
class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.getthumb()
        self.conta=ImageContainer(self.frameinput)
    def getthumb(self):
        tag={'tags':'scenery','page':'1'}
        print(tag)
        self.work=GetThumb(tag)
        self.work.Listofthumb.connect(self.Putonthumb)
        self.work.start()
        print("QThread started")
    def Putonthumb(self,ls):
        global pos
        thumb=ImageWidget()
        qlabel=thumb.setThumb(ls)
        self.conta.addWidget(qlabel,pos)
        pos+=1
class ImageContainer(QtGui.QFrame):
    def __init__(self,widgets):
        super(ImageContainer, self).__init__()
        self.area=widgets
        print(self.area.size())
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.area)
        self.total=QtGui.QWidget()
        self.total.setFixedSize(600,2000)
        self.area.setWidget(self.total)
        # self.total.show()
    def addWidget(self, widget,pos):
        widget.setParent(self.total)
        row=int(pos/2)*200
        col=pos%2*300
        # print(col,row)
        widget.move(col+20,row)
        # self.area.setWidgetResizable(True)
        widget.show()
        # print(self.total.children())

class ImageWidget(QtGui.QWidget):
    """
    put thumb into this label
    """
    prevSelected = None
    
    def __init__(self):
        super(ImageWidget, self).__init__()
    def setThumb(self, thumb):
        thumbq = QLabel(thumb[1])
        thumbq.setMouseTracking(True)
        res=QtGui.QPixmap()
        res.loadFromData(thumb[0])
        res=res.scaled(200,150,QtCore.Qt.KeepAspectRatio)#try to fit it 
        thumbq.setPixmap(res)
        return thumbq
class QLabel(QtGui.QLabel): #define the label style and click event
    def __init__(self,imgurl):
        super(QLabel, self).__init__()
        self.imgurl=imgurl
    def mousePressEvent(self,event):
        self.DownloadImage(self.imgurl)
        print("clicked")
    def leaveEvent(self,event):
        self.setStyleSheet(' ')
    def enterEvent(self,event):
        self.setStyleSheet('border: 4px solid rgb(255, 172, 151)')
    def DownloadImage(self,url):
        print(url)
        imgwork=GetImage(url)
        imgwork.start()
    def refreshpro(ls):
        print("refresh",ls)
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()   
    app.exec_()