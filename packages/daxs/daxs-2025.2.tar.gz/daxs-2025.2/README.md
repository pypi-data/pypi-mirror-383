# Data Analysis for X-ray Spectroscopy

## Usage at the ESRF

### In scripts

If you want to use the library in scripts you execute on the ESRF computing cluster, follow the steps below.

1. Use a terminal to log in on one of the computing cluster front ends: `ssh -Y account@cluster-access`. The `account` can be your personal SMIS account or the user experiment number. Enter the associated password when prompted.
2. Ask for resources: `srun --x11 --pty bash -l`. This will give you an interactive shell. In addition, you can add `--time=hh:mm:ss` to specify the maximum time the resources will be available; by default, it will be 1 hour.
3. Load the spectroscopy environment module: `module load spectroscopy`. The command loads an environment that contains the latest stable version of `daxs`.
4. Print the version of the library to test that everything went smoothly: `python -c "import daxs; print(daxs.__version__)"`.

If all goes well with the previous command and you don't get an error, you should be able to use the library in your scripts.

### In Jupyter notebooks

You can also use the library in Jupyter notebooks.

1. Connect to <https://jupyter-slurm.esrf.fr>.
2. Select the `Spectroscopy (latest)` in the `Jupyter environment` drop-down menu.
3. Change the `Job duration` in case you need to run your notebook for a longer time, than the default 1 hour.
4. Press `Start` at the bottom of the page.

![image](https://gitlab.esrf.fr/spectroscopy/daxs/-/raw/main/doc/images/jupyter-slurm.png){width=35%}

You can find more information about Jupyter at ESRF [here](https://confluence.esrf.fr/display/DAUWK/Jupyter+@+ESRF).

While this simplifies the usage, you will not be able to add Python packages to the virtual environment. If you want to use additional packages not present in the environment, either open an issue [here](https://gitlab.esrf.fr/apptainer/spectroscopy/-/issues) or install the library in your home directory, in a virtual environment (see below).

## Local installation

The latest stable version of the library can be installed using:

`pip install daxs`

The development version can be installed using:

`pip install [--ignore-installed] pip install git+https://gitlab.esrf.fr/spectroscopy/daxs.git`

The `--ignore-installed` argument **is required** to upgrade an existing installation.

Installing the library in a virtual environment is best to avoid messing up other Python packages. See [the official documentation](https://docs.python.org/3/tutorial/venv.html) on how to create and use virtual environments.

## Documentation

The documentation can be found at <https://daxs.readthedocs.io>.
