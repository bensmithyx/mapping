#!/usr/bin/env python3
# Created By Ben Smith and Joe Butler
import re, os, sys, random, subprocess

homeDir = os.environ['HOME']
sshDir = f"{homeDir}/.ssh"

if not os.path.exists(sshDir):
    os.makedirs(sshDir)

privateKey = f"{sshDir}/Crawl-id_rsa"
publicKey = f"{sshDir}/Crawl-id_rsa.pub"

os.system(f"rm -f {publicKey} {privateKey}")
os.system(f'ssh-keygen -q -N "" -f "{privateKey}" > /dev/null')

#implement later manual input of username and password
autousername = True
autopassword = True

username="admin"
password = "pass"

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
class Machine:
    def __init__(self,hostname,interfaces,ips,subnets,rules,ports,routes):
        self.hostname = hostname
        self.interfaces = interfaces
        self.ips = ips
        self.rules = rules
        self.subnets = subnets
        self.ports = ports
        self.routes = routes

def parsePorts(output):
    portPattern = r'(^\S+|(?<=:)\d+|"\S+")'
    portGroups=3
    matches = re.findall(portPattern,output,re.MULTILINE)
    
    filteredGroups=[]

    for i in range(0,int(len(matches)/3)):
       
        serviceName = matches[(i*portGroups)+2].replace('"','')
        if "," in serviceName:
            serviceName=serviceName.split(",")[0]
        matches[(i*portGroups)+2]= serviceName
        filteredGroups.append(f"{matches[(i*portGroups)+1]}/{matches[(i*portGroups)]} - {matches[(i*portGroups)+2]}")
   
    filteredGroups=list(set(filteredGroups))
    output = filteredGroups
    return output

def parseNatIptables(output):
    return [f"-t nat {line}" for line in output.split("\n")] 
        
def parseRules(output):
    return output.split("\n")

def parseInterfaces(output):
    return output.split("\n")

def parseIp(output):
    ips=[]
    for line in output.split("\n"):
        ips.append(line.split(" ")[1])
        
    return ips

def parseOutputAsObject(runDict):
    machine = Machine(
        hostname=runDict['hostname'],
        interfaces=runDict['interfaces'],
        ips=runDict['ips'],
        subnets=runDict['subnets'],
        rules=runDict['rules']+runDict['natRules'],
        ports=runDict['ports'],
        routes=runDict['routes']
    )
    return machine

def runCommand(command):
    commandOutput = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    result = commandOutput.communicate()[0].decode()
    return result.strip()

def runEnum():
    #a dictionary of information and the commands to get them
    commands = {
        "hostname":"hostname",
        "interfaces":"ip -o -4 addr | awk '{print $2\" \"$4}'| grep -v 'lo' | grep -v '127.0.0.1'",
        "rules":"sudo iptables -S",
        "natRules":"sudo iptables -t nat -S",
        "ports":"sudo ss -alntup| tail -n +2 | awk '{print $1\" \"$5\" \"$7}'",
        "routes":"ip route show | grep default | awk '{print $3}'"
    }

    #running each command and returning result
    for command in commands.keys():
        # #executing command
        # commandOutput = subprocess.Popen(commands[command],shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        # #getting output
        commands[command] = runCommand(commands[command])
        # result = commandOutput.communicate()[0].decode()
        # commands[command]=result.strip()

    #parsing output for better use
    commands['ports'] = parsePorts(commands['ports'])
    commands['rules'] = parseRules(commands['rules'])
    commands['natRules'] = parseNatIptables(commands['natRules'])
    commands['ips']=parseIp(commands['interfaces'])
    commands['subnets']=calculateSubnets(commands['ips'])

    #changing into a machine object
    machine = parseOutputAsObject(commands)
    return machine

def calculateSubnets(ips):
    subnets=[]
    for ip in ips:
        subnets.append(runCommand(f"netmask -c {ip}"))
    return subnets


def searchSubnet(subnet):
    found_ips = runCommand(f"nmap -n -T5 --min-rate 10000 -PU -sn {subnet} -oG - | awk '/Up$/{{print $2}}'")
    # print(found_ips)
    return found_ips
    

def hostname(ip):
    with subprocess.Popen(["ssh","-o","StrictHostKeyChecking=no",f"{ip}","hostname"], stdout=subprocess.PIPE) as output:
        data = output.stdout.read().decode().strip()
    print(data)
    return f"{data}"

def ipa(ip):
    allOutput=""
    if ip == "host":
        # Running ip addr and awking interfaces and ips with there subnet
        ps = subprocess.Popen("ip -o -4 addr | awk '{print $2\" \"$4}'| grep -v 'lo' | grep -v '127.0.0.1'",shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        allOutput=ps.communicate()
        output = allOutput[0].decode().split()
        if output[1] == "Permanently":
            output = output[11:]
    else:
        # Running ip addr and awking interfaces and ips with there subnet
        ps = subprocess.Popen(f"ssh -o StrictHostKeyChecking=no {ip} ip -o -4 addr | awk '{{print $2\" \"$4}}'| grep -v 'lo' | grep -v '127.0.0.1'",shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output = ps.communicate()[0].decode().split()
        if output[1] == "Permanently":
            output = output[11:]

    subnets = []
    ips = []
    interfaces = []
    indexes = []
    # Appending interfaces, ips and subnets to there lists
    for index in range(0,len(output),2):
        interfaces.append(output[index])
        ips.append(output[index+1][:-3])
        subnets.append(str(ipaddress.IPv4Interface(output[index+1]).network))
    return interfaces, ips, subnets

def rules(ip):
    rules = []
    # Running iptables to check for any firewall rules
    if ip == "host":
        ps = subprocess.Popen(f"sudo iptables -S && sudo iptables -t nat -S",shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output = ps.communicate()[0].decode().split('\n')
    else:
        ps = subprocess.Popen(f"ssh {ip} sudo iptables -S",shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output = ps.communicate()[0].decode().split('\n')
    del output[-1]
    rules.append([rule for rule in output])
    if ip != "host":
        ps = subprocess.Popen(f"ssh {ip} sudo iptables -t nat -S",shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        del output[-1]
        output = ps.communicate()[0].decode().split('\n')
        rules.append([rule for rule in output])
    return rules

def ports(ip):
    # Checking for open ports and services
    ports = []
    if ip == "host":
        ps = subprocess.Popen("""sudo ss -anp4 | tail -n +2 | awk '{print $5\" \"$7}'""",shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output = ps.communicate()[0].decode().split('\n')
    else:
        ps = subprocess.Popen(f"""ssh {ip} sudo ss -anp4 | tail -n +2 | awk '{{print $5\" \"$7}}'""",shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output = ps.communicate()[0].decode().split('\n')
    del output[-1]
    # Getting port and service from data  and appending it to an array
    for data in output:
        values = data.split()
        # Removing everything before : e.g. x.x.x.x:22
        port = values[0][values[0].index(":")+1:]
        if len(values) >1:
            # Finding the starting " and ending " so it can get the service name
            indexes = [i for i, ltr in enumerate(values[1]) if ltr == "\""]
            # Getting service name from data
            service = values[1][indexes[0]+1:indexes[1]]
            ports.append(f"{port} {service}")
    ports = list(dict.fromkeys(ports))
    return ports

def routes(ip):
    routes = {}
    if ip == "host":
        # Finding default route of machine
        ps = subprocess.Popen("ip route show | grep default | awk '{print $3}'",shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output = ps.communicate()[0].decode().strip()
    else:
        # Finding default route of machine
        ps = subprocess.Popen(f"ssh {ip} ip route show | grep default | awk '{{print $3}}'",shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output = ps.communicate()[0].decode().strip()

    routes["default"] = output
    return routes

def ssh(ip):
    os.system(f"ssh {ip}")

def nmap(subnet):
    ips = []
    ps = subprocess.Popen(f"nmap -n -T5 --min-rate 10000 -PU -sn {subnet} -oG - | awk '/Up$/{{print $2}}'",shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0].decode().split('\n')
    del output[-1]
    for data in output:
        #print(data)
        ips.append(data)
    return ips
def mapper():
    machines=[]
    searchedips=[]
    searchedsubnets=[]
    unsearchedips=[]

    localMachine = runEnum()
    machines.append(localMachine)
    searchedips.append([ip for ip in localMachine.ips])
    unsearchedsubnets = localMachine.subnets

    
    #https://stackoverflow.com/a/39195704 + me
    privateSubnetPattern = r"^([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!172\.(16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31))(?<!127)(?<!^10)(?<!^0)\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!192\.168)(?<!172\.(16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31))\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!\.255$)\/([0-9]|[1-2][0-9]|3[012])$"
    pattern = re.compile(privateSubnetPattern)

    
    while len(unsearchedsubnets)>0:

        #take subnet from unsearched and search it
        chosenSubnet = unsearchedsubnets.pop()
        matches = re.findall(pattern,chosenSubnet)
        if len(matches)>0:
            print(f"Skipping {chosenSubnet} because it's a public range")
            continue
        found_ips = searchSubnet(chosenSubnet).split("\n")
        # print(f"IP: {found_ip}")
        for ip in found_ips:
            if ip not in searchedips:
                unsearchedips.append(ip)
        
        for ip in unsearchedips:
            sshI(ip)
            searchedips.append()

        searchedsubnets.append(chosenSubnet)

    print(unsearchedips)

# self.hostname = hostname
#         self.interfaces = interfaces
#         self.ips = ips
#         self.rules = rules
#         self.subnets = subnets
#         self.ports = ports
#         self.routes = routes


#     # List to store machines on network
#     machines = []
#     searchedips = []
#     unsearchedips = []
#     searchedsubnets = []
#     unsearchedsubnets = []
#     count = 0
#     machineip = "host"
#     while True:
#         count +=1
#         # Outputing interfaces, ips and subnets to variable in list format so function does not get called more than once
#         ipaoutput = ipa(machineip)
#         for ip in ipaoutput[1]:
#             searchedips.append(ip)
#         for ip in ipaoutput[2]:
#             unsearchedsubnets.append(ip)
#         if count == 1:
#             machines.append(machine(hostname(ipaoutput[1][0]),ipaoutput[0],ipaoutput[1],ipaoutput[2],rules(machineip),ports(machineip),routes(machineip)))
#         else:
#             machines.append(machine(hostname(machineip),ipaoutput[0],ipaoutput[1],ipaoutput[2],rules(machineip),ports(machineip),routes(machineip)))
#         for subnet in unsearchedsubnets:
#             for ip in nmap(subnet):
#                 unsearchedips.append(ip)
#             searchedsubnets.append(subnet)
#         unsearchedips = list(set(unsearchedips)-set(searchedips))
#         unsearchedsubnets = list(set(unsearchedsubnets)-set(searchedsubnets))
#         print(f"Searchedips:\n{searchedips}\nUnsearchedips:\n{unsearchedips}")
#         print(f"Searchedsubnets:\n{searchedsubnets}")
#         if not unsearchedips:
#             break
#         if unsearchedips:
#             print(f"sshing into {unsearchedips[0]}")
#             machineip = unsearchedips[0]
#             del unsearchedips[0]

#     return machines

# while True:
#     check = input("1 - Output data to screen\n2 - Exit\n>")
#     if check == "1":
#         machines = mapper()
#         for machine in machines:
#             print(f"\n{Colour.Red}Hostname:{Colour.Reset} {machine.hostname}\n{Colour.titles}Interfaces:{Colour.Reset}")
#             [print(interface+" - "+ip) for interface,ip in zip(machine.interfaces,machine.ips)]
#             print(f"{Colour.titles}Rules:{Colour.Reset}")
#             [print(rule) for rule in machine.rules]
#             print(f"{Colour.titles}Subnets:{Colour.Reset}")
#             [print(interface+" - "+str(subnet)) for interface,subnet in zip(machine.interfaces,machine.subnets)]
#             print(f"{Colour.titles}Ports:{Colour.Reset}")
#             [print(port) for port in machine.ports]
#     elif check == "2":
#         break

mapper()