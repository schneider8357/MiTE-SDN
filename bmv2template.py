# decompyle3 version 3.9.0
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.8.0 (default, Nov 23 2019, 05:36:56) 
# [GCC 8.3.0]
# Embedded file name: GUIp4\bmv2template.py
p4str = '\nfrom mininet.net import Mininet\nfrom mininet.node import Switch, Host\nfrom mininet.log import setLogLevel, info, error, debug\nfrom mininet.moduledeps import pathCheck\nfrom sys import exit\nimport os\nimport tempfile\nimport socket\n\n\nclass P4Host(Host):\n    def config(self, **params):\n        r = super(Host, self).config(**params)\n\n        self.defaultIntf().rename("eth0")\n\n        for off in ["rx", "tx", "sg"]:\n            cmd = "/sbin/ethtool --offload eth0 %s off" % off\n            self.cmd(cmd)\n\n        # disable IPv6\n        self.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")\n        self.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")\n        self.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")\n\n        return r\n\n    def describe(self):\n        print "**********"\n        print self.name\n        print "default interface: %s\t%s\t%s" %(\n            self.defaultIntf().name,\n            self.defaultIntf().IP(),\n            self.defaultIntf().MAC()\n        )\n        print "**********"\n\nclass P4Switch(Switch):\n    """P4 virtual switch"""\n    device_id = 0\n\n    def __init__(self, name, sw_path = None, json_path = None,\n                 thrift_port = None,\n                 pcap_dump = False,\n                 log_console = False,\n                 verbose = False,\n                 device_id = None,\n                 enable_debugger = False,\n                 **kwargs):\n        Switch.__init__(self, name, **kwargs)\n        assert(sw_path)\n        assert(json_path)\n        # make sure that the provided sw_path is valid\n        pathCheck(sw_path)\n        # make sure that the provided JSON file exists\n        if not os.path.isfile(json_path):\n            error("Invalid JSON file.\n")\n            exit(1)\n        self.sw_path = sw_path\n        self.json_path = json_path\n        self.verbose = verbose\n        logfile = "/tmp/p4s.{}.log".format(self.name)\n        self.output = open(logfile, \'w\')\n        self.thrift_port = thrift_port\n        self.pcap_dump = pcap_dump\n        self.enable_debugger = enable_debugger\n        self.log_console = log_console\n        if device_id is not None:\n            self.device_id = device_id\n            P4Switch.device_id = max(P4Switch.device_id, device_id)\n        else:\n            self.device_id = P4Switch.device_id\n            P4Switch.device_id += 1\n        self.nanomsg = "ipc:///tmp/bm-{}-log.ipc".format(self.device_id)\n\n    @classmethod\n    def setup(cls):\n        pass\n\n    def check_switch_started(self, pid):\n        """While the process is running (pid exists), we check if the Thrift\n        server has been started. If the Thrift server is ready, we assume that\n        the switch was started successfully. This is only reliable if the Thrift\n        server is started at the end of the init process"""\n        while True:\n            if not os.path.exists(os.path.join("/proc", str(pid))):\n                return False\n            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n            sock.settimeout(0.5)\n            result = sock.connect_ex(("localhost", self.thrift_port))\n            if result == 0:\n                return  True\n\n    def start(self, controllers):\n        "Start up a new P4 switch"\n        info("Starting P4 switch {}.\n".format(self.name))\n        args = [self.sw_path]\n        for port, intf in self.intfs.items():\n            if not intf.IP():\n                args.extend([\'-i\', str(port) + "@" + intf.name])\n        if self.pcap_dump:\n            args.append("--pcap")\n            # args.append("--useFiles")\n        if self.thrift_port:\n            args.extend([\'--thrift-port\', str(self.thrift_port)])\n        if self.nanomsg:\n            args.extend([\'--nanolog\', self.nanomsg])\n        args.extend([\'--device-id\', str(self.device_id)])\n        P4Switch.device_id += 1\n        args.append(self.json_path)\n        if self.enable_debugger:\n            args.append("--debugger")\n        if self.log_console:\n            args.append("--log-console")\n        logfile = "/tmp/p4s.{}.log".format(self.name)\n        info(\' \'.join(args) + "\n")\n\n        pid = None\n        with tempfile.NamedTemporaryFile() as f:\n            # self.cmd(\' \'.join(args) + \' > /dev/null 2>&1 &\')\n            self.cmd(\' \'.join(args) + \' >\' + logfile + \' 2>&1 & echo $! >> \' + f.name)\n            pid = int(f.read())\n        debug("P4 switch {} PID is {}.\n".format(self.name, pid))\n        if not self.check_switch_started(pid):\n            error("P4 switch {} did not start correctly.\n".format(self.name))\n            exit(1)\n        info("P4 switch {} has been started.\n".format(self.name))\n\n    def stop(self):\n        "Terminate P4 switch."\n        self.output.flush()\n        self.cmd(\'kill %\' + self.sw_path)\n        self.cmd(\'wait\')\n        self.deleteIntfs()\n\n    def attach(self, intf):\n        "Connect a data port"\n        assert(0)\n\n    def detach(self, intf):\n        "Disconnect a data port"\n        assert(0)'

def zipallfiles(destfolder, fnamelist):
    print(fnamelist)
    from zipfile import ZipFile
    with ZipFile(destfolder + '/mininet_p4.zip', 'w') as zipObj:
        for fname in fnamelist:
            zipObj.write(fname)


header = 'import sys\nsys.path.append(\'../\')\nfrom mn.p4_mininet import P4Switch, P4Host\nfrom mininet.topo import Topo\nfrom mininet.net import Mininet\nfrom mininet.log import setLogLevel, info\nfrom mininet.cli import CLI\n\nimport argparse\n\nparser = argparse.ArgumentParser(description=\'Mininet demo\')\nparser.add_argument(\'--behavioral-exe\', help=\'Path to behavioral executable\', type=str, action="store", required=True)\nparser.add_argument(\'--json\', help=\'Path to JSON config file\', type=str, action="store", required=True)\nargs = parser.parse_args()\n\nclass DemoTopo(Topo):\n\t"Demo topology"\n\n\tdef __init__(self, sw_path, json_path, **opts):\n\t\t# Initialize topology and default options\n'
mainstr1 = '\ndef main():\n\ttopo = DemoTopo(args.behavioral_exe, args.json)\n\n\tnet = Mininet(topo=topo, host=P4Host, switch=P4Switch, controller=None)\n\tnet.start()\n'
mainstr2 = '\n\tprint "Ready !"\n\n\tCLI(net)\n\n\tnet.stop()\n'
mainstr0 = "\nif __name__ == '__main__':\n\tsetLogLevel('info')\n\tmain()\n"

def getsw(swlist):
    print(swlist)
    ctrport = 9090
    strsw = '\t\tTopo.__init__(self, **opts)\n'
    for swid in swlist:
        strsw += '\t\t' + swid + " = self.addSwitch('" + swid + "'"
        strsw += ',sw_path=sw_path,json_path=json_path,thrift_port=' + str(ctrport) + ')\n'
        ctrport += 1
    else:
        return strsw


def gethost(hostdata):
    strhost = ''
    for host in hostdata.keys():
        for hdata in hostdata[host]:
            strhost += '\t\t' + host + " = self.addHost('" + host + '\', ip="' + hdata[1] + '/' + hdata[2] + '", mac=\'' + hdata[3] + "')\n"

    else:
        return strhost


def genlink(linkdata):
    linkstr = ''
    for lk in linkdata:
        linkstr += '\t\tself.addLink(' + lk[0] + ',' + lk[1] + ')\n'
    else:
        return linkstr


def genSWConfig(swdata):
    configstr = ''
    for sid in swdata.keys():
        configstr += '\t' + sid + " = net.get('" + sid + "')\n"
        for ifc in swdata[sid]:
            configstr += '\t' + sid + ".setIP('" + ifc[1] + '/' + ifc[2] + "', intf = '" + sid + '-eth' + str(ifc[0] + 1) + "')\n"
            configstr += '\t' + sid + ".setMAC('" + ifc[3] + "', intf = '" + sid + '-eth' + str(ifc[0] + 1) + "')\n"

    else:
        return configstr


def genHostConfig(hostdata):
    configstr = ''
    for sid in hostdata.keys():
        configstr += '\t' + sid + " = net.get('" + sid + "')\n"
        for ifc in hostdata[sid]:
            configstr += '\t' + sid + '.setDefaultRoute("dev eth' + str(ifc[0]) + ' via ' + ifc[1] + '")\n'

    else:
        return configstr


def getAllConfig(sw, lk):
    swlist = []
    swdata = {}
    hostdata = {}
    hdata = {}
    linkdata = []
    for k in sw.keys():
        if sw[k].isSwitch():
            swlist.append(sw[k].caption)
            id, lst = sw[k].getConfig()
            swdata[id] = lst
        else:
            id, lst = sw[k].getConfig(1)
            print(id, lst)
            hostdata[id] = lst
            id, lst = sw[k].getConfig()
            print(id, lst)
            hdata[id] = lst
    else:
        print('lk:', lk)
        for l in lk.keys():
            if lk[l] != None:
                print('l:', l)
                swa = sw[lk[l].Aid].caption
                swb = sw[lk[l].Bid].caption
                linkdata.append([swa, swb])
        else:
            component = getsw(swlist) + gethost(hdata) + genlink(linkdata)
            config = genSWConfig(swdata) + genHostConfig(hostdata)
            return header + component + mainstr1 + config + mainstr2 + mainstr0
# okay decompiling MiTE4SDN.exe_extracted/PYZ-00.pyz_extracted/bmv2template.pyc
