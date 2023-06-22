from django.db import models
from celery import shared_task
from celery.utils.log import get_task_logger

from datetime import datetime, timedelta
from TempoMail import config

logger = get_task_logger(__name__)

class UserManager(models.Manager):
    @shared_task
    def terminate_user(uuid: str) -> None:
        user = User.objects.filter(uuid=uuid).first()
        if user: 
            user.delete()
            logger.info(f'user {user.uuid} terminated')

    def create_new(self, uuid: str):
        expiry_time = datetime.now() + timedelta(seconds=config.USER_LIFETIME)
        new_user, created = self.get_or_create(uuid=uuid, expiry_time=expiry_time)
        if not created:
            raise Exception(f'Attempted to create user that already exists ({uuid})')
        
        # schedule termination
        self.terminate_user.apply_async((uuid,), countdown=config.USER_LIFETIME)
        logger.info(f'user {new_user.uuid}, scheduled termination at {expiry_time}')
        return new_user
        


class User(models.Model):
    objects = UserManager()
    # Properties
    uuid = models.CharField(max_length=36)
    expiry_time = models.DateTimeField(default=datetime.now())

    def get_time_left(self) -> int:
        no_timezone = self.expiry_time.replace(tzinfo=None)
        seconds = (no_timezone - datetime.now()).seconds
        return seconds if seconds >= 0 else 0

    def __str__(self):
        return f'{self.uuid}'


class AddressManager(models.Manager):
    @shared_task
    def terminate_address(login: str, domain: str) -> None:
        address = Address.objects.filter(login=login, domain=domain).first()
        if address: 
            address.delete()
            logger.debug(f'address {address.login}@{address.domain} terminated')
    
    def create_new(self, login: str, domain: str, uuid: str):
        user = User.objects.filter(uuid=uuid).first()
        expiry_time = datetime.now() + timedelta(seconds=config.ADDRESS_LIFETIME)
        new_address, created = self.get_or_create(login=login, domain=domain, user=user, expiry_time=expiry_time)
        if not created:
            raise Exception(f'Attempted to create an address that already exists ({login}@{domain})')

        # schedule termination
        self.terminate_address.apply_async((login, domain), countdown=config.ADDRESS_LIFETIME)
        logger.debug(f'address {new_address.login}@{new_address.domain}, scheduled termination at {expiry_time}')
        return new_address


class Address(models.Model):
    objects = AddressManager()
    # Properties
    login = models.TextField()
    domain = models.TextField()
    expiry_time = models.DateTimeField(default=datetime.now())
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_time_left(self) -> int:
        no_timezone = self.expiry_time.replace(tzinfo=None)
        seconds = (no_timezone - datetime.now()).seconds
        return seconds if seconds >= 0 else 0

    def __str__(self):
        return f'{self.login}@{self.domain}, belongs to: {self.user.uuid}'

    
class Message(models.Model):
    external_id = models.IntegerField(default=0)
    sender = models.TextField()
    subject = models.TextField()
    content = models.TextField()
    date = models.DateTimeField()
    address = models.ForeignKey(Address, on_delete=models.CASCADE) # recipient 
    
    def formatted_date(self) -> str:
        return self.date.strftime('%-d %B %Y, %H:%M')

    def __str__(self):
        return f'{self.external_id}: from: {self.sender} subject: {self.subject}'

    