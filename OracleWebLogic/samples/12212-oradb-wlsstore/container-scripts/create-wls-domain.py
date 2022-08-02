# Copyright (c) 2014-2018 Oracle and/or its affiliates. All rights reserved.
#
#
#Licensed under the Universal Permissive License v 1.0 as shown at http://oss.oracle.com/licenses/upl.
#
#
# WebLogic on Docker Default Domain
#
# Domain, as defined in DOMAIN_NAME, will be created in this script. Name defaults to 'base_domain'.
#
# Author: monica.riccelli@oracle.com
# ==============================================
domain_name  = os.environ.get("DOMAIN_NAME", "base_domain")
admin_name  = os.environ.get("ADMIN_NAME", "AdminServer")
admin_username  = os.environ.get("ADMIN_USERNAME", "weblogic")
admin_pass  = os.environ.get("ADMIN_PASSWORD", "welcome1")
admin_port   = int(os.environ.get("ADMIN_PORT", "7001"))
domain_path = f'/u01/oracle/user_projects/domains/{domain_name}'
production_mode = os.environ.get("PRODUCTION_MODE", "prod")

print(f'domain_name     : [{domain_name}]');
print(f'admin_port      : [{admin_port}]');
print(f'domain_path     : [{domain_path}]');
print(f'production_mode : [{production_mode}]');
print(f'admin password  : [{admin_pass}]');
print(f'admin name      : [{admin_name}]');
print(f'admin username  : [{admin_username}]');

# Open default domain template
# ======================
readTemplate("/u01/oracle/wlserver/common/templates/wls/wls.jar")

set('Name', domain_name)
setOption('DomainName', domain_name)

# Disable Admin Console
# --------------------
# cmo.setConsoleEnabled(false)

# Configure the Administration Server and SSL port.
# =========================================================
cd('/Servers/AdminServer')
set('Name', admin_name)
set('ListenAddress', '')
set('ListenPort', admin_port)

# Define the user password for weblogic
# =====================================
cd(f'/Security/{domain_name}/User/weblogic')
cmo.setPassword(admin_pass)

# Write the domain and close the domain template
# ==============================================
setOption('OverwriteDomain', 'true')
setOption('ServerStartMode',production_mode)

cd('/NMProperties')
set('ListenAddress','')
set('ListenPort',5556)
set('CrashRecoveryEnabled', 'true')
set('NativeVersionEnabled', 'true')
set('StartScriptEnabled', 'false')
set('SecureListener', 'false')
set('LogLevel', 'FINEST')

# Set the Node Manager user name and password (domain name will change after writeDomain)
cd('/SecurityConfiguration/base_domain')
set('NodeManagerUsername', admin_username)
set('NodeManagerPasswordEncrypted', admin_pass)

# Write Domain
# ============
writeDomain(domain_path)
closeTemplate()

# Exit WLST
# =========
exit()
