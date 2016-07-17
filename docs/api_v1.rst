ML-Agent API Documentation
==========================

ML-Agent is a RESTful service that has 3 endpoints:

* Model IDs: list model ids for all models currently loaded
* Models: handles all CRUD (create, replace, update, and delete) operations for managing models
* Predict: handles queries to get predictions from specific loaded models

The v1 API endpoints are reached at:

* Model IDs: http://<url>:<port>/v1/models
* Models: http://<url>:<port>/v1/models/<model_id>
* Predict: http://<url>:<port>/v1/predict/<model_id>

where url and port is the url and port where ml-agent is running, and model_id is the unique ml-agent id for the model


More details on the APIs can be found in the code documentation here: :doc:`ml-agent.predict.resources.v1`

Each endpoint supports different HTTP request types. The supported request types and the corresponding endpoint actions
are shown below.  Only the HTTP requests types shown for each endpoint are valid.

+-----------+--------------+--------------------------+
| Endpoint  | HTTP Request | Action                   |
+===========+==============+==========================+
| Model IDs | GET          | List Model IDs           |
+-----------+--------------+--------------------------+
| Models    | GET          | List Model Details       |
|           +--------------+--------------------------+
|           | POST         | Create a New Model       |
|           +--------------+--------------------------+
|           | PUT          | Create or Update a Model |
|           +--------------+--------------------------+
|           | PATCH        | Update a Model           |
|           +--------------+--------------------------+
|           | DELETE       | Delete a Model           |
+-----------+--------------+--------------------------+
| Predict   | POST         | Get Prediction           |
+-----------+--------------+--------------------------+


The endpoints can be accessed via any mechanism that supports sending data through an HTTP request
(e.g. CURL, HttpURLConnection, etc.), but for clarity examples are provided below using python.


Common Python Setup
-------------------
The following examples will be using python with the requests and json packages. The following block shows setup that is
common to all interactions.  This assumes ML-Agent is running locally on port 8080, change the url to match your needs.

.. code-block:: python

    import requests
    import json

    url = 'http://localhost:8080/v1'
    headers = {'Content-Type': 'application/json'}

Model IDs Endpoint
------------------
The Model ID endpoint provides a json list of model ids for models loaded in ML-Agent.  Model IDs are unique strings that differentiate
models.  They are set at time of model creation and cannot be changed.

Example:

.. code-block:: python

    requests.get(url='{}/models'.format(url), headers=headers).content
    # '{"model_ids": ["1"]}'

Models Endpoint
---------------
The Models endpoint provides all management activities for loading, updating, and removing models from ML-Agent.
There are a set of fields (some optional) that are used to define a model which are shown below:

* model_id (str): unique string of id for model
* model_type (str): type of model must be valid member of ModelType enum
* local_path (optional, str): local path of model file - this is only used internally
* remote_path (str): remote location of model file to load 'protocol:///path/model.ext', protocol options are
  ['http', 'scp', 'hdfs', 'local']
* example (str): example feature vector to use for verifying model instantiation, using an empty string disables validation of the model on load
* output (float): output prediction expected from model when using the example
* timestamp (optional, int): epoch timestamp provided with model, defaults to current timestamp
* extras (optional, str): additional arguments to use when instantiating the model
* info (optional, str): additional information on the model
* status (optional, str): status of model must be valid member of ModelStatus enum, default 'paused'

Examples:

.. code-block:: python

    # setup required model information
    data = {'model_type': 'vw',
            'remote_path': 'local:///tmp/vw.model',
            'example': '',
            'output': 0,
            'status': 'active'}

    # create new model
    requests.post(url='{}/models/1'.format(url), data=json.dumps(data), headers=headers).content
    # '{"info": "", "status": "active", "model_id": "1", "timestamp": 1439477515,
    #   "remote_path": "local:///tmp/vw.model", "local_path": "/tmp/test_ml-agent_models/1/vw.model",
    #   "model_type": "vw", "output": 0.0, "example": "", "extras": ""}'

    # update model (all required fields must be included)
    data['info'] = 'updated with put'
    requests.put(url='{}/models/1'.format(url), data=json.dumps(data), headers=headers).content
    # '{"info": "updated with put", "status": "active", "model_id": "1", "timestamp": 1439478116,
    #   "remote_path": "local:///tmp/vw.model", "local_path": "/tmp/test_ml-agent_models/1/vw.model",
    #   "model_type": "vw", "output": 0.0, "example": "", "extras": ""}'

    # update with patch (only fields to be updated are included)
    patch = {'info': 'updated with patch'}
    requests.patch(url='{}/models/1'.format(url), data=json.dumps(patch), headers=headers).content
    # '{"info": "updated with patch", "status": "active", "model_id": "1", "timestamp": 1439478116,
    #   "remote_path": "local:///tmp/vw.model", "local_path": "/tmp/test_ml-agent_models/1/vw.model",
    #   "model_type": "vw", "output": 0.0, "example": "", "extras": ""}'

    # delete model
    requests.delete(url='{}/models/1'.format(url), headers=headers)
    # <Response [204]>


Predict Endpoint
----------------
The Predict endpoint provides predictions for a given model

Examples:

.. code-block:: python

    # examples for prediction
    example = {'example': '| genders__male'}
    batch = {'example': ['| genders__male', '| genders__female']}

    # predict single example
    requests.post(url='{}/predict/1'.format(url), data=json.dumps(example), headers=headers).content
    # '{"prediction": -0.13531726598739624}'

    # predict multiple examples (response is a list matching the order of the example list given)
    requests.post(url='{}/predict/1'.format(url), data=json.dumps(batch), headers=headers).content
    # '{"prediction": [-0.13531726598739624, -0.17753702402114868]}'
