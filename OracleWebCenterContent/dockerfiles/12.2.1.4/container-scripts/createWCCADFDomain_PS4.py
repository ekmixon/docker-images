#!/usr/bin/python
# Copyright (c) 2021, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl
#
# ==============================================

import os
import sys

import com.oracle.cie.domain.script.jython.WLSTException as WLSTException

class WCCADF12214Provisioner:

    CLUSTERS = {
        'wccadf_cluster1' : {}
    }

    SERVERS = {
        'WCCADF_server1' : {
            'ListenAddress': '',
            'ListenPort': 16225,
            'Machine': 'machine1',
            'Cluster': 'wccadf_cluster1'
        }
    }

    JRF_12214_TEMPLATES = {
        'extensionTemplates' : [
            '@@ORACLE_HOME@@/oracle_common/common/templates/wls/oracle.jrf_template.jar'
        ],
        'serverGroupsToTarget' : [ 'JRF-MAN-SVR' ]
    }

    WCCADF_12214_TEMPLATES = {
        'extensionTemplates' : [
            '@@ORACLE_HOME@@/wccontent/common/templates/wls/oracle.ucm.cs_adf_template.jar'
        ],
        'serverGroupsToTarget' : ['UCM-ADF-MGD-SVR']
    }    

    def __init__(self, oracleHome, javaHome, domainParentDir, adminServerPort, wccadfManagedServerPort):
        self.oracleHome = self.validateDirectory(oracleHome)
        self.javaHome = self.validateDirectory(javaHome)
        self.domainParentDir = self.validateDirectory(domainParentDir, create=True)
        self.SERVERS['WCCADF_server1']['ListenPort'] = int(wccadfManagedServerPort)
        return

    def createWCCADFDomain(self, name, user, password, db, dbPrefix, dbPassword):
        self.extendDomain(f'{self.domainParentDir}/{name}', db, dbPrefix, dbPassword)


    def extendDomain(self, domainHome, db, dbPrefix, dbPassword):
        print 'Extending domain at ' + domainHome
        readDomain(domainHome)

        print 'Creating WCCADF cluster...'
        for cluster in self.CLUSTERS:
            cd('/')
            create(cluster, 'Cluster')
            cd('Cluster/' + cluster)
            for param in  self.CLUSTERS[cluster]:
                set(param, self.CLUSTERS[cluster][param])

        print 'Creating WCCADF Server...'
        for server in self.SERVERS:
            cd('/')
            create(server, 'Server')
            cd('Server/' + server)
            for param in self.SERVERS[server]:
                set(param, self.SERVERS[server][param])
                print 'assigning ' + param + ' to ' + server + ':'
                print self.SERVERS[server][param]

        setOption('AppDir', self.domainParentDir + '/applications')

        print 'Applying WCCADF templates...'
        for extensionTemplate in self.WCCADF_12214_TEMPLATES['extensionTemplates']:
            addTemplate(self.replaceTokens(extensionTemplate))
        
        print 'Extension Templates added'

        print 'Getting Database Defaults...'
        getDatabaseDefaults()
        
        
        print 'Changing the MDS schema connection information...'
        dsName = 'mds-WCCUIMDSREPO'
        print 'Name of WCCADF MDS Datasource = ' + dsName
        cd('/')
        print 'Setting URL, Password and user for MDS Datasource...'
        cd('/JDBCSystemResource/' + dsName + '/JdbcResource/' + dsName)
        cd('JDBCDriverParams/NO_NAME_0')
        set('URL',"jdbc:oracle:thin:@//"+rcuDb)
        set('PasswordEncrypted', rcuSchemaPassword)
        cd('Properties/NO_NAME_0/Property/user')
        set('Value', rcuSchemaPrefix + '_MDS')

        print 'Targeting Server Groups...'
        serverGroupsToTarget = list(self.JRF_12214_TEMPLATES['serverGroupsToTarget'])
        serverGroupsToTarget.extend(self.WCCADF_12214_TEMPLATES['serverGroupsToTarget'])


        print 'Adding the WCC ADF user credential...'
        cd('/')
        cd('/Credential/TargetStore/oracle.wcc.security/TargetKey/wccadfConnectUser')
        create('c','Credential')
        cd('Credential')
        set('Username',domainUser)
        set('Password',domainPassword)        
         
        cd('/')
        for server in self.SERVERS:
            if not server == 'AdminServer':
                print "Overriding WCCADF templates default values :" + server
                cd('/Servers/' + server)
                for param in self.SERVERS[server]:
                    set(param, self.SERVERS[server][param])
                    print 'assigning ' + param + ' to ' + server + ':'
                    print self.SERVERS[server][param]   
    
        for server in self.SERVERS:
            if not server == 'AdminServer':
                print "Set CoherenceClusterSystemResource to defaultCoherenceCluster for server:" + server
                cd('/Servers/' + server)
                set('CoherenceClusterSystemResource', 'defaultCoherenceCluster')
        
        cd('/')
        for cluster in self.CLUSTERS:            
            print "Set CoherenceClusterSystemResource to defaultCoherenceCluster for cluster:" + cluster
            cd('/Cluster/' + cluster)
            set('CoherenceClusterSystemResource', 'defaultCoherenceCluster')

        print "Set WLS clusters as target of defaultCoherenceCluster:[" + ",".join(self.CLUSTERS) + "]"
        cd('/CoherenceClusterSystemResource/defaultCoherenceCluster')
        set('Target', ",".join(self.CLUSTERS))

        print 'Preparing to update domain... '
        updateDomain()
        print 'Domain updated successfully'
        closeDomain()

        return


    ###########################################################################
    # Helper Methods                                                          #
    ###########################################################################

    def validateDirectory(self, dirName, create=False):
        directory = os.path.realpath(dirName)
        if not os.path.exists(directory):
            if create:
                os.makedirs(directory)
            else:
                message = f'Directory {directory} does not exist'
                raise WLSTException(message)
        elif not os.path.isdir(directory):
            message = f'Directory {directory} is not a directory'
            raise WLSTException(message)
        return self.fixupPath(directory)


    def fixupPath(self, path):
        result = path
        if path is not None:
            result = path.replace('\\', '/')
        return result


    def replaceTokens(self, path):
        result = path
        if path is not None:
            result = path.replace('@@ORACLE_HOME@@', oracleHome)
        return result


#############################
# Entry point to the script #
#############################

def usage():
    print sys.argv[0] + sys.argv[1] + ' -oh <oracle_home> -jh <java_home> -parent <domain_parent_dir> [-name <domain-name>] ' + \
          '[-user <domain-user>] [-password <domain-password>] ' + \
          '-rcuDb <rcu-database> [-rcuPrefix <rcu-prefix>] [-rcuSchemaPwd <rcu-schema-password>]' + \
          '[-adminServerPort <admin_port>] [-wccadfManagedServerPort <wccadf_port>]'
    sys.exit(0)


if len(sys.argv) < 6:
    usage()

#oracleHome will be passed by command line parameter -oh.
oracleHome = None
#javaHome will be passed by command line parameter -jh.
javaHome = None
#domainParentDir will be passed by command line parameter -parent.
domainParentDir = None
#domainName is hard-coded to base_domain. You can change to other name of your choice. Command line parameter -name.
domainName = 'base_domain'
#domainUser will be passed by Command line paramter -user.
domainUser = None
#domainPassword will be passed by Command line parameter -password.
domainPassword = None
#rcuDb will be passed by command line parameter -rcuDb.
rcuDb = None
rcuSchemaPrefix = None
rcuSchemaPassword = None
#The datasource name is hard-coded.
dsName = 'mds-WCCUIMDSREPO'
#adminServerPort is hard-coded 7001.You can change to other port of your choice. Command line parameter -adminServerPort.
adminServerPort = '7001'

#wccadfManagedServerPort is hard-coded 16225.You can change to other port of your choice. Command line parameter -wccadfManagedServerPort.
wccadfManagedServerPort = '16225'


i = 1
while i < len(sys.argv):
    if sys.argv[i] == '-oh':
        oracleHome = sys.argv[i + 1]
        i += 2
    elif sys.argv[i] == '-jh':
        javaHome = sys.argv[i + 1]
        i += 2
    elif sys.argv[i] == '-parent':
        domainParentDir = sys.argv[i + 1]
        i += 2
    elif sys.argv[i] == '-name':
        domainName = sys.argv[i + 1]
        i += 2
    elif sys.argv[i] == '-user':
        domainUser = sys.argv[i + 1]
        i += 2
    elif sys.argv[i] == '-password':
        domainPassword = sys.argv[i + 1]
        i += 2
    elif sys.argv[i] == '-rcuDb':
        rcuDb = sys.argv[i + 1]
        i += 2
    elif sys.argv[i] == '-rcuPrefix':
        rcuSchemaPrefix = sys.argv[i + 1]
        i += 2
    elif sys.argv[i] == '-rcuSchemaPwd':
        rcuSchemaPassword = sys.argv[i + 1]
        i += 2
    elif sys.argv[i] == '-adminServerPort':
        adminServerPort = sys.argv[i + 1]
        i += 2
    elif sys.argv[i] == '-wccadfManagedServerPort':
        wccadfManagedServerPort = sys.argv[i + 1]
        i += 2
    else:
        print 'Unexpected argument switch at position ' + str(i) + ': ' + str(sys.argv[i])
        usage()
        sys.exit(1)

provisioner = WCCADF12214Provisioner(oracleHome, javaHome, domainParentDir, adminServerPort, wccadfManagedServerPort)
provisioner.createWCCADFDomain(domainName, domainUser, domainPassword, rcuDb, rcuSchemaPrefix, rcuSchemaPassword)