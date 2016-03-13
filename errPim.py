# This is a skeleton for Err plugins, use this to get started quickly.

from errbot import BotPlugin, botcmd
import subprocess
import os
import time
import urllib2
import re
import sys
import json
from bs4 import BeautifulSoup
from cStringIO import StringIO


class ErrPim(BotPlugin):
	"""An Err plugin skeleton"""
	min_err_version = '1.6.0' # Optional, but recommended
	max_err_version = '3.2.3' # Optional, but recommended

	# Passing split_args_with=None will cause arguments to be split on any kind
	# of whitespace, just like Python's split() does
	#@botcmd(split_args_with=None)
        @botcmd
    	def buscar(self, msg, args):

            arg='/usr/bin/sudo /usr/bin/mairix %s'%args
            p=subprocess.Popen(arg,shell=True,stdout=subprocess.PIPE)
            yield "Indexando ..." 
            data = p.communicate()
            yield data[0]

        @botcmd
    	def tran(self, msg, args):
		url = 'http://www.zaragoza.es/api/recurso/urbanismo-infraestructuras/tranvia?rf=html&results_only=false&srsname=utm30n'
		cadTemplate = 'Faltan: %d minutos (Destino %s)'

		if args:
			parada = args.upper()
		else:
			parada = "CAMPUS RIO EBRO"

		request = urllib2.Request(url)
		request.add_header("Accept",  "application/json")

		resProc = json.load(StringIO(urllib2.urlopen(request).read()))


		if resProc["totalCount"] > 0:
			for i in range(int(resProc["totalCount"])):
				if (resProc["result"][i]["title"].find(parada) >= 0):
					yield "Parada: " + resProc["result"][i]["title"] + " (" + parada + ")"
					for j in range(len(resProc["result"][i]["destinos"])):
						cad = cadTemplate % (resProc["result"][i]["destinos"][j]["minutos"], resProc["result"][i]["destinos"][j]["destino"])
						yield cad
		else:
			yield "Sin respuesta"


        @botcmd
    	def dir(self, msg, args):
		url='http://diis.unizar.es/?q=directorio'

		req = urllib2.Request(url) 
		directorio = urllib2.urlopen(req)

		soup = BeautifulSoup(directorio)

		name=args
		found=0
		yield "Buscando... "+name
		for record in soup.find_all('tr'):
		    if  re.match(".*"+name+".*", record.get_text(),re.IGNORECASE):
			txt=''
			for dato in record.find_all('td'):
				txt=txt +' ' + dato.get_text()
        		yield txt
			found = found + 1
		if (found==0):
			yield name+" not found."
