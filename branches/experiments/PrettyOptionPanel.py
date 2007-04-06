#!/usr/bin/python

import sys
from PyQt4.QtCore import Qt
from PyQt4.QtGui  import *


def clearLayout(layout):
  
  while layout.count() > 0:
    
    item = layout.takeAt(0).widget()
    if item: item.setParent(None)



class PrettyOptionPanelHeader(QFrame):
  
  SPACE_AFTER_ICON = 8
  
  def __init__(s, text, icon=None, parent=None):
    
    QFrame.__init__(s, parent)
    
    s.setFrameStyle(QFrame.Sunken | QFrame.StyledPanel)
    s.setAutoFillBackground(True)
    s.setBackgroundRole(QPalette.Mid)
    
    s.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
    
    s.text = text
    s.icon = icon
    
    s.relayout()


  def relayout(s):
    
    layout = s.layout()
    
    if layout:
      clearLayout(layout)
        
    else:
      layout = QHBoxLayout()
    
    if s.icon:
      
      icon = QLabel()
      icon.setPixmap(s.icon)
      icon.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    
      layout.addWidget(icon)
      layout.addSpacing(s.SPACE_AFTER_ICON)

    label = QLabel('<b><font size="+1">%s</font></b>' % s.text)
    label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    
    layout.addWidget(label)
    
    s.setLayout(layout)
  
  
  def setText(s, text):
    
    s.text = text
    s.relayout()
  
  
  def setIcon(s, pixmap):
    
    s.icon = pixmap
    s.relayout()






class PrettyOptionPanel(QFrame):
  
  MIN_LABEL_WIDTH = 64
  MIN_LEFT_MARGIN = 24

  def __init__(s, parent=None):

    QFrame.__init__(s, parent)
    s.setFrameStyle(QFrame.NoFrame)
    
    s.header = None
    s.contents = None

    s.relayout()


  def initLayout(s):
    
    s.setLayout(QGridLayout())
    s.layout().setColumnMinimumWidth(0, s.MIN_LEFT_MARGIN)
    s.layout().setColumnMinimumWidth(1, s.MIN_LABEL_WIDTH)
    s.currentRow = 1
    
    
  def relayout(s):
    
    layout = s.layout()
    
    if layout:
      clearLayout(layout)
      
    else:
      s.initLayout()
    
    
#    for groupname, groupitems in s.contents:


  def setHeader(s, headertext, headericon=None):
    
    if not headertext:
      s.header = None
      return
    
    s.header = PrettyOptionPanelHeader(headertext, headericon, s)
    
    ## XXX
    s.layout().addWidget(s.header, 0, 0, 1, -1)
    ## XXX


  def addGroup(s, name):
    
    label = QLabel("<b>" + name + "</b>", s)
    label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
    s.layout().addWidget(label, s.currentRow, 0, 1, -1)
    
    s.currentRow += 1


  def addItem(s, widget, label=None):
    
    if label:
      l = QLabel(label, s)
      l.setAlignment(Qt.AlignRight)
      l.setWordWrap(True)
      s.layout().addWidget(l, s.currentRow, 1)
    
    s.layout().addWidget(widget, s.currentRow, 2)
    
    s.currentRow += 1


if __name__ == "__main__":

  app = QApplication(sys.argv)
  
  window = QFrame()
  window.setLayout(QVBoxLayout())
  
  w = PrettyOptionPanel()
  
  window.layout().addWidget(w)
  
  w.setHeader("Connection parameters", QPixmap("/usr/kde/3.5/share/icons/crystalsvg/64x64/filesystems/network.png"))
  
  w.addGroup("General options")
  w.addItem(QLineEdit(), "Server:")
  w.addItem(QSpinBox(), "Port:")
  
  w.addGroup("Parameters")
  w.addItem(QCheckBox(), "SSL:")
  w.addItem(QComboBox())

  window.show()
  
  app.exec_()