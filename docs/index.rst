Welcome to VEKA Bot's documentation!
==================================

VEKA Bot is a modern, feature-rich Discord bot built with nextcord, featuring a modular architecture and best practices for scalability and maintainability.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   api
   contributing
   changelog

Features
--------

* Modern async/await syntax
* Modular cog-based command system
* Comprehensive error handling and logging
* Configuration management using YAML and environment variables
* Database integration ready (MongoDB & Redis)
* Clean and maintainable project structure

Quick Start
----------

1. Install the package:

   .. code-block:: bash

      pip install .

2. Set up your environment variables:

   .. code-block:: bash

      cp .env.example .env
      # Edit .env with your Discord bot token and other settings

3. Run the bot:

   .. code-block:: bash

      python main.py

For more detailed information, check out the :doc:`installation` and :doc:`usage` guides.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 