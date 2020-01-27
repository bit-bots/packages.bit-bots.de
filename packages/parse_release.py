import requests
from django.conf import settings

from packages.models import UpstreamState


def get_release_file(base_url: str) -> str:
    r = requests.get(base_url + 'dists/bionic/main/binary-amd64/Packages')
    return r.text


def parse_release_file(base_url: str) -> dict:
    file_contents = get_release_file(base_url)
    packages = dict()
    current_package = ''
    for line in file_contents.split('\n'):
        if line.startswith('Package'):
            current_package = line.split(':', 1)[1].strip()
        elif line.startswith('Version'):
            packages[current_package] = line.split(':', 1)[1].strip()
    return packages


def compare_release_files(upstream_packages: dict, own_packages: dict) -> dict:
    results = dict()
    for package in upstream_packages:
        # Skip python2 packages in upstream
        if not package.startswith('python3-') and not package.startswith('ros-melodic-'):
            continue

        upstream_version = upstream_packages[package]
        if package in own_packages.keys():
            own_version = own_packages[package]
            # ROS upstream uses different format (e.g. 1.12.7-0bionic.20191211.002449 instead of 1.12.7-0bionic
            if upstream_version.startswith(own_version):
                results[package] = UpstreamState.UP_TO_DATE
            else:
                results[package] = UpstreamState.UPDATE_AVAILABLE
        else:
            results[package] = UpstreamState.ONLY_UPSTREAM
    return results


def compare_releases() -> dict:
    upstream_packages = parse_release_file(settings.UPSTREAM_URL)
    own_packages = parse_release_file(settings.OWN_URL)
    return compare_release_files(upstream_packages, own_packages)
