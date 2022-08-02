#!/usr/bin/python
# Copyright (c)  2020,2021, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
import sys

#============================================================
#Connect To AdminServer and create Content Server Connection
#============================================================

adminHost     = os.environ.get("ADMIN_SERVER_CONTAINER_NAME")
adminPort     = os.environ.get("ADMIN_PORT")
adminName     = os.environ.get("ADMIN_USERNAME")
adminPassword = os.environ.get("ADMIN_PASSWORD")

configureConnection = os.environ.get("CONFIGURE_UCM_CONNECTION")
ucmConnectionName = 'wcp_ucm'
ucmHost = os.environ.get("UCM_HOST")
ucmPort = os.environ.get("UCM_PORT")
ucmPortalIdentifier = 'webcenter'
ucmSecurityGroup = 'UCM_Portal'
ucmAdminUserName = os.environ.get("UCM_ADMIN_USER")
ucmsocketType    = os.environ.get("UCM_SOCKET_TYPE")
ucmIntraDocServerPort = os.environ.get("UCM_INTRADOC_SERVER_PORT")
ucmClientSecurityPolicy = os.environ.get("UCM_CLIENT_SECURITY_POLICY")
ucmUsingSSL = os.environ.get("UCM_USING_SSL")

print('')
print('Configuring Content Server Connection');
print('=====================================');
print('Parameters :');
print(f'Configure Connection :{configureConnection}');
print(f'Connection Name :{ucmConnectionName}');
print(f'Server Host Name :{ucmHost}');
print(f'Port :{ucmPort}');
print(f'Portal Identifier :{ucmPortalIdentifier}');
print(f'Security Group :{ucmSecurityGroup}');
print(f'Admin User Name :{ucmAdminUserName}');
print(f'Socket Type :{ucmsocketType}');
print(f'UCM IntraDoc Server Port :{ucmIntraDocServerPort}');
print(f'UCM Client Security Policy :{ucmClientSecurityPolicy}');
print('')
print('')

if (ucmUsingSSL == 'true'):
    ucmUrl = f"https://{ucmHost}:{ucmPort}/idcnativews"
else:
    ucmUrl = f"http://{ucmHost}:{ucmPort}/idcnativews"

url = f"{adminHost}:{adminPort}"
connect(adminName, adminPassword, url)

deleteContentServerConnection(appName='webcenter', name=ucmConnectionName)
if ucmsocketType == 'socket':
    createContentServerConnection (appName='webcenter', name=ucmConnectionName, socketType=ucmsocketType, serverHost=ucmHost, serverPort=ucmIntraDocServerPort, isPrimary='true')
if ucmsocketType == 'jaxws':
    createContentServerConnection (appName='webcenter', name=ucmConnectionName, socketType=ucmsocketType, url=ucmUrl,adminUsername=ucmAdminUserName, clientSecurityPolicy=ucmClientSecurityPolicy, isPrimary='true')

setContentServerProperties(appName='webcenter', portalServerIdentifier=ucmPortalIdentifier, securityGroup=ucmSecurityGroup, adminUserName=ucmAdminUserName)
listContentServerConnections(appName='webcenter',verbose=1)
listContentServerProperties(appName='webcenter')

disconnect()
exit()

