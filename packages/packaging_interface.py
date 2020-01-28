import os
import subprocess
from typing import List

from django.conf import settings


def get_dependencies(package: str) -> List[str]:
    cmd = [
        "podman",
        "run",
        "--rm",
        "-a",
        "stdout",
        "packages-base",
        "./resolve_dependencies",
        package,
    ]
    output = subprocess.check_output(cmd).decode().strip()
    return [dep.strip() for dep in output.split("\n") if dep.strip() != package]


def build_package(package: str) -> str:
    cmd = [
        "podman",
        "run",
        "-v",
        f"{settings.OUTPUT_DIR}:/out",
        "packages-base",
        "./build_package",
        package,
    ]
    file_name = subprocess.check_output(cmd)
    file_path = os.path.join(settings.OUTPUT_DIR, file_name)
    return file_path


def sign_package(file_path: str) -> bool:
    cmd = [
        "dpkg-sig",
        "--sign",
        "builder",
        file_path,
    ]
    exit_code = subprocess.call(cmd)
    if exit_code != 0:
        print(f'Error signing package {file_path}!')
        return False
    return True


def deploy_package(file_path: str) -> bool:
    cmd = [
        "reprepro",
        "-b",
        "/var/www/packages/",
        "includedeb",
        "bionic",
        file_path,
    ]
    exit_code = subprocess.call(cmd)
    if exit_code != 0:
        print(f'Error deploying package {file_path}')
        return False
    return True