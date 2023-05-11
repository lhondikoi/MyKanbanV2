import requests
from datetime import datetime
from flask import current_app as app

def gchat(username, pending_cards):
    res = requests.post(
        app.config['GCHAT_WEBHOOK_URL'],
        json={
            'cardsV2': [{
                'card_id': str(datetime.now()),
                'card': {
                        'header': {
                            'title': f'Hi, {username}',
                            'subtitle': f'You have {len(pending_cards)} pending cards.',
                        },
                        'sections': [
                            {
                                'header': 'Pending Cards',
                                'widgets': [
                                    {
                                        'decoratedText': {
                                            'topLabel': card['title'],
                                            'text': card['time_remaining'],
                                            'startIcon': {
                                                'knownIcon': 'TICKET',
                                                'altText': 'card'
                                            }
                                        }
                                    }
                                for card in pending_cards
                                ]
                            }
                        ],
                }
            }]
    })
    return res