#!/usr/bin/env python3
# Created By Ben Smith and Joe Butler
from N2G import drawio_diagram
import re, ipaddress, os, sys
import random
#used by module in add_link overload
import hashlib
# overloading drawio_diagram functions
import xml.etree.ElementTree as ET
class customDiagram(drawio_diagram):
    #fill colour of shape
    fillColour="#FFFFFF"
    #used to generate a random number between 0 and gridMax for initial x,y of machines since they would spawn on top of eachother if not random
    gridMax = 2500
    #add custom xml to graph (xml will be parsed as default by module)
    def addToNodes(self,formattedXML):
        node = ET.fromstring(formattedXML)
        self.current_root.append(node)
    #add generic rectangle (used for custom diagram)
    def addRectangle(self,xmlId,parentId,value,x_pos,y_pos,width,height,colour,rotateStyle=""):
        rectangle="""
                <mxCell id="{id}" value="{value}" style="rounded=0;whiteSpace=wrap;html=1;fillColor={fillColour};{rotateStyle}" vertex="1" parent="{parentId}">
                    <mxGeometry x="{x_pos}" y="{y_pos}" width="{width}" height="{height}" as="geometry" />
            </mxCell>
                """
        formatted=rectangle.format(id=xmlId,value=value,parentId=parentId,style=self.default_node_style,x_pos=x_pos,y_pos=y_pos,width=width,height=height,fillColour=colour,rotateStyle=rotateStyle)
        self.addToNodes(formatted)
    #add conatiner for custom shape with relevant information
    def addContainer(self,xmlId,x_pos,y_pos,width,height):
        containerTemplate="""
        <mxCell id="{id}-3" value="" style="group" vertex="1" connectable="0" parent="1">
            <mxGeometry x="{x_pos}" y="{y_pos}" width="{width}" height="{height}" as="geometry" />
            </mxCell>
                """
        formatted=containerTemplate.format(id=xmlId,label=xmlId,style=self.default_node_style,x_pos=str(random.randint(0,self.gridMax)),y_pos=str(random.randint(0,self.gridMax)),width=width,height=height)
        self.addToNodes(formatted)
    #add rectangle representing subnets
    def subnetRectangle(self,xmlId,value,x_pos,y_pos,width,height):
        subnetTemplate="""
        <object id="{xmlId}" label="{xmlId}">
        <mxCell  style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
        <mxGeometry x="{x_pos}" y="{y_pos}" width="{width}" height="{height}" as="geometry" />
        </mxCell></object>
        """
        formatted=subnetTemplate.format(xmlId=xmlId,value=value,x_pos=str(random.randint(0,self.gridMax)),y_pos=str(random.randint(0,self.gridMax)),width=width,height=height)
        self.addToNodes(formatted)
    #
    def addSubnet(self,xmlId,subnet,width=120,height=60,x_pos=300,y_pos=200,**kwargs):
        self.node_data={}
        if super(customDiagram, self)._node_exists(xmlId, hostname=subnet):
            return
        self.nodes_ids[self.current_diagram_id].append(xmlId)
        self.subnetRectangle(xmlId,subnet,x_pos,y_pos,width,height)
    # overloading the add_link to bypass node checks, we already know the node exists because we make it before a connection but causes errors if it's not removed
    def add_link(
        self,
        source,
        target,
        style="",
        label="",
        data={},
        url="",
        src_label="",
        trgt_label="",
        src_label_style="",
        trgt_label_style="",
        link_id=None,
        **kwargs
    ):
        link_data = {}
        # check type of source and target attribute
        source_node_dict = source.copy() if isinstance(source, dict) else {"id": source}
        source = source_node_dict.pop("id")
        target_node_dict = target.copy() if isinstance(target, dict) else {"id": target}
        target = target_node_dict.pop("id")
        #commenting out existing node checks since our new add_machine function adds many shapes within a container that won't pass checks
        
        # check if target and source nodes exist, add it if not,
        # self._node_exists method will update node
        # if self.node_duplicates set to update, by default its set to skip
        # if not self._node_exists(source, **source_node_dict):
        #     self.add_node(id=source, **source_node_dict)
        # if not self._node_exists(target, **target_node_dict):
        #     self.add_node(id=target, **target_node_dict)
        # create link id if not given
        if link_id:
            link_id = "link_id:{}".format(link_id)
            edge_tup = link_id
        else:
            edge_tup = tuple(sorted([label, source, target, src_label, trgt_label]))
            link_id = hashlib.md5(",".join(edge_tup).encode()).hexdigest()
        if self._link_exists(link_id, edge_tup):
            return
        # try to get style from file
        if os.path.isfile(style[:5000]):
            with open(style, "r") as style_file:
                style = style_file.read()
        # create link
        link = ET.fromstring(
            self.drawio_link_object_xml.format(
                id=link_id,
                label=label,
                source_id=source,
                target_id=target,
                style=style or self.default_link_style,
            )
        )
        # add link source label
        if src_label:
            src_label_obj = ET.fromstring(
                self.drawio_link_label_xml.format(
                    id="{}-src".format(link_id),
                    label=src_label,
                    parent_id=link_id,
                    style=src_label_style or self.default_link_label_style,
                    x="-0.5",
                    rel="1",
                )
            )
            self.current_root.append(src_label_obj)
            kwargs["src_label"] = src_label
        # add link target label
        if trgt_label:
            trgt_label_obj = ET.fromstring(
                self.drawio_link_label_xml.format(
                    id="{}-trgt".format(link_id),
                    label=trgt_label,
                    parent_id=link_id,
                    style=trgt_label_style or self.default_link_label_style,
                    x="0.5",
                    rel="-1",
                )
            )
            self.current_root.append(trgt_label_obj)
            kwargs["trgt_label"] = trgt_label
        # add links data and url
        link_data.update(data)
        link_data.update(kwargs)
        link_data.update({"source": source, "target": target})
        link = self._add_data_or_url(link, link_data, url)
        # save link to graph
        self.current_root.append(link)

    #defining custom function to create shape instead of module's add_node so we can have custom diagrams
    def add_machine(self,xmlId,hostname,rules,ports,eth0,eth1,eth2,ipe0,ipe1,ipe2,label="",data={},url="",style="",width=120,height=60,x_pos=200,y_pos=150,**kwargs):
        
        """
        add_machine: returns None
        
        self - required as class function
        
        xmlId - string used to identify node on diagram (must be unique)
        hostname - hostname that will be displayed on diagram representing machine
        rules - shows iptables rules, displayed on diagram
        ports - shows open ports, displayed on diagram
                we assume machines will contain no more than 3 interfaces at this stage of development
        eth0 - box containing the word "eth0" to identify eth0 interface address
        eth1 - box containing the word "eth1" to identify eth1 interface address
        eth2 - box containing the word "eth2" to identify eth2 interface address
        ipe0 - shows the ip address of interface eth0 (e0) on diagram
        ipe1 - shows the ip address of interface eth1 (e1) on diagram
        ipe2 - shows the ip address of interface eth2 (e2) on diagram
        
        style - custom style to override basic (defined in custom xml anyway)
        width - 
        height -
                width and height of diagram (set as default for diagram design_
        x_pos -
        y_pos - 
                x, y coordinates to place machine diagram (measured from top-left corner of shape)
        
        label - unused but left from module function since overridden
        url - unused but left from module function since overridden
        kwargs - any other arguements - unused but left from module function since overriddent
        
        
        """
        
        # added hostname to exist check
        self.node_data = {}
        if super(customDiagram, self)._node_exists(xmlId, hostname=hostname, data=data, url=url):
            return
        self.nodes_ids[self.current_diagram_id].append(xmlId)
        # if not label.strip():
        #     label = xmlId
        
        # try to get style from file
        if os.path.isfile(style[:5000]):
            with open(style, "r") as style_file:
                style = style_file.read()
        #add container
        self.addContainer(xmlId,0,300,239,220)
        #remove ip boxes if there isn't an interface on current machine
        #Rules
        if ipe0 and ipe2:
            ruleswidth = 238.5
            padding = 0
        elif ipe0 and not ipe2:
            ruleswidth = 178.5
            padding = 0
        elif ipe2 and not ipe0:
            ruleswidth = 178.5
            padding = 60
        
        #adding rectangles relative to container to create custom shape to display information clearly
        # <mxGeometry x="0.5" y="180" width="238.5" height="40" as="geometry" />
        self.addRectangle(f"{xmlId}-rules",f"{xmlId}-3",f"{rules}",0.5+padding,180,ruleswidth,40,"#ACF3CF")
        #ports
        # <mxGeometry x="60" y="90" width="120" height="90" as="geometry" />
        self.addRectangle(f"{xmlId}-ports",f"{xmlId}-3",f"{ports}",60,90,120,90,"#ACF3CF")
        #eth2
        if ipe2:
            # <mxGeometry x="135" y="105" width="120" height="30" as="geometry" />
            self.addRectangle(f"{xmlId}-eth2",f"{xmlId}-3",f"eth2",135,105,120,30,"#E5D67A","rotation=-90;",)
            # <mxGeometry x="164" y="105" width="120" height="30" as="geometry" />
            self.addRectangle(f"{xmlId}-eth2ip",f"{xmlId}-3",f"{ipe2}",164,105,120,30,"#E5D67A","rotation=-90;",)
        if ipe0:
            #eth0
            # <mxGeometry x="-15" y="105" width="120" height="30" as="geometry" />
            self.addRectangle(f"{xmlId}-eth0",f"{xmlId}-3",f"eth0",-15,105,120,30,"#B593E1","rotation=90;")
            #ip - eth2ip
            #ip2 - eth0ip
            #<mxGeometry x="-45" y="105" width="120" height="30" as="geometry" />
            self.addRectangle(f"{xmlId}-eth0ip",f"{xmlId}-3",f"{ipe0}",-45,105,120,30,"#B593E1","rotation=90;")
        if ipe1:
            #eth1 -
            # <mxGeometry x="60" y="30" width="120" height="30" as="geometry" />
            self.addRectangle(f"{xmlId}-eth1",f"{xmlId}-3",f"eth1",60,30,120,30,"#93DCE1")
            #eth1ip
            # <mxGeometry x="60" width="120" height="30" as="geometry" />
            self.addRectangle(f"{xmlId}-eth1ip",f"{xmlId}-3",f"{ipe1}",60,0,120,30,"#93DCE1")
        #hostname
        # <mxGeometry x="60" y="60" width="120" height="30" as="geometry" />
        self.addRectangle(f"{xmlId}-hostname",f"{xmlId}-3",f"{hostname}",60,60,120,30,"#E76B6B")

path = sys.argv[1]
if os.path.isdir(path):
    #removing quotes in lab.conf so graphql produces correct graph upon linfo
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
                if "ifconfig" in line and "#ifconfig" not in line:
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
                if "iptables" in line and "#iptables" not in line:
                    rules.append(line)
                if "for i in" in line and "#for i in" not in line:
                    matches = re.findall(r"([\d]+)",line)
                    for port in matches:
                        ports.append(port)
                elif "service" in line or "start" in line and "#" not in line:
                    ports.append(line)
                if "route add" in line and "#route add" not in line:
                    matches = re.findall(r"gw\s+([\d\.]+)",line)
                    if line.split()[2] == "default":
                        routes[matches[0]] = "default"
                    elif line.split()[2] == "-net":
                        routes[matches[0]] = "normal"
        #parse config files for /etc/network/interfaces information
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
            #create new drawio diagram (custom diagram for custom shapes)
            diagram = customDiagram()
            diagram.add_diagram("Page-1")
            for machine in machines:
                #add machine to graph with relevant information
                diagram.add_machine(
                    xmlId=machine.hostname,
                    hostname = machine.hostname,
                    rules=[rule.strip() for rule in machine.rules] if machine.rules else "",
                    ports=[port.strip() for port in machine.ports] if machine.ports else "",
                    eth0= "eth0",
                    eth1= "eth1",
                    eth2= "eth2",
                    ipe0= machine.ips[machine.interfaces.index("eth0")]  if "eth0" in machine.interfaces else 0,
                    ipe1= machine.ips[machine.interfaces.index("eth1")] if "eth1" in machine.interfaces else 0,
                    ipe2= machine.ips[machine.interfaces.index("eth2")]  if "eth2" in machine.interfaces else 0,
                    )
    
            # add rectangles for subnets
            for subnet in allsubnets:
                diagram.addSubnet(f"{subnet}",f"{subnet}")
            
            #connect machines to subnets
            for subnet in allsubnets:
                for machine in machines:
                    if subnet in machine.subnets:
                        interface = machine.interfaces[(machine.subnets.index(subnet))]
                        diagram.add_link(f"{subnet}",machine.hostname+f"-{interface}ip")

            
            defaultLineStyle=r"fillColor=#a20025;strokeColor=#6F0000;strokeWidth=3;"
            normalLineStyle=r"fillColor=#1ba1e2;strokeColor=#006EAF;strokeWidth=3;"

            #add arrows to show routes (default and regular routes)
            for machine in machines:
                if len(machine.routes)>0:
                    destinationIps = [ipAddress for ipAddress in machine.routes.keys()]
                # print(f"{machine.hostname} - {destinationIps}")
                    for ipAddress in destinationIps:
                        #search other machines to see which machine the ip address belongs to
                        for destinationMachine in machines:
                            if ipAddress in destinationMachine.ips:
                                #identifying interfaces to draw arrow between
                                destinationInterface = destinationMachine.interfaces[(destinationMachine.ips.index(ipAddress))]
                                destinationSubnet = destinationMachine.subnets[(destinationMachine.ips.index(ipAddress))]
                                sourceInterface = machine.interfaces[(machine.subnets.index(destinationSubnet))]
                                if machine.routes[ipAddress] =="default":
                                    diagram.add_link(f"{machine.hostname}-{sourceInterface}ip",f"{destinationMachine.hostname}-{destinationInterface}ip",style=defaultLineStyle)
                                elif machine.routes[ipAddress] == "normal":
                                    diagram.add_link(f"{machine.hostname}-{sourceInterface}ip",f"{destinationMachine.hostname}-{destinationInterface}ip",style=normalLineStyle)

            # diagram.layout(algo="kk")
            #output xml generated to file
            diagram.dump_file(filename="Sample_graph.drawio", folder="./")
        #output data to screen
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
        #use linfo to parse lab.conf and use graphql to generate graph
        elif check == "3":
            os.system("linfo -a -m test.png")
        #exit
        elif check == "4":
            exit()
            
