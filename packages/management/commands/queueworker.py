import os
from time import sleep

import fasteners
from django.conf import settings
from django.core.management import BaseCommand, CommandError

from packages import packaging_interface
from packages.models import Package, LocalState, UpstreamState
from packages.parse_release import parse_release_file


class Command(BaseCommand):
    help = 'Run the queue worker building new packages'

    def handle(self, *args, **options):
        lock = fasteners.InterProcessLock(os.path.join(settings.OUTPUT_DIR, 'worker.lock'))
        gotten = lock.acquire(blocking=False)
        if Package.objects.filter(local_state=LocalState.IN_PROGRESS):
            print('There are still packages in progress. This should never happen.')
            return
        if gotten:
            queue = []
            while True:
                if not queue:
                    queue = list(Package.objects.filter(local_state=LocalState.QUEUED).values_list('id', flat=True))
                if not queue:
                    # Still no queue? Sleep.
                    sleep(30)
                    continue
                # Get first in queue
                package = Package.objects.get(id=queue[0])
                # Get dependencies
                dependencies = packaging_interface.get_dependencies(package.name)
                this_package_can_be_built = True
                for dependency in dependencies:
                    dep_package = Package.objects.get(name=dependency)
                    # Check if package is already built
                    if dep_package.upstream_state != UpstreamState.UP_TO_DATE:
                        # Remove from list and insert in front
                        dep_package.local_state = LocalState.QUEUED
                        dep_package.save()
                        if dep_package.id in queue:
                            queue.remove(dep_package.id)
                        queue.insert(0, dep_package.id)
                        this_package_can_be_built = False
                if this_package_can_be_built:
                    # No dependencies, we can build
                    package.local_state = LocalState.IN_PROGRESS
                    package.save()
                    package_path = packaging_interface.build_package(package.name)
                    if not os.path.exists(package_path):
                        print(f'Error building {package.name}')
                        break
                    # Sign package
                    success = packaging_interface.sign_package(package_path)
                    if not success:
                        print(f'Error signing {package.name}')
                        package.local_state = LocalState.QUEUED
                        package.save()
                        break
                    # Deploy package
                    success = packaging_interface.deploy_package(package_path)
                    if not success:
                        print(f'Error deploying {package.name}')
                        package.local_state = LocalState.QUEUED
                        package.save()
                        break
                    # Deploy was successful, reset package state and update version
                    package.local_state = LocalState.UP_TO_DATE
                    package.upstream_state = UpstreamState.UP_TO_DATE
                    package.version = parse_release_file(settings.LOCAL_URL)[package.name]
                    package.save()
                    queue.remove(package.id)
        else:
            raise CommandError(
                'The lockfile is present. There seems to be another instance of the queue worker running.\n'
                'Please stop it before starting a new one.\n'
                f'If this problem persists, delete {lock.path.decode()}.\n')
