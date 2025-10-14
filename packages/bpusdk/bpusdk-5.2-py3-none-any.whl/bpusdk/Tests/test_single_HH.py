import time
import warnings
import brainpy.math as bm
import numpy as np
import random
import os 
import sys
from pathlib import Path
import brainpy as bp
import pickle

current_path = os.getcwd()
sys.path.insert(0, current_path)
from bpusdk.BrainpyLib.lb2_SNN import lb2_SNN
from bpusdk.BrainpyLib.lb2_checkRes import lb2_checkRes
from bpusdk.BrainpyLib.lb2_deploy import lb2_deploy
from bpusdk.BrainpyLib.BrainpyBase import BrainpyBase

warnings.filterwarnings("ignore")
random.seed(1)
bm.random.seed(42)
bm.set_dt(0.02)

class HHNeuron(bp.DynamicalSystem):
    """HH神经元模型 - 支持多个独立的HH神经元"""
    def __init__(self, size, V_init=None, m_init=None, h_init=None, n_init=None):
        super().__init__()
        self.neuron_scale = [size, 0]  # [兴奋性神经元数量, 抑制性神经元数量]
        self.size = size
        self.initState = bm.random.DEFAULT.value
        
        # 设置初始值，如果未提供则使用默认值
        if V_init is None:
            V_initializer = bp.init.Constant(-60)
        else:
            if np.isscalar(V_init):
                V_initializer = bp.init.Constant(V_init)
            else:
                V_initializer = bp.init.Normal(V_init.mean(), V_init.std()) if len(V_init) > 1 else bp.init.Constant(V_init[0])
                
        if m_init is None:
            m_initializer = bp.init.Constant(0.05)
        else:
            if np.isscalar(m_init):
                m_initializer = bp.init.Constant(m_init)
            else:
                m_initializer = bp.init.Normal(m_init.mean(), m_init.std()) if len(m_init) > 1 else bp.init.Constant(m_init[0])
                
        if h_init is None:
            h_initializer = bp.init.Constant(0.6)
        else:
            if np.isscalar(h_init):
                h_initializer = bp.init.Constant(h_init)
            else:
                h_initializer = bp.init.Normal(h_init.mean(), h_init.std()) if len(h_init) > 1 else bp.init.Constant(h_init[0])
                
        if n_init is None:
            n_initializer = bp.init.Constant(0.3)
        else:
            if np.isscalar(n_init):
                n_initializer = bp.init.Constant(n_init)
            else:
                n_initializer = bp.init.Normal(n_init.mean(), n_init.std()) if len(n_init) > 1 else bp.init.Constant(n_init[0])

        # 创建HH神经元
        self.neuron = bp.dyn.HH(size, 
                               V_th=-10.,  # 动作电位阈值
                               V_initializer=V_initializer,
                               m_initializer=m_initializer,
                               h_initializer=h_initializer,
                               n_initializer=n_initializer)

    def update(self, inpS=None, inpI=0.):
        """更新神经元状态"""
        self.neuron(inpI)

    def dump(self, download_path, inpS, inpI, nStep, save=True, jit=True, txt=False):
        """保存软件仿真结果"""
        # 初始化状态
        S_init = np.zeros((1, self.neuron_scale[0]))
        # 对于HH神经元，初始V值应该是neuron.V.value
        V_init = np.array([self.neuron.V.value]) if np.isscalar(self.neuron.V.value) else self.neuron.V.value
        V_init = V_init.reshape(1, -1)  # 确保是二维数组
        
        runner = bp.DSRunner(self, monitors=['neuron.spike', 'neuron.V'], jit=jit)
        _ = runner.run(inputs=(inpS, bm.ones(nStep) * inpI))
        spikes = runner.mon['neuron.spike']
        voltages = runner.mon['neuron.V']
        
        S = np.vstack((S_init, spikes))
        V = np.vstack((V_init, voltages))
        
        if save:
            download_path = f"{download_path}/soft_data"
            download_dir = Path(download_path)
            download_dir.mkdir(exist_ok=True, parents=True)
            np.save(download_dir / "N_V.npy", V)
            np.save(download_dir / "N_spike.npy", S)
            
            # 保存连接矩阵（对于独立神经元，连接矩阵为空）
            test = BrainpyBase(self, inpI, {})
            conn_matrix = test.get_connection_matrix()
            with open(f'{download_dir}/connection.pickle', 'wb') as handle:
                pickle.dump(conn_matrix, handle, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            S = np.sum(S, axis=1)
            print("Spikes per step:", S)
        
        if txt:
            download_path = f"{download_path}/soft_data_txt"
            download_dir = Path(download_path)
            download_dir.mkdir(exist_ok=True, parents=True)
            for iStep in range(nStep+1):
                np.savetxt(f"{download_path}/V_step_{iStep:03}.txt", V[iStep, :], fmt="%.6f")
                np.savetxt(f"{download_path}/S_step_{iStep:03}.txt", S[iStep, :], fmt="%.0f")

def main():
    download_dir = "../data8/Lb2_single_HH_neuron"
    upload_dir = "../upload8/ResLb2_single_HH_neuron"
    n_neurons = 50  
    nStep = 20
    inpI = 00.  
    inpS = np.zeros((nStep, n_neurons))
    inpS = inpS.astype(bool)
 
    V_init = np.random.uniform(-70, -50, n_neurons)  
    m_init = np.random.uniform(0, 0.1, n_neurons)   
    h_init = np.random.uniform(0.5, 0.7, n_neurons) 
    n_init = np.random.uniform(0.2, 0.4, n_neurons)  
    single_HH = HHNeuron(n_neurons, V_init=V_init, m_init=m_init, h_init=h_init, n_init=n_init)
    
    # 创建空连接数据（无连接）
    arr = np.arange(n_neurons)
    # 创建一个空的连接矩阵，表示神经元之间没有连接
    empty_conn = np.array([[], []])  # 空的连接
    

    bpuset = lb2_SNN(single_HH, inpS, inpI)
    single_HH.dump(download_dir, inpS, inpI, nStep, save=True, jit=True)
    bpuset.gen_bin_data(download_dir)
    sender_path = "/home/test2/work/LBII_matrix/build/LBII"
    deploy = lb2_deploy(download_dir, upload_dir)
    deploy.run_from_host(nStep=nStep, sender_path=sender_path, device_id=8)
    
    # 比较结果
    check = lb2_checkRes(download_dir, upload_dir, nStep)
    check.bin2npy()
    check.npyVSnpy()

if __name__ == "__main__":
    main()