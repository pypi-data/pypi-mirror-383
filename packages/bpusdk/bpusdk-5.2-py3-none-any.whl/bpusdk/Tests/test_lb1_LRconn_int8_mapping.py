import time
import warnings
import random
import brainpy.math as bm
import jax
import numpy as np
from loguru import logger
import os 
import sys
import shutil
import json
from pathlib import Path
import pickle
import copy 

current_path = os.getcwd()
sys.path.insert(0, current_path)

from bpusdk.BrainpyLib.GenConn import gen_conn_int8_LRconn
from bpusdk.Models.EImodel_lb1_int8  import EINet
from bpusdk.BrainpyLib.lb1_SNN import lb1_SNN
from bpusdk.BrainpyLib.lb1_deploy import lb1_deploy
from bpusdk.BrainpyLib.lb1_checkRes import lb1_checkRes

warnings.filterwarnings("ignore")
random.seed(1)
bm.random.seed(42)
bm.set_dt(1.0)
key = jax.random.PRNGKey(1)

def mapping(download_dir, target_dir, target_size):
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    shutil.copytree(download_dir, target_dir)  
    dir_name_list = ['smt_96bit','weight','ndma_staddr','spdma','npu_ctrl','npu_ctrl','npu_ctrl','npu_ctrl']
    file_name_list = ['smt_','weight_','ndma_staddr_','spdma_','npu_after_','npu_all0_','npu_on_','npu_spike_']
    for dir_name,file_name in zip(dir_name_list,file_name_list):
        for iTile in range(1,target_size):
            ori_name = f'{download_dir}/{dir_name}/{file_name}{0}.bin'
            target_name = f'{target_dir}/{dir_name}/{file_name}{iTile}.bin'
            shutil.copy2(ori_name, target_name)
    
    json_path = download_dir + "/config.json"
    with open(json_path, 'r', encoding='utf8') as stream:
        config = json.load(stream)
    config['nRow'] = 36
    config['nCol'] = target_size//config['nRow']
    config['nTile'] = target_size
    with open(Path(target_dir)/"config.json", "w") as json_file:
        json.dump(config, json_file, indent=4)    
    return

def gen_net(nNeuron,fanOut):
    t0 = time.time()
    conn_list = gen_conn_int8_LRconn(nNeuron, fanOut)
    net = EINet([nNeuron//2,nNeuron//2], conn=["customized",conn_list], method = "euler")
    t1 = time.time()
    print(f"{nNeuron//1024}k network generated in {t1-t0:.2f} seconds")
    return net

def trans_line(x):
    result = []
    for item in range(len(x), 0, -8):
        tmp = []
        var = x[item-8:item]
        tmp.extend([var[6:8], var[4:6], var[2:4], var[0:2]])
        tmp = list(map(lambda x: int(x, 16), tmp))
        result.extend(tmp)
    return result

# 2: downRow, 1: topRow excl. topright, 0: Other
def determineTilePos(iTile,nRow,nCol):
    if iTile % nRow == nRow-1:
        return 2
    
    if iTile != (nCol*nRow)-nRow and iTile % nRow == 0:
        return 1
    
    else:
        return 0

#return 4 char = 16b
def gethexString(rid,end):
    binary_r = format(rid, '010b')  
    binary_string = f"1{binary_r}{end}"
    hex_string = format(int(binary_string, 2), '04x') 
    return hex_string

def createRouter(download_dir,nRow,nCol,hex=False):
    new_dir = Path(download_dir) / "route_info" if not hex else Path(download_dir)/ "hex" / "route_info" 
    if new_dir.exists():
        shutil.rmtree(new_dir)
    
    os.makedirs(new_dir, exist_ok=True)
    zeroPadding_4 = '0000' #16b
    changeRow = '\n' if hex else ''
    for iTile in range(nCol*nRow):
        file_name = f"/route_info_{iTile}.bin" if not hex else f"/route_info_{iTile}.hex"
        outfile_path = download_dir+"/route_info"+ file_name if not hex else download_dir+ "/hex/route_info"+file_name
        case = determineTilePos(iTile,nRow,nCol)
        match case: # 2: topRight/downRow, 1: topRow, 0: Other
            case 0:
                element_hex = gethexString(0, '10100')
                element_hex = gethexString(0, '10000')
                row_hex = element_hex+zeroPadding_4*15+changeRow
                data = row_hex
                
            case 1:
                element_hex = gethexString(0, '10110')
                element_hex = gethexString(0, '10000')
                row_hex = element_hex+zeroPadding_4*15+changeRow
                data = row_hex

            case 2:
                element_hex = gethexString(0, '10000')
                element_hex = gethexString(0, '10000')
                row_hex = element_hex+zeroPadding_4*15+changeRow
                data = row_hex

        element_hex = gethexString(0, '10000')
        row_hex = element_hex+zeroPadding_4*15+changeRow
        data = row_hex*120 + data*8
         
        if hex:
            lines = data.split('\n')
            lines.reverse()
            with open(outfile_path, 'a') as f_in:
                for line in lines:
                    if len(line) > 0:
                        f_in.write(line+'\n')
        else:
            data = bytearray(trans_line(data))
            with open(outfile_path, 'wb') as f_in:
                f_in.write(data)

def createTileid(download_dir,target_size):
    for iTile in range(target_size):
        path = f'{download_dir}/tile_id/tile_id_{iTile}.bin'        
        idx = np.array([iTile]).astype(np.int32)
        idx.tofile(path)

def createRemote4(download_dir,target_size):    
    new_dir = Path(download_dir) / "remote4" 
    if new_dir.exists():
        shutil.rmtree(new_dir)
    os.makedirs(new_dir, exist_ok=True)

    for iTile in range(target_size):
        path = f'{download_dir}/remote4/remote4_{iTile}.bin'    
        with open(path, "wb") as f:
            f.write(bytes.fromhex("0000000001000000"))

def createGlobalConn_dict(download_dir,target_size,local_conn):
    new_dir = Path(download_dir) / "globalConn" 
    if new_dir.exists():
        shutil.rmtree(new_dir)
    os.makedirs(new_dir, exist_ok=True)
            
    local_conn_reference = {}
    for iNeuron in local_conn:
        local_conn_reference[iNeuron] = list(local_conn[iNeuron].keys())    
    path = f'{download_dir}/globalConn/tile_{0}.pkl' 
    with open(path, "wb") as f:
        pickle.dump(local_conn_reference, f)
    
    for iTile in range(1,5):
        local_conn = {}  
        print(iTile)
        offset = 16*1024*8+15*1024*8*(iTile-1)
        for iNeuron in range(1024*8):
            if iNeuron not in local_conn:
                local_conn[iNeuron] = []            
            local_conn[iNeuron] = list(np.array(local_conn_reference[iNeuron])+offset-1024*8)
        for iNeuron in range(1024*8,1024*8*15):
            if iNeuron-1024*8+offset not in local_conn:
                local_conn[iNeuron-1024*8+offset] = []
            local_conn[iNeuron-1024*8+offset] = list(np.array(local_conn_reference[iNeuron])+-1024*8+offset)            

        path = f'{download_dir}/globalConn/tile_{iTile}.pkl' 
        with open(path, "wb") as f:
            pickle.dump(local_conn,f)

def createGlobalConn(download_dir,target_size,local_conn):
    new_dir = Path(download_dir) / "globalConn" 
    if new_dir.exists():
        shutil.rmtree(new_dir)
    os.makedirs(new_dir, exist_ok=True)
    
    #create local_conn_reference        
    local_conn_reference = {}
    for iNeuron in local_conn:
        local_conn_reference[iNeuron] = list(local_conn[iNeuron].keys())    
    
    #save tile0
    pre = []
    post = []
    for iNeuron in local_conn_reference:
        post_tmp = local_conn_reference[iNeuron]
        post.extend(post_tmp)
        pre_tmp = [iNeuron]*len(post_tmp)
        pre.extend(pre_tmp)
    pre = np.array(pre).astype(np.int32)
    post = np.array(post).astype(np.int32)
    conn_matrix = np.vstack((pre,post))
    path = f'{download_dir}/globalConn/tile_{0}.npy' 
    np.save(path,conn_matrix)
    
    for iTile in range(1,target_size):
        local_conn = {}  
        print(iTile)
        offset = 16*1024*8+15*1024*8*(iTile-1)
        #conn from npu0 tile0
        for iNeuron in range(1024*8):       
            local_conn[iNeuron] = list(np.array(local_conn_reference[iNeuron])+offset-1024*8)
        #conn from own tile
        for iNeuron in range(1024*8,1024*8*16):
            local_conn[iNeuron-1024*8+offset] = list(np.array(local_conn_reference[iNeuron])-1024*8+offset)            

        #dict to array
        pre = []
        post = []
        for iNeuron in local_conn:
            post_tmp = local_conn[iNeuron]
            post.extend(post_tmp)
            pre_tmp = [iNeuron]*len(post_tmp)
            pre.extend(pre_tmp)
        pre = np.array(pre).astype(np.int32)
        post = np.array(post).astype(np.int32)
        conn_matrix = np.vstack((pre,post))
        path = f'{download_dir}/globalConn/tile_{iTile}.npy' 
        np.save(path,conn_matrix)
    
if __name__ == "__main__":
    download_dir = "../data7/lb1_int8_128k"
    upload_dir = "../data7/Reslb1_int8_128k"
    target_dir = "../data7/lb1_int8_server"
    nNeuron = 16*2*4*1024
    nStep = 2
    fanOut = 13
    nRow = 6
    nCol = 24
    target_size = nRow*nCol

    #Gendata
    net = gen_net(nNeuron,fanOut)
    #net.dump(download_dir,nStep,jit=False)

    bpuset = lb1_SNN(net, config={"Dtype":"int8","Npu_NeuronNum":8192,"Npu_EdgeNum":40960,"group_to_disable":1024})
    # local_conn = bpuset.bpbase.connection_matrix
    # createGlobalConn(target_dir,target_size,local_conn)
    bpuset.gen_bin_data(download_dir)
    mapping(download_dir, target_dir, target_size)
    bpuset = lb1_SNN(net, config={"Dtype":"int8","Npu_NeuronNum":8192,"Npu_EdgeNum":40960,"group_to_disable":0})
    bpuset.gen_bin_data(target_dir)
    createTileid(target_dir,target_size)
    createRouter(target_dir,nRow,nCol,hex=False)
    createRemote4(target_dir,target_size)