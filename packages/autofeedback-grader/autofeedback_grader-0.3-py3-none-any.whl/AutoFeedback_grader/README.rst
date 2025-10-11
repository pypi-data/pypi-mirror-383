===========================
Grading student submissions
===========================

To install the grading package

.. code-block:: bash

    > pip install AutoFeedback_grader


API information
---------------

To interact directly with Canvas, you need to store your API key. The easiest way to do this is to run the ``canvas_selector`` utility.

.. code-block:: bash

    > python -m canvas_selector.canvas_selector

which will prompt you for the API information. The API_URL for qub is ``https://canvas.qub.ac.uk``. The ``API_KEY`` entry is your user-generated API access token from Canvas. To generate a token, navigate to canvas, click on your "Account" in the left hand menubar, scroll to "Approved integrations", and click on "New access token". Put in the requested details, and then copy the generated token.

You can also manually enter the information into ``~/.canvasapirc``:

.. code-block:: bash

    [DEFAULT]
    API_URL = https://canvas.qub.ac.uk
    API_KEY = 112480jfiodsajio32289hfiksdafhjkfhsdajk

To use this configuration with Docker (below), you will need to copy this file to the same directory as the DockerFile: ``<path to exercises repo directory>/.canvasapirc``.

Running with docker
-------------------

In order to safely download and run student-written code, we recommend that you use a virtual machine (docker image) to ensure no nefarious code is executed with access to your local data.

Installing docker (macOS)
~~~~~~~~~~~~~~~~~~~~~~~~~

Docker can be installed via macports:

.. code-block:: bash

    > sudo port install docker docker-credential-helper-osxkeychain colima

or homebrew

.. code-block:: bash

    > brew install colima docker docker-credential-helper

**You may already have, or be tempted to install, the Docker Desktop app. While it is "free to download" is it not at all clear that use within QUB is permitted without a license. QUB does not have such a license.**

Once installed, you start the docker daemon with

.. code-block:: bash

    > colima start
    INFO[0002] starting colima
    INFO[0002] runtime: docker
    INFO[0004] starting ...                   context=vm
    INFO[0016] provisioning ...               context=docker
    INFO[0017] starting ...                   context=docker
    INFO[0017] done

Building the docker image
~~~~~~~~~~~~~~~~~~~~~~~~~

The docker image is built with

.. code-block:: bash

    > docker build --tag 'gradepython' .

This only needs to be done once.

Running the docker image
~~~~~~~~~~~~~~~~~~~~~~~~

To run the docker image (which you will do everytime you want to mark student submissions)

.. code-block:: bash

    > docker run -it gradepython 

This will bring up a list of all your available Canvas courses. You can limit the choice to a given semester by using the term id:

.. code-block:: bash

    > docker run -it gradepython -s 2241_SPR

Navigate to the correct course with the up/down arrow keys, and press Enter to select. This in turn will bring up a list of all available assignments on the module (NB not just the programming assignments). You can select as many assignments as you wish to grade- use the up/down arrow keys, and then the right arrow or space bar to select. When you have selected all the assignments, press Enter.

If you know the course ID you can avoid this selection process and execute ``grade_ipynbs.py`` with the command line options:

.. code-block:: bash

    > docker run -it gradepython -c <course ID>

The script downloads those submissions which are currently unmarked, or which have received a grade of 0, marks them, and updates the grade on canvas. It will also give a summary of the number of those assignments marked which scored zero. This can be useful to show up errors in the marking- if everyone got zero, there may be a problem with the way the AutoFeedback tests are set up.
