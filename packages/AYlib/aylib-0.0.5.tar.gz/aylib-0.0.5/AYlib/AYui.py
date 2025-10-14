# -*- coding: utf-8 -*-
__doc__ = 'AYlib module'
__version__ = '0.0.4'
__author__ = 'Aaron Yang <3300390005@qq.com>'
__website__ = 'https://github.com/AaronYang233/AYlib/'
__license__ = 'Copyright © 2015 - 2021 AaronYang.'

import threading
import queue

# Optional imports with fallback
try:
    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.backend_bases import MouseButton
    from matplotlib.path import Path
    from matplotlib.patches import PathPatch
    from matplotlib.widgets import Button
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    # Mock classes for when matplotlib is not available
    class MockNP:
        def __init__(self):
            pass
        def arange(self, *args):
            return list(range(*args))
        def asarray(self, data):
            return data
    np = MockNP()
    
    class MockMatplotlib:
        def __init__(self):
            pass
    matplotlib = MockMatplotlib()
    
    class MockPath:
        MOVETO = 1
        CURVE4 = 4
        CLOSEPOLY = 79
    Path = MockPath()
    
    class MockPathPatch:
        def __init__(self, *args, **kwargs):
            pass
    PathPatch = MockPathPatch


q = queue.Queue(maxsize=0)

class AYui:
    def __init__(self,model=None,head=None,data=None,end=[0,0],language=None):
        self.model = model
        self.head = head
        self.data = data
        self.end = end
        self.showverts = True
        self.epsilon = 5
        self.language = language
        self.font = matplotlib.font_manager.FontProperties(fname=self.language)

    def AY_Plot(self,list_title="demo",xlabel_title="x/x",ylabel_title="y/y"):
        
        self.list_title = list_title
        self.xlabel_title = xlabel_title
        self.ylabel_title = ylabel_title
        
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available, AYui plotting functionality disabled")
            return
            
        if not self.model:
            print("Demo")
            x = np.arange(1,11)
            y = 2 * x +5
            plt.title(self.list_title,fontproperties=self.font)
            plt.xlabel(self.xlabel_title, fontproperties=self.font)
            plt.ylabel(self.ylabel_title, fontproperties=self.font)
            plt.plot(x,y)
            plt.show()

        if self.model == "interact":
            buffer = []
            xarray = []
            yarray = []
            
            fig,ax = plt.subplots()

            buffer.append((Path.MOVETO,self.head))
            for i in range(len(self.data)):
                buffer.append((Path.CURVE4,self.data[i]))
            buffer.append((Path.CLOSEPOLY,self.end))

            for i in range(len(buffer)):
                xarray.append(buffer[i][1][0])
                yarray.append(buffer[i][1][1])

            self.codes,self.verts = zip(*buffer)
            path = Path(self.verts,self.codes)
            patch = PathPatch(path, facecolor='green', edgecolor='blue', alpha=0.5)
            ax.add_patch(patch)
            self.ax = patch.axes
            canvas = self.ax.figure.canvas
            self.pathpatch = patch
            self.pathpatch.set_animated(True)
            x,y = zip(*self.pathpatch.get_path().vertices)

            if 0 < len(y):
                q.put(y)

            self.line, = ax.plot(
                x, y, marker='o', linestyle='None',markerfacecolor='r', animated=True)
            self._ind = None
        
            canvas.mpl_connect('draw_event', self.on_draw)
            canvas.mpl_connect('button_press_event', self.on_button_press)
            canvas.mpl_connect('button_release_event', self.on_button_release)
            canvas.mpl_connect('key_press_event', self.on_key_press)
            canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
            
            self.canvas = canvas
            #plt.figure('test')
            
            ax.set_title(self.list_title,fontproperties=self.font)
            ax.set_xlim(min(xarray)-1,max(xarray)+1)
            ax.set_ylim(min(yarray)-1,max(yarray)+1)
            plt.xlabel(self.xlabel_title, fontproperties=self.font)
            plt.ylabel(self.ylabel_title, fontproperties=self.font)
            
            ''' button define '''
            plt.subplots_adjust(bottom=0.2)
            axnext = plt.axes([0.5, 0.01, 0.1, 0.085])
            bnext = Button(axnext, 'stop')
            bnext.on_clicked(self.stop)

            aynext = plt.axes([0.65, 0.01, 0.1, 0.085])
            bneyt = Button(aynext, 'send')
            bneyt.on_clicked(self.send)

            aznext = plt.axes([0.8, 0.01, 0.1, 0.085])
            bnezt = Button(aznext, 'start')
            bnezt.on_clicked(self.start)
        
            plt.show()
            
    ''' interact define code '''
    def get_ind_under_point(self, event):
        """
        Return the index of the point closest to the event position or *None*
        if no point is within ``self.epsilon`` to the event position.
        """
        # display coords
        xy = np.asarray(self.pathpatch.get_path().vertices)
        xyt = self.pathpatch.get_transform().transform(xy)
        xt, yt = xyt[:, 0], xyt[:, 1]
        d = np.sqrt((xt - event.x)**2 + (yt - event.y)**2)
        ind = d.argmin()
        if d[ind] >= self.epsilon:
            ind = None
        return ind

    def on_draw(self, event):
        """Callback for draws."""
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.ax.draw_artist(self.pathpatch)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)

    def on_button_press(self, event):
        """Callback for mouse button presses."""
        if (event.inaxes is None
                or event.button != MouseButton.LEFT
                or not self.showverts):
            return
        self._ind = self.get_ind_under_point(event)
        
    def on_button_release(self, event):
        """Callback for mouse button releases."""
        if (event.button != MouseButton.LEFT
                or not self.showverts):
            return
        self._ind = None

    def on_key_press(self, event):
        """Callback for key presses."""
        if not event.inaxes:
            return
        if event.key == 't':
            self.showverts = not self.showverts
            self.line.set_visible(self.showverts)
            if not self.showverts:
                self._ind = None
        self.canvas.draw()

    def on_mouse_move(self, event):
        """Callback for mouse movements."""
        if (self._ind is None
                or event.inaxes is None
                or event.button != MouseButton.LEFT
                or not self.showverts):
            return

        vertices = self.pathpatch.get_path().vertices
        a = []
        for i in range(len(vertices)):
            a.append(vertices[i][1])

        if 0 < len(a):
            q.put(tuple(a))

        vertices[self._ind] = event.xdata, event.ydata
        self.line.set_data(zip(*vertices))
        self.canvas.restore_region(self.background)
        self.ax.draw_artist(self.pathpatch)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)
        

    ''' interact define code end '''

    ''' button define code start '''
    def start(self,event):
        print("start")
    
    def send(self,event):
        print("send")
        a = None
        while not q.empty():
            a = q.get()
        print(str(a))

    def stop(self,event):
        print("stop")
    ''' button define code end '''

if __name__ == "__main__":
    head    = [0,0]
    end     = [8,0]

    # AYui "model == interact" is cubic-bezier
    # about:    https://www.jasondavies.com/animated-bezier/
    # curve:    data[0]/data[1]/data[3]/data[4]
    # point:    data[2]/data[6]
    data = [[1,1],[2,1],[3,0],[4,-1],[5,-1],[6,0]]

    a = AYui("interact",head,data,end)
    a.AY_Plot("title","x","y")

    # chinese
    # a = AYui("interact",head,data,end,"./SourceHanSerifSC-Bold.otf")
    # a.AY_Plot("伺服电机控制器","时间","幅度")