# decompyle3 version 3.9.0
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.8.0 (default, Nov 23 2019, 05:36:56) 
# [GCC 8.3.0]
# Embedded file name: GUIp4\ryutemplate.py


def genSwitch(sw, ctrlist):
    hostconfig = ''
    swconfig = ''
    ctrconfig1 = ''
    ctrconfig2 = ''
    swlist = []
    swctr = []
    for i in ctrlist.keys():
        idctr = ctrlist[i][0]
        ctrconfig1 += '\tc' + str(idctr) + " = net.addController('c" + str(idctr) + "', controller=RemoteController, port=6633)" + '\n'
        ctrconfig2 += '\tc' + str(idctr) + '.start()' + '\n'
    else:
        for id in sw.keys():
            if not sw[id].isSwitch():
                hostconfig += '\t' + sw[id].caption + "  = net.addHost('" + sw[id].caption + "', ip = '" + sw[id].iface[0][sw[id].iface[0]['iptype']] + "', mac = '" + sw[id].iface[0]['mac'] + "', defaultRoute='via " + sw[id].iface[0]['gateway'] + "' )\n"
            else:
                swconfig += '\t' + sw[id].caption + " = net.addSwitch('" + sw[id].caption + "')\n"
                swlist.append(sw[id].caption)
                while sw[id].controller == None:
                    swctr.append('')

                swctr.append('c' + str(sw[id].controller[0]))
        else:
            return (
             hostconfig, swconfig, swlist, swctr, ctrconfig1, ctrconfig2)


def genLink(lk, sw):
    netstr = ''
    for l in lk.keys():
        if lk[l] != None:
            swa = lk[l].Aid
            swb = lk[l].Bid
            netstr += '\tnet.addLink( ' + sw[swa].caption + ', ' + sw[swb].caption + ", delay = '1ms')\n"
    else:
        return netstr


def genConfig(sw, lk, ctrlist):
    print(sw, lk, ctrlist)
    netconfig = "from mininet.cli import CLI\nfrom mininet.net import Mininet\nfrom mininet.node import RemoteController, OVSSwitch\nfrom mininet.link import TCLink\n\nif '__main__' == __name__:\n"
    netconfig += '\tnet = Mininet(controller=RemoteController, switch=OVSSwitch, link=TCLink, autoSetMacs = True)\n'
    hostconfig, swconfig, swlist, swctr, ctrconfig1, ctrconfig2 = genSwitch(sw, ctrlist)
    netconfig += ctrconfig1
    netconfig += hostconfig
    netconfig += swconfig
    netconfig += genLink(lk, sw)
    netconfig += '\tnet.build()\n'
    netconfig += ctrconfig2
    for i in range(len(swlist)):
        if swctr[i] != '':
            netconfig += '\t' + swlist[i] + '.start([' + swctr[i] + '])\n'
            netconfig += '\t' + swlist[i] + ".cmd( 'ovs-vsctl set Bridge " + swlist[i] + " protocols=OpenFlow13')\n"
    else:
        netconfig += '\tCLI(net)\n'
        netconfig += '\tnet.stop()\n'
        return netconfig
# okay decompiling MiTE4SDN.exe_extracted/PYZ-00.pyz_extracted/ryutemplate.pyc
