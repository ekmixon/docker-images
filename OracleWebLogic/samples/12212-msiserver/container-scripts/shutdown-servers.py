host = sys.argv[1]
port = sys.argv[2]
user_name = sys.argv[3]
password = sys.argv[4]
name = sys.argv[5]

print(f'host     : [{host}]');
print(f'port      : [{port}]');
print(f'user_name     : [{user_name}]');
print('password     : ********');
print(f'name     : [{name}]');

connect(user_name, password, f't3://{host}:{port}')
shutdown(name, 'Server', ignoreSessions='true')
exit()
