# decompyle3 version 3.9.0
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.8.0 (default, Nov 23 2019, 05:36:56) 
# [GCC 8.3.0]
# Embedded file name: GUIp4\MiTE4SDN.py
import tkinter as tk
from tkinter import messagebox
import json, random
from datetime import datetime as dt
from tkinter import ttk
from bmv2template import getAllConfig, p4str, zipallfiles
from ryutemplate import genConfig
from tkinter import filedialog
from tkinter.simpledialog import askstring

class DragDropMixin:

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.make_draggable(self)

    def make_draggable(self, widget):
        widget.bind('<Button-1>', self.on_drag_start)
        widget.bind('<B1-Motion>', self.on_drag_motion)

    def on_drag_start(self, event):
        widget = event.widget
        widget._drag_start_x = event.x
        widget._drag_start_y = event.y

    def on_drag_motion(self, event):
        widget = event.widget
        x = widget.winfo_x() - widget._drag_start_x + event.x
        y = widget.winfo_y() - widget._drag_start_y + event.y
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        grid = 5
        self.dx = x // grid * grid
        self.dy = y // grid * grid
        widget.place(x=(self.dx), y=(self.dy))


class DnDLabel(DragDropMixin, tk.Label):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.bind('<Double-Button-1>', self.changeLabel)
        self.bind('<Button-3>', self.delete)

    def setid(self, id):
        self.id = id

    def changeLabel(self, event):
        name = askstring('New Label', 'Label caption:')
        if name == '':
            name = '<empty string>'
        self['text'] = name

    def delete(self, event):
        global lbl
        lbl[self.id] = None
        self.destroy()


class Node:

    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.caption = kwargs['caption']
        self.info = {}
        self.move(kwargs['x'], kwargs['y'])
        if 'img' in kwargs.keys():
            self.setImage(kwargs['img'])
            self.imgstr = kwargs['img']
        else:
            self.img = None
            self.imgstr = ''
        if 'controller' in kwargs.keys():
            if kwargs['controller'] != None:
                self.controller = kwargs['controller']
                print('newcontroller', self.controller, self.controller[5].color)
            else:
                self.controller = None
        else:
            print('No controller')
            self.controller = None
        if 'color' in kwargs.keys():
            self.color = kwargs['color']
            print('newcolor', self.color)
        else:
            self.color = None
        self.cvtxt = None
        self.cvrect = None

    def isinside(self, x, y):
        if x > self.x:
            if x < self.x2:
                if y > self.y:
                    if y < self.y2:
                        return True
        return False

    def move(self, x, y):
        self.x = x
        self.y = y
        self.wd = 50
        self.x2 = self.x + self.wd
        self.y2 = self.y + self.wd

    def move2(self, x, y, can):
        self.unpack(can)
        grid = 10
        self.x = x // grid * grid
        self.y = y // grid * grid
        self.wd = 50
        self.x2 = self.x + self.wd
        self.y2 = self.y + self.wd
        self.pack(can)

    def setImage(self, imgfile):
        self.img = tk.PhotoImage(file=imgfile)

    def setController(self, controller):
        self.controller = controller

    def pack(self, cvs):
        if self.color != None:
            self.cvrect = cvs.create_rectangle((self.x), (self.y), (self.x + 25), (self.y + 25), fill=(self.color))
            self.cvtxt = cvs.create_text((self.x + 12), (self.y + 12), text=(self.caption))
        else:
            self.cvimg = cvs.create_image((self.x), (self.y), anchor='nw', image=(self.img))
            self.cvtxt = cvs.create_text((self.x + 25), (self.y + 55), text=(self.caption))
            if self.controller != None:
                print('color', self.controller[5].color)
                self.cvrect = cvs.create_oval((self.x + 20), (self.y - 10), (self.x + 30), (self.y), fill=(self.controller[5].color), width=1)

    def unpack(self, cvs):
        if self.color != None:
            cvs.delete(self.cvtxt)
            cvs.delete(self.cvrect)
            cvs.delete(self.cvimg)
            self.cvimg = None
            self.cvtxt = None
            self.cvrect = None
        else:
            cvs.delete(self.cvtxt)
            cvs.delete(self.cvimg)
            cvs.delete(self.cvrect)
            self.cvimg = None
            self.cvtxt = None
            self.cvrect = None

    def getData(self):
        data = {}
        data['id'] = self.id
        data['caption'] = self.caption
        data['info'] = self.info
        data['img'] = self.imgstr
        data['x'] = self.x
        data['y'] = self.y
        data['wd'] = self.wd
        data['x2'] = self.x2
        data['y2'] = self.y2
        if self.controller == None:
            data['controller'] = 'None'
        else:
            data['controller'] = self.controller[0]
        return data


class ConfigWindow:

    def __init__(self, sw, w):
        global ctrlist
        self.mainframe = tk.Frame(root, width=(w / 3))
        self.mainframe.place(x=(w / 3), y=50)
        self.itm = {}
        self.iface = sw.iface
        self.id = sw.id
        self.sw = sw.isSwitch()
        self.caption = sw.caption
        self.ctrdata = ['None']
        for ctlr in ctrlist.keys():
            self.ctrdata.append('C' + str(ctrlist[ctlr][0] + 1))
        else:
            print('self.ctrdata', self.ctrdata)
            self.drawFrame()

    def drawFrame(self):
        global state
        global sw
        state = 30
        self.title = tk.Label((self.mainframe), text=(self.caption))
        self.title.pack()
        tabpane = ttk.Notebook((self.mainframe), height=120, width=220)
        tabpane.pack()
        self.tab = {}
        for i in range(len(self.iface)):
            self.tab[i] = tk.Frame(tabpane)
            tabpane.add((self.tab[i]), text=('P-' + str(i)))
            ctr = 0
            for k in self.iface[i].keys():
                if k != 'gateway':
                    if k != 'ipv6':
                        self.itm['lbl' + str(i) + k] = tk.Label((self.tab[i]), text=k)
                        self.itm['lbl' + str(i) + k].place(x=0, y=(22 * (ctr + 1)))
                        self.itm['txt' + str(i) + k] = tk.Entry(self.tab[i])
                        self.itm['txt' + str(i) + k].insert('0', self.iface[i][k])
                        self.itm['txt' + str(i) + k].place(x=50, y=(22 * (ctr + 1)))
                        ctr += 1

        else:
            self.endframe = tk.Frame(self.mainframe)
            self.endframe.pack()
            self.lblport = tk.Label((self.endframe), text='Controller')
            self.lblport.pack(side='left')
            print('self.ctrdata', self.ctrdata)
            self.cmb = ttk.Combobox((self.endframe), width=12)
            self.cmb['values'] = self.ctrdata
            if sw[self.id].controller != None:
                self.cmb.current(sw[self.id].controller[0])
            else:
                self.cmb.current(0)
            self.cmb.pack(side='left')
            self.btnClose = tk.Button((self.mainframe), text='Close', command=(self.closewindow))
            self.btnClose.pack(side='right')
            self.btnSave = tk.Button((self.mainframe), text='Save', command=(self.saveconfig))
            self.btnSave.pack(side='right')

    def saveconfig(self):
        for i in range(len(self.iface)):
            for k in self.iface[i].keys():
                while self.sw:
                    if k != 'gateway':
                        while k != 'ipv6':
                            self.iface[i][k] = self.itm['txt' + str(i) + k].get()

                        self.iface[i][k] = self.itm['txt' + str(i) + k].get()

        else:
            sw[self.id].iface = self.iface
            if self.cmb.get() == 'None':
                sw[self.id].setController(None)
            else:
                ctrval = int(self.cmb.get()[1:2]) - 1
                sw[self.id].setController(ctrlist[ctrval])

    def closewindow(self):
        global state
        self.saveconfig()
        state = 0
        self.mainframe.destroy()


class ConfigController:

    def __init__(self, ctrdata, w):
        self.mainframe = tk.Frame(root, width=(w / 3 + 50))
        self.mainframe.place(x=(w / 3), y=50)
        self.id = ctrdata[0]
        self.caption = 'Controller ' + str(ctrdata[0] + 1)
        self.ip = ctrdata[3]
        self.port = ctrdata[4]
        self.drawFrame()

    def drawFrame(self):
        global state
        state = 30
        self.title = tk.Label((self.mainframe), text=(self.caption))
        self.title.pack()
        self.frameIP = tk.Frame(self.mainframe)
        self.frameIP.pack()
        self.lblIP = tk.Label((self.frameIP), text='IP')
        self.lblIP.pack()
        self.txtIP = tk.Entry((self.frameIP), text=(self.ip), width=10)
        self.txtIP.delete(0, 'end')
        self.txtIP.insert(0, self.ip)
        self.txtIP.pack()
        self.lblport = tk.Label((self.frameIP), text='Port')
        self.lblport.pack()
        self.txtport = tk.Entry((self.frameIP), text=(self.port), width=10)
        self.txtport.delete(0, 'end')
        self.txtport.insert(0, self.port)
        self.txtport.pack()
        self.btnSave = tk.Button((self.mainframe), text='Save', command=(self.saveconfig))
        self.btnSave.pack(side='left')
        self.btnClose = tk.Button((self.mainframe), text='Close', command=(self.closewindow))
        self.btnClose.pack(side='left')

    def saveconfig(self):
        ctrdata = ctrlist[self.id]
        ctrlist[self.id] = [ctrdata[0], ctrdata[1], ctrdata[2], self.txtIP.get(), self.txtport.get(), ctrdata[5]]

    def closewindow(self):
        global state
        self.saveconfig()
        state = 0
        self.mainframe.destroy()


class Switch(Node):

    def __init__(self, **kwargs):
        (super().__init__)(**kwargs)
        self.type = kwargs['type']
        self.iface = []
        self.link = []
        self.maxiface = kwargs['maxiface']
        for i in range(self.maxiface):
            self.link.append([None, None])
            self.iface.append({ 'iptype': 'ipv4', 'ipv4': '0.0.0.0', 'ipv6': '',
              'mac': '00:00:00:00:00:00',  'subnet': '24',  'gateway': ''})

    def __str__(self):
        return str(self.id) + '-' + self.caption

    def isSwitch(self):
        return self.type.find('Switch') > -1

    def getIP(self, ifc):
        ipt = self.iface[ifc]['iptype']
        return self.iface[ifc][ipt]

    def getConfig(self, mode=0):
        data = []
        if self.isSwitch():
            for i in range(len(self.link)):
                if self.link[i][0] != None:
                    data.append([i, self.getIP(i), self.iface[i]['subnet'], self.iface[i]['mac']])

        else:
            pass
        for i in range(len(self.link)):
            if self.link[i][0] != None:
                if mode != 0:
                    data.append([i, self.iface[i]['gateway']])
                else:
                    data.append([i, self.getIP(i), self.iface[i]['subnet'], self.iface[i]['mac']])
        else:
            return (
             self.caption, data)

    def configSwitch(self, ifc, iptype, ipv4, mac, subnet, gateway, ipv6=''):
        if ifc >= 0:
            if ifc < self.maxiface:
                self.iface[ifc]['iptype'] = iptype
                self.iface[ifc]['ipv4'] = ipv4
                self.iface[ifc]['ipv6'] = ipv6
                self.iface[ifc]['mac'] = mac
                self.iface[ifc]['subnet'] = subnet
                self.iface[ifc]['gateway'] = gateway

    def setIP(self, ifc, iptype, ipadr, gateway=''):
        if ifc >= 0:
            if ifc < self.maxiface:
                if self.iface[ifc]['iptype'] == 'ipv4':
                    self.iface[ifc]['ipv4'] = ipadr
                else:
                    self.iface[ifc]['ipv6'] = ipadr
                self.iface[ifc]['gateway'] = gateway

    def getAvailIface(self):
        availifaces = []
        for i in range(self.maxiface):
            if self.link[i][0] == None:
                availifaces.append(i)
        else:
            return availifaces

    def getFirstIface(self):
        availiface = self.getAvailIface
        if len(availiface) > 0:
            return availiface[0]
        return -1

    def addLink(self, ifc, swid, ifnumber):
        self.link[ifc] = [
         swid, ifnumber]

    def getData(self):
        data = super().getData()
        data['type'] = self.type
        data['maxiface'] = self.maxiface
        data['iface'] = self.iface
        data['link'] = self.link
        return data


class PopUp:

    def __init__(self, parent, sw, x, y, state=0):
        self.top = tk.Frame(parent)
        self.top.place(x=x, y=y)
        self.top['borderwidth'] = 2
        self.top['relief'] = 'raised'
        self.framelink = tk.Frame(self.top)
        self.framelink.pack()
        self.id = sw.id
        self.myLabel = tk.Label((self.framelink), text='Port :')
        self.myLabel.pack(side='left')
        self.n = tk.StringVar()
        self.port = ttk.Combobox((self.framelink), width=4, textvariable=(self.n))
        isian = sw.getAvailIface()
        self.port['values'] = isian
        self.port.pack(side='left')
        if state == 0:
            self.mySubmitButton = tk.Button((self.top), text='+ Link', command=(self.sendback), anchor='nw', width=12)
        else:
            self.mySubmitButton = tk.Button((self.top), text='Connect', command=(self.sendback), anchor='nw', width=12)
        self.mySubmitButton.pack()
        if len(isian) > 0:
            self.port.current(0)
            self.mySubmitButton['state'] = 'normal'
        else:
            self.mySubmitButton['state'] = 'disabled'
        self.deleteButton = tk.Button((self.top), text=('Configure ' + str(sw.caption)), command=(self.config), anchor='nw', width=12)
        self.deleteButton.pack()
        self.deleteButton = tk.Button((self.top), text=('Delete ' + str(sw.caption)), command=(self.delete), anchor='nw', width=12)
        self.deleteButton.pack()

    def sendback(self):
        global firstsw
        global secondsw
        global state
        if state == 1:
            firstsw = [
             self.id, int(self.port.get())]
        else:
            secondsw = [
             self.id, int(self.port.get())]
        state += 1
        self.top.destroy()

    def delete(self):
        global can
        global lk
        global selsw
        global state
        for i in range(len(sw[selsw].link)):
            print(selsw, i)
            print(sw[selsw])
            print(sw[selsw].link)
            if sw[selsw].link[i] != None:
                swid, ifid = sw[selsw].link[i]
                print(swid, ifid)
                if swid != selsw:
                    if swid != None:
                        if ifid != None:
                            sw[swid].link[ifid] = [
                             None, None]
            sw[selsw].link[i] = [
             None, None]
        else:
            for sellk in lk.keys():
                if lk[sellk] != None:
                    if not lk[sellk].Aid == selsw:
                        if lk[sellk].Bid == selsw:
                            pass
                    lk[sellk].delete()
                    lk[sellk] = None
            else:
                sw[selsw].unpack(can)
                del sw[selsw]
                state = 0
                self.top.destroy()

    def config(self):
        global mcw
        global state
        global w
        print(state, mcw, sw, selsw, w)
        if state == 1:
            state = 30
            mcw = ConfigWindow(sw[selsw], w)
            self.top.destroy()


class Link:

    def __init__(self, **kwargs):
        self.Aid = kwargs['A']
        self.Bid = kwargs['B']
        self.portA = kwargs['portA']
        self.portB = kwargs['portB']
        self.id = kwargs['id']
        self.name = kwargs['name']
        self.caption = kwargs['caption']
        self.x = -100
        self.y = -100
        self.m = 0
        self.bound = []
        self.cvitem = []

    def __str__(self):
        return str(self.id) + ':S' + str(self.Aid) + '-' + str(self.portA) + ' - ' + 'S' + str(self.Bid) + '-' + str(self.portB)

    def getlink(self, sw):
        return [
         sw[self.Aid].caption, sw[self.Bid].caption]

    def isinside(self, x, y):
        if x > self.bound[0]:
            if x < self.bound[2]:
                if y > self.bound[1]:
                    if y < self.bound[3]:
                        return True
        return False

    def repack(self, sw, can):
        self.delete()
        a = sw[self.Aid].x + 25
        b = sw[self.Aid].y + 25
        c = sw[self.Bid].x + 25
        d = sw[self.Bid].y + 25
        if c - a == 0:
            self.m = 100
        else:
            self.m = (d - b) / (c - a)
        self.x = a + (c - a) // 2
        self.y = b + (d - b) // 2
        self.bound = [self.x - 5, self.y - 5, self.x + 5, self.y + 5]
        self.cvitem.append(can.create_line(a, b, (self.x), (self.y), fill='blue', width=3))
        self.cvitem.append(can.create_line((self.x), (self.y), c, d, fill='blue', width=3))
        self.cvitem.append(can.create_oval((self.bound[0]), (self.bound[1]), (self.bound[2]), (self.bound[3]), fill='grey', outline='blue'))
        if sw[self.Aid].iface[self.portA]['iptype'] == 'ipv4':
            txta = sw[self.Aid].iface[self.portA]['ipv4']
        else:
            txta = sw[self.Aid].iface[self.portA]['ipv6']
        if sw[self.Bid].iface[self.portB]['iptype'] == 'ipv4':
            txtb = sw[self.Bid].iface[self.portB]['ipv4']
        else:
            txtb = sw[self.Bid].iface[self.portB]['ipv6']
        if self.m > -0.6 and self.m < 0.6:
            if a < c:
                acr = [
                 'sw', 'ne']
            else:
                acr = [
                 'ne', 'sw']
            e = (c - a) // 5
            f = (d - b) // 5
            self.cvitem.append(can.create_text((a + e), (b + f), anchor=(acr[0]), text=txta))
            self.cvitem.append(can.create_text((a + 4 * e), (b + 4 * f), anchor=(acr[1]), text=txtb))
        else:
            if b > d:
                acr = [
                 'nw', 'ne']
            else:
                acr = [
                 'ne', 'nw']
            e = (c - a) // 3
            f = (d - b) // 3
            self.cvitem.append(can.create_text((a + e), (b + f), anchor=(acr[0]), text=txta))
            self.cvitem.append(can.create_text((a + 2 * e), (b + 2 * f), anchor=(acr[1]), text=txtb))

    def delete(self):
        for itm in self.cvitem:
            can.delete(itm)
        else:
            self.cvitem = []

    def getData(self):
        data = {}
        data['Aid'] = self.Aid
        data['Bid'] = self.Bid
        data['portA'] = self.portA
        data['portB'] = self.portB
        data['id'] = self.id
        data['name'] = self.name
        data['caption'] = self.caption
        return data


def selectNode():
    curselect = selsw
    if prevsel != -1:
        pass


def checkselect(x, y):
    global selsw
    cursel = selsw
    selsw = -1
    for i in sw.keys():
        if sw[i].isinside(x, y):
            print('inside ', sw[i].id)
            if sw[i].cvimg != None:
                selsw = i
    else:
        if selsw != -1:
            if selsw != cursel:
                prevsel = cursel
        print('selected:', selsw)


def resetLinkcreate():
    global firstsw
    global pp
    global rtline
    global secondsw
    global selsw
    global state
    firstsw = []
    secondsw = []
    state = 0
    selsw = -1
    if pp != None:
        pp.top.destroy()
        pp = None
    can.delete(rtline)
    frameNewItem.move(-100, -100)


def lc(event):
    global ctrlk
    global pp
    global state
    print(event.x, event.y)
    if state == 0:
        checkselect(event.x, event.y)
        if selsw >= 0:
            sw[selsw].unpack(can)
            sw[selsw].pack(can)
        else:
            resetLinkcreate()
    else:
        checkselect(event.x, event.y)
        if selsw >= 0 and state == 2:
            state = 3
            pp = PopUp(root, sw[selsw], event.x, event.y, state)
            root.wait_window(pp.top)
            print('dest:', secondsw)
            if len(secondsw) > 0:
                lk[ctrlk] = newLink(A=(firstsw[0]), portA=(firstsw[1]), B=(secondsw[0]), portB=(secondsw[1]))
                sw[firstsw[0]].unpack(can)
                sw[firstsw[0]].pack(can)
                sw[secondsw[0]].unpack(can)
                sw[secondsw[0]].pack(can)
                sw[firstsw[0]].link[firstsw[1]] = secondsw
                sw[secondsw[0]].link[secondsw[1]] = firstsw
                resetLinkcreate()
            else:
                resetLinkcreate()
        else:
            resetLinkcreate()


def checklink(lk, x, y):
    sellk = -1
    for i in lk.keys():
        if lk[i] != None:
            if lk[i].isinside(x, y):
                sellk = i
    else:
        return sellk


def rc(event):
    global curpos
    global pp
    global state
    if state == 0:
        sellk = checklink(lk, event.x, event.y)
        if sellk > -1:
            sw[lk[sellk].Aid].link[lk[sellk].portA] = [None, None]
            sw[lk[sellk].Bid].link[lk[sellk].portB] = [None, None]
            lk[sellk].delete()
            lk[sellk] = None
        else:
            print(event.x, event.y, state)
            curpos = [event.x, event.y]
            checkselect(event.x, event.y)
            if selsw >= 0 and state == 0:
                state = 1
                pp = PopUp(root, sw[selsw], event.x, event.y)
                root.wait_window(pp.top)
                print('start:', firstsw)
            else:
                state = 20
                frameNewItem.move(event.x, event.y)
    else:
        if state >= 30:
            resetLinkcreate()


def selectcontroller(event):
    global ctrcontroller
    global ctrcw
    if ctrcw != None:
        ctrcw.mainframe.destroy()
        ctrcw = None
    print(event.x, event.y)
    if event.y > 10:
        if event.y < 35:
            if event.x > 10:
                if event.x < 10 + 25 * ctrcontroller:
                    ctrid = (event.x - 10) // 25
                    ctrcw = ConfigController(ctrlist[ctrid], w)


def lmdrag(event):
    global state
    if state == 0:
        state = 10
        checkselect(event.x, event.y)
        while state == 10:
            while selsw >= 0:
                for sellk in lk.keys():
                    if lk[sellk] != None:
                        updatelk = False
                        if lk[sellk].Aid == selsw:
                            updatelk = True
                            osw = lk[sellk].Bid
                        else:
                            if lk[sellk].Bid == selsw:
                                updatelk = True
                                osw = lk[sellk].Aid
                        if updatelk:
                            lk[sellk].repack(sw, can)
                            sw[osw].move2(sw[osw].x, sw[osw].y, can)

        sw[selsw].move2(event.x - 25, event.y - 25, can)


def lmrelease(event):
    global state
    if state == 10:
        state = 0


def deleteItem():
    print(event.x, event.y)
    checkselect(event.x, event.y)
    print('delete', selsw)
    sw[selsw].unpack(can)


def mm(event):
    global rtline
    if state == 2:
        can.delete(rtline)
        rtline = can.create_line((curpos[0]), (curpos[1]), (event.x), (event.y), fill='red', width=1)


def getrnd():
    return random.randint(0, h // 2)


def newSwitch(**kwargs):
    global ctrsw
    global ctrtypesw
    x = getrnd()
    y = getrnd()
    typesw = 'router'
    if 'x' in kwargs.keys():
        x = kwargs['x']
    if 'y' in kwargs.keys():
        y = kwargs['y']
    if 'type' in kwargs.keys():
        typesw = kwargs['type']
    sw[ctrsw] = Switch(id=ctrsw, caption=('s' + str(ctrtypesw + 1)), img=(typesw + '.png'), x=x, y=y, type=typesw, maxiface=8, controller=None)
    for i in range(sw[ctrsw].maxiface):
        ipv4 = '10.' + str(ctrtypesw + 1) + '.' + str(i) + '.1'
        if i < 10:
            ifid = '0' + str(i)
        else:
            ifid = str(i)
        swid = ctrtypesw + 1
        if swid < 10:
            swstr = '0' + str(swid)
        else:
            swstr = str(swid)
        mac = '00:00:00:' + swstr + ':00:' + ifid
        sw[ctrsw].configSwitch(i, 'ipv4', ipv4, mac, '24', '', ipv6='')
    else:
        sw[ctrsw].pack(can)
        ctrsw += 1
        ctrtypesw += 1


def newHost(**kwargs):
    global ctrsw
    global ctrtypehost
    x = getrnd()
    y = getrnd()
    if 'x' in kwargs.keys():
        x = kwargs['x']
    if 'y' in kwargs.keys():
        y = kwargs['y']
    sw[ctrsw] = Switch(id=ctrsw, caption=('h' + str(ctrtypehost + 1)), img='client.png', x=x, y=y, type='host', maxiface=2)
    for i in range(sw[ctrsw].maxiface):
        ipv4 = '10.' + str(ctrtypehost + 1) + '.0.' + str(100 + i)
        if i < 10:
            ifid = '0' + str(i)
        else:
            ifid = str(i)
        hostid = ctrtypehost + 1
        if hostid < 10:
            hoststr = '0' + str(hostid)
        else:
            hoststr = str(hostid)
        mac = '00:00:00:00:' + hoststr + ':' + ifid
        sw[ctrsw].configSwitch(i, 'ipv4', ipv4, mac, '24', '', ipv6='')
    else:
        sw[ctrsw].pack(can)
        ctrsw += 1
        ctrtypehost += 1


def newController(**kwargs):
    global ctrcontroller
    global ctrsw
    color = ['red','lightgreen','lightblue','yellow','magenta','cyan']
    x = getrnd()
    y = getrnd()
    if 'x' in kwargs.keys():
        x = kwargs['x']
    if 'y' in kwargs.keys():
        y = kwargs['y']
    name = 'C' + str(ctrcontroller + 1)
    imgstr = 'kotak.png'
    ip = '127.0.0.1'
    if 'ip' in kwargs.keys():
        ip = kwargs['ip']
    port = '6633'
    if 'port' in kwargs.keys():
        port = kwargs['port']
    x = 10 + ctrcontroller * 25
    y = 10
    newctr = Switch(id=ctrsw, caption=name, img=imgstr, x=x, y=y, type='controller', maxiface=1, color=(color[ctrcontroller % 6]))
    ctrlist[ctrcontroller] = [ctrcontroller,x,y,ip,port,newctr]
    ctrlist[ctrcontroller][5].pack(can)
    ctrsw += 1
    ctrcontroller += 1


def newLink(**kwargs):
    global ctrlk
    Aid = kwargs['A']
    Bid = kwargs['B']
    pA = kwargs['portA']
    pB = kwargs['portB']
    caption = 'L(' + str(Aid + 1) + '-' + str(Bid + 1) + ')'
    lk[ctrlk] = Link(id=ctrlk, name=caption, caption=caption, A=Aid, B=Bid, portA=pA, portB=pB)
    isswa, isswb = sw[Aid].isSwitch(), sw[Bid].isSwitch()
    if not isswa or isswb:
        ipadr = sw[Bid].getIP(pB).split('.')
        ipadr[3] = str(100 + pA)
        ipstr = '.'.join(ipadr)
        sw[Aid].setIP(pA, 'ipv4', ipstr, sw[Bid].getIP(pB))
    else:
        if isswa:
            if not isswb:
                ipadr = sw[Aid].getIP(pA).split('.')
                ipadr[3] = str(100 + pB)
                ipstr = '.'.join(ipadr)
                sw[Bid].setIP(pB, 'ipv4', ipstr, sw[Aid].getIP(pA))
    lk[ctrlk].repack(sw, can)
    print('create new link', ctrlk, lk[ctrlk])
    ctrlk += 1


def newLabel(**kwargs):
    global ctrlbl
    x = kwargs['x']
    y = kwargs['y']
    name = askstring('New Label', 'Label caption:')
    if name == '':
        name = '<empty string>'
    newlabel = DnDLabel(can, text=name, font=('Purisa', 12), bg='white')
    lbl[ctrlbl] = [name, x, y, newlabel]
    lbl[ctrlbl][3].setid(ctrlbl)
    lbl[ctrlbl][3].place(x=x, y=y)
    ctrlbl += 1


root = tk.Tk()
root.title('MiTE: Mininet Topology Editor for SDN')
w, h = root.winfo_screenwidth() * 3 // 4, root.winfo_screenheight() * 3 // 4
dw, dh = root.winfo_screenwidth() * 1 // 8, root.winfo_screenheight() * 1 // 8
root.geometry('%dx%d+%d+%d' % (w, h, dw, 50))
tabpane = ttk.Notebook(root, height=h, width=w)
tabpane.pack()
tab1 = ttk.Frame(tabpane)
tabpane.add(tab1, text=' Topology Editor ')
can = tk.Canvas(tab1, bg='white', height=h, width=w)
can.pack()
can.bind('<Button-1>', lc)
can.bind('<Double-Button-1>', selectcontroller)
can.bind('<Button-3>', rc)
can.bind('<B1-Motion>', lmdrag)
can.bind('<ButtonRelease-1>', lmrelease)
can.bind('<Motion>', mm)
projectname = ''
pp = None
state = 0
initfolder = '/'
mcw = None
ctrcw = None
lbl = {}
ctrlbl = 0
sw = {}
ctrlist = {}
ctrsw = 0
ctrtypesw = 0
ctrtypehost = 0
ctrcontroller = 0
lk = {}
ctrlk = 0
selsw = -1
prevsel = -1
firstsw = []
secondsw = []
curpos = []
rtline = can.create_line((-10), (-10), (-70), (-70), fill='red', width=1)

def resetPoject():
    global ctrlk
    global ctrsw
    global ctrtypehost
    global ctrtypesw
    global lbl
    global lk
    global sw
    can.delete('all')
    sw = {}
    lk = {}
    ctrsw = 0
    ctrlk = 0
    ctrtypesw = 0
    ctrtypehost = 0
    ctrlbl = 0
    for k in lbl.keys():
        if lbl[k] != None:
            lbl[k][3].destroy()
            lbl[k] = []
    else:
        lbl = {}


def loadProject():
    global ctrcontroller
    global ctrlbl
    global ctrlist
    global ctrlk
    global ctrsw
    global initfolder
    global projectname
    resetPoject()
    fname = filedialog.askopenfilename(initialdir=initfolder, title='Select file', filetypes=(('json files', '*.json'),
                                                                                              ('all files', '*.*')))
    foldername = '/'.join(fname.split('/')[:-1])
    initfolder = foldername
    initfolder
    if len(fname) < 3:
        return 'Error loading the project'
    print('fname:', fname)
    fstr = fname.split('/')
    projectname = fstr[len(fstr) - 1].split('.')[0]
    root.title('Network Studio - ' + projectname)
    alldata = json.load(open(fname, 'r'))
    print(alldata)
    swlist = alldata['sw']
    for swl in swlist:
        swid = swl['id']
        sw[swid] = Switch(id=swid, caption=(swl['caption']), img=(swl['img']), x=(swl['x']), y=(swl['y']), type=(swl['type']), maxiface=(swl['maxiface']))
        ifacedata = swl['iface']
        for i in range(len(ifacedata)):
            sw[swid].iface[i]['iptype'] = ifacedata[i]['iptype']
            sw[swid].iface[i]['ipv4'] = ifacedata[i]['ipv4']
            sw[swid].iface[i]['ipv6'] = ifacedata[i]['ipv6']
            sw[swid].iface[i]['mac'] = ifacedata[i]['mac']
            sw[swid].iface[i]['subnet'] = ifacedata[i]['subnet']
            sw[swid].iface[i]['gateway'] = ifacedata[i]['gateway']
        else:
            if swid > ctrsw:
                ctrsw = swid

    else:
        ctrsw += 1
        lklist = alldata['lk']
        for lkl in lklist:
            lk[lkl['id']] = Link(id=(lkl['id']), name=(lkl['name']), caption=(lkl['caption']), A=(lkl['Aid']), B=(lkl['Bid']), portA=(lkl['portA']), portB=(lkl['portB']))
            lk[lkl['id']].repack(sw, can)
            sw[lkl['Aid']].link[lkl['portA']] = [lkl['Bid'], lkl['portB']]
            sw[lkl['Bid']].link[lkl['portB']] = [lkl['Aid'], lkl['portA']]
            print(lkl['id'], lk[lkl['id']])
            if lkl['id'] > ctrlk:
                ctrlk = lkl['id']
        else:
            ctrlk += 1
            lbllist = alldata['lbl']
            print('lbllist:')

    for lb in lbllist:
        newlabel = DnDLabel(can, text=(lb[0]), font=('Purisa', 12), bg='white')
        lbl[ctrlbl] = [lb[0], lb[1], lb[2], newlabel]
        lbl[ctrlbl][3].setid(i)
        lbl[ctrlbl][3].place(x=(lb[1]), y=(lb[2]))
        ctrlbl += 1
    else:
        ctrcontroller = 0
        ctrlist = {}
        print('ctrlist:')
        datactr = {}
        for ctr in alldata['ctr']:
            datactr[ctr[0]] = ctr
        else:
            for i in range(len(datactr)):
                newController(x=(datactr[i][1]), y=(datactr[i][2]), ip=(datactr[i][3]), port=(datactr[i][4]))
            else:
                for swl in swlist:
                    swid = swl['id']
                    ctrid = swl['controller']
                    if ctrid != 'None':
                        ctrid = int(ctrid)
                        sw[swid].setController(ctrlist[ctrid])
                else:
                    for swl in swlist:
                        sw[swl['id']].pack(can)


def RandomProject():
    resetPoject()
    root.title('Network Studio - New Project')


def convertBMV2Mininet():
    global initfolder
    print('convertBMV2Mininet')
    foldername = filedialog.askdirectory()
    initfolder = foldername
    filename = 'mininet_p4.py'
    print(foldername, initfolder, filename)
    if len(filename) < 3:
        return 'Error saving the project'
    if filename.find('py') < 0:
        filename = filename + '.py'
    print('fname:', filename)
    strdata = getAllConfig(sw, lk)
    with open(filename, 'w') as f:
        f.write(strdata)
    import os
    if not os.path.exists('mn'):
        os.mkdir('mn')
    with open('mn/__init__.py', 'w') as fo:
        fo.write('')
    with open('mn/p4_mininet.py', 'w') as fo:
        fo.write(p4str)
    allfiles = [filename, 'mn/__init__.py', 'mn/p4_mininet.py']
    zipallfiles(foldername, allfiles)


def convertRyuMininet():
    global initfolder
    fname = filedialog.asksaveasfilename(initialdir=initfolder, title='Select file', filetypes=(('python files', '*.py'),
                                                                                                ('all files', '*.*')))
    foldername = '/'.join(fname.split('/')[:-1])
    initfolder = foldername
    if len(fname) < 3:
        return 'Error saving the project'
    if fname.find('py') < 0:
        fname = fname + '.py'
    strdata = genConfig(sw, lk, ctrlist)
    with open(fname, 'w') as f:
        f.write(strdata)


def showOF():
    tk.messagebox.showinfo('OpenFlow Menu:', 'Parse ryu controller application,\nArrange the OpenFlow tables,\nCreate application for the Controller\n')


def showHelp():
    tk.messagebox.showinfo('How to use:', 'Just start by right clicking the canvas.\nChoose the available menus,\nAnd save, open, and export your creation.\nBeware to not right clicking the link and label,\nOr it will be removed!')


def saveProject():
    global initfolder
    global projectname
    fname = filedialog.asksaveasfilename(initialdir=initfolder, title='Select file', filetypes=(('json files', '*.json'),
                                                                                                ('all files', '*.*')))
    foldername = '/'.join(fname.split('/')[:-1])
    initfolder = foldername
    if len(fname) < 3:
        return 'Error saving the project'
    if fname.find('json') < 0:
        fname = fname + '.json'
    print('fname:', fname)
    fstr = fname.split('/')
    projectname = fstr[len(fstr) - 1].split('.')[0]
    root.title('Network Studio - ' + projectname)
    alldata = {}
    alldata['sw'] = []
    for sid in sw.keys():
        print(sw[sid].getData())
        alldata['sw'].append(sw[sid].getData())
    else:
        alldata['lk'] = []
        print(lk.keys())
        for lid in lk.keys():
            if lk[lid] != None:
                print(lid)
                print(lk[lid])
                alldata['lk'].append(lk[lid].getData())
        else:
            alldata['lbl'] = []
            print(lbl)
            for lb in lbl.keys():
                print(lbl[lb])
                if lbl[lb] != None:
                    alldata['lbl'].append([lbl[lb][0], lbl[lb][3].winfo_rootx() - can.winfo_rootx(), lbl[lb][3].winfo_rooty() - can.winfo_rooty()])
            else:
                alldata['ctr'] = []
                for ctr in ctrlist.keys():
                    alldata['ctr'].append(ctrlist[ctr][:-1])
                else:
                    with open(fname, 'w') as fwrite:
                        fwrite.write(json.dumps(alldata))


def quit():
    root.destroy()


bar = tk.Menu(root)
fileMenu = tk.Menu(bar, tearoff=0)
fileMenu.add_command(label='New Project', command=RandomProject)
fileMenu.add_command(label='Open Project', command=loadProject)
fileMenu.add_command(label='Save Project', command=saveProject)
exportMenu = tk.Menu(fileMenu, tearoff=0)
exportMenu.add_command(label='Export to BMv2 Mininet (P4)', command=convertBMV2Mininet)
exportMenu.add_command(label='Export to Ryu Mininet (OF)', command=convertRyuMininet)
fileMenu.add_cascade(label='Export', menu=exportMenu)
fileMenu.add_command(label='Exit', command=quit)
bar.add_cascade(label='File', menu=fileMenu)
bar.add_command(label='Help', command=showHelp)
root.config(menu=bar)

class AdderMenu:

    def __init__(self, w):
        self.frameNewItem = tk.Frame(tab1, height=(h - 50), width=w)
        self.frameNewItem.place(x=(-100), y=(-100))
        self.frameNewItem['borderwidth'] = 2
        self.frameNewItem['relief'] = 'raised'
        lblNewItem = tk.Label((self.frameNewItem), text='New Item', width=10)
        lblNewItem.pack()
        btnNewOF = tk.Button((self.frameNewItem), text='OF Switch', command=(self.AddNewOFSwitch), width=10, anchor='nw')
        btnNewOF.pack()
        btnNewP4 = tk.Button((self.frameNewItem), text='P4 Switch', command=(self.AddNewP4Switch), width=10, anchor='nw')
        btnNewP4.pack()
        btnNewHost = tk.Button((self.frameNewItem), text='Host', command=(self.AddNewHost), width=10, anchor='nw')
        btnNewHost.pack()
        btnNewController = tk.Button((self.frameNewItem), text='Controller', command=(self.AddNewController), width=10, anchor='nw')
        btnNewController.pack()
        btnNewLabel = tk.Button((self.frameNewItem), text='Label', command=(self.AddNewLabel), width=10, anchor='nw')
        btnNewLabel.pack()

    def move(self, x, y):
        self.frameNewItem.place(x=x, y=y)
        self.curpos = [x, y]

    def AddNewOFSwitch(self):
        newSwitch(x=(self.curpos[0]), y=(self.curpos[1]), type='OFSwitch')
        resetLinkcreate()

    def AddNewP4Switch(self):
        newSwitch(x=(self.curpos[0]), y=(self.curpos[1]), type='P4Switch')
        resetLinkcreate()

    def AddNewHost(self):
        newHost(x=(self.curpos[0]), y=(self.curpos[1]))
        resetLinkcreate()

    def AddNewController(self):
        newController(x=(self.curpos[0]), y=(self.curpos[1]))
        resetLinkcreate()

    def AddNewLabel(self):
        newLabel(x=(self.curpos[0]), y=(self.curpos[1]))
        resetLinkcreate()


frameNewItem = AdderMenu(w)
root.mainloop()
# okay decompiling MiTE4SDN.exe_extracted/MiTE4SDN.pyc
