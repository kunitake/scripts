#!/bin/env python
import sys
import commands
import random
from getpass import getpass
from zabbix_api import ZabbixAPI
# Usage sys.argv[0] [munin_plugin_name] [target_template_name]
try:
    sys.argv[1]
except:
    sys.exit("You need installed munin_plugin_name")
else:
    munin_plugin_name = sys.argv[1]

try:
    sys.argv[2]
except:
    target_template_name = "Template_Munin_Plugins"
else:
    target_template_name = sys.argv[2]

# The hostname at which the Zabbix web interface is available
zabbix_server = "http://localhost/zabbix"
target_host_name="Zabbix server"

# Munin Plugin 
munin_plugin_dir = "/usr/share/munin/plugins/"
munin_config_command = munin_plugin_dir + munin_plugin_name + " config"
munin_value_command  = munin_plugin_dir + munin_plugin_name

# Imported Item Name
# UserParameter=munin[*] ex)UserParameter=munin[memory,active]
itemname="Munin Plugin $1.$2"

# Enter administrator credentials for the Zabbix Web Frontend
# Change below If you need interactive login
#username = raw_input('Username: ')
#password = getpass()
username = "Admin"
password = "zabbix"

# You may change log_level=6
zapi = ZabbixAPI(server=zabbix_server, path="", log_level=3)
zapi.login(username, password)
#print "Connected to Zabbix API Version %s" % zapi.api_version()

# Get hostid
#hostid=zapi.host.get({"filter":{"host":target_host_name}})[0]["hostid"]
templateid=zapi.template.get({"filter":{"host":target_template_name}})[0]["templateid"]

# Get Graph Item from Munin Plugin
graph_title=commands.getoutput(munin_config_command + '|grep graph_title|cut -d " " -f2-')
gitems = []
gitem_color = ""

value=commands.getoutput(munin_value_command)
valuelist=value.splitlines()

# Make Zabbix Item
for i,line in enumerate(valuelist):
  key=line.split(".")[0]
  key="munin[" + munin_plugin_name + "," + key + "]"
# createditemids = zapi.item.create({ 'name' : (itemname) ,'key_' : key, 'hostid' : (hostid) ,'type' : '0' ,'value_type' : '0' , 'delay': '30', 'interface_id': '' })["itemids"][0]
  createditemids = zapi.item.create({ 'name' : (itemname) ,'key_' : key, 'hostid' : (templateid) ,'type' : '0' ,'value_type' : '0' , 'delay': '30' })["itemids"][0]
  for x in range(1,6):
    gitem_color = gitem_color + random.choice("0123456789abcdef")
  gitems.append({'itemid': (createditemids) ,'drawtype':'0','sortorder':'0','color': (gitem_color),'yaxisside':'0','calc_fnc':'2','type':'0'})
  gitem_color = ""

# Make Zabbix Graph
createdgraphids = zapi.graph.create([{'gitems': (gitems) ,'name': (graph_title),'width':'900','height':'200','yaxismin':'0.0000','yaxismax':'3.0000','templateid':'0','show_work_period':'1','show_triggers':'1','graphtype':'0','show_legend':'1','show_3d':'0','percent_left':'0.0000','percent_right':'0.0000','ymin_type':'0','ymax_type':'0','ymin_itemid':'0','ymax_itemid':'0'}])["graphids"][0]

#
print 'Import Finish.'
