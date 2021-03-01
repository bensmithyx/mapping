#!/usr/bin/env python3
from N2G import drawio_diagram
import re, ipaddress, os, sys
import random
# overloading drawio_diagram functions

import xml.etree.ElementTree as ET
class customDiagram(drawio_diagram):
    counter=0
    # def __init__(self,*args, **kwargs):
    #     self.drawing = ET.fromstring(self.drawio_drawing_xml)
    #     self.nodes_ids = {}  # dictionary of {diagram_name: [node_id1, node_id2]}
    #     self.edges_ids = {}  # dictionary of {diagram_name: [edge_id1, edge_id2]}
    #     self.node_duplicates = node_duplicates
    #     self.link_duplicates = link_duplicates
    #     self.current_diagram = None
    #     self.current_diagram_id = ""
    #     self.default_node_style = "rounded=1;whiteSpace=wrap;html=1;"
    #     self.default_link_style = "endArrow=none;"
    #     self.default_link_label_style = "labelBackgroundColor=#ffffff;"
        # <mxGeometry relative="1" as="geometry"/>
        #https://jgraph.github.io/mxgraph/docs/js-api/files/model/mxGeometry-js.html
        #super(customDiagram, self).__init__(*args,**kwargs)

        #variables to change - hostname, rules, ports, eth0, eth1, eth2, ipe0, ipe1, ipe2, xmlId
    def add_node(self,xmlId,hostname,rules,ports,eth0,eth1,eth2,ipe0,ipe1,ipe2,label="",data={},url="",style="",width=120,height=60,x_pos=200,y_pos=150,**kwargs):
        #reset xml entity
        self.counter+=1
        print(self.counter)
        template = """<object id="{id}" label="{label}">
      <mxCell style="{style}" vertex="1" parent="1">
          <mxGeometry x="{x_pos}" y="{y_pos}" width="{width}" height="{height}" as="geometry"/>
      </mxCell>
    </object>"""

        """

    <object id="{id}" label="{label}">
      <mxCell style="{style}" vertex="1" parent="1">
          <mxGeometry x="{x_pos}" y="{y_pos}" width="{width}" height="{height}" as="geometry"/>
      </mxCell>
    </object>

        """

        '''template="""<object id="{xmlId}-objId" label="label"><mxCell id="{xmlId}--1" value="" style="group" parent="1" vertex="1" connectable="0"><mxGeometry x="250" y="240" width="239" height="220" as="geometry" /></mxCell><mxCell id="{xmlId}--2" value="{rules}" style="rounded=0;whiteSpace=wrap;html=1;shadow=0;glass=0;sketch=0;" parent="{xmlId}--1" vertex="1"><mxGeometry x="0.5" y="180" width="238.5" height="40" as="geometry" /></mxCell><mxCell id="{xmlId}--3" value="" style="group;fillColor=none;gradientColor=none;rounded=1;shadow=0;glass=0;sketch=0;" parent="{xmlId}--1" vertex="1" connectable="0"><mxGeometry width="239" height="180" as="geometry" /></mxCell><mxCell id="{xmlId}--4" value="{ports}" style="rounded=0;whiteSpace=wrap;html=1;" parent="{xmlId}--3" vertex="1"><mxGeometry x="60" y="90" width="120" height="90" as="geometry" /></mxCell><mxCell id="{xmlId}--5" value="{eth2}" style="rounded=0;whiteSpace=wrap;html=1;rotation=-90;" parent="{xmlId}--3" vertex="1"><mxGeometry x="135" y="105" width="120" height="30" as="geometry" /></mxCell><mxCell id="{xmlId}--6" value="{eth0}" style="rounded=0;whiteSpace=wrap;html=1;rotation=90;" parent="{xmlId}--3" vertex="1"><mxGeometry x="-15" y="105" width="120" height="30" as="geometry" /></mxCell><mxCell id="{xmlId}--7" value="{ipe2}" style="rounded=0;whiteSpace=wrap;html=1;rotation=-90;" parent="{xmlId}--3" vertex="1"><mxGeometry x="164" y="105" width="120" height="30" as="geometry" /></mxCell><mxCell id="{xmlId}--8" value="{ipe0}" style="rounded=0;whiteSpace=wrap;html=1;rotation=90;" parent="{xmlId}--3" vertex="1"><mxGeometry x="-45" y="105" width="120" height="30" as="geometry" /></mxCell><mxCell id="{xmlId}--9" value="{eth1}" style="rounded=0;whiteSpace=wrap;html=1;rotation=0;" parent="{xmlId}--3" vertex="1"><mxGeometry x="60" y="30" width="120" height="30" as="geometry" /></mxCell><mxCell id="{xmlId}--10" value="{ipe1}" style="rounded=0;whiteSpace=wrap;html=1;rotation=0;" parent="{xmlId}--3" vertex="1"><mxGeometry x="60" width="120" height="30" as="geometry" /></mxCell><mxCell id="{xmlId}--11" value="{hostname}" style="rounded=0;whiteSpace=wrap;html=1;" parent="{xmlId}--3" vertex="1"><mxGeometry x="60" y="60" width="120" height="30" as="geometry" /></mxCell></object>"""
        '''
        """
        Method to add node to the diagram.
        **Parameters**
        * xmlId (str) mandatory, unique node identifier, usually equal to node name
        * hostname hostname of machine
        * label (str) node label, if not provided, set equal to id
        * data (dict) dictionary of key value pairs to add as node data
        * url (str) url string to save as node url attribute
        * width (int) node width in pixels
        * height (int) node height in pixels
        * x_pos (int) node position on x axis
        * y_pos (int) node position on y axis
        * style (str) string containing DrawIO style parameters to apply to the node
        """

        # added hostname to exist check
        node_data = {}
        if super(customDiagram, self)._node_exists(xmlId, label=label,hostname=hostname, data=data, url=url):
            return
        self.nodes_ids[self.current_diagram_id].append(xmlId)
        if not label.strip():
            label = xmlId
        # try to get style from file
        if os.path.isfile(style[:5000]):
            with open(style, "r") as style_file:
                style = style_file.read()
        # create node element with new
        #
        # formatted=template.format(
        #     xmlId=xmlId,
        #     label=label,
        #     hostname = hostname,
        #     rules=rules,
        #     ports=ports,
        #     eth0=eth0,
        #     eth1=eth1,
        #     eth2=eth2,
        #     ipe0=ipe0,
        #     ipe1=ipe1,
        #     ipe2=ipe2,
        #     width=width if str(width).strip() else 120,
        #     height=height if str(height).strip() else 60,
        #     x_pos=x_pos,
        #     y_pos=y_pos,
        #     style=style if style else self.default_node_style,
        # )
        # print(f"\n\n\n\{formatted}\n\n\n")
        #run pls
        # formatted = template.format(id=xmlId)

        self.drawio_node_object_xml = """<object id="{id}" label="{label}">
      <mxCell style="{style}" vertex="1" parent="1">
          <mxGeometry x="{x_pos}" y="{y_pos}" width="{width}" height="{height}" as="geometry"/>
      </mxCell>
    </object>"""
        formatted=self.drawio_node_object_xml.format(id=xmlId,label=xmlId,style=self.default_node_style,x_pos=x_pos,y_pos=y_pos,width=120,height=60)
        self.drawio_node_object_xml=self.drawio_node_object_xml.format(id=xmlId,label=label,style=self.default_node_style,x_pos=x_pos,y_pos=y_pos,width=120,height=60)
        self.drawio_node_object_xml=formatted
        node = ET.fromstring(formatted)
        # add data attributes and/or url to node
        node_data.update(data)
        node_data.update(kwargs)
        node = super(customDiagram, self)._add_data_or_url(node, node_data, url)
        self.current_root.append(node)


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
        def __init__(self,hostname,interfaces,ips,rules,subnets,ports):
            self.hostname = hostname
            self.interfaces = interfaces
            self.ips = ips
            self.rules = rules
            self.subnets = subnets
            self.ports = ports
    # Opening lab.conf to find all of the hostnames
    with open(f"{path}/lab.conf","r") as files:
        file = files.read()

    # Find all hostnames and removing duplicates
    hostnames_with_duplicates = re.findall(".+?(?=\[)",file)
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
            machines.append(machine(hostname,interfaceslist,iplist,rules,subnets,ports))
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
                diagram.add_node(xmlId=subnet.replace("/","."),
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
            # with open("Sample_graph.drawio","r+") as file:
            #     file.seek(0)
            #     file.write("""<mxGraphModel dx="1098" dy="583" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
            #       <root>""")
            # with open("Sample_graph.drawio","a") as file:
            #     file.write("""</root>
            #     </mxGraphModel>""")
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
