import time
import warnings
import brainpy.math as bm
import numpy as np
import random
import os 
import sys

current_path = os.getcwd()
sys.path.insert(0, current_path)
from bpusdk.Models.EImodel_Izhikevich import EINet
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
    arr = np.arange(nExc+nInh) #一个参数 默认起点0，步长为1 返回一个有终点和起点的固定步长的排列
    shuffled_arr = np.random.permutation(arr)   #对arr随机排序
    data = np.vstack((arr,shuffled_arr))        #对arr和打乱后的arr在竖直方向堆叠  arr
                                                #                                shuffled——arr

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
    download_dir = "../data8/Lb2_Izhikevich_64k"
    upload_dir = "../upload8/ResLb2_Izhikevich_64k"
    nExc = 8*1024
    nInh = 8*1024
    nStep = 20

    # Gendata\
    net = gen_net(nExc,nInh) #生成神经网络
    inpI = 0.                                      
    inpS = np.zeros((nStep, nExc+nInh))#创建一个形状为 (nStep, nExc+nInh) 的二维零数组：
                           #行数 = 时间步数 nStep 列数 = 神经元总数 nExc + nInh 应该是用于数据输入
    inpS = inpS.astype(bool)    #将 NumPy 数组转换为指定的数据类型。它创建数组的新副本（除非指定 copy=False），并将所有元素转换为目标数据类型。
    bpuset = lb2_SNN(net, inpS, inpI,config={"Is_Y_First":True})
    #inps输入脉冲数据 inpI外部输入数据  config: 硬件配置字典（默认为空  mode: 运行模式（0-3）
    net.dump(download_dir,inpS,inpI,nStep,save=True,jit=False)   #在软件中跑 
    bpuset.gen_bin_data(download_dir) #为了在硬件中跑
    # bpuset.gen_hex_data(download_dir)

    # Deploy
    deploy = lb2_deploy(download_dir,upload_dir)
    sender_path = "/home/test2/work/LBII_matrix/build/LBII"
    deploy.run_from_host(nStep=nStep, sender_path=sender_path, device_id=2)
    # deploy.run_from_driver(nStep=nStep,device_id=2,dmos=False,save_ncu=1) #

    # Compare results or convert bin to npy
    check = lb2_checkRes(download_dir, upload_dir, nStep)
    check.bin2npy()
    check.npyVSnpy()  