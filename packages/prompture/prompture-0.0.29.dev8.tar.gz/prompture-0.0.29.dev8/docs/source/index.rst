.. Prompture documentation master file, created by
   sphinx-quickstart on Mon Sep 29 17:33:04 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Prompture Documentation
=======================

Prompture is a Python library for structured LLM data extraction. It provides an API-first approach to ask LLMs to return structured JSON and run cross-model tests.

**Key Features:**

- **Multi-LLM Support**: Works with OpenAI, Anthropic, Google, Groq, and more
- **Structured Output**: Get consistent JSON responses from any LLM
- **Field Definitions**: Define your data structure with validation
- **Cross-Model Testing**: Compare results across different models
- **Driver Architecture**: Extensible design for adding new LLM providers

.. note::
   Prompture is currently in development (version 0.0.23.dev1). APIs may change between versions.

Quick Start
-----------

Install Prompture:

.. code-block:: bash

   pip install prompture

Basic usage:

.. code-block:: python

   from prompture import extract_and_jsonify
   
   # Extract structured data
   result = extract_and_jsonify(
       prompt="Extract name and age from: John is 25 years old",
       fields={
           "name": "name",
           "age": "age"
       },
       model_name="openai/gpt-4"
   )
   
   print(result)
   # Output: {"name": "John", "age": 25}

Documentation
=============

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   field_definitions_reference
   examples
   contributing

API Reference
=============

.. toctree::
   :maxdepth: 2
   :caption: API Documentation:

   api/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
