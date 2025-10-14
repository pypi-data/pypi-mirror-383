
import os
import numpy as np
import urllib
import wget
import warnings
warnings.filterwarnings("ignore")

    
names = ['GMM_C/GMM_C.png', 'GMM_C/GMM_C_Brazil_4.png', 'GMM_C/GMM_C_covariances.npy', 'GMM_C/GMM_C_means.npy', 'GMM_C/GMM_C_weights.npy', \
    'GMM_CA/GMM_CA.png', 'GMM_CA/GMM_CA_Brazil_6.png', 'GMM_CA/GMM_CA_covariances.npy', 'GMM_CA/GMM_CA_means.npy', 'GMM_CA/GMM_CA_weights.npy', \
    'GMM_CB/GMM_CB.png', 'GMM_CB/GMM_CB_Brazil_8.png', 'GMM_CB/GMM_CB_covariances.npy', 'GMM_CB/GMM_CB_means.npy', 'GMM_CB/GMM_CB_weights.npy', \
    'GMM_CBA/GMM_CBA.png', 'GMM_CBA/GMM_CBA_Brazil_14.png', 'GMM_CBA/GMM_CBA_Brazil_refined_12.png', 'GMM_CBA/GMM_CBA_covariances.npy', 'GMM_CBA/GMM_CBA_means.npy', 'GMM_CBA/GMM_CBA_refined.png', 'GMM_CBA/GMM_CBA_weights.npy', \
    'xgbc_kca.json', 'xgbc_kca.png', 'xgbc_kcb.json', 'xgbc_kcb.png', 'xgbc_kcba.json', 'xgbc_kcba.png', 'xgbc_sus_c.json', 'xgbc_sus_c.png', \
    'xgbc_sus_ca.json', 'xgbc_sus_ca.png', 'xgbc_sus_cb.json', 'xgbc_sus_cb.png', 'xgbc_sus_cba.json', 'xgbc_sus_cba.png', \
    'xgbr_c.json', 'xgbr_c.png', \
    'xgbr_ca_c0_a1_k0.json', 'xgbr_ca_c0_a1_k0.png', 'xgbr_ca_c1_a0_k0.json', 'xgbr_ca_c1_a0_k0.png', \
    'xgbr_ca_c1_a1_k0.json', 'xgbr_ca_c1_a1_k0.png', 'xgbr_ca_c1_a1_k1.json', 'xgbr_ca_c1_a1_k1.png', \
    'xgbr_cba_c0_b0_a1.json', 'xgbr_cba_c0_b0_a1.png', 'xgbr_cba_c0_b1_a0_k0.json', 'xgbr_cba_c0_b1_a0_k0.png', \
    'xgbr_cba_c0_b1_a0_k1.json', 'xgbr_cba_c0_b1_a0_k1.png', 'xgbr_cba_c0_b1_a1.json', 'xgbr_cba_c0_b1_a1.png', \
    'xgbr_cba_c1_b0_a0.json', 'xgbr_cba_c1_b0_a0.png', 'xgbr_cba_c1_b0_a1.json', 'xgbr_cba_c1_b0_a1.png', \
    'xgbr_cba_c1_b1_a0.json', 'xgbr_cba_c1_b1_a0.png', 'xgbr_cba_c1_b1_a1.json', 'xgbr_cba_c1_b1_a1.png', \
    'xgbr_cb_c0_b1_k0.json', 'xgbr_cb_c0_b1_k0.png', 'xgbr_cb_c0_b1_k1.json', 'xgbr_cb_c0_b1_k1.png', \
    'xgbr_cb_c1_b0.json', 'xgbr_cb_c1_b0.png', 'xgbr_cb_c1_b1.json', 'xgbr_cb_c1_b1.png']
    
path_ = os.path.dirname(np.__file__.replace('numpy','savic').replace('__init__.py', '')) + '/Output/ML/models/'

for name in names:
    is_file_ = os.path.isfile(path_+name)
    if is_file_:
        size_ = os.path.getsize(path_+name)
        url_ = "https://raw.githubusercontent.com/MihailoMartinovic/SAVIC/main/Output/ML/models/" + name 
        online_size_ = urllib.request.urlopen(url_).headers['Content-Length']
        
        #print('')
        #print('file already updated', name, 'size: ', size_, '   online size:', online_size_, name)
        #print('')
        
        if int(size_) != int(online_size_):
            print('file requires update, starting download ... ', name)
            os.remove(path_+name)
            if '/' in name:
                print(name.split('/'))
                wget.download(url_, out = path_ + name.split('/')[0] + '/')
            else:
                wget.download(url_, out = path_)
    else:
        print('')
        print('file missing, starting download ... ', name)
        url_ = "https://raw.githubusercontent.com/MihailoMartinovic/SAVIC/main/Output/ML/models/" + name 
        print(url_)
        print('')
        if '/' in name:
            print(name.split('/'))
            wget.download(url_, out = path_ + name.split('/')[0] + '/')
        else:
            wget.download(url_, out = path_)
        print('')

names = ['SAVIC_Examples.h5', 'SAVIC_readme.pdf', 'SAVIC_testing.ipynb', 'Article_I_Statistical_Trends.pdf', 'Article_II_Classification_and_Multidimensional_Mapping.pdf']

path_ = os.path.dirname(np.__file__.replace('numpy','savic').replace('__init__.py', '')) + '/tutorial/'

for name in names:
    is_file_ = os.path.isfile(path_+name)
    if is_file_:
        size_ = os.path.getsize(path_+name)
        url_ = "https://raw.githubusercontent.com/MihailoMartinovic/SAVIC/main/tutorial/" + name 
        online_size_ = urllib.request.urlopen(url_).headers['Content-Length']
        
        #print('')
        #print('file already updated', name, 'size: ', size_, '   online size:', online_size_, name)
        #print('')
        
        if int(size_) != int(online_size_):
            print('file requires update, starting download ... ', name)
            os.remove(path_+name)
            if '/' in name:
                print(name.split('/'))
                wget.download(url_, out = path_ + name.split('/')[0] + '/')
            else:
                wget.download(url_, out = path_)
    else:
        print('')
        print('file missing, starting download ... ', name)
        url_ = "https://raw.githubusercontent.com/MihailoMartinovic/SAVIC/main/tutorial/" + name 
        print(url_)
        print('')
        if '/' in name:
            print(name.split('/'))
            wget.download(url_, out = path_ + name.split('/')[0] + '/')
        else:
            wget.download(url_, out = path_)
        print('')
 
