#Copyright (c) 2019, 2020, Oracle and/or its affiliates.
#
#Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
# WebLogic on Docker Default Domain
#
# Domain, as defined in DOMAIN_NAME, will be created in this script. Name defaults to 'base_domain'.
#
# Since : June, 2019
# Author: monica.riccelli@oracle.com
# ===================================

import os
import socket

def getEnvVar(var):
  val=os.environ.get(var)
  if val==None:
    print "ERROR: Env var ",var, " not set."
    sys.exit(1)
  return val

# This python script is used to create a WebLogic domain
domain_name                   = DOMAIN_NAME
admin_server_name             = ADMIN_NAME
admin_port                    = int(ADMIN_LISTEN_PORT)
server_port                   = int(MANAGED_SERVER_PORT)
managed_server_name_base      = MANAGED_SERVER_NAME_BASE
number_of_ms                  = int(CONFIGURED_MANAGED_SERVER_COUNT)
domain_path                   = os.environ.get("DOMAIN_HOME")
cluster_name                  = CLUSTER_NAME
cluster_type                  = CLUSTER_TYPE
production_mode               = PRODUCTION_MODE

print(f'domain_path              : [{domain_path}]');
print(f'domain_name              : [{domain_name}]');
print(f'admin_server_name        : [{admin_server_name}]');
print(f'admin_port               : [{admin_port}]');
print(f'cluster_name             : [{cluster_name}]');
print(f'server_port              : [{server_port}]');
print(f'number_of_ms             : [{number_of_ms}]');
print(f'cluster_type             : [{cluster_type}]');
print(f'managed_server_name_base : [{managed_server_name_base}]');
print(f'production_mode          : [{production_mode}]');

# Open default domain template
# ============================
readTemplate("/u01/oracle/wlserver/common/templates/wls/wls.jar")

set('Name', domain_name)
setOption('DomainName', domain_name)
create(domain_name,'Log')
cd(f'/Log/{domain_name}');
set('FileName', f'{domain_name}.log')

# Configure the Administration Server
# ===================================
cd('/Servers/AdminServer')
set('ListenPort', admin_port)
set('Name', admin_server_name)


# Set the admin user's username and password
# ==========================================
cd(f'/Security/{domain_name}/User/weblogic')
cmo.setName(username)
cmo.setPassword(password)

# Write the domain and close the domain template
# ==============================================
setOption('OverwriteDomain', 'true')


# Create a cluster
# ================
cd('/')
cl=create(cluster_name, 'Cluster')

if cluster_type == "CONFIGURED":

  # Create managed servers
  for index in range(number_of_ms):
    cd('/')
    msIndex = index+1

    cd('/')
    name = f'{managed_server_name_base}{msIndex}'

    create(name, 'Server')
    cd(f'/Servers/{name}/')
    print(f'managed server name is {name}');
    set('ListenPort', server_port)
    set('NumOfRetriesBeforeMSIMode', 0)
    set('RetryIntervalBeforeMSIMode', 1)
    set('Cluster', cluster_name)

else:
  print(f'Configuring Dynamic Cluster {cluster_name}')

  templateName = f"{cluster_name}-template"
  print(f'Creating Server Template: {templateName}')
  st1=create(templateName, 'ServerTemplate')
  print(f'Done creating Server Template: {templateName}')
  cd(f'/ServerTemplates/{templateName}')
  cmo.setListenPort(server_port)
  cmo.setCluster(cl)

  cd(f'/Clusters/{cluster_name}')
  create(cluster_name, 'DynamicServers')
  cd(f'DynamicServers/{cluster_name}')
  set('ServerTemplate', st1)
  set('ServerNamePrefix', managed_server_name_base)
  set('DynamicClusterSize', number_of_ms)
  set('MaxDynamicClusterSize', number_of_ms)
  set('CalculatedListenPorts', false)

  print(f'Done setting attributes for Dynamic Cluster: {cluster_name}');

# Write Domain
# ============
writeDomain(domain_path)
closeTemplate()
domain_name                   = DOMAIN_NAME
# Update Domain
readDomain(domain_path)
cd('/')
setOption('ServerStartMode',production_mode)
updateDomain()
closeDomain()
domain_name                   = DOMAIN_NAME
domain_name
# Exit WLST
# =========
exit()
