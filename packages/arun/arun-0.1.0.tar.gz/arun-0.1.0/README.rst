arun
====

Make asyncio service fast with arun. See example dir with example of usage.

Run example
-----------

.. code:: bash

    python examples/example.py --manage \
      --config examples/example.conf \
      --logconfig examples/logging.conf

Get service stats
-----------------

.. code:: bash

    curl -H "content-type: application/json" -X POST \
      -d '{"jsonrpc": 2.0, "method": "stats", "params": {}, "id": 1}' \
      http://127.0.0.1:8080/manage

Run reconfigure service
-----------------------

.. code:: bash

    curl -H "content-type: application/json" -X POST \
      -d '{"jsonrpc": 2.0, "method": "reconfig", "params": {}, "id": 2}' \
      http://127.0.0.1:8080/manage

Handilng singnals
-----------------

.. code:: bash

    kill -SIGTERM $(pgrep application)

``arun`` BSD license.
