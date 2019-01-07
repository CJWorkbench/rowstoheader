rowstoheader
------------

Workbench module that moves selected rows to the header

Developing
----------

First, get up and running:

1. ``pip3 install pipenv``
2. ``pipenv sync`` # to download dependencies
3. ``pipenv run ./setup.py test`` # to test

To add a feature on the Python side:

1. Write a test in ``test_rowstoheader.py``
2. Run ``pipenv run ./setup.py test`` to prove it breaks
3. Edit ``rowstoheader.py`` to make the test pass
4. Run ``pipenv run ./setup.py test`` to prove it works
5. Commit and submit a pull request

To develop continuously on Workbench:

1. Check out the columnchart repository in a sibling directory to your checked-out Workbench code.
2. Start Workbench with ``bin/dev start``
3. In a separate tab in the Workbench directory, run ``pipenv run ./manage.py develop-module rowstoheader``
4. Edit this code; the module will be reloaded in Workbench immediately. In the Workbench website, modify parameters to execute the reloaded code.
