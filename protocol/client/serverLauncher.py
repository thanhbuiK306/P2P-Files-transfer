from tkinter import *
from tkinter import filedialog
from tkinter.messagebox import showerror, showwarning, showinfo, askyesno
from server import Server
import time
import os
import copy
from pathlib import Path

server = None

def runServer():
  global server

  server = Server()
  server.run()
  while (server.active):
    time.sleep(0.01)
    if (server.active == False):
      server = None
      showerror("Error", "Fail binding address!")
      return
  Label(serverInfo, text=server.server_ip).grid(row=2, column=1, sticky=W)
  Label(serverInfo, text=server.port).grid(row=1, column=1, sticky=W)
  runButton.configure(state = "disable", cursor = "arrow")

def updateListPeer():

  listPeer = server.connections
  peerListBox.delete(0, "end")
  if (len(listPeer) > 0):
    peerListBox.configure(state = "normal") 
    for i in range(len(listPeer)):
      peerListBox.insert(i, " " + listPeer[i]["port"])
  else:
    peerListBox.delete(0, "end")
    
def showListFile(var):
  pass
#   try:
#     str = peerListBox.get(peerListBox.curselection())
#   except:
#     return
#   index = 0
#   peerName = str.replace(" ", "")
#   peerDatas = copy.deepcopy(server.jsonPeerDatas)
#   if (peerDatas == []):
#     fileListbox.delete(0, "end")
#   else:
#     for i in range(len(peerDatas)):
#       if (peerDatas[i]["name"] == peerName):
#         fileListbox.configure(state = "normal")
#         for file in peerDatas[i]["listFile"]:
#           fileListbox.insert(index, " " + file)
#           index = index + 1
#         break

def ping():
  try:
    str = peerListBox.get(peerListBox.curselection())
  except:
    return
  peerName = str.replace(" ", "")
  # server.ping(peerName)

def onClosing():

  if askyesno("Quit", "Are you sure"):
    global server
    if ((server != None) and (server.active == False)):
      server.endSystem()
      print("Shutting down the server..")
    root.destroy()

root = Tk()
root.title("Server GUI")
# root.geometry("500x500")
root.resizable(0, 0)

# Create Client Info Frame
infoFrame = Frame(root)
Label(infoFrame, text="Server Info", font = ("Helvetica", 18)).grid(row=0, sticky=W+E)
infoFrame.grid(row=0, column=0, padx=10, pady=10)

# Server Info
serverInfo = Frame(infoFrame)
serverInfo.grid(row=1, column=0, padx=10, pady=10, sticky=W)
Label(serverInfo, text="Server:", font = ("Helvetica", 14)).grid(row=0, column=0, sticky=W)
Label(serverInfo, text="Port:").grid(row=1, column=0, sticky=W)
Label(serverInfo, text="IP:").grid(row=2, column=0, sticky=W)
# serverPortEntry = Entry(serverInfo, font = ("Helvetica", 11), width = 7)
# serverPortEntry.grid(row=1, column=1, sticky=W)

runButton = Button(infoFrame, text="Connect", border = 0, borderwidth = 0, relief = "sunken", cursor = "hand2", command = runServer)
runButton.grid(row=1, column=1)

# Frame(root, highlightbackground = "#252525", highlightthickness = 5, width = 500).grid(row=1)

# # Create List Frame
# listFrame = Frame(root)
# listFrame.grid(row=2, sticky=W)
# Label(listFrame, text="List", font = ("Helvetica", 18)).grid(row=0, padx=10, pady=10, sticky=W)

# # Peer List Frame
# listPeerFrame = Frame(listFrame)
# listPeerFrame.grid(row=1, column=0, padx=10, pady=10, sticky=W)
# Label(listPeerFrame, text = "List Peer", font = ("Helvetica", 14)).grid(row=0, column=0)
# peerArea = Frame(listPeerFrame, background="white")
# peerArea.grid(row=1, column=0, padx=10, pady= 10)
# scroll = Scrollbar(peerArea)
# peerListBox = Listbox(peerArea, yscrollcommand = scroll.set, font = ("Helvetica", 11), width = 25, height = 7, 
#                      bg = "white", selectbackground = "#ff904f", selectforeground = "white", activestyle = "none", 
#                      highlightthickness = 0, borderwidth = 0, selectmode = "single", cursor = "hand2", state = "disabled", exportselection=0)
# # peerListBox.bind("<<ListboxSelect>>", showListFile)
# scroll.pack(side = "right", fill = "y")
# peerListBox.pack(side = "left", padx = 5, pady = 5)
# refreshButton = Button(listPeerFrame, text="Refresh", border = 0, borderwidth = 0, relief = "sunken", cursor = "hand2", command = updateListPeer)
# refreshButton.grid(row=2, column=0, sticky=W, padx=10, pady= 10)
# pingButton = Button(listPeerFrame, text="Ping", border = 0, borderwidth = 0, relief = "sunken", cursor = "hand2", command = ping)
# pingButton.grid(row=2, column=0, sticky=E, padx=10, pady= 10)

# # File List Frame
# listFileFrame = Frame(listFrame)
# listFileFrame.grid(row=1, column=1, padx=10, pady=10, sticky=N+W)
# Label(listFileFrame, text = "List file", font = ("Helvetica", 14)).grid(row=0)
# fileArea = Frame(listFileFrame, background="white")
# fileArea.grid(row=1, padx=10, pady= 10)
# scroll = Scrollbar(fileArea)
# fileListbox = Listbox(fileArea, yscrollcommand = scroll.set, font = ("Helvetica", 11), width = 25, height = 7, 
#                      bg = "white", selectbackground = "#ff904f", selectforeground = "white", activestyle = "none", 
#                      highlightthickness = 0, borderwidth = 0, selectmode = "single", cursor = "hand2", state = "disabled", exportselection=0)
# scroll.pack(side = "right", fill = "y")
# fileListbox.pack(side = "left", padx = 5, pady = 5)

root.protocol("WM_DELETE_WINDOW", onClosing)
root.mainloop()