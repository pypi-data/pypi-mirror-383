import os
import numpy as np
import wget
import warnings
warnings.filterwarnings("ignore")

# ---------------------------
# Files to download
# ---------------------------

MODEL_FILES = [
    'GMM_C/GMM_C.png', 'GMM_C/GMM_C_Brazil_4.png', 'GMM_C/GMM_C_covariances.npy', 'GMM_C/GMM_C_means.npy', 'GMM_C/GMM_C_weights.npy',
    'GMM_CA/GMM_CA.png', 'GMM_CA/GMM_CA_Brazil_6.png', 'GMM_CA/GMM_CA_covariances.npy', 'GMM_CA/GMM_CA_means.npy', 'GMM_CA/GMM_CA_weights.npy',
    'GMM_CB/GMM_CB.png', 'GMM_CB/GMM_CB_Brazil_8.png', 'GMM_CB/GMM_CB_covariances.npy', 'GMM_CB/GMM_CB_means.npy', 'GMM_CB/GMM_CB_weights.npy',
    'GMM_CBA/GMM_CBA.png', 'GMM_CBA/GMM_CBA_Brazil_14.png', 'GMM_CBA/GMM_CBA_Brazil_refined_12.png', 'GMM_CBA/GMM_CBA_covariances.npy', 
    'GMM_CBA/GMM_CBA_means.npy', 'GMM_CBA/GMM_CBA_refined.png', 'GMM_CBA/GMM_CBA_weights.npy',
    'xgbc_kca.json', 'xgbc_kca.png', 'xgbc_kcb.json', 'xgbc_kcb.png', 'xgbc_kcba.json', 'xgbc_kcba.png',
    'xgbc_sus_c.json', 'xgbc_sus_c.png', 'xgbc_sus_ca.json', 'xgbc_sus_ca.png', 'xgbc_sus_cb.json', 'xgbc_sus_cb.png',
    'xgbc_sus_cba.json', 'xgbc_sus_cba.png',
    'xgbr_c.json', 'xgbr_c.png',
    'xgbr_ca_c0_a1_k0.json', 'xgbr_ca_c0_a1_k0.png', 'xgbr_ca_c1_a0_k0.json', 'xgbr_ca_c1_a0_k0.png',
    'xgbr_ca_c1_a1_k0.json', 'xgbr_ca_c1_a1_k0.png', 'xgbr_ca_c1_a1_k1.json', 'xgbr_ca_c1_a1_k1.png',
    'xgbr_cba_c0_b0_a1.json', 'xgbr_cba_c0_b0_a1.png', 'xgbr_cba_c0_b1_a0_k0.json', 'xgbr_cba_c0_b1_a0_k0.png',
    'xgbr_cba_c0_b1_a0_k1.json', 'xgbr_cba_c0_b1_a0_k1.png', 'xgbr_cba_c0_b1_a1.json', 'xgbr_cba_c0_b1_a1.png',
    'xgbr_cba_c1_b0_a0.json', 'xgbr_cba_c1_b0_a0.png', 'xgbr_cba_c1_b0_a1.json', 'xgbr_cba_c1_b0_a1.png',
    'xgbr_cba_c1_b1_a0.json', 'xgbr_cba_c1_b1_a0.png', 'xgbr_cba_c1_b1_a1.json', 'xgbr_cba_c1_b1_a1.png',
    'xgbr_cb_c0_b1_k0.json', 'xgbr_cb_c0_b1_k0.png', 'xgbr_cb_c0_b1_k1.json', 'xgbr_cb_c0_b1_k1.png',
    'xgbr_cb_c1_b0.json', 'xgbr_cb_c1_b0.png', 'xgbr_cb_c1_b1.json', 'xgbr_cb_c1_b1.png'
]

TUTORIAL_FILES = [
    'SAVIC_Examples.h5', 'SAVIC_readme.pdf', 'SAVIC_testing.ipynb', 
    'Article_I_Statistical_Trends.pdf', 'Article_II_Classification_and_Multidimensional_Mapping.pdf'
]

# ---------------------------
# Base paths and URLs
# ---------------------------

BASE_PATH_MODELS = os.path.dirname(np.__file__.replace('numpy','savic').replace('__init__.py', '')) + '/Output/ML/models/'
BASE_PATH_TUTORIAL = os.path.dirname(np.__file__.replace('numpy','savic').replace('__init__.py', '')) + '/tutorial/'

BASE_URL_MODELS = "https://raw.githubusercontent.com/MihailoMartinovic/SAVIC/main/Output/ML/models/"
BASE_URL_TUTORIAL = "https://raw.githubusercontent.com/MihailoMartinovic/SAVIC/main/tutorial/"

# ---------------------------
# Helper function to download missing
# ---------------------------

def download_if_missing(base_path, base_url, name):
    local_path = os.path.join(base_path, name)
    folder = os.path.dirname(local_path)
    os.makedirs(folder, exist_ok=True)

    if os.path.isfile(local_path):
        #print(f"[OK] {name} exists, skipping download")
        return

    url = base_url + name
    print(f"[MISSING] {name} downloading...")
    wget.download(url, out=folder)
    print(f" -> Downloaded: {name}")

# ---------------------------
# Download models
# ---------------------------

for name in MODEL_FILES:
    download_if_missing(BASE_PATH_MODELS, BASE_URL_MODELS, name)

# ---------------------------
# Download tutorial files
# ---------------------------

for name in TUTORIAL_FILES:
    download_if_missing(BASE_PATH_TUTORIAL, BASE_URL_TUTORIAL, name)
