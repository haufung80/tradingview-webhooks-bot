# actions
REGISTERED_ACTIONS = ['PrintData',
                      # 'IBOrderExecute',
                      # 'FutuOrderExecute',
                      'BybitOrderExecute'
                      ]

# events
REGISTERED_EVENTS = ['WebhookReceived',
                     # 'IBWebhook',
                     'BybitWebhook',
                     # 'FutuWebhook'
                     ]

# links
REGISTERED_LINKS = [
    ('PrintData', 'WebhookReceived'),
    # ('FutuOrderExecute', 'FutuWebhook'),
    ('BybitOrderExecute', 'BybitWebhook'),
    # ('IBOrderExecute', 'IBWebhook')
]
