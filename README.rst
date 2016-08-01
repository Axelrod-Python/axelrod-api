Axelrod API
===========

A RESTful API for the Axelrod-Python library using Django and the Django Rest Framework.

Getting Started
---------------

To run this project, you will need to install `Docker <https://docs.docker.com/>`_ on your machine.

Once Docker is installed and running, enter the following command from within the project folder to start the web and database servers:

.. code::

  docker-compose up

To view the browseable API, on Linux and Windows, visit http://0.0.0.0:8000
On Mac, you will first need to find the ip address of your Docker virtual machine using:

.. code::

    docker-machine ip default

and then use that address in place of 0.0.0.0
