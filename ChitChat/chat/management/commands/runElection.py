from django.core.management.base import BaseCommand
from chat.election import elect_leader
from pymongo import MongoClient

class Command(BaseCommand):
    help = 'Run leader election'
    
    def handle(self, *args, **options):
        elect_leader()
 
        