# This is a skeleton for Err plugins, use this to get started quickly.

from errbot import BotPlugin, botcmd
import configparser
import subprocess
import os
import time
#import urllib2
import urllib.request
import requests
import re
import sys
import json
import pickle
from bs4 import BeautifulSoup
#from cStringIO import StringIO
import io #import StringIO
from twitter import *
import facebook
from linkedin import linkedin
import dateparser

def end(msg=""):
    return("END"+msg)

class ErrPim(BotPlugin):
    """An Err plugin skeleton"""
    min_err_version = '1.6.0' # Optional, but recommended
    max_err_version = '4.3.4' # Optional, but recommended

    def get_configuration_template(self):
        """ configuration entries """
        config = {
            'pathMail': '',
        }
        return config

    def _check_config(self, option):

        # if no config, return nothing
        if self.config is None:
            return None
        else:
            # now, let's validate the key
            if option in self.config:
                return self.config[option]
            else:
                return None

    def search(self, msg, args):
        path = self._check_config('pathMail')
        arg='/usr/bin/sudo -H -u %s /usr/bin/mairix "%s"'%(path, args)
        p=subprocess.Popen(arg,shell=True,stdout=subprocess.PIPE)
        data = p.communicate()
        return data[0]

    @botcmd
    def sm(self, msg, args):
        yield "Indexando ..." 
        yield self.search(msg, args)
        yield end()

    @botcmd(split_args_with=None)
    def sf(self, msg, args):
        yield "Searching %s"%args[0] 
        yield self.search(msg, args[0])
        if len(args) > 1:
           yield " in %s"%args[1] 

        path = self._check_config('pathMail')
        yield path
	# We are using mairix, which leaves a link to the messages in the
	# Search folder. Now we just look for the folders where the actual
	# messages are located.
        arg='/usr/bin/sudo -H -u %s /bin/ls -l /home/%s/Maildir/.Search/cur' % (path, path)
        p=subprocess.Popen(arg,shell=True,stdout=subprocess.PIPE)
        data = p.communicate()
        
        folders = []
        
        for i in data[0].decode("utf-8").split('\n')[1:]:
            j = i[i.find('/.')+2:]
            folder = j[:j.find('/')]
            if folder and 'mairix' not in folder and not folder in folders: 
                if (len(args) == 1) or (len(args)>1 and folder.find(args[1])>=0):
                    folders.append(folder)

        yield folders
        yield end()

    @botcmd
    def tran(self, msg, args):
        url = 'http://www.zaragoza.es/api/recurso/urbanismo-infraestructuras/tranvia?rf=html&results_only=false&srsname=utm30n'
        cadTemplate = 'Faltan: [%d, %d] minutos (Destino %s)'
        
        if args:
           parada = args.upper()
        else:
           parada = "CAMPUS RIO EBRO"
        
        cad = 'Faltan: %s minutos (Destino %s)'
        request = urllib.request.Request(url)
        headers = {"Accept":  "application/json"}
        response = requests.get(url, headers = headers)
        resProc = response.json() 
        if resProc["totalCount"] > 0:
           tit = 0
           for i in range(int(resProc["totalCount"])):
               if (resProc["result"][i]["title"].find(parada) >= 0):
                  if (tit == 0):
                      yield "Parada: " + resProc["result"][i]["title"] + " (" + parada + ")"
                      tit = 1
                  dest = {}
                  for j in range(len(resProc["result"][i]["destinos"])):
                      myDest = resProc["result"][i]["destinos"][j]["destino"] 
                      if myDest in dest:
                          dest[myDest].append(resProc["result"][i]["destinos"][j]["minutos"])
                      else:
                          dest[myDest] = [resProc["result"][i]["destinos"][j]["minutos"]]
                  for j in dest.keys():
                      yield cad % (dest[j], j)
        else:
           yield "Sin respuesta"
        yield end()

    @botcmd
    def dir(self, msg, args):
        url='http://diis/?q=directorio'
        
        req = urllib.request.Request(url) 
        directorio = urllib.request.urlopen(req)
        
        soup = BeautifulSoup(directorio)
        
        name=args
        found=0
        yield('Looking for... "{0}" '.format(name))
        #self.send(msg.frm,
        #          'Buscando... "{0}" '.format(name),
        #          in_reply_to=msg,
        #          groupchat_nick_reply=True)
        for record in soup.find_all('tr'):
            if  re.match(".*"+name+".*", record.get_text(),re.IGNORECASE):
                 txt=''
                 for dato in record.find_all('td'):
                     txt=txt +' ' + dato.get_text()
                 yield(txt)
                 found = found + 1
        if (found==0):
            yield('"{0}" not found.'.format(name))
            #self.send(msg.frm,
            #          '"{0}" not found.'.format(name),
            #          in_reply_to=msg,
            #          groupchat_nick_reply=True)
        yield('{0}'.format(end()))
        #self.send(msg.frm,
        #          '{0}'.format(end()),
        #          in_reply_to=msg,
        #          groupchat_nick_reply=True)

