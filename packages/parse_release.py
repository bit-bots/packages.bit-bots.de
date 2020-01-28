import requests


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
            # ROS upstream uses different format (e.g. 1.12.7-0bionic.20191211.002449 instead of 1.12.7-0
            version_line = line.split(':', 1)[1].strip()
            packages[current_package] = version_line.split('bionic', 1)[0]
    return {p: v for p, v in packages.items() if p.startswith('python3-') or p.startswith('ros-melodic-')}
