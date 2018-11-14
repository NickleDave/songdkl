import sys as sys
import os as os

import scipy as sc
from pylab import specgram, psd
import numpy as np

from sklearn import mixture

from songdkl.utils import audio

"""A script to calculate the song divergence between two birds. It is aplied as follows:
python Song_D_KL_calc.py folder_with_songs_from_bird_1 folder_with_songs_from_bird_2 number_of_syllable_calsses_bird_1 number_of_syllable_classes_bird_2
e.g.  python bird_data/y25/ bird_data/y34br6/ 9 10
It expects the songs to be in mono wave format and have a .wav suffix.
The output is a tab delimited string formatted as follows:
foldername_bird1 foldername_bird2 n_syl_classes_bd1 n_syl_classes_bd2 n_basis_set SD_bd1_ref_bd2_song SD_bd2_ref_bd1_comp n_syls_bd1 n_syls_bd2
e.g. y25 y32br6 9 10 50 0.039854682578 0.0340690226514 3000 3000

IMPORTANT! In our paper we always use the number of syllables in the tutor song for both syllable # values.  
This is meant to be conservative, basically give the bird learning the benefit of the doubt that it actually coppied all
of the syllables in the tutor song.  Emperically, changing these numbers doesn't have much impact on the divergence
calculations (see the paper)

IMPORTANT! Throughout the paper we calculated PSDs for the raw wave forms of syllables.  This is the default setting for this script. If your song is contaminated with low frequency noise this noise may be incorporated into the model for song potentially causing over estimates of song D_KL if there is low frequency noise in the tutor song but not the tutee song.  This could occur if the birds were recorded under different conditions or in different sound recording boxes.  If you uncomment line 99 below, the script will calculate the song D_KL using filtered syllable data. We only advise this if you have low frequency noise that is differential between the tutor and tutee song and you don't want that noise incorporated into the song D_KL calculations."""

def calculate_songdkl(path1,path2):
    fils1=[x for x in os.listdir(path1) if x[-4:]== '.wav']
    fils2=[x for x in os.listdir(path2) if x[-4:]== '.wav']
    
    fils1=fils1[:120]
    fils2=fils2[:120]
    
    filename1=path1.split('/')[-2]
    filename2=path2.split('/')[-2]
    
    datano=10000 #variable to constrain the amount of data used
    
    k=int(sys.argv[3]) #number of syllable classes in song 1
    k2=int(sys.argv[4]) #number of syllable classes in song 2
    
    #get syllables from all of the songs in folder 1
    syls1=[]
    objss1=[]
    for file in fils1:
        song=impwav(path1+file)
        if len(song[0])<1: break
        syls,objs,frq=(getsyls(song))
        objss1.append(objs)
        syls1.append([frq]+syls)
    
    
     
    #get syllables from all of the songs in folder 2
    syls2=[]
    objss2=[]
    for file in fils2:
        song=impwav(path2+file)
        if len(song[0])<1: break
        syls,objs,frq=(getsyls(song))
        objss2.append(objs)
        syls2.append([frq]+syls)
    
    
    #convert syllables into PSDs
    segedpsds1=[]
    for x in syls1[:datano]:
        fs=x[0]
        nfft=int(round(2**14/32000.0*fs))
        segstart=int(round(600/(fs/float(nfft))))
        segend=int(round(16000/(fs/float(nfft))))
        psds=[psd(norm(y),NFFT=nfft,Fs=fs) for y in x[1:]]
        spsds=[norm(n[0][segstart:segend]) for n in psds]
        for n in spsds: segedpsds1.append(n)
        if len(segedpsds1)>datano: break
    
    #convert syllables to PSDs
    segedpsds2=[]
    for x in syls2[:datano]:
        fs=x[0]
        nfft=int(round(2**14/32000.0*fs))
        segstart=int(round(600/(fs/float(nfft))))
        segend=int(round(16000/(fs/float(nfft))))
        psds=[psd(norm(y),NFFT=nfft,Fs=fs) for y in x[1:]]
        spsds=[norm(n[0][segstart:segend]) for n in psds]
        for n in spsds: segedpsds2.append(n)
        if len(segedpsds2)>datano: break
    
    #establish basis set:
    basis_set=segedpsds1[:50] #select the first 50 syllables of the reference song as the basis set
    #basis_set=[segedpsds1[rnd.randint(0,len(segedpsds1))] for x in range(50)] #select a random set of 50 syllablse as the basis set
    
    
    lone=len(segedpsds1)
    ltwo=len(segedpsds2)
    lone_half=int(lone/2)
    ltwo_half=int(ltwo/2)
    
    #calculate distance matrices:
    d1=sc.spatial.distance.cdist(segedpsds1[:lone_half],basis_set,'sqeuclidean')
    
    d1_2=sc.spatial.distance.cdist(segedpsds1[lone_half:lone],basis_set,'sqeuclidean')
    
    d2=sc.spatial.distance.cdist(segedpsds2[:ltwo_half],basis_set,'sqeuclidean')
    
    d2_2=sc.spatial.distance.cdist(segedpsds2[ltwo_half:ltwo],basis_set,'sqeuclidean')
    
    mx=np.max([np.max(d1),np.max(d2),np.max(d1_2),np.max(d2_2)])
    
    #convert to similarity matrices:
    s1=1-(d1/mx)
    s1_2=1-(d1_2/mx)
    s2=1-(d2/mx)
    s2_2=1-(d2_2/mx)
    
    #estimate GMMs:
    mod1=mixture.GMM(n_components=k,n_iter=100000,n_init=5,covariance_type='full')
    mod1.fit(s1)
    
    mod2=mixture.GMM(n_components=k2,n_iter=100000,n_init=5,covariance_type='full')
    mod2.fit(s2)
    
    len2=len(s2)
    len1=len(d1)
    
    #calculate likelihoods for held out data:
    score1_1=mod1.score(s1_2)
    score2_1=mod2.score(s1_2)
    
    score1_2=mod1.score(s2_2)
    score2_2=mod2.score(s2_2)
    
    len2=float(len(basis_set))
    len1=float(len(basis_set))
    
    #calculate song divergence (DKL estimate):
    score1= np.log2(np.e)*((np.mean(score1_1))-(np.mean(score2_1)))
    score2= np.log2(np.e)*((np.mean(score2_2))-(np.mean(score1_2)))
    
    score1=score1/len1
    score2=score2/len2
    
    #output
    print filename1+'\t'+filename2+'\t'+str(k)+'\t'+str(k2)+'\t'+str(len2)+'\t'+str(score1)+'\t'+str(score2)+'\t'+str(len(segedpsds1))+'\t'+str(len(segedpsds2))


if __name__ == '__main__':
    path1 = sys.argv[1]
    path2 = sys.argv[2]
    calculate_songdkl(path1, path2)