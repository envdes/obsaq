About
=====

This notebook demonstrates how to use the `ObsAQ <https://github.com/envdes/obsaq>`__ package in a Jupyter notebook.

Contributors: `Haofan Wang  <https://github.com/Airwhf/>`_, `Zhiyi Song <https://github.com/onebravekid>`_, `David Topping <https://research.manchester.ac.uk/en/persons/david.topping>`_, `Zhonghua Zheng <https://zhonghua-zheng.github.io/>`_ (Email: zhonghua.zheng@manchester.ac.uk)

Installation
============

Step 1: create an environment via conda

        .. code-block:: shell

                conda create -n obsaq python=3.8
                conda activate obsaq
                conda install numpy pandas pyreadr

Step 2: install using pip:

        .. code-block:: shell

                pip install obsaq

(Optional) Step 3: install offline:

        .. code-block:: shell

                git clone https://github.com/envdes/obsaq
                cd obsaq
                python setup.py install
