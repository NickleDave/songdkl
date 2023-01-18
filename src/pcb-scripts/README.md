This folder contains the scrips from the original PLOS Comp. Bio. paper

Mets, David G., and Michael S. Brainard.  
"An automated approach to the quantitation of vocalizations and vocal learning in the songbird."  
PLoS computational biology 14.8 (2018): e1006437.  
<https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1006437&rev=2>

As shared under "Supporting Information" here:
https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1006437#sec025  

The `conda` environment files 
were found through trial-and-error 
but seem to allow installing all the dependencies.
These are required because more recent versions of the 
dependencies may change the outputs.
In particular, the updated implementation of 
`GaussianMixtureModel` in scikit-learn.
See related discussion on this issue:
<https://github.com/NickleDave/songdkl/issues/29>

The environment creation command was:
```console
mamba create -n songdkl-pcb-new python=2.7 "mahotas<=1.4.9" matplotlib "scikit-learn<=0.18" scipy joblib -c conda-forge -c defaults
```

To recreate the environment from the environment.yml, do:
```console
conda env create -f environment.yml
```

To recreate the environment from spec-file.txt, do:
```console
conda create --name songdkl --file spec-file.txt
```

The spec-file.txt is more closely tied to the platform it was created on, in this case Linux.
