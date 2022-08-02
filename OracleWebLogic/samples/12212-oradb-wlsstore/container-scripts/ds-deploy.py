# Copyright (c) 2014-2018 Oracle and/or its affiliates. All rights reserved.
#
#Licensed under the Universal Permissive License v 1.0 as shown at http://oss.oracle.com/licenses/upl.
##
# WLST Online for deploying a Data Source
# It will read the domain under DOMAIN_HOME by default
#
# author: Monica Riccelli <monica.riccelli@oracle.com>
# since: December, 2017
from java.io import FileInputStream
import java.lang
import os
import string


print('***Starting WLST Online Configure DS***');

#Read Properties
##############################

# 1 - Connecting details - read from system arguments
##############################
domainname = os.environ.get('DOMAIN_NAME', 'base_domain')
admin_name = os.environ.get('ADMIN_NAME', 'AdminServer')
domainhome = os.environ.get(
    'DOMAIN_HOME', f'/u01/oracle/user_projects/domains/{domainname}'
)

adminport = os.environ.get('ADMIN_PORT', '7001')
username = os.environ.get('ADMIN_USER', 'weblogic')
password = os.environ.get('ADMIN_PASSWORD', 'welcome1')
admin_url='t3://localhost:7001'

print(f'admin_name  : [{admin_name}]');
print(f'admin_user  : [{username}]');
print(f'admin_password  : [{password}]');
print(f'admin_port  : [{adminport}]');
print(f'domain_home  : [{domainhome}]');
print(f'dsname  : [{dsname}]');
print(f'admin_url  : [{admin_url}]');
print(f'target_type  : [{target_type}]');

# Connect to the AdminServer.
connect(username, password, "t3://localhost:7001")

edit()
startEdit()

from java.io import FileInputStream
cd('/')
cmo.createJDBCSystemResource(dsname)

cd(f'/JDBCSystemResources/{dsname}/JDBCResource/{dsname}')
cmo.setName(dsname)

cd(
    f'/JDBCSystemResources/{dsname}/JDBCResource/{dsname}/JDBCDataSourceParams/{dsname}'
)

set('JNDINames',jarray.array([String(dsjndiname)], String))

cd(
    f'/JDBCSystemResources/{dsname}/JDBCResource/{dsname}/JDBCDriverParams/{dsname}'
)

cmo.setUrl(dsurl)
cmo.setDriverName(dsdriver)
set('Password', dspassword)

cd(
    f'/JDBCSystemResources/{dsname}/JDBCResource/{dsname}/JDBCConnectionPoolParams/{dsname}'
)

cmo.setTestTableName('SQL SELECT 1 FROM DUAL\r\n\r\n')
cmo.setInitialCapacity(int(cp_initial_capacity))

cd(
    f'/JDBCSystemResources/{dsname}/JDBCResource/{dsname}/JDBCDriverParams/{dsname}/Properties/{dsname}'
)

cmo.createProperty('user')

cd(
    f'/JDBCSystemResources/{dsname}/JDBCResource/{dsname}/JDBCDriverParams/{dsname}/Properties/{dsname}/Properties/user'
)

cmo.setValue(dsusername)

cd(
    f'/JDBCSystemResources/{dsname}/JDBCResource/{dsname}/JDBCDataSourceParams/{dsname}'
)

cmo.setGlobalTransactionsProtocol('TwoPhaseCommit')

activate()

from java.io import FileInputStream
startEdit()
cd(f'/JDBCSystemResources/{dsname}')
set(
    'Targets',
    jarray.array(
        [ObjectName(f'com.bea:Name={admin_name},Type={target_type}')],
        ObjectName,
    ),
)


activate()
# Update Domain, Close It, Exit
# ==========================

disconnect()
exit()
print('***End of  WLST Online Configure DS***');
