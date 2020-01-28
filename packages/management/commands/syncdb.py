from django.conf import settings
from django.core.management import BaseCommand
from django.db.models import ObjectDoesNotExist

from packages.models import Package, UpstreamState, LocalState
from packages.parse_release import parse_release_file


class Command(BaseCommand):
    help = 'Synchronizes the database with the local package archive'

    def handle(self, *args, **kwargs):
        self._create_upstream_packages()
        self._update_local_packages()

    def _update_local_packages(self):
        packages = parse_release_file(settings.LOCAL_URL)
        for package_name in packages:
            try:
                package = Package.objects.get(name=package_name)
                upstream_version = package.version
                local_version = packages[package_name]
                if upstream_version == local_version:
                    package.upstream_state = UpstreamState.UP_TO_DATE
                    package.local_state = LocalState.UP_TO_DATE
                elif upstream_version > local_version:
                    package.upstream_state = UpstreamState.UPDATE_AVAILABLE
                    package.local_state = LocalState.QUEUED
                    package.version = packages[package_name]
                else:
                    print(f'Error: Package {package_name} newer than upstream')
                    package.upstream_state = UpstreamState.UNKNOWN
                package.save()
            except ObjectDoesNotExist:
                print(f'Error: Package {package_name} does not exist in upstream')

    def _create_upstream_packages(self):
        packages = parse_release_file(settings.UPSTREAM_URL)
        for package_name in packages:
            try:
                package = Package.objects.get(name=package_name)
                print(f'Updating package {package_name}')
                package.version = packages[package_name]
                package.upstream_state = UpstreamState.ONLY_UPSTREAM
                package.save()
            except ObjectDoesNotExist:
                print(f'Adding package {package_name} {packages[package_name]}')
                Package.objects.create(name=package_name, version=packages[package_name],
                                       upstream_state=UpstreamState.ONLY_UPSTREAM)
