import time
import warnings
import brainpy.math as bm
import numpy as np
import random
import os 
import sys

current_path = os.getcwd()
sys.path.insert(0, current_path)
from bpusdk.Models.EImodel_AdQuaIF import EINet
from bpusdk.BrainpyLib.lb2_SNN import lb2_SNN
from bpusdk.BrainpyLib.lb2_checkRes import lb2_checkRes
from bpusdk.BrainpyLib.lb2_deploy import lb2_deploy

warnings.filterwarnings("ignore")
random.seed(1)
# np.random.seed(1)
bm.random.seed(42)
bm.set_dt(0.1)

def gen_net(nExc,nInh):
    nNeuron = nExc+nInh

    t0 = time.time()
    arr = np.arange(nExc+nInh)
    shuffled_arr = np.random.permutation(arr)   
    data = np.vstack((arr,shuffled_arr))        

    conn = ["customized",data] 
    #conn = ['FixedPostNum', 1] 
    # conn = ['FixedPreNum', 5] 
    # conn = ['FixedTotalNum', 5] 
    # conn = ['FixedProb', 5/nNeuron] 
    # conn = ["prob", 5/nNeuron] 

    net = EINet(nExc, nInh, conn=conn, method = "euler")
    t1 = time.time()
    print(f"{nNeuron//1024}k network generated in {t1-t0:.2f} seconds")
    return net

if __name__ == "__main__":
    download_dir = "../data8/Lb2_AdQuaIF_64k"
    upload_dir = "../upload8/ResLb2_AdQuaIF_64k"
    nExc = 8*1024
    nInh = 8*1024
    nStep = 20

    # Gendata\
    net = gen_net(nExc,nInh) #生成神经网络
    inpI = 100.                                      
    inpS = np.zeros((nStep, nExc+nInh))
    inpS = inpS.astype(bool)    
    bpuset = lb2_SNN(net, inpS, inpI,config={"Is_Y_First":True})
    net.dump(download_dir,inpS,inpI,nStep,save=True,jit=False)   
    bpuset.gen_bin_data(download_dir) #为了在硬件中跑
    #bpuset.gen_hex_data(download_dir)

    # Deploy
    deploy = lb2_deploy(download_dir,upload_dir)
    sender_path = "/home/test2/work/LBII_matrix/build/LBII"
    deploy.run_from_host(nStep=nStep, sender_path=sender_path, device_id=10)
    # deploy.run_from_driver(nStep=nStep,device_id=2,dmos=False,save_ncu=1) #

    # Compare results or convert bin to npy
    check = lb2_checkRes(download_dir, upload_dir, nStep)
    check.bin2npy()
    check.npyVSnpy()  