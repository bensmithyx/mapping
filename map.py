#!/usr/bin/env python3
from N2G import drawio_diagram
import re, ipaddress, os

os.system("sed -i 's/\"//g' lab.conf")
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
with open("lab.conf","r") as files:
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
    with open(f"{hostname}.startup") as startupfile:
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
    with open(f"{hostname}.startup") as startupfile:
        fullfile = startupfile.read()
        if "ifup" in fullfile:
            with open(f"{hostname}/etc/network/interfaces","r") as interfacefile:
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
        diagram = drawio_diagram()
        diagram.add_diagram("Page-1")
        for machine in machines:
            diagram.add_node(id=machine.hostname)

        for subnet in allsubnets:
            diagram.add_node(id=subnet)

        for subnet in allsubnets:
            for machine in machines:
                if subnet in machine.subnets:
                    diagram.add_link(subnet, machine.hostname)

        diagram.layout(algo="kk")
        diagram.dump_file(filename="Sample_graph.draw.io", folder="./")
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
