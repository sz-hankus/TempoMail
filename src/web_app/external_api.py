from random import choice
import requests
from json import loads 
from datetime import datetime

from utils.generate_login import generate_login
from web_app import models

API_BASE='https://www.1secmail.com/api/v1/'
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def get_random_address() -> tuple[str, str]:
    login = generate_login()
    domains = loads(requests.request('GET', f'{API_BASE}?action=getDomainList').content.decode('utf-8'))
    return (login, choice(domains))


def update_messages(address: models.Address) -> None:
    """
    Fetches and saves messages which do not exist in the database yet.  
    """
    login, domain = address.login, address.domain
    message_list = loads(requests.request('GET', f'{API_BASE}?action=getMessages&login={login}&domain={domain}').content.decode('utf-8'))
    for message in message_list:
        # skip the already existing messages
        if models.Message.objects.filter(address=address, external_id=message['id']).exists():
            continue
        message_data = fetch_message(address, message['id'])
        # get_or_create for safety
        models.Message.objects.get_or_create(
            external_id=message_data['id'],
            sender=message_data['from'],
            subject=message_data['subject'],
            content=message_data['body'],
            date=datetime.strptime(message_data['date'], TIME_FORMAT),
            address=address)            


def fetch_message(address: models.Address, message_id: str) -> dict:
    login, domain = address.login, address.domain
    message_data = loads(requests.request('GET', f'{API_BASE}?action=readMessage&login={login}&domain={domain}&id={message_id}').content.decode('utf-8'))
    return message_data
