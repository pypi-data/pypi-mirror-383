import warnings
import brainpy.math as bm
import time
import numpy as np
import os 
import sys

current_path = os.getcwd()
sys.path.insert(0, current_path)
from bpusdk.Models.EImodel import EINet
from bpusdk.BrainpyLib.lb1_SNN import lb1_SNN
from bpusdk.BrainpyLib.lb1_deploy import lb1_deploy
from bpusdk.BrainpyLib.lb1_checkRes import lb1_checkRes
import random

warnings.filterwarnings("ignore")
random.seed(1)
bm.random.seed(42)
bm.set_dt(1.0)

def gen_net(nExc,nInh):
    t0 = time.time()
    nNeuron = nExc+nInh
    arr = np.arange(nExc+nInh)
    shuffled_arr = np.random.permutation(arr)   
    data = np.vstack((arr,shuffled_arr))
    net = EINet(population_sizes=[nExc,nInh], conn=["customized",data] , method = "euler")
    t1 = time.time()
    print(f"{nNeuron//1024}k network generated in {t1-t0:.2f} seconds")
    return net


if __name__ == "__main__":
    download_dir = "../data7/lb1_96k"
    upload_dir = "../upload7/Reslb1_96k"
    nExc = 48*1024
    nInh = 48*1024
    nStep = 20

    #Gendata
    net = gen_net(nExc,nInh)
    inpI = 100.                                      
    bpuset = lb1_SNN(net, inpI)
    #net.dump(download_dir,inpI,nStep)           
    bpuset.gen_bin_data(download_dir)
    
    # # Deploy
    # deploy = lb1_deploy(download_dir,upload_dir)
    # deploy.run_from_driver(nStep=nStep,device_id=10,run=False)
