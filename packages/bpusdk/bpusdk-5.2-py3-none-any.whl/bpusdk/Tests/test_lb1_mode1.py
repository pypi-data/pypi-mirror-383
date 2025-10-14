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
import math

warnings.filterwarnings("ignore")
random.seed(1)
bm.random.seed(42)
bm.set_dt(1.0)

# 0: other, 1: right coloum, 2: bottom right
def determinePopolationPos(iPopulation,nRow,nCol,Y_first):
    if Y_first:
        if iPopulation == nCol*nRow*16-1:
            return 2
        if (iPopulation > (nCol-1)*nRow*16) and (iPopulation%16==15):
            return 1
        else:
            return 0
    else:
        if iPopulation == nCol*nRow*16-1:
            return 2
        if (iPopulation % (nCol*16)) == nCol*16-1:
            return 1
        else:
            return 0
        
def createConn(nNeuron, nRow, nCol,Y_first):
    population_size = 1024
    nPopulation = math.ceil(nNeuron/population_size)
    nPopulation_per_tile = math.floor(4096*4/population_size) #TODO: consider different case
    res = []
    for iPopulation in range(nPopulation):
        #create intra-population connections for all populations
        local_idx = np.arange(iPopulation*population_size, (iPopulation+1)*population_size)
        #intra_pairs = np.stack((np.random.permutation(local_idx), np.random.permutation(local_idx)), axis=0)
        intra_pairs = np.stack((local_idx, np.roll(local_idx, -1)), axis=0)
        res.append(intra_pairs)

        #no inter-population connections for last population
        case = determinePopolationPos(iPopulation,nRow, nCol,Y_first)
        
        if Y_first:
            match case: # 0: other, 1: right coloum, 2: bottom right
                case 0:
                    if iPopulation%16==15:
                        iNeibor = iPopulation+(nRow*16-15)
                    else :
                        iNeibor = iPopulation+1                   
                    neighbor_idx = np.arange(iNeibor*population_size,(iNeibor+1)*population_size)
                    #inter_pairs = np.stack((np.random.permutation(local_idx), np.random.permutation(neighbor_idx)), axis=0)
                    inter_pairs = np.stack((local_idx, neighbor_idx), axis=0)
                    res.append(inter_pairs)  
                case 1:
                    iNeibor = iPopulation+16
                    neighbor_idx = np.arange(iNeibor*population_size,(iNeibor+1)*population_size)
                    #inter_pairs = np.stack((np.random.permutation(local_idx), np.random.permutation(neighbor_idx)), axis=0)
                    inter_pairs = np.stack((local_idx, neighbor_idx), axis=0)
                    res.append(inter_pairs)  
        else:    
            match case: # 0: other, 1: right coloum, 2: bottom right
                case 0:
                    iNeibor = iPopulation+1
                    neighbor_idx = np.arange(iNeibor*population_size,(iNeibor+1)*population_size)
                    #inter_pairs = np.stack((np.random.permutation(local_idx), np.random.permutation(neighbor_idx)), axis=0)
                    inter_pairs = np.stack((local_idx, neighbor_idx), axis=0)
                    
                    res.append(inter_pairs)  
                case 1:
                    iNeibor = iPopulation+nPopulation_per_tile*nCol
                    neighbor_idx = np.arange(iNeibor*population_size,(iNeibor+1)*population_size)
                    #inter_pairs = np.stack((np.random.permutation(local_idx), np.random.permutation(neighbor_idx)), axis=0)
                    inter_pairs = np.stack((local_idx, neighbor_idx), axis=0)
                    res.append(inter_pairs)  
    res = np.hstack(res)
    return res

def gen_net(nExc,nInh,nRow,nCol,Y_first):
    t0 = time.time()
    connect_prob = createConn(nExc+nInh,nRow,nCol,Y_first)
    conn = ["customized",connect_prob] 
    net = EINet(population_sizes=[nExc,nInh], conn=conn, method = "euler")
    t1 = time.time()
    print(f"{nExc+nInh//1024}k network generated in {t1-t0:.2f} seconds")
    return net

if __name__ == "__main__":
    download_dir = "../data7/LB1_192k"
    upload_dir = "../upload7/LB1_192k_new_original"
    nExc = 96*1024
    nInh = 96*1024
    nStep = 100
    nRow = 6
    nCol = 2
    Y_first = True
    
    #Gendata
    net = gen_net(nExc,nInh,nRow,nCol,Y_first)
    inpE = 100.                                      
    bpuset = lb1_SNN(net,inpE=inpE)
    net.dump(download_dir,nStep,inpE=inpE)           
    bpuset.gen_bin_data(download_dir)
    
    # Deploy
    # deploy = lb1_deploy(download_dir,upload_dir)
    # deploy.run_from_driver(nStep=nStep,device_id=10,run=False)

    check = lb1_checkRes(download_dir, upload_dir, nStep)
    check.bin2npy(v_dump=False)
    check.npyVSnpy(v_dump=False) 
