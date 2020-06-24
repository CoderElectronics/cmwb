#/usr/bin/env python3
from cefpython3 import cefpython as cef
from tkinter.ttk import *
import tkinter as tk
import logging as _logging
import sys
import os
import json
import platform
import ctypes
import lib.bookmarks as bm
import lib.history as ht

# Fix for PyCharm hints warnings
WindowUtils = cef.WindowUtils()

# Platforms
WINDOWS = (platform.system() == "Windows")
LINUX = (platform.system() == "Linux")
MAC = (platform.system() == "Darwin")

# Globals
logger = _logging.getLogger("tkinter_.py")
baseconfpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config/base.json")

def saveOptions():
    with open(baseconfpath, mode="w") as fn:
        fn.write(json.dumps(curConf))

class MainFrame(tk.Frame):

    def __init__(self, root):
        self.browser_frame = None
        self.navigation_bar = None

        # Root
        root.geometry(winsize)
        tk.Grid.rowconfigure(root, 0, weight=1)
        tk.Grid.columnconfigure(root, 0, weight=1)

        # MainFrame
        tk.Frame.__init__(self, root)
        self.master.title("CmWb Mini Browser")
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.master.bind("<Configure>", self.on_root_configure)
        self.bind("<Configure>", self.on_configure)
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)

        # NavigationBar
        self.navigation_bar = NavigationBar(self)
        self.navigation_bar.grid(row=0, column=0,
                                 sticky=(tk.N + tk.S + tk.E + tk.W))
        tk.Grid.rowconfigure(self, 0, weight=0)
        tk.Grid.columnconfigure(self, 0, weight=0)

        # BrowserFrame
        self.browser_frame = BrowserFrame(self, self.navigation_bar)
        self.browser_frame.grid(row=1, column=0,
                                sticky=(tk.N + tk.S + tk.E + tk.W))
        tk.Grid.rowconfigure(self, 1, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)

        # Pack MainFrame
        self.pack(fill=tk.BOTH, expand=tk.YES)

    def on_root_configure(self, _):
        logger.debug("MainFrame.on_root_configure")
        if self.browser_frame:
            self.browser_frame.on_root_configure()

    def on_configure(self, event):
        logger.debug("MainFrame.on_configure")
        if self.browser_frame:
            width = event.width
            height = event.height
            if self.navigation_bar:
                height = height - self.navigation_bar.winfo_height()
            self.browser_frame.on_mainframe_configure(width, height)

    def on_focus_in(self, _):
        logger.debug("MainFrame.on_focus_in")

    def on_focus_out(self, _):
        logger.debug("MainFrame.on_focus_out")

    def on_close(self):
        if self.browser_frame:
            self.browser_frame.on_root_close()
        winsize = str(self.winfo_width())+"x"+str(self.winfo_height())
        curConf["window_size"] = winsize
        saveOptions()
        self.master.destroy()

    def get_browser(self):
        if self.browser_frame:
            return self.browser_frame.browser
        return None

    def get_browser_frame(self):
        if self.browser_frame:
            return self.browser_frame
        return None

class BrowserFrame(tk.Frame):

    def __init__(self, master, navigation_bar=None):
        self.navigation_bar = navigation_bar
        self.closing = False
        self.browser = None
        tk.Frame.__init__(self, master)
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        self.bind("<Configure>", self.on_configure)
        self.focus_set()

    def embed_browser(self):
        window_info = cef.WindowInfo()
        rect = [0, 0, self.winfo_width(), self.winfo_height()]
        window_info.SetAsChild(self.get_window_handle(), rect)
        self.browser = cef.CreateBrowserSync(window_info,
                                             url=homeurl) #todo
        assert self.browser
        self.browser.SetClientHandler(LoadHandler(self))
        self.browser.SetClientHandler(FocusHandler(self))
        self.message_loop_work()

    def get_window_handle(self):
        if self.winfo_id() > 0:
            return self.winfo_id()
        elif MAC:
            from AppKit import NSApp
            import objc
            return objc.pyobjc_id(NSApp.windows()[-1].contentView())
        else:
            raise Exception("Couldn't obtain window handle")

    def message_loop_work(self):
        cef.MessageLoopWork()
        self.after(10, self.message_loop_work)

    def on_configure(self, _):
        if not self.browser:
            self.embed_browser()

    def on_root_configure(self):
        # Root <Configure> event will be called when top window is moved
        if self.browser:
            self.browser.NotifyMoveOrResizeStarted()

    def on_mainframe_configure(self, width, height):
        if self.browser:
            if WINDOWS:
                ctypes.windll.user32.SetWindowPos(
                    self.browser.GetWindowHandle(), 0,
                    0, 0, width, height, 0x0002)
            elif LINUX:
                self.browser.SetBounds(0, 0, width, height)
            self.browser.NotifyMoveOrResizeStarted()

    def on_focus_in(self, _):
        logger.debug("BrowserFrame.on_focus_in")
        if self.browser:
            self.browser.SetFocus(True)

    def on_focus_out(self, _):
        logger.debug("BrowserFrame.on_focus_out")
        if self.browser:
            self.browser.SetFocus(False)

    def on_root_close(self):
        if self.browser:
            self.browser.CloseBrowser(True)
            self.clear_browser_references()
        self.destroy()

    def clear_browser_references(self):
        self.browser = None

class LoadHandler(object):

    def __init__(self, browser_frame):
        self.browser_frame = browser_frame

    def OnLoadStart(self, browser, **_):
        if self.browser_frame.master.navigation_bar:
            self.browser_frame.master.navigation_bar.set_url(browser.GetUrl())
            ht.addhistory(str(browser.GetUrl()))

class FocusHandler(object):

    def __init__(self, browser_frame):
        self.browser_frame = browser_frame

    def OnTakeFocus(self, next_component, **_):
        logger.debug("FocusHandler.OnTakeFocus, next={next}"
                     .format(next=next_component))

    def OnSetFocus(self, source, **_):
        logger.debug("FocusHandler.OnSetFocus, source={source}"
                     .format(source=source))
        return False

    def OnGotFocus(self, **_):
        """Fix CEF focus issues (#255). Call browser frame's focus_set
           to get rid of type cursor in url entry widget."""
        logger.debug("FocusHandler.OnGotFocus")
        self.browser_frame.focus_set()

class NavigationBar(tk.Frame):
    def __init__(self, master):
        self.back_state = tk.NONE
        self.forward_state = tk.NONE
        self.back_image = None
        self.forward_image = None
        self.reload_image = None
        tk.Frame.__init__(self, master)

        # Back button
        back = b'iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAYAAABWzo5XAAAAQklEQVR4AWMY2aAeiDsoNaQEiP8D8bThZcg8ahjyD4gPAvEBvBgPaKDcIAToRvIaIyHFpBjGQC3Dpg1Kw9oYRi4AAJl0JUbdjniaAAAAAElFTkSuQmCC'        
        self.back_image = tk.PhotoImage(data=back)
        self.back_image = self.back_image.zoom(buttonzoom).subsample(100)
        self.back_button = tk.Button(self, image=self.back_image,command=self.go_back)
        self.back_button.grid(row=0, column=0)

        # Forward button
        forward = b'iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAYAAABWzo5XAAAAQklEQVR4AWMY2aADiOupYdA0IP4PxCWDzrB51DKMkRTDDhDAB4H4H8wwahnUQA2vdQ+oIQzUMmQawhDKs0g3w8gFALkHJVrl/e0QAAAAAElFTkSuQmCC'        
        self.forward_image = tk.PhotoImage(data=forward)
        self.forward_image = self.forward_image.zoom(buttonzoom).subsample(100)
        self.forward_button = tk.Button(self, image=self.forward_image,command=self.go_forward)
        self.forward_button.grid(row=0, column=1)

#        Reload button
        refresh = b'iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAQAAAD8x0bcAAAAlElEQVR4AcXKscpBYQCA4ec/+Tv3wM0ouQWyMnIxMsLqAowoMZCVYHEJykDJ8lnOcPSV1bO99fqdVMdFcLPUkIgpOglmuobOxgoif9auKr5qCuo+lU38y9naRctTMM1vDwPxEmRbapHlS1Ve310m26KFvS35bRotNUHLVxVXG4lIwdjRSM9ccFAilmhYuQku2lK/8gZIyzMM742LtAAAAABJRU5ErkJggg=='        
        self.reload_image = tk.PhotoImage(data=refresh)
        self.reload_image = self.reload_image.zoom(buttonzoom).subsample(100)
        self.reload_button = tk.Button(self, image=self.reload_image,command=self.reload)
        self.reload_button.grid(row=0, column=2)

#       Homepage button
        home = b'iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAQAAAD8x0bcAAAAY0lEQVR4AcXKtwFFYAAA4XtRqRSHsQEzWMS/iDXUKjMYRs6ZRviuPS5k43DAJS1z2eGRtwlWvfHJR/m8mZEIyGcFSIzIROQrRci0TGLyjWJUetbqYgEspxBRFu5Pgop4anpCAUkSY9O4nd/xAAAAAElFTkSuQmCC'        
        self.home_image = tk.PhotoImage(data=home)
        self.home_image = self.home_image.zoom(buttonzoom).subsample(100)
        self.home_button = tk.Button(self, image=self.home_image,command=self.go_home)
        self.home_button.grid(row=0, column=3)

#       Devtools button
        devtools = b'iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAQAAAD8x0bcAAAAp0lEQVR4AYTKIQjCYBSF0YNgFGbH3oNV/96bPaytNy1Gw9qyybSe7Gm9a4f1PYsM9hA8X7tcs52S2kk2XiL1trFwED86WCjC4GnOIBT5pPxZVIpKBWD7XTInoz3YG51kqE16a7DWm9SSRrhbAVh5CI2Fi9CZoRPOkpvQAmiFK0C+HT8Ds+yBrH4MeaiHXeB8Z4gIsYFJOFrIiGBehucYSp7DkgpRiQ4Ambhd7cRztqEAAAAASUVORK5CYII='        
        self.dev_image = tk.PhotoImage(data=devtools)
        self.dev_image = self.dev_image.zoom(buttonzoom).subsample(100)
        self.dev_button = tk.Button(self, image=self.dev_image,command=self.devtools)
        self.dev_button.grid(row=0, column=4)

#       Extensions button
        extensionsdata = b'iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAQAAAD8x0bcAAAAqElEQVR4AZXQgQYCURBG4QMBNkFAFUAoIBbIAhIIAiCAFBBA5Qr1OtEzBIJ9hIgFUEWkmBjrWpkufQcMPxi+NCgTxhbhSkzQA0HYY+qQaKKl+VWnIOaNGGVEeEsEux6e+zlK8NbBkVeiT2aMUnZ0KVggZneqeFMEuxa5CkdzcGGDGnPgaU4S6wU3Vsw5h0dtAIbWaIRoJ1BNRHtRo2CCwzEDFeG0Af/4AEmFnIpiLkZSAAAAAElFTkSuQmCC'        
        self.ext_image = tk.PhotoImage(data=extensionsdata)
        self.ext_image = self.ext_image.zoom(buttonzoom).subsample(100)
        self.ext_button = tk.Button(self, image=self.ext_image,command=self.insertCont, anchor="ne")
        self.ext_button.grid(row=0, column=7)

#       Load URL Box
        loaddata = b'iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAQAAAD8x0bcAAAAS0lEQVR4AWMYcqCcQYqQkn6G/wwFhJV000aJGMNhBk04rx27KRIMtxleMaiiK8FU9oDhGYMiVAlOIANU9gGmBJ+yx0AlBIHQoIhnAPvJGSMKv0BeAAAAAElFTkSuQmCC'        
        self.load_image = tk.PhotoImage(data=loaddata)
        self.load_image = self.load_image.zoom(buttonzoom).subsample(100)
        self.ext_button = tk.Button(self, image=self.load_image,command=self.urlboxload, anchor="ne")
        self.ext_button.grid(row=0, column=6)

#	    Settings Icon
        settingsdata = b'iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAYAAABWzo5XAAAAIElEQVR4AWMYGDAKJoAxgn2ACDyBmgaNem3Ua4TBKAAA2Kk2AbLe+1QAAAAASUVORK5CYII='        
        self.set_image = tk.PhotoImage(data=settingsdata)
        self.set_image = self.set_image.zoom(buttonzoom).subsample(100)
        self.ext_button = tk.Button(self, image=self.set_image,command=self.settings, anchor="ne")
        self.ext_button.grid(row=0, column=8)

        # Url entry
        self.url_entry = tk.Entry(self, width=500)
        self.url_entry.grid(row=0, column=5)
        self.url_entry.bind("<Return>", self.urlboxloadbind)

        tk.Grid.rowconfigure(self, 0, weight=100)
        tk.Grid.columnconfigure(self, 5, weight=100)

        # Update state of buttons
        self.update_state()

    def go_back(self):
        if self.master.get_browser():
            self.master.get_browser().GoBack()

    def go_forward(self):
        if self.master.get_browser():
            self.master.get_browser().GoForward()

    def go_home(self):
        if self.master.get_browser():
            self.master.get_browser().StopLoad()
            self.master.get_browser().LoadUrl(homeurl)

    def urlboxloadbind(self, n):
        if self.master.get_browser():
            self.master.get_browser().StopLoad()
            self.master.get_browser().LoadUrl(self.url_entry.get())

    def urlboxload(self):
        if self.master.get_browser():
            self.master.get_browser().StopLoad()
            self.master.get_browser().LoadUrl(self.url_entry.get())

    def insertCont(self):
        if self.master.get_browser():
            self.master.get_browser().ExecuteJavascript("document.innerHTML=\"<p>Hello</p>\";")

    def reload(self):
        if self.master.get_browser():
            self.master.get_browser().Reload()

    def extensions(self):
        return

    def settings(self):
        return

    def devtools(self):
        if self.master.get_browser():
            self.master.get_browser().ShowDevTools()

    def set_url(self, url):
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, url)

    def on_url_focus_in(self, _):
        logger.debug("NavigationBar.on_url_focus_in")

    def on_url_focus_out(self, _):
        logger.debug("NavigationBar.on_url_focus_out")

    def on_load_url(self, _):
        if self.master.get_browser():
            self.master.get_browser().StopLoad()
            self.master.get_browser().LoadUrl(self.url_entry.get())

    def on_button1(self, _):
        """Fix CEF focus issues (#255). See also FocusHandler.OnGotFocus."""
        logger.debug("NavigationBar.on_button1")
        self.master.master.focus_force()

    def update_state(self):
        browser = self.master.get_browser()
        if not browser:
            if self.back_state != tk.DISABLED:
                self.back_button.config(state=tk.DISABLED)
                self.back_state = tk.DISABLED
            if self.forward_state != tk.DISABLED:
                self.forward_button.config(state=tk.DISABLED)
                self.forward_state = tk.DISABLED
            self.after(100, self.update_state)
            return
        if browser.CanGoBack():
            if self.back_state != tk.NORMAL:
                self.back_button.config(state=tk.NORMAL)
                self.back_state = tk.NORMAL
        else:
            if self.back_state != tk.DISABLED:
                self.back_button.config(state=tk.DISABLED)
                self.back_state = tk.DISABLED
        if browser.CanGoForward():
            if self.forward_state != tk.NORMAL:
                self.forward_button.config(state=tk.NORMAL)
                self.forward_state = tk.NORMAL
        else:
            if self.forward_state != tk.DISABLED:
                self.forward_button.config(state=tk.DISABLED)
                self.forward_state = tk.DISABLED
        self.after(100, self.update_state)

#Options
curConf = {}

homeurl = ""
buttonzoom = 0
winsize = ""

with open(baseconfpath, mode="r") as fn:
    curConf = json.load(fn)

if not "home_url" in curConf:
    curConf["home_url"] = "https://www.google.com/"

if not "button_zoom" in curConf:
    curConf["button_zoom"] = 100

if not "window_size" in curConf:
    curConf["window_size"] = "800x600"

homeurl = curConf["home_url"]
buttonzoom = curConf["button_zoom"]
winsize = curConf["window_size"]
saveOptions()

logger.setLevel(_logging.INFO)
stream_handler = _logging.StreamHandler()
formatter = _logging.Formatter("[%(filename)s] %(message)s")
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
logger.info("CEF Python {ver}".format(ver=cef.__version__))
logger.info("Python {ver} {arch}".format(
        ver=platform.python_version(), arch=platform.architecture()[0]))
logger.info("Tk {ver}".format(ver=tk.Tcl().eval('info patchlevel')))
assert cef.__version__ >= "55.3", "CEF Python v55.3+ required to run this"
sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error

root = tk.Tk()
root.style = Style()
#('clam', 'alt', 'default', 'classic')
root.style.theme_use("alt")

app = MainFrame(root)

# Tk must be initialized before CEF otherwise fatal error (Issue #306)
cef.Initialize()
app.mainloop()
cef.Shutdown()
