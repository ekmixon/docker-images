#
# Copyright (c) 2014, 2019 Oracle and/or its affiliates. All rights reserved.
#
#Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#

import os
import sys

import com.oracle.cie.domain.script.jython.WLSTException as WLSTException

class Infra12213Provisioner:

    MACHINES = {
        'machine1' : {
            'NMType': 'SSL',
            'ListenAddress': 'localhost',
            'ListenPort': 5658
        }
    }

    CLUSTERS = {
        'infra_cluster' : {}
    }


    JRF_12213_TEMPLATES = {
        'baseTemplate' : '@@ORACLE_HOME@@/wlserver/common/templates/wls/wls.jar',
        'extensionTemplates' : [
            '@@ORACLE_HOME@@/oracle_common/common/templates/wls/oracle.jrf_template.jar',
            '@@ORACLE_HOME@@/oracle_common/common/templates/wls/oracle.jrf.ws.async_template.jar',
            '@@ORACLE_HOME@@/oracle_common/common/templates/wls/oracle.wsmpm_template.jar',
            '@@ORACLE_HOME@@/oracle_common/common/templates/wls/oracle.ums_template.jar',
            '@@ORACLE_HOME@@/em/common/templates/wls/oracle.em_wls_template.jar'
        ],
        'serverGroupsToTarget' : [ 'JRF-MAN-SVR', 'WSMPM-MAN-SVR' ]
    }

    def __init__(self, oracleHome, javaHome, domainParentDir, adminListenPort, adminName, adminPortEnabled, administrationPort, managedName, managedServerPort, prodMode):
        self.oracleHome = self.validateDirectory(oracleHome)
        self.javaHome = self.validateDirectory(javaHome)
        self.domainParentDir = self.validateDirectory(domainParentDir, create=True)
        return

    def createInfraDomain(self, name, user, password, db, dbPrefix, dbPassword, adminListenPort, adminName, adminPortEnabled, administrationPort, managedName, managedServerPort, prodMode):
        domainHome = self.createBaseDomain(name, user, password, adminListenPort, adminName, adminPortEnabled, administrationPort, managedName, managedServerPort, prodMode)
        self.extendDomain(domainHome, db, dbPrefix, dbPassword)

    def createBaseDomain(self, name, user, password, adminListenPort, adminName, adminPortEnabled, administrationPort, managedName, managedServerPort, prodMode):
        baseTemplate = self.replaceTokens(self.JRF_12213_TEMPLATES['baseTemplate'])

        readTemplate(baseTemplate)
        setOption('DomainName', name)
        setOption('JavaHome', self.javaHome)
        setOption('ServerStartMode', prodMode)
        set('Name', domainName)

        # Set Administration Port
        # =======================
        if adminPortEnabled != "false":
           set('AdministrationPort', int(administrationPort))
           set('AdministrationPortEnabled', 'true')

        baseTemplate = self.replaceTokens(self.JRF_12213_TEMPLATES['baseTemplate'])

        cd('/Servers/AdminServer')
        #set('ListenAddress', '%s-%s' % (domain_uid, admin_server_name_svc))
        set('ListenPort', int(adminListenPort))
        set('Name', adminName)
        if adminPortEnabled != "false":
           create('AdminServer','SSL')
           cd('SSL/AdminServer')
           set('Enabled', 'True')

        # Define the user password for weblogic
        # =====================================
        cd(f'/Security/{domainName}/User/weblogic')
        set('Name', user)
        set('Password', password)

        baseTemplate = self.replaceTokens(self.JRF_12213_TEMPLATES['baseTemplate'])

        for cluster in self.CLUSTERS:
            cd('/')
            create(cluster, 'Cluster')
            cd(f'Cluster/{cluster}')
            for param in  self.CLUSTERS[cluster]:
                set(param, self.CLUSTERS[cluster][param])

        baseTemplate = self.replaceTokens(self.JRF_12213_TEMPLATES['baseTemplate'])

        for machine in self.MACHINES:
            cd('/')
            create(machine, 'Machine')
            cd(f'Machine/{machine}')
            create(machine, 'NodeManager')
            cd(f'NodeManager/{machine}')
            for param in self.MACHINES[machine]:
                set(param, self.MACHINES[machine][param])


        baseTemplate = self.replaceTokens(self.JRF_12213_TEMPLATES['baseTemplate'])

        cd('/')
        create(managedName, 'Server')
        cd(f'/Servers/{managedName}/')
        print(f'managed server name is {managedName}');
        #   set('ListenAddress', '%s-%s' % (domain_uid, name_svc))
        set('ListenPort', int(managedServerPort))
        set('Cluster', 'infra_cluster')
        if adminPortEnabled != "false":
            create(managedName,'SSL')
            cd(f'SSL/{managedName}')
            set('Enabled', 'True')

        setOption('OverwriteDomain', 'true')
        domainHome = f'{self.domainParentDir}/{name}'

        baseTemplate = self.replaceTokens(self.JRF_12213_TEMPLATES['baseTemplate'])

        writeDomain(domainHome)
        closeTemplate()
        baseTemplate = self.replaceTokens(self.JRF_12213_TEMPLATES['baseTemplate'])

        return domainHome


    def extendDomain(self, domainHome, db, dbPrefix, dbPassword):
        print 'Extending domain at ' + domainHome
        print 'Database  ' + db 
        readDomain(domainHome)
        setOption('AppDir', self.domainParentDir + '/applications')

        print 'Applying JRF templates...'
        for extensionTemplate in self.JRF_12213_TEMPLATES['extensionTemplates']:
            addTemplate(self.replaceTokens(extensionTemplate))

        print 'Extension Templates added'

        print 'Configuring the Service Table DataSource...'
        fmwDb = 'jdbc:oracle:thin:@' + db
        print 'fmwDatabase  ' + fmwDb 
        cd('/JDBCSystemResource/LocalSvcTblDataSource/JdbcResource/LocalSvcTblDataSource')
        cd('JDBCDriverParams/NO_NAME_0')
        set('DriverName', 'oracle.jdbc.OracleDriver')
        set('URL', fmwDb)
        set('PasswordEncrypted', dbPassword)

        stbUser = dbPrefix + '_STB'
        cd('Properties/NO_NAME_0/Property/user')
        set('Value', stbUser)

        print 'Getting Database Defaults...'
        getDatabaseDefaults()

        print 'Targeting Server Groups...'
        serverGroupsToTarget = list(self.JRF_12213_TEMPLATES['serverGroupsToTarget'])
        cd('/')
        setServerGroups(managedName, serverGroupsToTarget)
	print "Set CoherenceClusterSystemResource to defaultCoherenceCluster for server:" + managedName
        cd('/Servers/' + managedName)
        set('CoherenceClusterSystemResource', 'defaultCoherenceCluster')

        cd('/')
        for cluster in self.CLUSTERS:
            print "Set CoherenceClusterSystemResource to defaultCoherenceCluster for cluster:" + cluster
            cd('/Cluster/' + cluster)
            set('CoherenceClusterSystemResource', 'defaultCoherenceCluster')

        print "Set WLS clusters as target of defaultCoherenceCluster:[" + ",".join(self.CLUSTERS) + "]"
        cd('/CoherenceClusterSystemResource/defaultCoherenceCluster')
        set('Target', ",".join(self.CLUSTERS))

        print 'Preparing to update domain...'
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
    print sys.argv[0] + ' -oh <oracle_home> -jh <java_home> -parent <domain_parent_dir> [-name <domain-name>] ' + \
          '[-user <domain-user>] [-password <domain-password>] ' + \
          '-rcuDb <rcu-database> [-rcuPrefix <rcu-prefix>] [-rcuSchemaPwd <rcu-schema-password>]'
    sys.exit(0)

# Uncomment for Debug only
#print str(sys.argv[0]) + " called with the following sys.argv array:"
#for index, arg in enumerate(sys.argv):
#    print "sys.argv[" + str(index) + "] = " + str(sys.argv[index])

if len(sys.argv) < 6:
    usage()

#oracleHome will be passed by command line parameter -oh.
oracleHome = None
#javaHome will be passed by command line parameter -jh.
javaHome = None
#domainParentDir will be passed by command line parameter -parent.
domainParentDir = None
#domainUser is hard-coded to weblogic. You can change to other name of your choice. Command line paramter -user.
domainUser = 'weblogic'
#domainPassword will be passed by Command line parameter -password.
#domainPassword = 'welcome1'
domainPassword = None
#rcuDb will be passed by command line parameter -rcuDb.
rcuDb = None
#change rcuSchemaPrefix to your infra schema prefix. Command line parameter -rcuPrefix.
rcuSchemaPrefix = 'DEV12'
#change rcuSchemaPassword to your infra schema password. Command line parameter -rcuSchemaPwd.
#rcuSchemaPassword = 'welcome1'
rcuSchemaPassword = None

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
    elif sys.argv[i] == '-adminListenPort':
        adminListenPort = sys.argv[i + 1]
        i += 2
    elif sys.argv[i] == '-adminName':
        adminName = sys.argv[i + 1]
        i += 2
    elif sys.argv[i] == '-adminPortEnabled':
        adminPortEnabled = sys.argv[i + 1]
        i += 2
    elif sys.argv[i] == '-administrationPort':
        administrationPort = sys.argv[i + 1]
        i += 2
    elif sys.argv[i] == '-managedName':
        managedName = sys.argv[i + 1]
        i += 2
    elif sys.argv[i] == '-managedServerPort':
        managedServerPort = sys.argv[i + 1]
        i += 2
    elif sys.argv[i] == '-prodMode':
        prodMode = sys.argv[i + 1]
        i += 2
    else:
        print 'Unexpected argument switch at position ' + str(i) + ': ' + str(sys.argv[i])
        usage()
        sys.exit(1)

provisioner = Infra12213Provisioner(oracleHome, javaHome, domainParentDir, adminListenPort, adminName, adminPortEnabled, administrationPort, managedName, managedServerPort, prodMode)
provisioner.createInfraDomain(domainName, domainUser, domainPassword, rcuDb, rcuSchemaPrefix, rcuSchemaPassword, adminListenPort, adminName, adminPortEnabled, administrationPort, managedName, managedServerPort, prodMode)
