ML-Agent Installation
=====================

ML-Agent depends on Python 2.7 and has libraries built for CentOS and Mac OSX systems.
Instructions for installation on both Mac and CentOS are provided below.

Mac OSX
-------
Create a new virtual environment (here we're assuming you put all your virtual environments under ~/.virtualenvs,
and that your current working directory is the ml-agent folder):

.. code-block:: bash

    # if you don't already have the repo
    git clone https://github.com/gramhagen/ml-agent
    cd ml-agent

    # create new virtual environment
    virtualenv ~/.virtualenvs/ml-agent
    source ~/.virtualenvs/ml-agent/bin/activate

    # install path and requirements
    echo `pwd` > ~/.virtualenvs/ml-agent/lib/python-2.7/site-packages/ml-agent.pth
    cd deploy
    pip install -r requirements.txt

    # install vowpal wabbit library and binding
    tar xzf vowpal_wabbit_7.10.tgz
    cp vowpal_wabbit_7.10/OSX/10.10.4/pylibvw.so ~/.virtualenvs/ml-agent/lib/python-2.7/site-packages/
    cp -r vowpal_wabbit_7.10/vowpal_wabbit ~/.virtualenvs/ml-agent/lib/python-2.7/site-packages/
    rm -rf vowpal_wabbit_7.10

    # restart virtualenv and run test suite
    deactivate
    source ~/.virtualenvs/ml-agent/bin/activate
    ./check.sh
