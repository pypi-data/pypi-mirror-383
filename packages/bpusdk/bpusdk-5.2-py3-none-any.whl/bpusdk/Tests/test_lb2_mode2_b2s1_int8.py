import time
import warnings
import brainpy.math as bm
import numpy as np
import random
import os 
import sys

current_path = os.getcwd()
sys.path.insert(0, current_path)
from bpusdk.Models.EImodel_lb2_int8 import EINet
from bpusdk.BrainpyLib.lb2_SNN import lb2_SNN
from bpusdk.BrainpyLib.lb2_checkRes import lb2_checkRes
from bpusdk.BrainpyLib.lb2_deploy import lb2_deploy
from bpusdk.BrainpyLib.GenConn import gen_conn_int8_random

warnings.filterwarnings("ignore")
random.seed(1)
bm.random.seed(42)
bm.set_dt(2.0)
def gen_net(nExc,nInh,fanout):
    t0 = time.time()
    conn_list = gen_conn_int8_random(nExc+nInh,fanout,groupSize=8)
    net = EINet(population_sizes=[nExc,nInh], conn=["customized",conn_list], method = "euler")
    t1 = time.time()
    print(f"{(nExc+nInh)//1024}k network generated in {t1-t0:.2f} seconds")
    return net

if __name__ == "__main__":
    download_dir = "../data7/Lb2_mode2_b2s1_int8_256k"
    upload_dir = "../upload7/ResLb2_mode2_b2s1_int8_256k"
    nExc = 128*1024
    nInh = 128*1024
    fanout = 1
    nStep = 15
    
    # Gendata
    net = gen_net(nExc,nInh,fanout)
    inpI = 2.                                       
    bpuset = lb2_SNN(net, inpI=inpI, config = {"Base":2,"Dtype":"int8"}, mode=2)
    net.dump(download_dir,nStep,inpI=inpI,save=True,jit=True)     
    bpuset.gen_bin_data(download_dir)   
    # bpuset.gen_hex_data(download_dir)   

    # Deploy
    deploy = lb2_deploy(download_dir,upload_dir)
    sender_path = "/home/test2/work/LBII_matrix/build/LBII"
    deploy.run_from_host(nStep=nStep,sender_path=sender_path,device_id=14)
    #deploy.run_from_driver(nStep=nStep,device_id=3,dmos=False,save_ncu=0)

    # Compare results or convert bin to npy
    check = lb2_checkRes(download_dir, upload_dir, nStep)
    check.bin2npy(v_dump=True)  # Convert bin to npy
    check.npyVSnpy(v_dump=True,w_dump=True) 
    
