import os 
import sys
import numpy as np

current_path = os.getcwd()
sys.path.insert(0, current_path)
from bpusdk.MatrixLib.lb2_pool import lb2_pool
from bpusdk.MatrixLib.lb2_checkRes import lb2_checkRes
from bpusdk.MatrixLib.lb2_deploy import lb2_deploy
import time 

np.random.seed(42)


def cal_pooling_out_size(input_height, input_width, pool_size, stride, padding=(0, 0)):
    """
    """
    output_height = (input_height + 2 * padding[0] - pool_size[0]) // stride[0] + 1
    output_width = (input_width + 2 * padding[1] - pool_size[1]) // stride[1] + 1
    
    return output_height, output_width

def res_reshape(C_res, B_nRow, B_nCol, stride, padding):
    C_res = np.array(C_res)
    B, _, H = C_res.shape
    H_div_8 = H // 8
    result = []
    for b in range(B):
        block_result = []
        for i in range(H_div_8):
            block = C_res[b, :, i*8:(i+1)*8]
            first_column = block[:, 0]
            block_result.extend(first_column)
        result.extend([block_result])

    result = np.array(result)
    output_height, output_width = cal_pooling_out_size(B_nRow, B_nCol, (2, 2), (stride, stride), padding=(padding, padding))
    N = result.shape[1]
    if N > output_height * output_width:
        result = result[:, :output_height*output_height]
    result = result.reshape((B, output_height, output_height))
    return result

download_dir = "../data7/Lb2_pool"
upload_dir = "../upload7/ResLb2_pool"

batchsize = 1
B_nRow = 3
B_nCol = 3
# B = np.random.uniform(-2.0, 2.0, size=(batchsize, B_nRow, B_nCol))
# B = np.random.randint(1, 4, size=(batchsize, B_nRow, B_nCol))

B = np.array([[[1, 2, 3], [4, 5, 6], [7, 8, 9]]])

stride = 1
padding = 1

iMode = 5     #{max pool:4, avg pool:5}

#GenData
t0 = time.time()
matrix = lb2_pool(B, iMode, stride=stride, padding=padding)
B_ori = matrix.get_transformed_matrix()
print("B:", B, "\n") 
print("B_ori:", B_ori, "\n")
riscV_dir = "/home/test2/work/uger_t/Riscv-gcc-tool"
#riscV_dir =  "/home/gdiist/work/Riscv-gcc-tool"
matrix.gen_bin_file(download_dir,riscV_dir)

t1 = time.time()
print(f'GenData finished. Time cost: {t1-t0:.2f} s')
        
# # Deploy
sender_path = "/home/test2/work/LBII_matrix/build/LBII"
deploy = lb2_deploy(download_dir,upload_dir)
deploy.run_from_host(sender_path=sender_path,device_id=6,saveAB=True,run=True,mode=3)

# # CheckData
t0 = time.time()
check = lb2_checkRes(download_dir, upload_dir)

A_res, B_res, C_res = check.bin2npy_small_BC_v2()
# print("A_res:", A_res, "\n")
print("B_res:", np.array(B_res), "\n")
print("C_res:", C_res, "\n")
C_reshape= res_reshape(C_res, B_nRow, B_nCol, stride, padding)
print("B:\n", B, "\n") 
print("C_reshape:\n", C_reshape, "\n")

t1 = time.time()
print(f'CheckData finished. Time cost: {t1-t0:.2f} s')

