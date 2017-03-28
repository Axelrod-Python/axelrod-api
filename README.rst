Axelrod API
===========

A `RESTful <https://en.wikipedia.org/wiki/Representational_state_transfer>`_ API for the Axelrod-Python library using `Django <https://www.djangoproject.com/>`_ and the `Django Rest Framework <http://www.django-rest-framework.org/>`_.

Getting Started
---------------

To run this project, you will need to install `Docker <https://docs.docker.com/>`_ on your machine.

Once Docker is installed and running, enter the following command from within the project folder to start the web and database servers:

.. code::

  docker-compose up

This will take several minutes the first time you run it as it needs to download and install all the necessary components into a docker container.

If successful, you should see the following messages at the end of the installation and configuration:

.. code::

  web_1  | Django version 1.10.6, using settings 'api.config.settings'
  web_1  | Starting development server at http://0.0.0.0:8000/
  web_1  | Quit the server with CONTROL-C.

and you can view the browseable API in your browser at http://localhost:8000

On OS X, you may need to use the IP address of your docker virtual machine rather then 'localhost' To find that address, use the following command:

.. code::

    docker-machine ip default

If you installed the Kitematic tool, you should also see your new containers in its list and you can start and stop them from there rather than the command line from now on.
