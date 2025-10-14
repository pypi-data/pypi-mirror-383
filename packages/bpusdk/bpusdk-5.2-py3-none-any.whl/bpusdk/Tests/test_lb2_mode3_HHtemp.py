import time
import warnings
import brainpy.math as bm
import numpy as np
import random
import os 
import sys
import matplotlib.pyplot as plt

current_path = os.getcwd()
sys.path.insert(0, current_path)
from bpusdk.Models.EImodel_HHtemp import EINet
from bpusdk.BrainpyLib.lb2_SNN import lb2_SNN
from bpusdk.BrainpyLib.lb2_checkRes import lb2_checkRes
from bpusdk.BrainpyLib.lb2_deploy import lb2_deploy

warnings.filterwarnings("ignore")
random.seed(1)
bm.random.seed(42)
dt = 0.005
bm.set_dt(dt)

def gen_net(nExc,nInh,temp):
    t0 = time.time()  
    data = [np.array([])]
    conn = ["customized",data] 
    net = EINet(population_sizes=[nExc+nInh], conn=conn, method = "euler",temp=temp)
    t1 = time.time()
    print(f"{nExc+nInh//1024}k network generated in {t1-t0:.2f} seconds")
    return net

if __name__ == "__main__":
    download_dir = "../data7/Lb2_mode3_HHtemp_55_5000"
    upload_dir = "../upload7/ResLb2_mode3_HHtemp_55_5000"
    nExc = 1
    nInh = 1
    #nStep = int(6/dt)
    nStep = 50
    temp = 55

    # # Gendata
    net = gen_net(nExc,nInh,temp)
    inpI = 0.                                        
    bpuset = lb2_SNN(net,inpI, mode=3)
    net.dump(download_dir,nStep,inpI=inpI)     
    bpuset.gen_bin_data(download_dir)
    #bpuset.gen_hex_data(download_dir)

    # # Deploy
    deploy = lb2_deploy(download_dir,upload_dir)
    sender_path = "/home/test2/work/LBII_matrix/build/LBII"
    deploy.run_from_host(nStep=nStep,sender_path=sender_path,device_id=14,run=True)
    # deploy.run_from_driver(nStep=nStep,device_id=16,dmos=False)

    # # # # Compare results or convert bin to npy
    check = lb2_checkRes(download_dir, upload_dir, nStep,single_neuron=True)
    [hw_v] = check.bin2npy(spike_dump=False,prefix="1")
    errorflag = check.npyVSnpy(s_dump=False,w_dump = False,print_log=True)
    print(f"Error flag: {errorflag}")
    
    plt.plot(hw_v[:,0], label='hw_v')
    plt.savefig("./55_5000.png", dpi=300)
