import time
import warnings
import brainpy.math as bm
import numpy as np
import random
import os 
import sys

current_path = os.getcwd()
sys.path.insert(0, current_path)
from bpusdk.Models.EImodel_singleSyn import EINet
from bpusdk.BrainpyLib.lb2_SNN import lb2_SNN
from bpusdk.BrainpyLib.lb2_checkRes import lb2_checkRes
from bpusdk.BrainpyLib.lb2_deploy import lb2_deploy
from bpusdk.BrainpyLib.GenConn import gen_conn_random 

warnings.filterwarnings("ignore")
random.seed(1)
bm.random.seed(42)
bm.set_dt(1.0)
def gen_net(nExc,nInh,fanOut):
    t0 = time.time()
    conn_list = gen_conn_random(nExc+nInh,fanOut)
    net = EINet(population_sizes=[nExc,nInh], conn=["customized",conn_list] , method = "euler")
    t1 = time.time()
    print(f"{(nExc+nInh)//1024}k network generated in {t1-t0:.2f} seconds")
    return net

if __name__ == "__main__":
    download_dir = "../data7/Lb2_b2s1_32k"
    upload_dir = "../upload7/ResLb2_b2s1_32k"
    nExc = 16*1024
    nInh = 16*1024
    fanOut = 4
    nStep = 20

    #Gendata
    net = gen_net(nExc,nInh,fanOut)
    inpI = 100.                                       
    bpuset = lb2_SNN(net, inpI=inpI, config = {"Base":2})
    net.dump(download_dir,nStep, inpI=inpI,save=True,jit=True)     
    bpuset.gen_bin_data(download_dir)
    # bpuset.gen_hex_data(download_dir)

    # Deploy
    deploy = lb2_deploy(download_dir,upload_dir)
    sender_path = "/home/test1/work/LBII_matrix/build/LBII"
    deploy.run_from_host(nStep=nStep,sender_path=sender_path,device_id=15)
    # deploy.run_from_driver(step=nStep,device_id=7,dmos=False)

    # # Compare results or convert bin to npy
    check = lb2_checkRes(download_dir, upload_dir, nStep)
    check.bin2npy()
    check.npyVSnpy() 