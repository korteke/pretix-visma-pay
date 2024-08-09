VismaPay
==========================

This is a plugin for [Pretix](https://github.com/pretix/pretix)

Visma Pay payment plugin.
API reference documentation [API](https://www.vismapay.com/docs/web_payments/?page=full-api-reference)

Development setup
-----------------

1. Make sure that you have a working [pretix development setup](https://docs.pretix.eu/en/latest/development/setup.html).

2. Clone this repository.

3. Activate the virtual environment you use for pretix development.

4. Execute ``python setup.py develop`` within this directory to register this application with pretix's plugin registry.

5. Execute ``make`` within this directory to compile translations.

6. Restart your local pretix server. You can now use the plugin from this repository for your events by enabling it in
   the 'plugins' tab in the settings.

This plugin has CI set up to enforce a few code style rules. To check locally, you need these packages installed::

    pip install flake8 isort black

To check your plugin for rule violations, run::

    black --check .
    isort -c .
    flake8 .

You can auto-fix some of these issues by running::

    isort .
    black .

To automatically check for these issues before you commit, you can run ``.install-hooks``.

Building for prod
-----------------

`python3 -m pip install --upgrade build`   
`python3 -m build`

Generated artifact (.whl file) will be in `dist` directory.

Installing
----------
Move .whl file to server and run.

`pip install pretix_visma_pay-X.X.X-py3-none-any.whl`

Build docker container with Visma Pay plugin
--------------------------------------------
Copy file to the `build` directory and add lines below to he Dockerfile

```
COPY pretix_visma_pay-X.X.X-py3-none-any.whl /pretix
RUN pip3 install /pretix/pretix_visma_pay-X.X.X-py3-none-any.whl
```

License
-------


Copyright 2024 Keijo Korte

Released under the terms of the Apache License 2.0
