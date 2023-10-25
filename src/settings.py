# actions
REGISTERED_ACTIONS = ['PrintData', 'IBOrderExecute']

# events
REGISTERED_EVENTS = ['IBWebhook', 'WebhookReceived']

# links
REGISTERED_LINKS = [('IBOrderExecute', 'IBWebhook'), ('PrintData', 'WebhookReceived')]

