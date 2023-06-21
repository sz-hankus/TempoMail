from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.core.exceptions import BadRequest
from django.forms.models import model_to_dict

from uuid import uuid4 as rand_uuid

from . import models, external_api


# Views for the web_app
def home(request: HttpRequest):
    uuid = request.COOKIES.get('uuid', None)
    if not uuid:
        new_id = str(rand_uuid())
        new_user = models.User.objects.create_new(new_id)
        response = render(request, 'web_app/home.html', {'addresses': []})
        response.set_cookie('uuid', new_id)
        return response
    elif uuid and not models.User.objects.filter(uuid=uuid).exists():
        new_user = models.User.objects.create_new(uuid)
        return render(request, 'web_app/home.html', {'addresses': []})

    user = models.User.objects.filter(uuid=uuid).first()
    addresses = models.Address.objects.filter(user=user)
    return render(request, 'web_app/home.html', {'addresses': addresses})


def inbox(request: HttpRequest):
    uuid = request.COOKIES.get('uuid', None)
    login = request.GET.get('login', None)
    domain = request.GET.get('domain', None)
    if not login or not domain:
        raise BadRequest('HTTP parameters (login or domain) were not set')
    user = models.User.objects.filter(uuid=uuid).first()
    address = models.Address.objects.filter(user=user, login=login, domain=domain).first()
    if not address:
        raise BadRequest('No such address')

    # make a request to the external API and save new messages
    message_list = external_api.fetch_message_list(address)
    external_api.save_new_from_list(address, message_list)

    context = {
        'title': f'{login}@{domain} inbox',
        'address': address,
        'messages': models.Message.objects.filter(address=address).all(),
    }
    return render(request, 'web_app/inbox.html', context)


def message(request: HttpRequest):
    uuid = request.COOKIES.get('uuid', None)
    login = request.GET.get('login', None)
    domain = request.GET.get('domain', None)
    message_id = request.GET.get('id', None)
    if not all((login, domain, message_id)):
        raise BadRequest('HTTP query parameters (login, domain or id) were not set')

    user = models.User.objects.filter(uuid=uuid).first()
    address = models.Address.objects.filter(user=user, login=login, domain=domain).first()
    message = models.Message.objects.filter(external_id=message_id, address=address).first()
    if not all((user, address, message)):
        raise BadRequest('No such message')
    
    return render(request, 'web_app/message.html', model_to_dict(message))


def get_new_address(request: HttpRequest):
    uuid = request.COOKIES.get('uuid', None)
    user = models.User.objects.filter(uuid=uuid).first()
    if not uuid or not user:
        return redirect('/')

    login, domain = external_api.get_random_address()

    models.Address.objects.create_new(login, domain, user.uuid)
    return redirect('/') 


def delete_address(request: HttpRequest):
    uuid = request.COOKIES.get('uuid', None)
    login = request.GET.get('login', None)
    domain = request.GET.get('domain', None)
    if not uuid:
        return redirect('/')
    if not login or not domain:
        raise BadRequest('HTTP query parameters (login or domain) were not set')
    
    address = models.Address.objects.filter(login=login, domain=domain).first()
    if not address:
        raise BadRequest(f'Address {login}@{domain} does not exist')

    address.delete()    
    return redirect('/')