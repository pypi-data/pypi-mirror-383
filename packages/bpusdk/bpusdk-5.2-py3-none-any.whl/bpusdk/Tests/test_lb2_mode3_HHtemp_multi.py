import time
import warnings
import brainpy.math as bm
import numpy as np
import random
import os 
import sys
import matplotlib.pyplot as plt
import shutil
from pathlib import Path

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

def copy_ncu(upload_dir, download_dir):
    prefix = 0
    last_step = len(os.listdir(upload_dir))-1
    for iTile in range(1):
        for iNpu in range(4):
            src_path = f"{upload_dir}/step{last_step}/ncu_check/{prefix}tile{iTile}_npu{iNpu}.bin"
            dst_path = f"{download_dir}/ncu/tile{iTile}_npu{iNpu}.bin"
            shutil.copyfile(src_path, dst_path)
    prefix = 1
    for iTile in range(1):
        for iNpu in range(4):
            src_path = f"{upload_dir}/step{last_step}/ncu_check/{prefix}tile{iTile}_npu{iNpu}.bin"
            dst_path = f"{download_dir}/ncu{prefix}/tile{iTile}_npu{iNpu}.bin"
            shutil.copyfile(src_path, dst_path)

def check_stage(iStep, nStep):
    nStep_cumsum = np.cumsum(nStep)
    for iStage in range(len(nStep)-1, -1, -1):
        if iStep > nStep_cumsum[iStage]:
            iStep_local = iStep - nStep_cumsum[iStage]
            return [iStage+1,iStep_local]
    return [0, iStep]
    
def merge_result(upload_dir,nStep):
    relative_path = Path(f"{upload_dir}")
    upload_dir = relative_path.resolve()
    if os.path.isdir(upload_dir):
        shutil.rmtree(upload_dir)
    os.makedirs(upload_dir, exist_ok=True)

    for iStep in range(np.sum(nStep)+1):
        [iStage,iStep_local] = check_stage(iStep, nStep)
        dst_dir = os.path.join(upload_dir, f"step{iStep}")
        src_dir = os.path.join(f"{upload_dir}_{iStage}", f"step{iStep_local}")
        os.makedirs(dst_dir, exist_ok=True)       
        shutil.copytree(f'{src_dir}/ncu_check', f'{dst_dir}/ncu_check', dirs_exist_ok=True)
    print("data_merged successfully")                     
                            
def gen_net(nExc,nInh,temp):
    t0 = time.time()  
    data = [np.array([])]
    conn = ["customized",data] 
    net = EINet(population_sizes=[nExc+nInh], conn=conn, method = "euler",temp=temp)
    t1 = time.time()
    print(f"{nExc+nInh//1024}k network generated in {t1-t0:.2f} seconds")
    return net

if __name__ == "__main__":
    download_dir = "../data7/Lb2_mode3_16k_HHtemp"
    upload_dir = "../upload7/ResLb2_mode3_16k_HHtemp"
    nExc = 8*1024
    nInh = 8*1024
    nStep = [int(60/dt),int(2/dt),int(50/dt)]
    #nStep = [int(1/dt),int(2/dt),int(1/dt)]
    inpI = [0,15,0]
    temp = 42

    # # # Gendata sw data
    # net = gen_net(nExc,nInh,temp)                                    
    # for iStage in range(len(nStep)): 
    #     bpuset = lb2_SNN(net, inpI=inpI[iStage], mode=3)
    #     bpuset.gen_bin_data(download_dir)
    #     if iStage > 0:
    #         copy_ncu(f"{upload_dir}_{iStage-1}", download_dir)
            
    #     deploy = lb2_deploy(download_dir,f"{upload_dir}_{iStage}")
    #     sender_path = "/home/test1/work/LBII_matrix/build/LBII"
    #     deploy.run_from_host(step=nStep[iStage],sender_path=sender_path,device_id=3,run=True)

    # merge_result(upload_dir,nStep)
    # net.dump(download_dir,nStep,inpI=inpI)    
    
    # # # # Compare results or convert bin to npy
    check = lb2_checkRes(download_dir,upload_dir,np.sum(nStep),single_neuron=True)
    [hw_v] = check.bin2npy(spike_dump=False,prefix="1")
    errorflag = check.npyVSnpy(s_dump=False,w_dump = False,print_log=False)
    print(f"Error flag: {errorflag}")
    
    plt.subplot(3,1,1)
    plt.plot(hw_v[:,0])
    plt.title('hw_v')
    
    plt.subplot(3,1,2)
    sw_output_path = download_dir + "/soft_data"
    sw_v     = np.load(sw_output_path+"/N_V.npy").astype(np.float32)
    plt.plot(sw_v[:,0])
    plt.title('sw_v')
  
    plt.subplot(3,1,3)
    sw_output_path = download_dir + "/soft_data"
    diff     = np.abs(hw_v[:,0]-sw_v[:,0])
    plt.plot(diff[:])
    plt.title('diff')
    
    plt.tight_layout()    
    plt.savefig("./42_20000.png", dpi=300)
    