ObsAQ: A Python package for obtaining observational air quality data
--------------------------------------------------------------------
|docs| |GitHub| |license|

.. |GitHub| image:: https://img.shields.io/badge/GitHub-ObsAQ-brightgreen.svg
   :target: https://github.com/envdes/obsaq/ 

.. |Docs| image:: https://img.shields.io/badge/docs-ObsAQ-brightgreen.svg
   :target: https://junjieyu-uom.github.io/obsaq/

.. |license| image:: https://img.shields.io/badge/License-MIT-blue.svg
   :target: https://github.com/envdes/obsaq/blob/main/LICENSE

Contributors: `Haofan Wang  <https://github.com/Airwhf/>`_, `Zhiyi Song <https://github.com/onebravekid>`_, `David Topping <https://research.manchester.ac.uk/en/persons/david.topping>`_, `Zhonghua Zheng <https://zhonghua-zheng.github.io/>`_ (zhonghua.zheng@manchester.ac.uk)

Installation
------------
Step 1: create an environment::

    $ conda create -n obsaq python=3.11

    $ conda activate obsaq

    $ conda install -c conda-forge numpy pandas pyreadr

Step 2: install using pip::

    $ pip install obsaq

(optional) install from source:: 

    $ git clone https://github.com/envdes/obsaq
    $ cd obsaq
    $ python setup.py obsaq

How to use it?
--------------
Python

1. Users can read the `download_aurn.ipynb<docs/notebook/download_aurn.ipynb>`_ to learn how to download observations from AURN, and read the `download_rdata.ipynb<docs/notebook/download_rdata.ipynb>`_ to learn how to download observations from Rdata.

2. Users can read the `read_aurn.ipynb<docs/notebook/read_aurn.ipynb>`_ to learn how to read observations from AURN directly, and read the `read_rdata.ipynb<docs/notebook/read_rdata.ipynb>`_ to learn how to read observations from Rdata directly.

How to ask for help
-------------------
The `GitHub issue tracker <https://github.com/envdes/obsaq/issues>`_ is the primary place for bug reports. 
