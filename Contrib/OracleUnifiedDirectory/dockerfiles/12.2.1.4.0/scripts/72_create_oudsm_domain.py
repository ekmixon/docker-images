# ----------------------------------------------------------------------
# Trivadis AG, Infrastructure Managed Services
# Saegereistrasse 29, 8152 Glattbrugg, Switzerland
# ----------------------------------------------------------------------
# Name.......: create_OUDSM.py
# Author.....: Stefan Oehrli (oes) stefan.oehrli@trivadis.com
# Editor.....: Stefan Oehrli
# Date.......: 2017.12.04
# Revision...:
# Purpose....: Script to create OUDSM Domain
# Notes......:
# Reference..: This script is a copy from the Git repository 
#              https://github.com/oehrlis/oradba_init 
# License....: Licensed under the Universal Permissive License v 1.0 as 
#              shown at http://oss.oracle.com/licenses/upl.
# ----------------------------------------------------------------------
# Modified...:
# see git revision history for more information on changes/updates
# TODO.......:
# ----------------------------------------------------------------------
import os

# define environment variables
domain_name      = os.environ.get('DOMAIN_NAME', "oudsm_domain")
domain_path = os.environ.get('DOMAIN_HOME', f"/u01/domains/{domain_name}")
admin_port       = int(os.environ.get('PORT', "7001"))
admin_sslport    = int(os.environ.get('PORT_SSL', "7002"))
admin_user       = os.environ.get('ADMIN_USER', "weblogic")
admin_pass       = "ADMIN_PASSWORD"


print(f'Domain Name     : [{domain_name}]')
print(f'Domain Path     : [{domain_path}]')
print(f'Admin Port      : [{admin_port}]')
print(f'Admin SSL Port  : [{admin_sslport}]')
print(f'User            : [{admin_user}]')
print(f'Password        : [{admin_pass}]')

# create WLS Domain
createOUDSMDomain(domainLocation        = domain_path,
                  weblogicPort          = admin_port,
                  weblogicSSLPort       = admin_sslport,
                  weblogicUserName      = admin_user,
                  weblogicUserPassword  = admin_pass)