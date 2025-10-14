import time
import warnings
import brainpy.math as bm
import numpy as np
import random
import os 
import sys
import shutil
import json
from pathlib import Path

current_path = os.getcwd()
sys.path.insert(0, current_path)
from bpusdk.Models.EImodel_lb2_int8 import EINet
from bpusdk.BrainpyLib.lb2_SNN import lb2_SNN
from bpusdk.BrainpyLib.lb2_checkRes import lb2_checkRes
from bpusdk.BrainpyLib.lb2_deploy import lb2_deploy
from bpusdk.BrainpyLib.GenConn import gen_conn_int8_random


def mapping(download_dir, target_dir, target_size):
    origianl_size = 6
    nLoop = target_size//origianl_size
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    shutil.copytree(download_dir, target_dir)  
    dir_name_list = ['smt','weight','index','ncu']
    for dir_name in dir_name_list:
        for iLoop in range(nLoop):
            for iTile_original in range(origianl_size):
                iTile_target = iTile_original+iLoop*origianl_size
                for iNpu in range(4):
                    ori_name = f'{download_dir}/{dir_name}/tile{iTile_original}_npu{iNpu}.bin'
                    target_name = f'{target_dir}/{dir_name}/tile{iTile_target}_npu{iNpu}.bin'
                    shutil.copy2(ori_name, target_name)
    dir_name_list = ['route_info']
    for dir_name in dir_name_list:
        for iLoop in range(nLoop):
            for iTile_original in range(origianl_size):
                iTile_target = iTile_original+iLoop*origianl_size
                ori_name = f'{download_dir}/{dir_name}/tile{iTile_original}.bin'
                target_name = f'{target_dir}/{dir_name}/tile{iTile_target}.bin'
                shutil.copy2(ori_name, target_name)
    return


def write_config(target_dir, target_size):
    json_path = download_dir + "/config.json"
    with open(json_path, 'r', encoding='utf8') as stream:
        config = json.load(stream)
    config['nRow'] = 6
    config['nCol'] = target_size//config['nRow']
    config['nTile'] = 6
    config['syn_calcu_tw'] = 3000000
    #config['syn_calcu_tw'] = 50000000
    with open(Path(target_dir)/"config.json", "w") as json_file:
        json.dump(config, json_file, indent=4) 

warnings.filterwarnings("ignore")
random.seed(1)
bm.random.seed(42)
bm.set_dt(2.0)
def gen_net(nExc,nInh,fanout):
    t0 = time.time()
    conn_list = gen_conn_int8_random(nExc+nInh,fanout,groupSize=8)
    net = EINet(population_sizes=[nExc,nInh], conn=["customized",conn_list] , method = "euler")
    t1 = time.time()
    print(f"{(nExc+nInh)//1024}k network generated in {t1-t0:.2f} seconds")
    return net

if __name__ == "__main__":
    nTile = 6
    download_dir = f"../data7/Lb2_b2s1_int8_{nTile}"
    target_dir = f"../data7/Lb2_b2s1_int8_mapping"
    upload_dir = f"../upload7/ResLb2_b2s1_int8_mapping_ori"
    nExc = 64*1024*nTile
    nInh = 64*1024*nTile
    fanout = 6
    nStep = 15
    target_size = 6*18
    
    # # # #Gendata
    net = gen_net(nExc,nInh,fanout)
    inpI = 2.                                           
    bpuset = lb2_SNN(net,inpI,config = {"Base":2,"Dtype":"int8"})
    net.dump(download_dir,nStep,inpI=inpI,save=True,jit=False)     
    bpuset.gen_bin_data(download_dir)     
    mapping(download_dir,target_dir,target_size)
    write_config(target_dir,target_size)  

    #Deploy
    deploy = lb2_deploy(target_dir,upload_dir)
    sender_path = "/home/gdiist1/work/beartic/LBII_matrix/build/LBII"
    deploy.run_from_host(nStep=nStep,sender_path=sender_path,device_id=1,run=True)
    #deploy.run_from_driver(step=nStep,device_id=7,dmos=False)

    #Compare results or convert bin to npy
    check = lb2_checkRes(download_dir, upload_dir, nStep)
    check.bin2npy(nChip=3,nStep=2,print_log=False)
    check.npyVSnpy_multi_model(print_log=False) 
    # check.bin2npy()
    # check.npyVSnpy() 
    
    # nTile = 6
    # target_dir = f"/home/user/test_LBII_run/Lb2_b2s1_int8_mapping"
    # nStep = 15

    # for iXDMA in range(16):
    #     print(f"checking bpu{iXDMA}")
    #     upload_dir = f"/home/user/test_LBII_run/LBII_run_tmpRes{iXDMA}"
    #     check = lb2_checkRes(target_dir, upload_dir, nStep)
    #     check.bin2npy(nChip=3,nStep=2,print_log=False)
    #     check.npyVSnpy_multi_model(print_log=False) 
    #     # check.bin2npy()
    #     # check.npyVSnpy() 