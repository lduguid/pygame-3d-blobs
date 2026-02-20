#from tkinter import Label                       # get a widget object

'''
1. Loads a widget class from the tkinter module
2. Makes an instance of the imported Label class
3. Packs (arranges) the new Label in its parent widget
4. Calls mainloop to bring up the window and start the tkinter event loop
'''

#widget = Label(None, text='Hello GUI world!')   # make one
#widget.pack()                                   # arrange it
#widget.mainloop()                               # start event loop

from tkinter import *

root = Tk()
Label(root, text='Hello GUI world!').pack(side=TOP)
root.mainloop()