import numpy as np
import matplotlib.pyplot as plt 
import matplotlib,sys
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from PyQt4 import QtCore, QtGui, uic
qtCreatorFile = "yaoshi.ui" # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
path=sys.path[0]
def lerr(y,n,y_0,n_0,prec_y,prec_x):
    flag=1
    yep=1
    while(flag and n>0):
        if(y[n-1]<y[n]):
            if((y_0-y[n-1])<prec_y):
                n=n-1
            else:
                flag=0
                yep=0
        elif((n_0-n)<prec_x):
            n=n-1
        else:
            flag=0
            yep=1
        return yep

def rerr(y,n,y_0,n_0,prec_y,prec_x):
    flag=1
    yep=1
    while(flag):
        if(y[n+1]<y[n] and n<len(y)-1):
            if((y_0-y[n+1])<prec_y):
                n=n+1
            else:
                flag=0
                yep=0
        elif((n-n_0)<prec_x):
            n=n+1
        else:
            flag=0
            yep=1
        return yep
class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.OK.clicked.connect(self.FindPeaks)
        self.connect(self.Filepath, QtCore.SIGNAL('triggered()'), self.showDialog)
    def showDialog(self):
        global path
        path = QtGui.QFileDialog.getOpenFileName(self, 'Open file','/',"Text files (*.txt)")
    def FindPeaks(self):
        global path
        arr=np.loadtxt(path)
        x=arr[:,:1][:,0]
        y=arr[:,1:][:,0]
        prec_x=int(self.axis.text())
        prec_y=int(self.ayis.text())
        allx=arr[:,:1][:,0][-1:][0]-arr[:,:1][:,0][:1][0] # range of  axis
        ally=arr[:,1:][:,0].max()-arr[:,1:][:,0].min() # range of ayis
        peak=[[],[]]
        for n in range(1,len(y)-2):
            if(y[n-1]<y[n] and y[n]>y[n+1]):
                y_0=y[n]
                n_0=n
                if(rerr(y,n,y_0,n_0,prec_y,prec_x)==0 and lerr(y,n,y_0,n_0,prec_y,prec_x)==0):
                    peak[0].append(x[y==y[n]])
                    peak[1].append(y[n])
        for i in range(0,len(peak[0])-1):
            strs="x:"+str(peak[0][i][0])+"        Peak:"+ str(peak[1][i])
            self.Peaks.append(strs)
        if(peak[0][0]==519.4):
            self.Peaks.append("IS KEY")
        else:
            self.Peaks.append("NOT KEY")
        fig = plt.figure()
        self.canvas = FigureCanvas(fig)
        self.lay.addWidget(self.canvas)
        ax=fig.add_subplot(111)
        ax.scatter(peak[0], peak[1], c="red",s=20)
        ax.plot(x,y)
        self.canvas.draw()
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()   
    app.exec_()