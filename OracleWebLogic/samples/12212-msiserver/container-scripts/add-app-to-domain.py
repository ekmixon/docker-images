domain_path  = sys.argv[1]
number_of_ms = int(sys.argv[2])
app_name = sys.argv[3]
app_location = sys.argv[4]
ms_name_prefix = sys.argv[5]

print(f'domain_path     : [{domain_path}]');
print(f'app_name     : [{app_name}]');
print(f'app_location     : [{app_location}]');
print(f'number_of_ms     : [{number_of_ms}]');
print(f'ms_name_prefix     : [{ms_name_prefix}]');

# Open default domain template
# ======================
readDomain(domain_path)

# Configure App
# =============
cd('/')
create(app_name, 'AppDeployment')
cd(f'/AppDeployments/{app_name}/')
set('StagingMode', 'nostage')
set('SourcePath', app_location)
targets = ms_name_prefix + str(1)
for index in range(2, number_of_ms + 1):
  targets = targets + f',{ms_name_prefix + str(index)}'
set('Target', targets)

# Write Domain
# ============
updateDomain()

# Exit WLST
# =========
exit()
