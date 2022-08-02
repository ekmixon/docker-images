import sys

domain_name  = sys.argv[1]
template_location = sys.argv[2]
domain_path = sys.argv[3] + f'/{domain_name}'
user_name = sys.argv[4]
password = sys.argv[5]
as_port = int(sys.argv[6])
ms_name = sys.argv[7]
ms_port = int(sys.argv[8])
production_mode = sys.argv[9]
number_of_ms = int(sys.argv[10])
ms_name_prefix = sys.argv[11]

print(f'domain_name     : [{domain_name}]');
print(f'template_location     : [{template_location}]');
print(f'domain_path     : [{domain_path}]');
print(f'user_name     : [{user_name}]');
print('password     : ********');
print(f'as_port      : [{as_port}]');
print(f'ms_name  : [{ms_name}]');
print(f'ms_port     : [{ms_port}]');
print(f'production_mode : [{production_mode}]');
print(f'number_of_ms : [{number_of_ms}]');
print(f'ms_name_prefix  : [{ms_name_prefix}]');

# Open default domain template
# ======================
readTemplate(template_location)

set('Name', domain_name)
setOption('DomainName', domain_name)

# Disable Admin Console
# --------------------
cmo.setConsoleEnabled(false)

# Configure the Administration Server and SSL port.
# =========================================================
cd('/Servers/AdminServer')
set('ListenPort', as_port)

# Define the user password for weblogic
# =====================================
cd(f'/Security/%s/User/{user_name}' % domain_name)
cmo.setPassword(password)

# Write the domain and close the domain template
# ==============================================
setOption('OverwriteDomain', 'true')
setOption('ServerStartMode',production_mode)

# Create Server & set MSI configuration
# =====================================
cd('/')
sys.stdout.write(f'Creating {number_of_ms} servers')
sys.stdout.flush()
for index in range(1, number_of_ms + 1):
  cd('/')
  sys.stdout.write('.')
  sys.stdout.flush()
  create(ms_name_prefix + str(index), 'Server')
  cd(f'/Servers/{ms_name_prefix + str(index)}/')
  set('ListenPort', ms_port)
  set('NumOfRetriesBeforeMSIMode', 0)
  set('RetryIntervalBeforeMSIMode', 1)
import sys

# Write Domain
# ============
writeDomain(domain_path)
closeTemplate()

# Exit WLST
# =========
exit()
