# actions
REGISTERED_ACTIONS = ['PrintData', 'IBOrderExecute', 'BybitOrderExecute']

# events
REGISTERED_EVENTS = ['BybitWebhook', 'WebhookReceived', 'IBWebhook']

# links
REGISTERED_LINKS = [('IBOrderExecute', 'IBWebhook'), ('BybitOrderExecute', 'BybitWebhook'), ('PrintData', 'WebhookReceived')]

