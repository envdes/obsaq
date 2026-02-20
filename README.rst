ObsAQ: A Python package for accessing observational air quality data
--------------------------------------------------------------------
|DOI| |docs| |GitHub| |license|

.. |DOI| image:: https://zenodo.org/badge/805810422.svg
   :target: https://zenodo.org/doi/10.5281/zenodo.11391797

.. |GitHub| image:: https://img.shields.io/badge/GitHub-obsaq-brightgreen.svg
   :target: https://github.com/envdes/obsaq/ 

.. |Docs| image:: https://img.shields.io/badge/docs-obsaq-brightgreen.svg
   :target: https://envdes.github.io/obsaq/

.. |license| image:: https://img.shields.io/badge/License-MIT-blue.svg
   :target: https://github.com/envdes/obsaq/blob/main/LICENSE

Contributors: `Haofan Wang <https://github.com/Airwhf/>`_, `Zhiyi Song <https://github.com/onebravekid>`_, `Congbo Song <https://github.com/songnku>`_, `Zongbo Shi <https://www.birmingham.ac.uk/staff/profiles/gees/shi-zongbo>`_, `David Topping <https://research.manchester.ac.uk/en/persons/david.topping>`_, `Zhonghua Zheng <https://zhonghua-zheng.github.io/>`_ (zhonghua.zheng@manchester.ac.uk)

Installation
------------
Step 1: create an environment::

    $ conda create -n obsaq python=3.12

    $ conda activate obsaq

    $ conda install -c conda-forge numpy pandas pyreadr

Step 2: install using pip::

    $ pip install obsaq

(optional) install from source:: 

    $ git clone https://github.com/envdes/obsaq
    $ cd obsaq
    $ python setup.py install

How to use it?
--------------
Python

Please check the `tutorial <https://envdes.github.io/obsaq/>`_ for more information.

Recent Update
-------------
This version introduces major improvements in:

- Robust pollutant and time filtering (cross-year supported)
- Improved merging and duplicate-column handling
- Flexible configuration loading
- Cleaner, more reproducible outputs

We recommend upgrading to the latest version.

Data Validation
---------------
The downloaded datasets have been cross-checked against the official AURN website data and the original RData sources. Site counts were found to be consistent across sources.

How to ask for help
-------------------
The `GitHub issue tracker <https://github.com/envdes/obsaq/issues>`_ is the primary place for bug reports. 
