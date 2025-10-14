import os 
import sys
import numpy as np
import time

current_path = os.getcwd()
sys.path.insert(0, current_path)
from bpusdk.MatrixLib.lb2_matrix import lb2_matrix
from bpusdk.MatrixLib.lb2_checkRes import lb2_checkRes
from bpusdk.MatrixLib.lb2_deploy import lb2_deploy

np.random.seed(42)
batchsize = 1
A_nRow = 16384
A_nCol = 128
B_nRow = A_nRow
B_nCol = A_nCol

A = np.random.uniform(-1.0, 1.0, size=(batchsize,A_nRow,A_nCol))
B = np.random.uniform(-1.0, 1.0, size=(batchsize,B_nRow,B_nCol))
iMode = 1   #{GEMA:0, GEMPM:1}

download_dir = f"../data7/Lb2_GEMA_batch"
upload_dir = f"../upload7/ResLb2_GEMA_batch"
saveAB = False

#GenData
t0 = time.time()
matrix = lb2_matrix(A,B,iMode)
riscV_dir = "/home/test2/work/Riscv-gcc-tool"
matrix.gen_bin_file(download_dir,riscV_dir,binary=True)
t1 = time.time()
# print(f'GenData finished. Time cost: {t1-t0:.2f} s')

# # Deploy
sender_path = "/home/test2/work/LBII_matrix/build/LBII"
deploy = lb2_deploy(download_dir,upload_dir)
deploy.run_from_host(sender_path=sender_path,device_id=6,saveAB=saveAB)

# # CheckData
t0 = time.time()
check = lb2_checkRes(download_dir, upload_dir)
C = check.bin2npy(saveAB=saveAB,dump=True)
check.npyVSnpy(checkAB=saveAB,diff_threshold=1E-3)
t1 = time.time()
print(f'CheckData finished. Time cost: {t1-t0:.2f} s')

