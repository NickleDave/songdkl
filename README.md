# songdkl

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
The package is developed with `poetry`.
To set up a development environment, do the following in the terminal:  
* install `poetry` following their instructions: <https://python-poetry.org/docs/#installation>
* clone this repository: `git clone https://github.com/NickleDave/songdkl.git` 
* navigate into the directory that corresponds to this repository, and use `poetry` to set up  
    ```console
    $ cd songdkl
    $ poetry install
    ```

## usage
To compute the songdkl between 2 birds
`$ songdkl-cli --songdkl bird1_dir bird2_dir`

To estimate number of syllables in a bird's song
`$ sondkl-cli --numsyls bird1_dir`