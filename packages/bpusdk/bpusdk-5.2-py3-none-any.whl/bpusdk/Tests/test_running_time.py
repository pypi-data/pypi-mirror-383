import time
import warnings
import brainpy.math as bm
import numpy as np
from loguru import logger
import argparse
import os 
import sys

current_path = os.getcwd()
sys.path.insert(0, current_path)
from bpusdk.Models.neuron4EIModel import EINet
from bpusdk.BrainpyLib.lb1_SNN import ASIC_SNN
from bpusdk.BrainpyLib.lb2_SNN import lb2_SNN

warnings.filterwarnings("ignore")

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', type=str, default='LYRA2', help='LYRAP, LYRA1 or LYRA2')
    parser.add_argument('--config_dir', default='./HardwareConfig/Config_28nm_Base1_Split1.yaml', help='hardware configuration path')
    parser.add_argument('--neuronType', type=str, default='Izhikevich', help='LIF, Izhikevich, or HH')
    parser.add_argument('--neuronScope', type=int, default=16, help='neuron scope (k)')
    parser.add_argument('--synapseFactor', type=int, default=5, help='synapse factor')
    parser.add_argument('--precision', type=str, default='fp32', help='simulation precision, fp32, fp16 or int8')
    parser.add_argument('--neuronFactor', type=float, default=0.5, help='factor of different neurons')
    parser.add_argument('--step', type=int, default=100, help='simulation time step')
    parser.add_argument('--seed', type=int, default=42, help='random seed')
    parser.add_argument('--fanOut', type=int, default=5, help='fanOut')
    parser.add_argument('--groupSize', type=int, default=8, help='groupSize')
    parser.add_argument('--download_dir', default='./download/ei_data_asic', help='download path')
    parser.add_argument('--upload_dir', default='./upload/ei_data_asic', help='upload path')
    opt = parser.parse_args()
    opt.download_dir = rf'../download/ei_data_{opt.neuronScope}k_asic'
    opt.upload_dir = rf'../upload/ei_sim_{opt.neuronScope}k_asic'
    
    return opt

def test(opt):
    label_list = []
    time_list = []
    
    np.random.seed(opt.seed)
    bm.random.seed(opt.seed)
    total_num = opt.neuronScope * 1024
    connect_prob = opt.synapseFactor / total_num
    ex_num = int(total_num * opt.neuronFactor)
    ih_num = int(total_num * (1 - opt.neuronFactor))
    download_dir = opt.download_dir
    upload_dir = opt.upload_dir
    
    t0 = time.time()
    net = EINet(ex_num, ih_num, connect_prob, method='exp_auto', 
                allow_multi_conn=True, neuron_type=opt.neuronType)
    t1 = time.time()
    logger.info('Initial Brainpy Network. Elapsed: %.2f s\n' % (t1-t0))  # 输出
    label_list.append("Init Brainpy")
    time_list.append(t1-t0)

    nStep = opt.step
    inpI = 0.                                    # Constant current stimuli injected to all neurons during all steps 
    inpS = np.zeros((nStep, total_num))           # No spike stimuli 
    config_dir = opt.config_dir
    
    if opt.device == 'LYRA1':
        bpuset = ASIC_SNN(net, inpS, inpI, config_file=config_dir)
        bpuset.gen_bin_data(download_dir)    
        # mode 0,1,2 = no file saved, save spike, save all
        bpuset.deploy(download_dir, upload_dir)
        bpuset.simu(nStep)
        
    elif opt.device == 'LYRA2':
        bpuset = lb2_SNN(net, inpS, inpI, config_file=config_dir)
        bpuset.gen_bin_data(download_dir)
        deploy = deploy_28nm(download_dir, upload_dir)
        deploy.run(step=20,reset=True)


if __name__ == "__main__":
    opt = parse_opt()
    test(opt)
