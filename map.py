#!/usr/bin/env python3
from N2G import drawio_diagram
import re, ipaddress, os, sys
import random
# overloading drawio_diagram functions
import xml.etree.ElementTree as ET

class customDiagram(drawio_diagram):
    fillColour="#FFFFFF"
    def addToNodes(self,formattedXML):
        node = ET.fromstring(formattedXML)
        self.current_root.append(node)

    def addRectangle(self,xmlId,parentId,value,x_pos,y_pos,width,height,rotateStyle=""):
        rectangle="""
                <mxCell id="{id}" value="{value}" style="rounded=0;whiteSpace=wrap;html=1;fillColor={fillColour};{rotateStyle}" vertex="1" parent="{parentId}">
                    <mxGeometry x="{x_pos}" y="{y_pos}" width="{width}" height="{height}" as="geometry" />
            </mxCell>
                """
        formatted=rectangle.format(id=xmlId,value=value,parentId=parentId,style=self.default_node_style,x_pos=x_pos,y_pos=y_pos,width=width,height=height,fillColour=self.fillColour,rotateStyle=rotateStyle)
        self.addToNodes(formatted)

    def addContainer(self,xmlId,x_pos,y_pos,width,height):
        containerTemplate="""
        <mxCell id="{id}-3" value="" style="group" vertex="1" connectable="0" parent="1">
            <mxGeometry x="{x_pos}" y="{y_pos}" width="{width}" height="{height}" as="geometry" />
            </mxCell>
                """
        formatted=containerTemplate.format(id=xmlId,label=xmlId,style=self.default_node_style,x_pos=str(random.randint(0,2500)),y_pos=str(random.randint(0,2500)),width=width,height=height)
        self.addToNodes(formatted)

    def add_node(self,xmlId,hostname,rules,ports,eth0,eth1,eth2,ipe0,ipe1,ipe2,label="",data={},url="",style="",width=120,height=60,x_pos=200,y_pos=150,**kwargs):
        # added hostname to exist check
        self.node_data = {}
        if super(customDiagram, self)._node_exists(xmlId, label=label,hostname=hostname, data=data, url=url):
            return
        self.nodes_ids[self.current_diagram_id].append(xmlId)
        if not label.strip():
            label = xmlId
        # try to get style from file
        if os.path.isfile(style[:5000]):
            with open(style, "r") as style_file:
                style = style_file.read()
        #x="250" y="240" width="239" height="220"
        #  <mxGeometry width="239" height="180" as="geometry" />
        #add container
        self.addContainer(xmlId,0,300,239,220)
        #add individual rectangle

        #Rules
        # <mxGeometry x="0.5" y="180" width="238.5" height="40" as="geometry" />
        self.addRectangle(f"{xmlId}-rules",f"{xmlId}-3",f"{xmlId}-rules",0.5,180,238.5,40)

        #empty
        #   <mxGeometry width="239" height="180" as="geometry" />
        # self.addRectangle(f"{xmlId}-empty1",f"{xmlId}-3",f"{xmlId}-empty",x_pos,y_pos,239,180)

        #ports
        # <mxGeometry x="60" y="90" width="120" height="90" as="geometry" />
        self.addRectangle(f"{xmlId}-ports",f"{xmlId}-3",f"{xmlId}-ports",60,90,120,90)

        #eth2
        # <mxGeometry x="135" y="105" width="120" height="30" as="geometry" />
        self.addRectangle(f"{xmlId}-eth2",f"{xmlId}-3",f"{xmlId}-eth2",135,105,120,30,"rotation=-90;")

        #eth0
        # <mxGeometry x="-15" y="105" width="120" height="30" as="geometry" />
        self.addRectangle(f"{xmlId}-eth0",f"{xmlId}-3",f"{xmlId}-eth0",-15,105,120,30,"rotation=90;")

        #ip - eth2ip
        # <mxGeometry x="164" y="105" width="120" height="30" as="geometry" />
        self.addRectangle(f"{xmlId}-eth2ip",f"{xmlId}-3",f"{xmlId}-eth2ip",164,105,120,30,"rotation=-90;")

        #ip2 - eth0ip
        #<mxGeometry x="-45" y="105" width="120" height="30" as="geometry" />
        self.addRectangle(f"{xmlId}-eth0ip",f"{xmlId}-3",f"{xmlId}-eth0ip",-45,105,120,30,"rotation=90;")

        #eth1 -
        # <mxGeometry x="60" y="30" width="120" height="30" as="geometry" />
        self.addRectangle(f"{xmlId}-eth1",f"{xmlId}-3",f"{xmlId}-eth1",60,30,120,30)

        #eth1ip
        # <mxGeometry x="60" width="120" height="30" as="geometry" />
        self.addRectangle(f"{xmlId}-eth1ip",f"{xmlId}-3",f"{xmlId}-eth1ip",60,0,120,30)

        #hostname
        # <mxGeometry x="60" y="60" width="120" height="30" as="geometry" />
        self.addRectangle(f"{xmlId}-hostname",f"{xmlId}-3",f"{xmlId}-hostname",60,60,120,30)

        # self.addRectangle(f"{xmlId}-1",f"{xmlId}-3",f"{xmlId}-value",0,0,width,height)
        # self.addRectangle(f"{xmlId}-2",f"{xmlId}-3",f"{xmlId}-value2",0,height,width,height)
        # self.addRectangle(f"{xmlId}-1",f"{xmlId}-3",f"{xmlId}-value","410","180",width,height)
        # self.addRectangle(f"{xmlId}-2",f"{xmlId}-3",f"{xmlId}-value2","410","240",width,height)

path = sys.argv[1]
if os.path.isdir(path):
    os.system(f"sed -i 's/\"//g' {path}/lab.conf")
    # Adding in colourful text
    class Colour:
        Black = "\u001b[30m"
        Red = "\u001b[31m"
        Green = "\u001b[32m"
        Yellow = "\u001b[33m"
        Blue = "\u001b[34m"
        Magenta = "\u001b[35m"
        White = "\u001b[37m"
        Cyan = "\u001b[36m"
        Reset = "\u001b[0m"
        titles = Cyan
    class machine:
        def __init__(self,hostname,interfaces,ips,rules,subnets,ports,routes):
            self.hostname = hostname
            self.interfaces = interfaces
            self.ips = ips
            self.rules = rules
            self.subnets = subnets
            self.ports = ports
            self.routes = routes
    # Opening lab.conf to find all of the hostnames
    with open(f"{path}/lab.conf","r") as files:
        file = files.read()

    # Find all hostnames and removing duplicates
    hostnames_with_duplicates = re.findall(r".+?(?=\[)",file)
    hostnames = list(dict.fromkeys(hostnames_with_duplicates))
    files.close()
    # List to store machines on network
    machines = []
    allsubnets = []
    # Reading through contents of all startupfiles for found hostnames
    for hostname in hostnames:
        with open(f"{path}/{hostname}.startup") as startupfile:
            filecontents = startupfile.readlines()
            # List to data to class
            interfaceslist = []
            iplist = []
            rules = []
            subnets = []
            ports = []
            routes = {}
            # Finding all need data from files
            for line in filecontents:
                if "ifconfig" in line:
                    if "netmask" in line:
                        matches = re.findall(r"netmask\s+([\d\.]+)",line)
                        netmask = matches[0]
                        cidr = sum([bin(int(x)).count('1') for x in netmask.split('.')])
                        interfaceslist.append(line.split()[1])
                        iplist.append(line.split()[2])
                        subnets.append(str(ipaddress.IPv4Interface(line.split()[2]+'/'+str(cidr)).network))
                        allsubnets.append(str(ipaddress.IPv4Interface(line.split()[2]+'/'+str(cidr)).network))
                    else:
                        interfaceslist.append(line.split()[1])
                        iplist.append(line.split()[2][:-3])
                        subnets.append(str(ipaddress.IPv4Interface(line.split()[2]).network))
                        allsubnets.append(str(ipaddress.IPv4Interface(line.split()[2]).network))
                if "iptables" in line:
                    rules.append(line)
                if "for i in" in line:
                    matches = re.findall(r"([\d]+)",line)
                    for port in matches:
                        ports.append(port)
                elif "service" in line or "start" in line:
                    ports.append(line)
                if "route add" in line:
                    matches = re.findall(r"gw\s+([\d\.]+)",line)
                    if line.split()[2] == "default":
                        routes[matches[0]] = "default"
                    elif line.split()[2] == "-net":
                        routes[matches[0]] = "normal"

        with open(f"{path}/{hostname}.startup") as startupfile:
            fullfile = startupfile.read()
            if "ifup" in fullfile:
                with open(f"{path}/{hostname}/etc/network/interfaces","r") as interfacefile:
                    contents = interfacefile.readlines()
                    switch = False
                    for line in contents:
                        if "iface" in line and "iface lo" not in line:
                            switch = True
                            tmpinterface = line.split()[1]
                        matches = re.findall(r"address\s+([\d\.]+)",line)
                        if matches:
                            if switch:
                                interfaceslist.append(tmpinterface)
                                iplist.append(matches[0])
                                switch = False
            machines.append(machine(hostname,interfaceslist,iplist,rules,subnets,ports,routes))
        startupfile.close()
    allsubnets = list(dict.fromkeys(allsubnets))
    while True:
        check = input("1 - Make draw.io image\n2 - Output data to screen\n3 - Make linfo image\n4 - Exit\n>")
        if check == "1":
            diagram = customDiagram()
            diagram.add_diagram("Page-1")
            for machine in machines:
                diagram.add_node(
                    xmlId=machine.hostname,
                    hostname = machine.hostname,
                    rules=str(machine.rules),
                    ports=str(machine.ports),
                    eth0= "eth0",
                    eth1= "eth1",
                    eth2= "eth2",
                    ipe0= machine.ips[machine.interfaces.index("eth0")]  if "eth0" in machine.interfaces else "",
                    ipe1= machine.ips[machine.interfaces.index("eth1")] if "eth1" in machine.interfaces else "",
                    ipe2= machine.ips[machine.interfaces.index("eth2")]  if "eth2" in machine.interfaces else "",
                    label="")
            '''
            for subnet in allsubnets:
                diagram.add_node(xmlId,
                hostname = "",
                rules="",
                ports="",
                eth0= "",
                eth1= "",
                eth2= "",
                ipe0= "",
                ipe1= "",
                ipe2= "",
                label="")'''

            '''for subnet in allsubnets:
                for machine in machines:
                    if subnet in machine.subnets:
                        diagram.add_link(subnet, machine.hostname)'''

            diagram.layout(algo="circle")
            diagram.dump_file(filename="Sample_graph.drawio", folder="./")
        elif check == "2":
            for subnet in allsubnets:
                print(f"\n{Colour.White}{'-'*10}\nSubnet {subnet}\n{'-'*10}{Colour.Reset}")
                for machine in machines:
                    if subnet in machine.subnets:
                        print(f"\n{Colour.Red}Hostname:{Colour.Reset} {machine.hostname}\n{Colour.titles}Interfaces:{Colour.Reset}")
                        [print(interface+" - "+ip) for interface,ip in zip(machine.interfaces,machine.ips)]
                        print(f"{Colour.titles}Rules:{Colour.Reset}")
                        [print(rule.strip()) for rule in machine.rules]
                        print(f"{Colour.titles}Subnets:{Colour.Reset}")
                        [print(interface+" - "+str(subnet)) for interface,subnet in zip(machine.interfaces,machine.subnets)]
                        print(f"{Colour.titles}Ports:{Colour.Reset}")
                        [print(port.strip()) for port in machine.ports]
        elif check == "3":
            os.system("linfo -a -m test.png")
        elif check == "4":
            break
