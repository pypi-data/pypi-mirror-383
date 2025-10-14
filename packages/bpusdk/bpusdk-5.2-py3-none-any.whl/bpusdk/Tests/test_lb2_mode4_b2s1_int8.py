import time
import warnings
import random
import brainpy.math as bm
import jax

import os 
import sys

current_path = os.getcwd()
sys.path.insert(0, current_path)
from bpusdk.BrainpyLib.GenConn import gen_conn_int8_LRconn,gen_conn_int8_lb2_random
from bpusdk.Models.EImodel_lb2_int8  import EINet
from bpusdk.BrainpyLib.lb2_SNN import lb2_SNN
from bpusdk.BrainpyLib.lb2_deploy import lb2_deploy
from bpusdk.BrainpyLib.lb2_checkRes import lb2_checkRes

warnings.filterwarnings("ignore")
random.seed(1)
bm.random.seed(42)
bm.set_dt(2.0)
key = jax.random.PRNGKey(1)

def gen_net(nExc,nInh,fanOut):
    t0 = time.time()
    conn_list = gen_conn_int8_LRconn(nExc+nInh, fanOut, groupSize=8)
    #conn_list = gen_conn_int8_lb2_random(nExc+nInh,fanOut,groupSize=8)
    net = EINet(population_sizes=[nExc,nInh], conn=["customized",conn_list] , method = "euler")
    t1 = time.time()
    print(f"{(nExc+nInh)//1024}k network generated in {t1-t0:.2f} seconds")
    return net

if __name__ == "__main__":
    download_dir = "../data7/Lb2_mode4_b2s1_int8_128k_correct"     
    #download_dir = "../data7/Lb2_mode4_b2s1_int8_mapping"     
    upload_dir = "../upload7/ResLb2_mode4_b2s1_int8_correct"
    nExc = 64*1024
    nInh = 64*1024
    nStep = 3
    fanOut = 10

    #Gendata
    net = gen_net(nExc,nInh,fanOut)
    inpI = 2.      
    net.dump(download_dir,nStep,inpI=inpI,save=True,jit=True)     
    bpuset = lb2_SNN(net,inpI=inpI,config={"Base":2,"Dtype":"int8","group_to_disable":0})
    bpuset.gen_bin_data(download_dir)
    
    deploy = lb2_deploy(download_dir,upload_dir)
    sender_path = "/home/test1/work/LBII/build/LBII"
    deploy.run_from_host(nStep=nStep,sender_path=sender_path,device_id=15,run=False)
    # deploy.run_from_driver(nStep=nStep,device_id=16,dmos=False)
    
    check = lb2_checkRes(download_dir, upload_dir, nStep)
    check.bin2npy()
    check.npyVSnpy()  