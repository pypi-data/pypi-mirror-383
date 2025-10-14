import time
import warnings
import random
import brainpy.math as bm
import jax
import numpy as np
from loguru import logger
import os 
import sys

current_path = os.getcwd()
sys.path.insert(0, current_path)
from bpusdk.BrainpyLib.GenConn import gen_conn_int8_random
from bpusdk.Models.EImodel_lb1_int8  import EINet
from bpusdk.BrainpyLib.lb1_SNN import lb1_SNN
from bpusdk.BrainpyLib.lb1_deploy import lb1_deploy
from bpusdk.BrainpyLib.lb1_checkRes import lb1_checkRes

warnings.filterwarnings("ignore")
random.seed(42)
bm.random.seed(42)
np.random.seed(42)
bm.set_dt(1.0)
key = jax.random.PRNGKey(1)

def gen_net(nExc,nInh,fanOut):
    t0 = time.time()
    conn_list = gen_conn_int8_random(nExc+nInh,fanOut,groupSize=8)

    # src = np.arange(nExc+nInh)
    # dst = np.roll(src,-1)
    # conn_list = np.vstack((src,dst))

    net = EINet(population_sizes=[nExc,nInh], conn=["customized",conn_list] , method = "euler")
    t1 = time.time()
    print(f"{(nExc+nInh)//1024}k network generated in {t1-t0:.2f} seconds")
    return net

if __name__ == "__main__":
    download_dir = "../data7/lb1_int8_768k_0.5"
    upload_dir = "../data7/Reslb1_int8_768k_0.5"
    nExc = 384*1024
    nInh = 384*1024
    nStep = 15
    fanOut = 12

    #Gendata
    net = gen_net(nExc,nInh,fanOut)
    net.dump(download_dir,nStep,save=True,jit=False)     
    bpuset = lb1_SNN(net,config={"Dtype":"int8","Npu_NeuronNum":8192,"Npu_EdgeNum":40960})
    bpuset.gen_bin_data(download_dir)

    # os.system(rf"scp -r {download_dir}/smt_96bit root@10.6.51.141:/root/work/data/lb1_int8_768k_0.5/")
    # os.system(rf"scp -r {download_dir} root@10.6.51.141:/root/work/data/ ")
    # os.system(rf"rsync -av -e ssh --exclude='soft_data' {download_dir} root@10.6.51.141:/root/work/data/")
    # # Deploy
    # deploy = lb1_deploy(download_dir,upload_dir)
    # deploy.run_from_driver(nStep=nStep,device_id=10,run=False)
