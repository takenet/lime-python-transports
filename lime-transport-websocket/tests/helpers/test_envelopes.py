SESSIONS = {
    'authenticating': {
        'id': '0',
        'from': '127.0.0.1:8124',
        'state': 'authenticating'
    },
    'established': {
        'id': '0',
        'from': '127.0.0.1:8124',
        'state': 'established'
    }
}

MESSAGES = {
    'pong': {
        'type': 'text/plain',
        'content': 'pong'
    }
}

NOTIFICATIONS = {
    'pong': {
        'event': 'pong'
    }
}

COMMANDS = {
    'ping_response': lambda envelope: {'id': envelope['id'], 'method': 'get', 'status': 'success'}
}
