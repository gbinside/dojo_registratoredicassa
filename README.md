dojo_registratoredicassa
========================

A Tkinter python application with http json interface

The program will listen on port 5000

You can GET or POST to /

* GET will give you the scanner barcode; if more than one barcode is scanned, they will be put in queue; the standard respose is like

    {"status": "OK", "barcode": "1231212"}

    OR

    {"status": "Empty"}

* POST: posting a json like the following you will print that in the top element of the GUI

    {"display": "0,00"}

    OR

    {"display": "TOTAL 0,00"}

