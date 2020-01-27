from django.conf import settings
from django.core.management import BaseCommand
from django.db.models import ObjectDoesNotExist

from packages.models import Package
from packages.parse_release import parse_release_file


class Command(BaseCommand):
    help = 'Synchronizes the database with the local package archive'

    def handle(self, *args, **kwargs):
        packages = parse_release_file(settings.OWN_URL)
        for package_name in packages:
            try:
                package = Package.objects.get(name=package_name)
                print(f'Updating package {package_name}')
                package.version = packages[package_name]
                package.save()
            except ObjectDoesNotExist:
                print(f'Adding package {package_name}')
                package = Package.objects.create(name=package_name, version=packages[package_name])

