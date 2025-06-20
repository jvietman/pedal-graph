# imports
from tkinter import *
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import json

# custom imports
from timer import *
from controller import *
from fixedlist import *

# config
with open("config.json", "r") as f:
    data = json.load(f)
    f.close()

with open("theme.json", "r") as f:
    theme = json.load(f)
    f.close()

# setup
root = Tk()
root.geometry("700x500")
root.title("Pedal Graph")

root.config(background=theme["background"])

# styles
style = ttk.Style()
style.theme_use('alt')
style.configure("brakepedal.Horizontal.TProgressbar", background='red')
style.configure("gaspedal.Horizontal.TProgressbar", background='green')

# frames
frame = Frame(root, background=theme["background"])
frame.place(anchor=N, relwidth=1, relheight=0.2, relx=0.5, rely=0)
graph = Frame(root, background=theme["background"])
graph.place(anchor=S, relwidth=1, relheight=0.8, relx=0.5, rely=1)

# progressbars
brakeval = IntVar()
brakebar = ttk.Progressbar(frame, orient=HORIZONTAL, variable=brakeval, style="brakepedal.Horizontal.TProgressbar", length=180)
brakebar.place(anchor=W, relwidth=0.2, relheight=0.6, relx=0.05, rely=0.5)
gasval = IntVar()
gasbar = ttk.Progressbar(frame, orient=HORIZONTAL, variable=gasval, style="gaspedal.Horizontal.TProgressbar", length=180)
gasbar.place(anchor=W, relwidth=0.2, relheight=0.6, relx=0.3, rely=0.5)

# settings frame
recording = True

def togglerecord():
    global recording
    
    if recording:
        recordbutton.config(relief="raised", background="gray")
        recording = False
    else:
        recordbutton.config(relief="sunken", background="red")
        recording = True

def clearrecord():
    global brakevalues, gasvalues
    
    brakevalues = []
    gasvalues = []

recordbutton = Button(frame, text="Record", relief="sunken", background="red", command=togglerecord)
recordbutton.place(anchor=E, relwidth=0.15, relheight=0.5, relx=0.95, rely=0.5)
clearbutton = Button(frame, text="Clear", command=clearrecord)
clearbutton.place(anchor=E, relwidth=0.15, relheight=0.5, relx=0.75, rely=0.5)

# graph
fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, graph)
canvas.get_tk_widget().place(anchor=N, relheight=0.7, relwidth=0.95, relx=0.5, rely=0.05)
viewposition = DoubleVar()
positionslider = Scale(graph, from_=0, to=1, variable=viewposition, orient=HORIZONTAL)
positionslider.place(anchor=S, relwidth=0.95, relx=0.5, rely=0.95)
viewdistance = DoubleVar()
viewdistance.set(data["viewdistance"])
distanceslider = Scale(graph, from_=10, to=200, variable=viewdistance, orient=HORIZONTAL)
distanceslider.place(anchor=S, relwidth=0.95, relx=0.5, rely=0.85)

# controller
con = controller()

# values
updatetime = data["updatetime"]
update = timer(updatetime)


brakevalues = []
gasvalues = []

def runtime(length):
    r, t = [], 0
    for i in range(length):
        r.append(t)
        t+=updatetime
    return r

def getvalues(arr, distance):
    if len(arr) >= distance:
        return arr[-distance:]
    else:
        v = []
        for i in range(distance-len(arr)):
            v.append(0)
        return v + arr[-distance:]

while True:
    if not con.connected:
        messagebox.showerror("Pedal Graph", "No gamepad connected.")
        exit()

    # progressbar
    brakeval.set(con.brakepedal)
    gasval.set(con.gaspedal)

    # view sliders
    positionslider.config(from_=len(brakevalues))
    if len(brakevalues) <= data["viewdistance"]:
        distanceslider.config(to=data["viewdistance"])
    else:
        distanceslider.config(to=len(brakevalues))

    # update graph
    if update.reached():
        # log values
        if recording:
            brakevalues.append(con.brakepedal)
            gasvalues.append(con.gaspedal)
        
        # update graph
        ax.clear()
        r = runtime(int(viewdistance.get()))
        ax.plot(r, getvalues(brakevalues[:int(-viewposition.get())], int(viewdistance.get())), color="red")
        ax.plot(r, getvalues(gasvalues[:int(-viewposition.get())], int(viewdistance.get())), color="green")
        ax.set_ylim(1, 120)
        canvas.draw()
        
        update.reset()
    root.update()