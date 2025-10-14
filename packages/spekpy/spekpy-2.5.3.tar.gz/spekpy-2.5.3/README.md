# SpekPy:

## A Python software toolkit for modelling the x-ray spectra from x-ray tubes

## Table of Contents

- [What SpekPy is](#what-spekpy-is)
- [What SpekPy is not](#what-spekpy-is-not)
- [Try before you install](#try-before-you-install)
- [How to install SpekPy](#how-to-install-spekpy)
- [How to use SpekPy](#how-to-use-spekpy)
- [The software license](#the-software-license)
- [About us](#about-us)
- [Contacts](#contacts)
- [Our book](#our-book)
- [How to reference SpekPy](#how-to-reference-spekpy)

## What SpekPy is

SpekPy is a powerful and free software toolkit for calculating and manipulating the spectra of x-ray tubes. The code is
written in the Python programming language. It can be used in a Python interpreter or from a Python script. For more
information on SpekPy, please see
[Further information](https://bitbucket.org/spekpy/spekpy_release/wiki/Further%20information).

Initially, SpekPy could only model x-ray tubes with the classic "reflection" geometry. With release v2.5.0, however, it
was extended to model transmission targets. Currently it is capable of modelling both possibilities for several target
materials. For W targets, tube potentials ranging from 10 to 500 kV can be selected. For Cr, Cu, Mo, Rh, Ag, Au targets,
the more restricted range of 10 to 50 kV is possible.

## What SpekPy is not

SpekPy is a toolkit, not a command-line program or a piece of software with a fancy Graphical User Interface (i.e. a
GUI). If you want to use it you will have to write a Python script or type commands yourself. Fortunately, SpekPy is
easy to use and both it and Python are free. An alternative, for basic calculations, is to use
[SpekPy Web](https://spekpy.smile.ki.se/), our online web application.

SpekPy also isn't a "medical device" (or "software as a medical device"). This means that it shouldn't be used in any
way that influences diagnosis, prevention, monitoring, prediction, prognosis, or treatment of human beings.

## Try before you install

### SpekPy Web

The easiest way to get started with SpekPy is via the web app. You can find the SpekPy Web app
[here](https://spekpy.smile.ki.se/).

### Binder

Alternatively,
[this link](https://mybinder.org/v2/git/https%3A%2F%2Fbitbucket.org%2Fspekpy%2Fspekpy_release%2Fsrc%2Fmaster/HEAD?filepath=SpekPy-Notebook.ipynb)
launches a Jupyter notebook running SpekPy.

Binder can be slow to load, but gives you a chance to try scripting with SpekPy before installing.

Tips:

- Click on a code-block and press **Run** to run the code snippet
- If the plot doesn't show after running the code-block, try pressing **Run** again

## How to install SpekPy

### New for 2024

SpekPy is now available in the PyPI package index. This means that it can be installed in a Python environment using
pip, without dowloading the source from this repository:

```
pip install spekpy
```

Thanks go to [Xandra Campo Blanco](https://github.com/lmri-met/uspekpy) for making this possible.

### Install from source

You can download the source from here. Click on **Source** on the menu to the left to go to the source code. Then you
can
clone the git repository (click on the **Clone** button on that page for more info). Alternatively, you can download the
software as a zip file by clicking on **Downloads**.

SpekPy is designed to be compatible with both Python2 (2.6 or higher) and Python3 (3.6 or higher). Note, however, that
Python2 is officially depreciated by the Python Software Foundation as of 1st January 2020.

We typically install and uninstall SpekPy using the standard Python _pip_ utility. You can do this by navigating to the
SpekPy directory in a command window and typing:

```
pip install .
```

The package needs the standard NumPy and SciPy libraries. If these are not installed already, the SpekPy installation
process will try to install them for you.

To be able to save spectrum states and create new filter materials, you need write permission for where you install. If
you don't have admin rights on the account you want to use for SpekPy, you can try:

```
pip install . --user
```

This should install SpekPy to you local user space. You can probably successfully install SpekPy via running the
_setup.py_ script or _easy_install_. The latter is depreciated, however, and the former is less convenient if you want
to
uninstall/reinstall.

### Advice for Anaconda Python

If you use Anaconda Python, it is good to be aware that in some cases _pip_ and _conda_ installations of packages can
cause
conflicts. We recommend creating a clean conda environment:

```
conda create -n spekpy-env python=3.7 numpy scipy matplotlib
```

before proceeding with:

```
conda activate spekpy-env
pip install .
```

Installing _NumPy_ and _SciPy_ first, using the conda installer, should ensure that you have no conflicts.

## How to use SpekPy

Here's an example of some Python code, to model a tungsten target (default) reflection-type (default) tube:

```python
#!python

import spekpy as sp

r = sp.Spek(kvp=80, th=12)  # Generate a spectrum (80 kV, 12 degree tube angle)
r.filter('Al', 4.0)  # Filter by 4 mm of Al

hvl = r.get_hvl1()  # Get the 1st half-value layer in mm Al

print(hvl)  # Print out the HVL value
```

Here's an example of how to model a transmission tube with a 10um thick copper target:

```python
import spekpy as sp

t = sp.Spek(kvp=80, trans=True, thick=10, targ='Cu')  # Target thickness entered in um
t.filter('Be', 250e-3)  # Filter thickness entered in mm i.e. 250 um of Al;

phi = t.get_flu()  # Get the total integrated fluence

print(phi)  # Print out the fluence
```

To see a complete list of SpekPy tools (methods and functions), please take a look at the
[Function glossary](https://bitbucket.org/spekpy/spekpy_release/wiki/Function%20glossary).

## The software license

The software toolkit is available under the permissive MIT License. Yes, you could put it in your software application
and make millions of dollars and not have to pay us a dime! Please do credit and reference us though.

## About us

SpekPy was developed by Gavin Poludniowski and Robert Bujila with considerable help from Artur Omar. The work was
initiated (by Gavin) at the University of Surrey in the UK and continued in Sweden, at the Karolinska University
Hospital (with Robert and Artur). Our academic associations are with Karolinska Institutet [KI] (both Gavin and Artur)
and the Royal Technical University [KTH] (Robert). Robert Bujila has now moved to GE Healthcare (Waukesha, WI, USA).

The models underlying SpekPy V2 were developed by Artur Omar, Gavin Poludniowski and Pedro Andreo.

The SpekPy Web app was developed by Robert Vorbau (Karolinska University Hospital) in collaboration with Gavin
Poludniowski.

## Contacts

Drop me an email if you have a query, suggestion or have found a bug:

Email: gpoludniowski@gmail.com

Please do let us know about any bugs. You can either email or raise an issue using the **Issues** option in the
left-hand panel.

## Our book

_Calculating X-ray Tube Spectra: Analytical and Monte Carlo Approaches_, (CaXTuS) by Gavin Poludniowski, Artur Omar,
Pedro Andreo.

Key Features of CaXTuS:

- Covers simple modelling approaches as well as full Monte Carlo simulation of x-ray tubes.
- Bremsstrahlung and characteristic contributions to the spectrum are discussed in detail.
- Learning is supported by free open-source software and an online repository of code.
- An online repository of the code that accompanies this book can be found
  [here](https://bitbucket.org/caxtus/book).

## How to reference SpekPy

### Primary references

1. G Poludniowski, A Omar, R Bujila and P Andreo, _Technical Note: SpekPy v2.0—a software toolkit for modeling x-ray
   tube spectra_. Med Phys. 2021; https://doi.org/10.1002/mp.14945

2. R Bujila, A Omar and G Poludniowski, _A validation of SpekPy: a software toolkit for modelling x-ray tube spectra_.
   Phys Med. 2020; 75:44-54.

3. Vorbau R, Poludniowski G. _Technical note: SpekPy Web-online x-ray spectrum calculations using an interface to the
   SpekPy toolkit_. J Appl Clin Med Phys. 2024;25(3):e14301.

### Secondary references

1. A Omar, P Andreo and G Poludniowski, _A model for the energy and angular distribution of x rays emitted from an x-ray
   tube. Part I. Bremsstrahlung production_. Med Phys. 2020; 47(10):4763-4774

2. A Omar, P Andreo and G Poludniowski, _A model for the energy and angular distribution of x rays emitted from an x-ray
   tube. Part II. Validation of x-ray spectra from 20 to 300 kV_. Med Phys. 2020; 47(9):4005-4019

3. A Omar, P Andreo and G Poludniowski, _A model for the emission of K and L x rays from an x-ray tube_. NIM B 2018;
   437:36-47.

4. G Poludniowski, _Calculation of x-ray spectra emerging from an x-ray tube. Part II. X-ray production and filtration
   in x-ray targets_. Med Phys. 2007; 34(6):2175-86.

5. G Poludniowski and PM Evans, _Calculation of x-ray spectra emerging from an x-ray tube. Part I. electron penetration
   characteristics in x-ray targets_. Med Phys. 2007; 34(6):2164-74.

6. G Poludniowski, et al., _SpekCalc: a program to calculate photon spectra from tungsten anode x-ray tubes_. Phys Med
   Biol. 2009; 54(19):N433-8.

7. A Omar, P Andreo and G Poludniowski, _Performance of different theories for the angular distribution of
   bremsstrahlung produced by keV electrons incident upon a target_. Radiat. Phys. and Chem. 2018; 148:73-85.
