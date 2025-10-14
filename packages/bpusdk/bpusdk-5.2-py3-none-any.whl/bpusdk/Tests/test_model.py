import brainpy.math as bm
import numpy as np
import random
import os 
import sys
import warnings

current_path = os.getcwd()
sys.path.insert(0, current_path)
from bpusdk.Models.EImodel import EINet
# from bpusdk.Models.EImodel_basic import EINet
# from bpusdk.Models.EImodel_basic_v2 import EINet
from bpusdk.BrainpyLib.lb2_SNN import lb2_SNN
from bpusdk.BrainpyLib.Common import gen_conn 
from bpusdk.BrainpyLib.lb2_checkRes import lb2_checkRes
from bpusdk.BrainpyLib.lb2_deploy import lb2_deploy


warnings.filterwarnings("ignore")
random.seed(1)
bm.random.seed(42)
bm.set_dt(1.0)


import brainpy.math as bm
import brainpy as bp
import numpy as np
import random

class SNN(bp.DynamicalSystem):
    def __init__(self, neu_num, method='euler'):
        super().__init__()
        self.initState = bm.random.DEFAULT.value
        self.neuron_scale = [neu_num]
        self.V_init = -68.

        # 簇发放(bursting)
        self.neu = bp.dyn.ExpIFRefLTC(neu_num, 
                               V_initializer=bm.random.randn(neu_num) + self.V_init, method=method)

        # TODO！实现适应性指数整合发放（AdExIF）模型的适应（adaptation）、起始簇发放（initial bursting）、瞬时锋发放（transient spiking）、激发锋发放（tonic spiking）、延迟发放（delayed spiking）


    def update(self, x):
        self.neu(x)
        return self.neu.spike
    

random.seed(1)
bm.random.seed(42)
bm.set_dt(0.1)

download_dir = "../data7/Lb2_16k_ori"
upload_dir = "../upload7/ResLb2_16k_ori"
neu_num = 6
nStep = 600

net = SNN(neu_num)
inpI = 65.
inpS = np.zeros((nStep, neu_num))
bpuset = lb2_SNN(net, inpS, inpI)
bpuset.gen_bin_data(download_dir)


  