ML-Agent Execution
===================

ML-Agent can run under different configurations:

- Staging
    - uses staging database: optimization-stg/ml-agent
    - logging level is DEBUG and logs are written to /var/log/research/ml-agent.log
    - models files are copied locally to /tmp/ml-agent_models
- Production
    - uses production database: optimization03/ml-agent
    - logging level is ERROR and logs are written to /var/log/research/ml-agent.log
    - models files are copied locally to /tmp/ml-agent_models
- Test
    - uses local sqllite database
    - logging level is DEBUG and logs are streamed to stdout
    - models files are copied locally to /tmp/test_ml-agent_models

see configurations module for more details: :ref:`configurations_ref`

ML-Agent is started by executing run_ml-agent.py and providing 2 optional parameters:

- env: this is the configuration environment to use: [test|stage|prod], default is test
- port: this is the port for ml-agent to listen for requests, default is 8080

Example:

.. code-block:: bash

    /usr/local/model_training/virtualenv/ml-agent/bin/python run_ml-agent.py --env=stage --port=8256
