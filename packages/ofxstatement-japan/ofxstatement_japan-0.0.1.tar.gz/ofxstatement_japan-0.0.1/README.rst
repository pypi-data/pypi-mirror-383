~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
OFXStatement plugin for Japan banks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This project provides plugins for Japanese banks for `ofxstatement`_.

`ofxstatement`_ is a tool to convert proprietary bank statement to OFX format,
suitable for importing to GnuCash. Plugin for ofxstatement parses a
particular proprietary bank statement format and produces common data
structure, that is then formatted into an OFX file.

.. _ofxstatement: https://github.com/kedder/ofxstatement

Supported Banks
===============

Prestia (SMBC Trust Bank)
--------------------------

This plugin supports CSV exports from Prestia (SMBC Trust Bank) online banking.

Installation
============

You can install the plugin from source::

  $ git clone https://github.com/elrandar/ofxstatement-japan.git
  $ cd ofxstatement-japan
  $ pip install -e .

Usage
=====

List available plugins::

  $ ofxstatement list-plugins
  The following plugins are available:

    prestia          Prestia (SMBC Trust Bank) Japan CSV statement plugin

Convert Prestia CSV to OFX::

  $ ofxstatement convert -t prestia statement.csv statement.ofx

The plugin will automatically detect and use CP932 (Shift-JIS) encoding, which
is the default encoding used by Japanese banks.

Configuration
=============

If you need to customize the encoding, create a configuration file at
``~/.config/ofxstatement/config.ini``::

  [prestia]
  encoding = utf-8

CSV Format
==========

The Prestia plugin expects CSV files with the following format:

* Column 1: Date (YYYY/MM/DD)
* Column 2: Description (Japanese and English)
* Column 3: Amount (e.g., "-1,590 JPY" or "+500,000 JPY")
* Column 4: Account number

Development
===========

To set up a development environment::

  $ git clone https://github.com/elrandar/ofxstatement-japan.git
  $ cd ofxstatement-japan
  $ python3 -m venv .venv
  $ source .venv/bin/activate  # On Windows: .venv\Scripts\activate
  $ pip install -e .

Run tests::

  $ pip install pytest
  $ pytest tests/
