from django.db import models
from celery import shared_task
from celery.utils.log import get_task_logger
from TempoMail import config

logger = get_task_logger(__name__)

class UserManager(models.Manager):
    @shared_task
    def terminate_user(uuid: str) -> None:
        user = User.objects.filter(uuid=uuid).first()
        if user: 
            user.delete()
            logger.log(1, f'user {user.uuid} deleted')

    def create_new(self, uuid: str):
        new_user, created = self.get_or_create(uuid=uuid)
        if not created:
            raise Exception(f'Attempted to create user that already exists ({uuid})')
        self.terminate_user.apply_async((uuid,), countdown=config.USER_LIFETIME)
        return new_user


class User(models.Model):
    objects = UserManager()
    # Properties
    uuid = models.CharField(max_length=36)

    def __str__(self):
        return f'{self.uuid}'


class AddressManager(models.Manager):
    @shared_task
    def terminate_address(login: str, domain: str) -> None:
        address = Address.objects.filter(login=login, domain=domain).first()
        if address: 
            address.delete()
            logger.log(1, f'address {address.login}@{address.domain} deleted')
    
    def create_new(self, login: str, domain: str, uuid: str):
        user = User.objects.filter(uuid=uuid).first()
        new_address, created = self.get_or_create(login=login, domain=domain, user=user)
        if not created:
            raise Exception(f'Attempted to create an address that already exists ({login}@{domain})')
        # schedule termination
        self.terminate_address.apply_async((login, domain), countdown=config.ADDRESS_LIFETIME)
        return new_address


class Address(models.Model):
    objects = AddressManager()
    # Properties
    login = models.TextField()
    domain = models.TextField()
    # TODO: dodać expiry_time = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.login}@{self.domain}, belongs to: {self.user.uuid}'

    
class Message(models.Model):
    external_id = models.IntegerField(default=0)
    sender = models.TextField()
    subject = models.TextField()
    content = models.TextField()
    date = models.DateTimeField()
    address = models.ForeignKey(Address, on_delete=models.CASCADE) # recipient 
    
    def __str__(self):
        return f'{self.external_id}: from: {self.sender} subject: {self.subject}'

    