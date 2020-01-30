import os
import subprocess
from typing import List

from django.conf import settings


def get_dependencies(package: str) -> List[str]:
    cmd = [
        "docker",
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
        "docker",
        "run",
        "--rm",
        "-v",
        f"{settings.OUTPUT_DIR}:/out",
        "packages-base",
        "./build_package",
        package,
    ]
    file_name = subprocess.check_output(cmd).decode().strip()
    file_path = os.path.join(settings.OUTPUT_DIR, file_name)
    return file_path


def sign_package(file_path: str) -> bool:
    cmd = [
        "dpkg-sig",
        "--sign",
        "builder",
        file_path,
    ]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if p.returncode != 0:
        print(f'Error signing package {file_path}!')
        print(p.stdout)
        return False
    return True


def deploy_package(file_path: str) -> bool:
    cmd = [
        "reprepro",
        "-b",
        settings.DEPLOY_DIR,
        "includedeb",
        "bionic",
        file_path,
    ]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if p.returncode != 0:
        print(f'Error deploying package {file_path}')
        print(p.stdout)
        return False
    return True
