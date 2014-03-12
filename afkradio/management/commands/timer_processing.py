from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
	help = 'Processes the items in Timer.models to do various actions'

	def handle(self, *args, **options):
		print 'test'	
