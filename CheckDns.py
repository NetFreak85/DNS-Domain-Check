#!/bin/python3.9
# coding=utf-8

##################
# Import Section #
##################

import textwrap
import argparse
import socket
import ipaddress
import dns.resolver

####################
# Function Section #
####################

# Function that validate a IPv4 Address
def validate_ip(ip):

    #We divided the IPv4 format and if the list dont have 4 octes return false
    ip_Splited = ip.split('.')
    if len(ip_Splited) != 4:
        return False
    
    #We evaluate each octec
    for oct in ip_Splited:

        # If the octec is not digit return false
        if not oct.isdigit():
            return False

        #If the octec number is not in range (0 <= oct <= 255) we return false
        if int(oct) < 0 or int(oct) > 255:
            return False

    return True

# Function that perform the DNS Resolution
def dns_Resolver(dnsServer, query, port, timeout, record):

    #Variable that will store the DNS Query Result
    dns_Return = ""

    #Set the DNS Server for DNS query
    dns.resolver.nameservers = [dnsServer]

    #Set the Timeout for DNS query
    dns.resolver.Timeout = timeout

    #Set the Port for DNS query
    dns.resolver.port = port
    
    #result = dns.resolver.resolve(query, record)

    try:
        #Perform dns resolution
        result = dns.resolver.resolve(query, record)
    except dns.resolver.NoAnswer:
        #When we consult a record for a CNAME with no record configured the NoAnswer exception trigger, with this we change the record type to A
        result = dns.resolver.resolve(query, "A")
    except dns.resolver.NXDOMAIN:
        return ""

    #Copy the DNS result into the dns_Record variable
    for dns_Record in result:
        dns_Return = dns_Record.to_text()

    return dns_Return

# Function that validate the IP Address or FQDN Reachability
def check_Recheability(host, port, timeout):
    try:

        if not validate_ip(host):
            host = dns_Resolver(host, host, port, timeout, "A")

        #We check if the Hostis a Valid Address
        ipaddress.ip_address(host)

        #Set socket timeout
        socket.setdefaulttimeout(timeout)

        #Open socket to host "Host" to port "Port"
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))

        #Close socket connection
        socket.close(2)

        #Return True if the socket works without problem
        return True
    except ValueError:
        print('address/netmask is invalid: %s' % host)
    except socket.timeout:
        print("Connection to DNS Server " + host + " Timeout")
        exit()
    except socket.herror:
       exit(print("Unknown host or FQDN/IP Address unreachable"))

# Function Argument Definition
def get_args():

    # Argument Parser Definition
    parser = argparse.ArgumentParser(
                prog = 'CheckDns.py',
                usage='use "python %(prog)s --help" for more information',
                description = textwrap.dedent('''
        ############################################################################
        #  ____  _   _ ____   __     ___    _     ___ ____    _  _____ ___  ____   #
        # |  _ \| \ | / ___|  \ \   / / \  | |   |_ _|  _ \  / \|_   _/ _ \|  _ \  #
        # | | | |  \| \___ \   \ \ / / _ \ | |    | || | | |/ _ \ | || | | | |_) | #
        # | |_| | |\  |___) |   \ V / ___ \| |___ | || |_| / ___ \| || |_| |  _ <  #
        # |____/|_| \_|____/     \_/_/   \_\_____|___|____/_/   \_\_| \___/|_| \_\ #
        #                                                                          #
        ############################################################################
        '''),
                epilog="############################################################################",
                formatter_class=argparse.RawTextHelpFormatter
                )

    # Argument Timeout Definition
    parser.add_argument('-t', '--timeout',
                        help = 'DNS Timeout Definition\n ',
                        type = int,
                        default = 10,
                        required = False)

    # Argument DNS Port definition
    parser.add_argument('-p','--port',
                        help=textwrap.dedent('''\nDNS Port Configuration\nDefault DNS Port value is 53\n\n'''),
                        type = int,
                        default = 53,
                        required = False)

    # Argument DNS Record Tyoe
    parser.add_argument('-r','--record',
                        help=textwrap.dedent('''\nDNS Record Type\nDefault DNS Record Type is A\n\n'''),
                        type = str,
                        default = "A",
                        required = False)

    # Argument DNS Server
    parser.add_argument('-s', '--server',
                        help = '\nDNS FQDN/IP Address\n ',
                        type=str,
                        required = True)

    # Argument DNS Query
    parser.add_argument('-q', '--querry',
                        help = '\nDNS Record to be Check\n ',
                        type=str,
                        required = True)

    #
    # The following Arguments help to the monitoring team to know where the query will be executed 
    #

    # Argument DNS Query Site Attribute
    parser.add_argument('--site',
                        help = 'DNS Recored Site to be Check\n ',
                        type=str,
                        required = False)

    # Argument DNS Query Enviroment Attribute
    parser.add_argument('--env',
                        help = '\nDNS Recored Enviroment to be Check\n ',
                        type=str,
                        required = False)

    # Argument DNS Query Discipline Attribute
    parser.add_argument('--discipline',
                        help = '\nDNS Recored Discipline to be Check\n ',
                        type=str,
                        required = False)

    #
    # Argument that diferenciate between Technologies (F5 GTM or DNS)
    #

    # Argument DNS Query Technology Attribute
    parser.add_argument('--tech',
                        help = '\nDNS Recored Techonology\n ',
                        type=str,
                        choices=['dns','f5'],
                        default = "dns",
                        required = False)

    #
    # DEBUG Mode Argument Definition
    #

    # Argument Debug Mode
    parser.add_argument('--debug',
                        help = 'Debug mode ',
                        action = 'store_true',
                        required = False)

    return parser.parse_args()

#Main Funcion
def main():

    #Var for while loop in order to check cname records
    notIp = True

    #Temporary Var for the DNS CNAME Query
    tmpRecord = ""

    # Variable for arguments
    arg = get_args()

    # Check if there is reachibility to the DNS server and the Port is open
    check_Recheability(arg.server,arg.port,arg.timeout)

    # We check if the query is for a CNAME record
    if str(arg.record).lower() == "cname":

        #Temporary Var for the DNS Query
        tmpRecord = arg.querry

        #In the CNAMEs we evaluate all the DNS resolution
        while notIp:

            #Var that store the DNS respond for the temRecord Var
            tmp = dns_Resolver(arg.server, tmpRecord, arg.port, arg.timeout, arg.record)

            #We check if the Hostis a Valid Address, if not we perform the DNS resolution
            if validate_ip(tmp):

                #If Debug Mode is enable, we print the DNS Query Result
                if arg.debug:
                    print (tmp)
                
                notIp = False
                print('dns_domain,domain="%s",site="%s",environment=%s,discipline=%s,technology=%s service_status=%s' % (arg.querry,arg.site, arg.env, arg.discipline, arg.tech, 1))
        
            #If the DNS Replay is not an IP Address we update the tmpRecord Variable with the new value or stop the loop if the respond is emptly
            else:

                #If the DNS Resolution is emptly we end the loop and print an service status 0
                if str(tmp) == "":
                    print('dns_domain,domain="%s",site="%s",environment=%s,discipline=%s,technology=%s service_status=%s' % (arg.querry,arg.site, arg.env, arg.discipline, arg.tech, 0))
                    notIp = False

                #If the DNS Resolution is a CNAME we update the var tmpRecord with the new value
                else:
                    
                    #If Debug Mode is enable, we print the DNS Query Result
                    if arg.debug:
                        print(tmp)
                    
                    #We update the tmpRecord with the CNAME Resolution performed in the old loop
                    tmpRecord = tmp
                
    else:

        # Function that return the DNS value for A Records

        a_record = dns_Resolver(arg.server, arg.querry, arg.port, arg.timeout, arg.record)

        #We print the result if the Debug Mode is Activated
        if arg.debug:
            print(a_record)

        #If the DNS Respond is Null or Emptly we print service_status = 0
        if a_record == "":
             print('dns_domain,domain="%s",site="%s",environment=%s,discipline=%s,technology=%s service_status=%s' % (arg.querry,arg.site, arg.env, arg.discipline, arg.tech, 0))
        
        #If we received DNS respond with correct value we print service_status = 1
        else:
            print('dns_domain,domain="%s",site="%s",environment=%s,discipline=%s,technology=%s service_status=%s' % (arg.querry,arg.site, arg.env, arg.discipline, arg.tech, 1))

#Main program
if __name__ == '__main__':
    exit(main())
