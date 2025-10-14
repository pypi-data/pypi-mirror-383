from brainpy._src.dynold.synapses.base import _SynSTP
from brainpy._src.dnn import linear
from brainpy._src.dyn import synapses
from brainpy._src.integrators import odeint
from brainpy._src.initialize import Initializer, variable_
from brainpy.types import ArrayType, Shape
from brainpy.synapses import Exponential

import jax.numpy as jnp
from typing import Union, Optional, Callable
import brainpy.math as bm
import brainpy as bp
import numpy as np
import random
import logging
from pathlib import Path
import jax

from bpusdk.BrainpyLib.BrainpyBase import BrainpyBase

class LifRef(bp.NeuGroupNS):
    def __init__(self, size: Shape, V_rest : float = 0., V_th: float = 1., V_reset: float = 0., leaky_input: bool = False,
               tau: float = 2., spike_fun=bm.surrogate.arctan, mode=None, reset_mode='soft', tau_ref=None, data_type = 'int8'):
        super().__init__(mode=mode, size = size)

        self.reset_mode = bp.check.is_string(reset_mode, candidates=['hard', 'soft'])
        self.V_th = bp.check.is_float(V_th)
        self.V_reset = bp.check.is_float(V_reset)
        self.V_rest = bp.check.is_float(V_rest)
        self.spike_fun = bp.check.is_callable(spike_fun)
        self.tau = bp.check.is_float(tau)
        self.tau_ref = tau_ref
        self.leaky_input = leaky_input
        self.data_type = data_type
        self.R = 1.0

        # variables
        self.V = bm.Variable(jnp.zeros((1,) + size, dtype=bm.float_), batch_axis=0, dtype = bm.float32)
        self.input = bm.Variable(jnp.zeros_like(self.V), batch_axis=0, dtype = bm.float64)
        self.spike = bm.Variable(jnp.zeros(size), batch_axis=0, dtype = bm.float32)
        self.num  = size[0]
        self.count_down = np.zeros(size[0])

        self.integral = odeint(method='exp_auto', f=self.derivative)

    def derivative(self, V, t, I_ext):
        return (-V + self.V_rest + self.R * I_ext) / self.tau

    def reset_state(self, batch_size):
        self.V.value = jnp.zeros((batch_size,) + self.size, dtype=bm.float_)

    def clear_input(self):
        self.input.value = jnp.zeros_like(self.input.value)

    def update(self, x):
        #global iStep
        self.count_down -= 1
        self.count_down = np.clip(self.count_down,0,self.tau_ref)
        self.input += (x)

        # Update V
        # V = V + (2 * V + I_spike + I_x) / tau
        leaky_mem = (1 + 1/self.tau)
        quan_mem = leaky_mem * self.V

        leaky_input = 1 / self.tau
        quan_input = (leaky_input * self.input)

        V = quan_mem + quan_input

        # Reset wst to tRef
        ii = np.where(self.count_down != 0)
        V[0,ii] = self.V_reset
        spike =  bm.Variable((V - self.V_th) > 0)
        #spike = self.spike_fun(V - self.v_threshold)
        self.spike.value = spike[0].astype("float32")
        self.count_down += self.spike.value*self.tau_ref

        # Reset wst to spike
        # V = V_reset * spike + (1 - spike) * V
        self.V.value = (bm.ones_like(self.V.value) * self.V_reset * self.spike + (1 - self.spike) * V).astype(jnp.float32)
        self.clear_input()
        return self.spike

    def __call__(self, x):
      return self.update(x)

class Exponentials(Exponential):
  def __init__(
      self,
      pre,
      post,
      conn,
      output,
      stp: Optional[_SynSTP] = None,
      comp_method: str = 'sparse',
      g_max: Union[float, ArrayType, Initializer, Callable] = 1.,
      delay_step: Union[int, ArrayType, Initializer, Callable] = None,
      tau: Union[float, ArrayType] = 8.0,
      method: str = 'exp_auto',

      # other parameters
      name: str = None,
      mode: bm.Mode = None,
      stop_spike_gradient: bool = False,
  ):
    super(Exponential, self).__init__(pre=pre,
                                      post=post,
                                      conn=conn,
                                      output=output,
                                      stp=stp,
                                      name=name,
                                      mode=mode)
    self.comp_method = comp_method
    self.tau = tau
    if bm.size(self.tau) != 1:
      raise ValueError(f'"tau" must be a scalar or a tensor with size of 1. But we got {self.tau}')

    # connections and weights
    self.g_max, self.conn_mask = self._init_weights(g_max, comp_method, sparse_data='csr')
    #self.conn_mask = (np.load("W:/int8/post_list.npy"), np.load("W:/int8/pre_list.npy"))

    # variables
    self.g_low = variable_(bm.zeros, self.post.num, self.mode)    # 这里self.post为输出层神经元
    self.delay_step = self.register_delay(f"{self.pre.name}.spike", delay_step, self.pre.spike)   # 得到前一层神经元的脉冲延迟，self.pre为输入层
    self.comm = linear.EventCSRLinear(conn, g_max)
    self.syn = synapses.Expon(post.varshape, tau=tau, method=method)
  def reset_state(self, batch_size=None):
    self.g_low.value = variable_(bm.zeros, self.post.num, batch_size)
    self.output.reset_state(batch_size)
    if self.stp is not None: self.stp.reset_state(batch_size)

  def update(self,  pre_spike=None):
    global iStep
    # Get delays
    if pre_spike is None:
      pre_spike = self.get_delay_data(f"{self.pre.name}.spike", self.delay_step)
    else:
      pre_spike += self.get_delay_data(f"{self.pre.name}.spike", self.delay_step)
    pre_spike = bm.as_jax(pre_spike)

    # update sub-components
    self.output.update() # 这里的self.out为synout，synout的父类会自动调用filter函数

    # 正常的脉冲累计
    if self.comp_method == 'sparse':
        f = lambda s: bm.event.csrmv(self.g_max, self.conn_mask[0], self.conn_mask[1], s,
          shape=(self.pre.num, self.post.num),
          transpose=True
        )
        post_vs = f(pre_spike)

    self.post_vs = post_vs
    wcc = bm.exp(- 1 / self.tau)
    wcc = 1
    # g = g * exp(-1/tau) + post_vs
    self.g_low.value = ((wcc*self.g_low.value + post_vs)).astype(jnp.float32)

    # output
    self.output(self.g_low.value)
    return self.g_low.value

class ENet_V3(bp.Network):
    def __init__(self, num_exc, pre_list, post_list,method='exp_auto', **kwargs):
        super(ENet_V3, self).__init__(**kwargs)
        self.initState = bm.random.DEFAULT.value
        self.neuron_scale = [num_exc]

        # 导入神经元数目
        self.num_exc = num_exc
        pre_list = np.array(pre_list)
        post_list = np.array(post_list)

        # 初始化读取变量
        sizeE = (num_exc, )
        E = LifRef(size=sizeE, V_rest=0., V_th=10., V_reset=0., tau=0.1, tau_ref=5.)

        # synapses
        E_pars = dict(output=bp.synouts.CUBA(), g_max=1, tau=1.)
        conn = bp.conn.IJConn(i=pre_list, j=post_list)
        #conn2 = bp.conn.FixedProb(prob=0.0001, allow_multi_conn=True)
        conn = conn(pre_size=self.num_exc, post_size=self.num_exc)
        self.E2E = Exponentials(E, E, conn, **E_pars, method=method)
        self.E = E
        self.neuron_scale = 1.0

    def create_input_I(self,x):
        input_I = np.zeros((1,self.num_exc))
        nNeuron_in_tile = 16*1024*2*4
        nTile = int(np.ceil(self.num_exc/nNeuron_in_tile))
        for iTile in range(nTile):
            iStart = iTile*nNeuron_in_tile+15*8*1024
            iEnd = iTile*nNeuron_in_tile+16*8*1024
            input_I[0,iStart:iEnd] += x
        return input_I

    def run(self, spike_I, step, download_dir):
        download_dir = Path(download_dir)
        download_dir.mkdir(exist_ok=True)

        (download_dir / 'soft_data' ).mkdir(exist_ok=True)
        (download_dir / 'soft_data'/'spike' ).mkdir(exist_ok=True)
        (download_dir / 'soft_data'/'mem' ).mkdir(exist_ok=True)
        (download_dir / 'soft_data'/'all' ).mkdir(exist_ok=True)

        global iStep
        V_list = []
        spike_list = []
        g_E2E_list = []
        for iStep in range(step):
            input_I = self.create_input_I(1)
            if iStep == 0:
                g = self.E2E(spike_I[iStep])
            else:
                g = self.E2E()
            self.E.input += input_I
            #self.E.input += g
            self.E(bm.zeros_like(self.E.input))

            np.save(download_dir / f"soft_data/spike/E_{str(iStep).zfill(3)}_spike.npy", self.E.spike.value)
            np.save(download_dir / f"soft_data/mem/E_{str(iStep).zfill(3)}_V.npy", self.E.V.value)
            if iStep % 10 == 0:
                logging.info(f"The {str(iStep).zfill(3)}-th Epoch Over")

            V_list.append(self.E.V.value.copy())
            spike_list.append(self.E.spike.copy())
            g_E2E_list.append(g.copy())

        V_list = np.array(V_list).reshape(step,self.num_exc)
        spike_list = np.array(spike_list)
        g_E2E_list = np.array(g_E2E_list)
        np.save(download_dir / f"soft_data/all/N_V.npy", V_list)
        np.save(download_dir / f"soft_data/all/N_spike.npy",spike_list)
        np.save(download_dir / f"soft_data/all/E2E_g.npy",g_E2E_list)
        
        for i in range(iStep):
            nStep = np.sum(spike_list[i,:])
            print(f"step {i},nSpike {int(nStep)}")
