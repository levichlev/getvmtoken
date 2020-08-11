#!/usr/bin/python

from flask import Flask
from flask_restful import Api, Resource, reqparse
from vmware.vapi.vsphere.client import create_vsphere_client
import random
import sys, getopt
import requests
import urllib3
session = requests.session()


def main(argv):
	# Disable certification verify
	session.verify = False
	urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
	serverAdd = ''
	username = ''
	password = ''
	VM = ''
	datacenter = ''
	try:
		opts, args = getopt.getopt(argv,"ha:u:p:v:d:",["address=","username=","password=","VM=","datacenter="])
	except getopt.GetoptError:
		print ('usage: gettoken.py -a <vcenter_address> -u <username> -p <password> -v <VM_name> -d <datacenter_name>')
		sys.exit(2)
	for opt, arg in opts:
		if (opt == '-h'):
			print ("usage: gettoken.py -a <vcenter_address> -u <username> -p <password> -v <VM_name> -d <datacenter_name>")
			sys.exit()
		elif opt in ("-a","--address"):
			serverAdd = arg
		elif opt in ("-u","--username"):
			username = arg
		elif opt in ("-p","--password"):
			password = arg
		elif opt in ("-v","--VM"):
			VM = arg
		elif opt in ("-d","--datacenter"):
			datacenter = arg
	# vCenter connection
	vc = create_vsphere_client(server=serverAdd, username=username, password=password, session=session)

	# Datacenter search
	dcSummary = vc.vcenter.Datacenter.list(vc.vcenter.Datacenter.FilterSpec(names={datacenter}))
	vmNames = {VM,}
	if dcSummary == []:
		print ("Datacenter not found")
		sys.exit(2)
	vmDatacenters = {dcSummary[0].datacenter,} 

	# VM search
	Spec = vc.vcenter.vm.console.Tickets.CreateSpec(vc.vcenter.vm.console.Tickets.Type('VMRC'))
	vmSummary = vc.vcenter.VM.list(vc.vcenter.VM.FilterSpec(names=vmNames,datacenters=vmDatacenters))
	if vmSummary == []: # Если ответ пустой - вывод ошибки
		print ('VM not found!')
		sys.exit(2)
	# Ticket generation and exit
	vmid = vmSummary[0].vm
	ticket = vc.vcenter.vm.console.Tickets.create(vmid,Spec)
	print (ticket.ticket)
	sys.exit()
if __name__ == "__main__":
	main(sys.argv[1:])
