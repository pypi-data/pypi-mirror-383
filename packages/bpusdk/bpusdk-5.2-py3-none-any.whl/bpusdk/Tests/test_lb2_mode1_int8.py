import time
import warnings
import brainpy.math as bm
import numpy as np
import random
import math
from itertools import product
from tqdm import tqdm
import os
import shutil
from pathlib import Path
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
bm.set_dt(1.0)

# 0: other, 1: right coloum, 2: bottom right
def determinePopolationPos(iPopulation,nRow,nCol,Y_first):
    nPopulation_per_tile = 16*8 #128
    if Y_first:
        if iPopulation == nCol*nRow*nPopulation_per_tile-1:
            return 2
        if (iPopulation > (nCol-1)*nRow*nPopulation_per_tile) and (iPopulation%nPopulation_per_tile==(nPopulation_per_tile-1)):
            return 1
        else:
            return 0
    else:
        if iPopulation == nCol*nRow*nPopulation_per_tile-1:
            return 2
        if (iPopulation % (nCol*nPopulation_per_tile)) == nCol*nPopulation_per_tile-1:
            return 1
        else:
            return 0

# 0: other, 1: right coloum, 2: bottom right 3: top right, 4:left colum
def determineTilePos(iTile,nRow,nCol,Y_first):
    if Y_first:
        if iTile < nRow:
            return 4
        
        if iTile == (nRow*(nCol-1)):
            return 3
        
        if iTile == (nCol*nRow)-1:
            return 2
            
        if iTile > (nRow*(nCol-1)):
            return 1
        
        else:
            return 0
    else:
        if (iTile % (nCol)) == 0:
            return 4
        
        if iTile == nCol-1:
            return 3
        
        if iTile == (nCol*nRow)-1:
            return 2
            
        if (iTile % (nCol)) == nCol-1:
            return 1
        
        else:
            return 0


def createConn(nNeuron, fanOut, nRow, nCol,Y_first):
    population_size = 1024
    nPopulation_per_tile = 16*8 #128
    nPopulation = math.ceil(nNeuron/population_size)
    res = []
    for iPopulation in range(nPopulation):
        case = determinePopolationPos(iPopulation,nRow, nCol,Y_first)
        if Y_first:
            match case: # 0: other, 1: right coloum, 2: bottom right
                case 0:
                    nConn_inter = 2
                    nConn_intra = fanOut-nConn_inter
                    #cross tile
                    if iPopulation%nPopulation_per_tile==nPopulation_per_tile-1:
                        iNeibor = iPopulation+(nRow*nPopulation_per_tile-(nPopulation_per_tile-1))
                    #within same tile  
                    else:
                        iNeibor = iPopulation+1 
                case 1:
                    nConn_inter = 2
                    nConn_intra = fanOut-2*nConn_inter
                    iNeibor = iPopulation+nPopulation_per_tile 
                case 2:
                    nConn_inter = 0
                    nConn_intra = fanOut
            #inter_conn        
            if nConn_inter > 0:
                inter_pairs = gen_conn_int8_random(population_size,nConn_inter,groupSize=8)
                inter_pairs[0,:] += iPopulation*population_size
                inter_pairs[1,:] += iNeibor*population_size                       
                res.append(inter_pairs)  
            tmp_max = np.max(inter_pairs)
            if tmp_max> nNeuron:
                print(1)
            #intra_conn
            if nConn_intra > 0:           
                intra_conn = gen_conn_int8_random(population_size,nConn_intra,groupSize=8)
                intra_conn[:,:] += iPopulation*population_size              
                res.append(intra_conn)  
            tmp_max = np.max(intra_conn)
            if tmp_max> nNeuron:
                print(1)
    res = np.hstack(res)
    return res

def trans_line(x):
    result = []
    for item in range(len(x), 0, -8):
        tmp = []
        var = x[item-8:item]
        tmp.extend([var[6:8], var[4:6], var[2:4], var[0:2]])
        tmp = list(map(lambda x: int(x, 16), tmp))
        result.extend(tmp)
    return result

#return 4 char = 16b
def gethexString(rid,end):
    binary_r = format(rid, '010b')  
    binary_string = f"1{binary_r}{end}"
    hex_string = format(int(binary_string, 2), '04x') 
    return hex_string

#assume only one tile apart
def createRouter(download_dir,nRow,nCol,Y_first,hex=False):
    nPopulation_per_tile = 128
    new_dir = Path(download_dir) / "route_info" if not hex else Path(download_dir)/ "hex" / "route_info" 
    if new_dir.exists():
        shutil.rmtree(new_dir)
    
    os.makedirs(new_dir, exist_ok=True)
    zeroPadding_4 = '0000' #16b
    changeRow = '\n' if hex else ''
    for iTile in range(nCol*nRow):
        file_name = f"/tile{iTile}.bin" if not hex else f"/tile{iTile}.hex"
        outfile_path = download_dir+"/route_info"+ file_name if not hex else download_dir+ "/hex/route_info"+file_name
        case = determineTilePos(iTile,nRow,nCol,Y_first)
        match case: # 0: other, 1: right coloum, 2: bottom right 3: top right, 4:left colum
            case 0:
                element_hex = gethexString(iTile, '10000')
                row_hex = zeroPadding_4*3 + element_hex+changeRow
                data = row_hex*(nPopulation_per_tile-1)
                
                element_hex0 = gethexString(iTile, '10001')
                element_hex1 = gethexString(iTile-nRow, '10000')

                row_hex = zeroPadding_4*2 + element_hex1 + element_hex0 +changeRow
                data = row_hex + data    
            case 1:
                element_hex = gethexString(iTile, '10000')
                row_hex = zeroPadding_4*3 + element_hex+changeRow
                data = row_hex*(nPopulation_per_tile-1)


                element_hex0 = gethexString(iTile, '10100')
                element_hex1 = gethexString(iTile-nRow, '10000')
                element_hex2 = gethexString(iTile-1, '10000')                    

                row_hex = zeroPadding_4 + element_hex2 +element_hex1 + element_hex0 +changeRow
                data = row_hex + data   
            case 2:
                element_hex = gethexString(iTile, '10000')
                row_hex = zeroPadding_4*3 + element_hex+changeRow
                data = row_hex*(nPopulation_per_tile-1)

                element_hex0 = gethexString(iTile, '10000')
                element_hex1 = gethexString(iTile-nRow, '10000')
                element_hex2 = gethexString(iTile-1, '10000')

                row_hex = zeroPadding_4 + element_hex2 +element_hex1 + element_hex0 +changeRow
                data = row_hex + data    
            case 3:
                element_hex = gethexString(iTile, '10000')
                row_hex = zeroPadding_4*3 + element_hex+changeRow
                data = row_hex*(nPopulation_per_tile-1)

                element_hex0 = gethexString(iTile, '10100')
                element_hex1 = gethexString(iTile-nRow, '10000')

                row_hex = zeroPadding_4*2 +element_hex1 + element_hex0 +changeRow
                data = row_hex + data   
            case 4:
                element_hex = gethexString(iTile, '10000')
                row_hex = zeroPadding_4*3 + element_hex +changeRow
                data = row_hex*(nPopulation_per_tile-1)

                element_hex0 = gethexString(iTile, '10001')
                row_hex = zeroPadding_4*3 + element_hex0 +changeRow
                data = row_hex + data          
         
        if hex:
            lines = data.split('\n')
            lines.reverse()
            with open(outfile_path, 'a') as f_in:
                for line in lines:
                    if len(line) > 0:
                        f_in.write(line+'\n')
        else:
            data = bytearray(trans_line(data))
            with open(outfile_path, 'wb') as f_in:
                f_in.write(data)


warnings.filterwarnings("ignore")
random.seed(1)
bm.random.seed(42)
bm.set_dt(2.0)

def gen_net(nExc,nInh,fanOut,nRow,nCol,Y_first):
    t0 = time.time()
    conn = createConn(nExc+nInh,fanOut,nRow,nCol,Y_first)
    #np.save('./globalConn.npy',conn)
    print(f"globalConn saved")
    net = EINet(population_sizes=[nExc,nInh], conn=["customized",conn], method = "euler")
    t1 = time.time()
    print(f"{(nExc+nInh)//1024}k network generated in {t1-t0:.2f} seconds")
    return net
       
if __name__ == "__main__":
    # download_dir = "../data7/Lb2_mode1_b2s1_int8_1536k"
    # upload_dir = "../upload7/ResLb2_mode1_b2s1_int8_1536k"
    # nExc = 768*1024
    # nInh = 768*1024
    # nStep = 10
    # nRow = 6
    # nCol = 2
    # fanOut = 9
    # Y_first = True
    
    download_dir = "../data7/Lb2_mode1_b2s1_int8_4608k"
    upload_dir = "../upload7/ResLb2_mode1_b2s1_int8_4608k"
    nExc = 2304*1024
    nInh = 2304*1024
    nStep = 10
    nRow = 6
    nCol = 6
    fanOut = 10
    Y_first = True
        
    #Gendata
    net = gen_net(nExc,nInh,fanOut,nRow,nCol,Y_first)
    inpI = 2.                                       
    bpuset = lb2_SNN(net, inpI=inpI, mode=1,config={"nRow":nRow,"nCol":nCol,'Is_Y_First':Y_first,"Base":2,"Dtype":"int8"})
    net.dump(download_dir,nStep,inpI=inpI,save=True,jit=True)     
    bpuset.gen_bin_data(download_dir)
    res = createRouter(download_dir, nRow, nCol, Y_first, hex=False)

    deploy = lb2_deploy(download_dir,upload_dir)
    sender_path = "/home/gdiist1/work/beartic/LBII_matrix/build/LBII"
    deploy.run_from_host(nStep=nStep,sender_path=sender_path,device_id=1,run=False)
    # deploy.run_from_driver(nStep=nStep,device_id=16,dmos=False)

    # # Compare results or convert bin to npy
    check = lb2_checkRes(download_dir, upload_dir, nStep)
    # check.bin2npy()
    check.npyVSnpy() 