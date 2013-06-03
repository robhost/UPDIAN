import re

def validate_server(server):
    errors = []

    if not server.hostname:
        errors.append('Hostname must not be empty.')

    if server.port is not None and (server.port < 1 or server.port > 65535):
        errors.append('Port has to be an integer between 1 and 65535 if set.')

    if server.user and re.search('[@\s]', server.user):
        errors.append('Username must not include @-signs or whitespace.')

    if (server.gateway and
        not re.match('^([^@:\s]+@)?([^@:\s]+)(:\d+)?$', server.gateway)):
        errors.append('Gateway must be given in format "user@host:port". '
                      'User and port are optional.')

    return errors
