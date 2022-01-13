import heroku3
import os

from threading import Thread
cloud = heroku3.from_key('9547234d-b116-4026-a708-2579d1035303')
app=cloud.apps()['matanhackbot']
dynolist = app.dynos()
status=len(dynolist)

from tkinter import *
root = Tk()

def gettext():
    if status==1:
        text='Выключить'
    elif status==0:
        text='Включить'
    return text
def toff():
    os.system("heroku ps:scale worker=0 -a matanhackbot")
def ton():
    os.system("heroku ps:scale worker=1 -a matanhackbot")
def lg():
    os.system("heroku logs -a matanhackbot -t")
def change(event):
    global status
    if status==1:
        status=0
        b['text'] = gettext()
        lad['text']='Статус: '+str(status)
        Thread(target=toff, args=()).start()
        
    elif status==0:
        status=1
        b['text'] = gettext()
        lad['text']='Статус: '+str(status)
        Thread(target=ton, args=()).start()
 

def logs(event):
    Thread(target=lg, args=()).start()


lad = Label(text='Статус: '+str(status), width=30, height=3)
lad.pack()

b = Button(text=gettext(), width=20, height=3)
b.bind('<Button-1>', change)
b.pack()

lb = Button(text='Логи', width=20, height=3)
lb.bind('<Button-1>', logs)
lb.pack()

root.mainloop()