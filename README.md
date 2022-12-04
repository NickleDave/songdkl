# songdkl
[![Continuous Integration Status](https://github.com/NickleDave/songdkl/actions/workflows/ci.yml/badge.svg)](https://github.com/NickleDave/songdkl/actions/workflows/ci.yml/badge.svg)
## About
automated quantitation of vocal learning in the songbird

As described in:  
Mets, David G., and Michael S. Brainard.  
"An automated approach to the quantitation of vocalizations and vocal learning in the songbird."  
PLoS computational biology 14.8 (2018): e1006437.  
<https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1006437&rev=2>

Data for demo and testing is from the following Dryad data package:  
Mets, David G.; Brainard, Michael S. (2019), 
Data from: An automated approach to the quantitation of vocalizations and vocal learning in the songbird., 
Dryad, Dataset, <https://doi.org/10.5061/dryad.8tn4660>  
Dataset can be downloaded here:  
<https://datadryad.org/stash/dataset/doi:10.5061/dryad.8tn4660>

## Installation
### as a user
`$ pip install songdkl`  
We recommend installing into a virtual environment, 
in order to capture the compute environment for computational projects.
For more information and good practices, please see:  
<https://the-turing-way.netlify.app/reproducible-research/renv.html>

### as a developer
This project uses the library [nox](https://nox.thea.codes/en/stable/) 
as a [task runner](https://scikit-hep.org/developer/tasks), 
to automate tasks like setting up a development environment.
Each task is represented as what nox calls a "session", 
and you can run a session by invoking nox 
at the command-line with the name of the session.

So, to set up a virtual environment for development 
with `songdkl` installed in "editable" mode, 
run the "dev" session.

We suggest using [pipx](https://github.com/pypa/pipx) 
to install nox in an isolated environment, 
so that nox can be accessed system-wide without affecting 
anything else on your machine.

1. Install [`pipx`](), e.g. with [brew](https://github.com/pypa/pipx#on-macos)
   (and [brew works on Linux too](https://docs.brew.sh/Homebrew-on-Linux))
2. Install nox with pipx: `pipx install nox`
3. Use nox to run the `dev` session: `nox -s dev`
4. Activate the virtual environment: `. ./.venv/bin/activate` (and/or tell your IDE to use it)

## Usage
`songdkl` provides a command-line interface (cli) 
that allows the user to run the program from the terminal.

The cli makes two commands available:
* `calculate`, to compute the songdkl between two directories of songs, e.g., from 2 birds  
  `$ songdkl calculate bird1_dir bird2_dir`

* `numsyls`, to estimate the number of syllables in a bird's song  
  `$ songdkl numsyls bird1_dir`

For details on usage, please run `songdkl --help`.

## Citation
If you use this software, please cite the DOI:  
[![DOI](https://zenodo.org/badge/157573537.svg)](https://zenodo.org/badge/latestdoi/157573537)

Please also cite the original paper:
Mets, David G., and Michael S. Brainard.  
"An automated approach to the quantitation of vocalizations and vocal learning in the songbird."  
PLoS computational biology 14.8 (2018): e1006437.  
<https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1006437&rev=2>
```
@article{mets2018automated,
  title={An automated approach to the quantitation of vocalizations and vocal learning in the songbird},
  author={Mets, David G and Brainard, Michael S},
  journal={PLoS computational biology},
  volume={14},
  number={8},
  pages={e1006437},
  year={2018},
  publisher={Public Library of Science San Francisco, CA USA}
}
```
If you use the accompanying Dryad dataset, please cite that as well:  
Mets, David G.; Brainard, Michael S. (2019), 
Data from: An automated approach to the quantitation of vocalizations and vocal learning in the songbird., 
Dryad, Dataset, <https://doi.org/10.5061/dryad.8tn4660>  
