packages.bit-bots.de
====================

This repository contains the source code for packages.bit-bots.de, our ROS package mirror. All
packages are built with Python 3 instead of Python 2 as in the official releases.

Preparation
-----------

The python dependencies are managed using pipenv. To install pipenv, use the package manager of
your distribution or `pip3 install --user pipenv`.

The dependencies can be installed using `pipenv sync`. No further dependencies are needed to run
the server. To also build the ROS packages, the following additional packages have to be installed:

* `reprepro` to manage the release repository
* `dpkg-sig` to sign packages
* `docker` to run the build container
* `python3-uwsgi` and `uwsgi-plugin-python3` to deploy the production server with uwsgi

To be able to build packages, the base image has to be built. Navigate into the `docker` directory
and execute `docker built -t packages-base .`.

Configuration
-------------

Before you start the application, adjust the Django settings, especially

* the secret key
* the debug setting
* the allowed hosts
* the database settings
* the local and upstream url
* the output and deploy directory

Then, to set up the database, type `pipenv run ./manage.py migrate`.

Launch
------

The application can be launched with `pipenv run ./manage.py runserver` for development or with
uwsgi (`uwsgi --ini uwsgi.ini`).

Additionally, there are two commands that should be run (they are already included in the
`uwsgi.ini` file). `pipenv run ./manage.py syncdb` synchronizes the database with the upstream
package repository (`UPSTREAM_URL` in settings). This command should be run regularly to react to
upstream updates. `pipenv run ./manage.py queueworker` is the process that builds the packages. It
should always run in the background.

How it works
------------

When packages are requested, the build is scheduled by putting the package in a queue. Then, a
container is run where the build and run dependencies of the first package in the queue are
resolved. These packages are filtered for ROS packages that are not already built and inserted at
the front of the queue.

When no dependencies are missing, the package can be built. This step is executed in a container,
where the original ROS package is downloaded using `apt-get source`. Then, some replacements are
executed to replace Python 2 with Python 3. All build dependencies are installed via
`mk-build-deps` and the package is built using `debuild`. The resulting packages is put into the
`OUTPUT_DIR`. It is then signed outside of the container with `dpkg-sig` using the default private
key of the user running the queue worker. Please do not set a passphrase for the GPG key that
should be used for signing. After the package is signed, it is deployed to `DEPLOY_DIR` using
`reprepro`.
