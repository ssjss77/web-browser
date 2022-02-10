import sys
import os
import json
# [...]

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                             QPushButton, QLabel, QLineEdit,
                             QTabBar, QTabWidget, QFrame, QStackedLayout, QHBoxLayout,
                             QShortcut, QKeySequenceEdit)
from PyQt5.QtGui import QIcon, QWindow, QImage, QKeySequence, QPixmap
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *

class AdressBar(QLineEdit):
    def __init__(self):
        super().__init__()

    def mousePressEvent(self, e) :
        self.selectAll()

class App(QFrame):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ilham web brower")
        self.setBaseSize(1000,400)
        self.setMinimumSize(1000,400)
        self.CreateApp()
        self.setWindowIcon(QtGui.QIcon('logo.png'))

    def CreateApp(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        #Create tabs
        self.tabbar = QTabBar(movable= True, tabsClosable=True)
        self.tabbar.tabCloseRequested.connect(self.CloseTab)
        self.tabbar.tabBarClicked.connect(self.SwitchTab)

        self.tabbar.setCurrentIndex(0)
        self.tabbar.setDrawBase(False)

        #keep track of tabs
        self.tabCount = 0
        self.tabs = []

        #Set ToolBAr Buttons
        self.BackButton = QPushButton("<")
        self.BackButton.clicked.connect(self.GoBack)
        self.ForwardButton = QPushButton(">")
        self.ForwardButton.clicked.connect(self.GoForward)
        self.ReloadButton = QPushButton("")
        self.ReloadButton.clicked.connect(self.ReloadPage)


        #Create Addressbar
        self.toolBar = QWidget()
        self.toolBarLayout = QHBoxLayout()
        self.addressBar = AdressBar()

        self.addressBar.returnPressed.connect(self.BrowseTo)

        self.toolBar.setLayout(self.toolBarLayout)

        self.toolBarLayout.addWidget(self.BackButton)
        self.toolBarLayout.addWidget(self.ForwardButton)
        self.toolBarLayout.addWidget(self.ReloadButton)

        self.toolBarLayout.addWidget(self.addressBar)


        #New tab button
        self.AddTabButton = QPushButton('+')
        self.AddTabButton.clicked.connect(self.addTab)
        self.toolBarLayout.addWidget(self.AddTabButton)
        #Create shortcuts
        self.shortcutNewtab = QShortcut(QKeySequence("Ctrl+T"),self)
        self.shortcutNewtab.activated.connect(self.addTab)

        self.shortcutReload = QShortcut(QKeySequence("Ctrl+R"),self)
        self.shortcutReload.activated.connect(self.ReloadPage)

        #Set main view
        self.container = QWidget()
        self.container.layout = QStackedLayout()
        self.container.setLayout(self.container.layout)

        self.layout.addWidget(self.tabbar)
        self.layout.addWidget(self.toolBar)
        self.layout.addWidget(self.container)

        self.setLayout(self.layout)
        self.addTab()
        self.show()

    def CloseTab(self, i):
        self.tabbar.removeTab(i)
        print(i)

    def addTab(self):
        i = self.tabCount

        self.tabs.append(QWidget())
        self.tabs[i].layout = QVBoxLayout()
        self.tabs[i].setObjectName("tab" + str(i))

        #Open webview
        self.tabs[i].content = QWebEngineView()
        self.tabs[i].content.load(QUrl.fromUserInput("http://google.com"))

        self.tabs[i].content.titleChanged.connect(lambda: self.setTabContent(i, "title"))
        self.tabs[i].content.iconChanged.connect(lambda: self.setTabContent(i, "icon"))
        self.tabs[i].content.urlChanged.connect(lambda: self.setTabContent(i,"url"))
        #Add webview to tabs layout
        self.tabs[i].layout.addWidget(self.tabs[i].content)

        #set top level tab from [] to layout
        self.tabs[i].setLayout(self.tabs[i].layout)

        #add tab to top level stackedwidget
        self.container.layout.addWidget(self.tabs[i])
        self.container.layout.setCurrentWidget(self.tabs[i])
        # set the tab at top of screen
        self.tabbar.addTab("Tab " + str(i+1))
        self.tabbar.setTabData(i,{"object": "tab" + str(i), "initial": str(i)} )
        self.tabbar.setCurrentIndex(i)

        self.tabCount += 1

    def SwitchTab(self, i):
        if self.tabbar.tabData(i):
            tab_data = self.tabbar.tabData(i)["object"]
            tab_content = self.findChild(QWidget, (tab_data))
            self.container.layout.setCurrentWidget(tab_content)

    def BrowseTo(self):
        text = self.addressBar.text()
        print(text)
        i = self.tabbar.currentIndex()
        tab = self.tabbar.tabData(i)["object"]
        wv = self.findChild(QWidget, tab).content
        if "http" not in text:
            if "." not in text:
                url = "http://google.com/#q=" + text
            else:
                url = "http://" + text
        else:
            url = text

        wv.load( QUrl.fromUserInput( text ) )

    def setTabContent(self,i, type):

        tab_name = self.tabs[i].objectName()
        count = 0
        running = True
        current_tab = self.tabbar.tabData(self.tabbar.currentIndex())["object"]
        if current_tab == tab_name and type == "url":
            new_url = self.findChild(QWidget, tab_name).content.url().toString()
            self.addressBar.setText(new_url)
            return False
        while running :
            tab_data_name = self.tabbar.tabData(count)
            if tab_name == tab_data_name["object"]:
                if type == "title":
                    newTitle = self.findChild(QWidget, tab_name).content.title()
                    self.tabbar.setTabText(count, newTitle)
                elif type == "icon":
                    newIcon = self.findChild(QWidget, tab_name).content.icon()
                    self.tabbar.setTabIcon(count, newIcon)
                running = False
            else:
                count += 1

    def GoBack(self):
        activeIndex = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(activeIndex)["object"]
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.back()

    def GoForward(self):
        activeIndex = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData( activeIndex )["object"]
        tab_content = self.findChild( QWidget, tab_name ).content

        tab_content.forward()

    def ReloadPage(self):
        activeIndex = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData( activeIndex )["object"]
        tab_content = self.findChild( QWidget, tab_name ).content
        tab_content.reload()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    #os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = "667"
    window = App()
    app.setWindowIcon( QtGui.QIcon( 'logo.png' ) )
    app.setWindowIcon(QIcon(QPixmap('logo.png')))

    with open("style.css", "r") as style:
        app.setStyle(style.read())
    sys.exit(app.exec_())