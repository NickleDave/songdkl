# songdkl

the Kullback-Leibler divergence between two distributions corresponding
to specific song data

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

associated with this paper:  
Derégnaucourt S, Gahr M (2013) 
Horizontal transmission of the father’s song in the Zebra Finch (Taeniopygia guttata). 
Biology Letters 9(4): 20130247. <https://doi.org/10.1098/rsbl.2013.0247>

## installation
`$ pip install songdkl`

## usage
To compute the songdkl between 2 birds
`$ songdkl-cli --songdkl bird1_dir bird2_dir`

To estimate number of syllables in a bird's song
`$ sondkl-cli --numsyls bird1_dir`