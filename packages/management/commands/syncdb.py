from typing import Dict

from django.conf import settings
from django.core.management import BaseCommand
from django.db.models import ObjectDoesNotExist

from packages.models import Package, UpstreamState, LocalState
from packages.parse_release import parse_release_file


class Command(BaseCommand):
    help = 'Synchronizes the database with the local package archive'

    def handle(self, *args, **kwargs):
        upstream_packages = parse_release_file(settings.UPSTREAM_URL)
        local_packages = Package.objects.in_bulk(field_name='name')  # type: Dict[str, Package]
        to_create = []
        for package_name in upstream_packages:
            if package_name in local_packages.keys():
                # Package in local packages -> Check for upstream version
                if upstream_packages[package_name] == local_packages[package_name].version:
                    local_packages[package_name].upstream_state = UpstreamState.UP_TO_DATE
                elif upstream_packages[package_name] <= local_packages[package_name].version:
                    print(f'Package {package_name} newer than upstream package')
                else:
                    # Update available, put into queue
                    local_packages[package_name].upstream_state = UpstreamState.UPDATE_AVAILABLE
                    local_packages[package_name].local_state = LocalState.QUEUED
            else:
                # Package not in local packages -> Add
                to_create.append(Package(name=package_name, version=upstream_packages[package_name],
                                         upstream_state=UpstreamState.ONLY_UPSTREAM))
        Package.objects.bulk_create(to_create)
        Package.objects.bulk_update(local_packages.values(), ['local_state', 'upstream_state'])
