labmanager
=========

A small CLI tool to list and run Python lab programs stored in `programs/`.

Usage examples:

Run with module mode:

python -m labcli list
python -m labcli run hello

Package layout:

labcli/
  __init__.py
  __main__.py
  cli.py
programs/
  hello.py
  math_demo.py
