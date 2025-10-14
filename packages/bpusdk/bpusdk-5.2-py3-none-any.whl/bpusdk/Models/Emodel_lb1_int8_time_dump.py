from brainpy._src.integrators import odeint
from typing import Union, Callable, Optional, Sequence
from brainpy.synapses import Exponential
from brainpy.types import ArrayType
from brainpy._src.dynsys import DynamicalSystem
from brainpy._src.dyn.base import SynDyn
from brainpy._src.mixin import AlignPost
from brainpy._src.context import share
from brainpy._src.dyn.neurons import lif
from brainpy.check import is_initializer
from brainpy._src.integrators import odeint, sdeint, JointEq
from functools import partial

import warnings
import brainpy as bp
import numpy as np
import brainpy.math as bm
from typing import Callable
from pathlib import Path
import pickle
from bpusdk.BrainpyLib.BrainpyBase import BrainpyBase
import time
from brainpy.types import Shape, ArrayType, Sharding
from typing import Union, Callable, Optional, Any, Sequence
from brainpy._src.initialize import ZeroInit, OneInit, noise as init_noise

warnings.filterwarnings('ignore')

def createConn(nNeuron,fanOut,groupSize):
    nGroup = int(np.ceil(nNeuron/groupSize)) #last group may have a different size
    group_pre_list = list(np.arange(nGroup))
    group_pre_list = [item for item in group_pre_list for _ in range(fanOut)]
   
    pre_list = []
    post_list = []
    
    for ipre,pre in enumerate(group_pre_list):
        ipre = ipre%fanOut
        if pre >= nGroup-2:
            tmp_pre = np.arange(pre*groupSize,pre*groupSize+groupSize)
            tmp_post = [pre*groupSize+groupSize-1024+ipre]*groupSize
        elif pre == 0:
            tmp_pre = np.arange(pre*groupSize,pre*groupSize+groupSize)
            tmp_post = [pre*groupSize+groupSize+1024+ipre]*groupSize
        else:
            tmp_pre = np.arange(pre*groupSize,pre*groupSize+groupSize)
            tmp_post = [pre*groupSize+groupSize+ipre]*groupSize
        pre_list.extend(tmp_pre)
        post_list.extend(tmp_post)
    # np.save("pre_list",pre_list)
    # np.save("post_list",post_list)
    return np.array([pre_list,post_list])
  
# eqvivalent to bp.dyn.LifRef
class LifRef(lif.LifRefLTC):
  def __init__(
      self,
      size: Shape,
      sharding: Optional[Sharding] = None,
      keep_size: bool = False,
      mode: Optional[bm.Mode] = None,
      spk_fun: Callable = bm.surrogate.InvSquareGrad(),
      spk_dtype: Any = None,
      detach_spk: bool = False,
      spk_reset: str = 'soft',
      method: str = 'exp_auto',
      name: Optional[str] = None,
      init_var: bool = True,
      scaling: Optional[bm.Scaling] = None,

      # old neuron parameter
      V_rest: Union[float, ArrayType, Callable] = 0.,
      V_reset: Union[float, ArrayType, Callable] = -5.,
      V_th: Union[float, ArrayType, Callable] = 20.,
      R: Union[float, ArrayType, Callable] = 1.,
      tau: Union[float, ArrayType, Callable] = 10.,
      V_initializer: Union[Callable, ArrayType] = ZeroInit(),

      # new neuron parameter
      tau_ref: Union[float, ArrayType, Callable] = 0.,
      ref_var: bool = False,

      # noise
      noise: Optional[Union[float, ArrayType, Callable]] = None):
    
    # initialization
    super().__init__(
      size=size,
      name=name,
      keep_size=keep_size,
      mode=mode,
      method=method,
      sharding=sharding,
      spk_fun=spk_fun,
      detach_spk=detach_spk,
      spk_dtype=spk_dtype,
      spk_reset=spk_reset,

      init_var=False,
      scaling=scaling,

      V_rest=V_rest,
      V_reset=V_reset,
      V_th=V_th,
      R=R,
      tau=tau,
      V_initializer=V_initializer,

      noise=noise,
    )
    
    # parameters
    self.V_rest = np.int8((self.offset_scaling(self.init_param(V_rest))))
    self.V_reset = np.int8(self.offset_scaling(self.init_param(V_reset)))
    self.V_th = np.int8(self.offset_scaling(self.init_param(V_th)))
    self.tau = np.int8(self.init_param(tau))
    self.R = np.int8(self.init_param(R))

    # initializers
    self._V_initializer = is_initializer(V_initializer)

    # noise
    self.noise = init_noise(noise, self.varshape)

    # integral
    if self.noise is not None:
      self.integral = sdeint(method=self.method, f=self.derivative, g=self.noise)
    else:
      self.integral = odeint(method=method, f=self.derivative)

    # variables
    if init_var:
      self.reset_state(self.mode)
      

    # parameters
    self.ref_var = ref_var
    self.tau_ref = self.init_param(tau_ref)

    # variables
    if init_var:
      self.reset_state(self.mode)
  
  def reset_state(self, batch_size=None, **kwargs):
    #self.V = self.offset_scaling(self.init_variable(self._V_initializer, batch_size))
    self.V = self.offset_scaling(bm.Variable(self._V_initializer(self.size),dtype=np.int8))
    self.spike = self.init_variable(partial(bm.zeros, dtype=self.spk_dtype), batch_size)
    self.t_last_spike = self.init_variable(bm.ones, batch_size)
    self.t_last_spike.fill_(-1e7)
    if self.ref_var:
      self.refractory = self.init_variable(partial(bm.zeros, dtype=bool), batch_size)
      
  def derivative(self, V, t, I):
    return (-V + self.V_rest + self.R * I) / self.tau

  def update(self, x=None):
    #self.integral = odeint(method=method, f=self.derivative,show_code=True)

    #------------LifRef(LifRefLTC)------------
    x = 0. if x is None else x
    #x = self.sum_current_inputs(self.V.value, init=x)
    #return super().update(x)

    #-----------LifRefLTC(LifLTC)-----------
    t = share.load('t')
    dt = share.load('dt')

    # integrate membrane potential
  
    #V = self.integral(self.V.value, t, x, dt) + self.sum_delta_inputs()
    
    delta = (self.V.value - self.V_rest + x) * self.tau
    delta_int8 = np.clip(delta, -128, 127)
    V = np.clip(self.V.value + delta_int8, -128, 127)
        
    # refractory
    refractory = (t - self.t_last_spike) <= self.tau_ref
    V = bm.where(refractory, self.V.value, V)

    spike = V > self.V_th
    V = bm.where(spike, self.V_reset, V)
    # if self.ref_var:
    #   self.refractory.value = bm.logical_or(refractory, spike)
    t_last_spike = bm.where(spike, t, self.t_last_spike.value)

    self.V.value = V
    self.spike.value = spike
    self.t_last_spike.value = t_last_spike
    return spike
  
#eqvivalant with bp.dyn.Expon
class ConstantExpon(SynDyn, AlignPost):
  def __init__(
      self,
      size: Union[int, Sequence[int]],
      keep_size: bool = False,
      sharding: Optional[Sequence[str]] = None,
      method: str = 'exp_auto',
      name: Optional[str] = None,
      mode: Optional[bm.Mode] = None,

      # synapse parameters
      tau: Union[float, ArrayType, Callable] = 8.0,
  ):
    super().__init__(name=name,
                     mode=mode,
                     size=size,
                     keep_size=keep_size,
                     sharding=sharding)

    # parameters
    self.tau = self.init_param(tau)

    # functionodeint
    self.integral = odeint(self.derivative, method=method,show_code=False)
    self._current = None

    self.reset_state(self.mode)

  def derivative(self, g, t):
    return -g / self.tau

  def reset_state(self, batch_or_mode=None, **kwargs):
    #self.g = self.init_variable(bm.zeros, batch_or_mode)
    self.g = bm.Variable(bm.zeros(self.size),dtype=np.int8)

  def update(self, x=None):
    #self.integral.showcode = True
    #self.g.value = self.integral(self.g.value, share['t'], share['dt'])
    self.g.value = self.g.value

    # if x is not None:
    #   self.add_current(x)
    return self.g.value

  def add_current(self, x):
    self.g.value += x

  def return_info(self):
    return self.g

class Exponential(bp.Projection): 
  def __init__(self, nNeuron, pre, post, delay, prob, g_max, tau, E, method,allow_multi_conn):
    super().__init__()
    conn = self.createConn(nNeuron,prob, pre, post,allow_multi_conn)
    self.pron = bp.dyn.FullProjAlignPost(
      pre=pre,
      delay=delay,
      # Event-driven computation
      comm=bp.dnn.EventCSRLinear(conn, g_max), 
      syn=ConstantExpon(size=post.num, tau=tau,method=method),
      out=bp.dyn.CUBA(), # COBA network
      post=post
    )

  def createConn_by_prepost(self, nNeuron, prob, pre, post, allow_multi_conn):
      pre_list_ori,post_list_ori = prob
      ii_pre = np.where(pre_list_ori<nNeuron[0]) if pre.name[-1] == '0' else np.where(pre_list_ori>=nNeuron[0])
      ii_post = np.where(post_list_ori<nNeuron[0]) if post.name[-1] == '0' else np.where(post_list_ori>=nNeuron[0])
      ii = set(ii_pre[0]) & set(ii_post[0])
      ii = np.array(list(ii))

      if len(ii) == 0:
          conn = bp.conn.FixedProb(0, pre=pre.num, post=post.num, allow_multi_conn=True) 
      
      else:
          pre_list = pre_list_ori[ii]
          offset_pre = 0 if pre.name[-1] == '0' else nNeuron[0]
          pre_list -= offset_pre

          post_list = post_list_ori[ii]
          offset_post = 0 if post.name[-1] == '0' else nNeuron[0]
          post_list -= offset_post

          conn = bp.conn.IJConn(i=pre_list, j=post_list)
          conn = conn(pre_size=pre.num, post_size=post.num)
      return conn
  
  def createConn(self, nNeuron, conn, pre, post, allow_multi_conn):
      match conn[0]:
          case 'customized':
              conn = self.createConn_by_prepost(nNeuron, conn[1], pre, post, allow_multi_conn)
          case 'FixedPreNum':
              conn = bp.conn.FixedPreNum(conn[1], pre=pre.num, post=post.num, allow_multi_conn=allow_multi_conn)
          case 'FixedPostNum':
              conn = bp.conn.FixedPostNum(conn[1], pre=pre.num, post=post.num, allow_multi_conn=allow_multi_conn)
          case 'FixedTotalNum':
              conn = bp.conn.FixedTotalNum(conn[1], pre=pre.num, post=post.num, allow_multi_conn=allow_multi_conn)
          case 'FixedProb':
              conn = bp.conn.FixedProb(conn[1], pre=pre.num, post=post.num, allow_multi_conn=allow_multi_conn)
          case 'FixedPostNum':
              conn = bp.conn.FixedPostNum(conn[1], pre=pre.num, post=post.num, allow_multi_conn=allow_multi_conn)
          case _:
              print(f"conn is of unsopported type")     
      return conn
  
  def update(self, *args, **kwargs):
    nodes = tuple(self.nodes(level=1, include_self=False).subset(DynamicalSystem).unique().values())
    if len(nodes):
      for node in nodes:
        node.update(*args, **kwargs)
    else:
      raise ValueError('Do not implement the update() function.')
  
class ENet(bp.DynamicalSystem):
    def __init__(self, ne, conn, method, allow_multi_conn=True):
        super().__init__()
        self.initState = bm.random.DEFAULT.value
        self.neuron_scale = [ne, ne]
        self.E = LifRef(ne, V_rest=0.0, V_th=10.0, V_reset=0.0, tau=1.0, tau_ref=0,
                               V_initializer=bp.init.Constant(0),method=method)

        self.E2E = Exponential(self.neuron_scale, self.E, self.E, delay=0.,
                               prob=conn, g_max=1, tau=1., E=0.,method=method,allow_multi_conn=allow_multi_conn)
        self.ne = ne

    def create_input_I(self,x):
        input_I = np.zeros((self.ne))
        nNeuron_in_tile = 16*1024*2*4
        nTile = int(np.ceil(self.ne/nNeuron_in_tile))
        for iTile in range(nTile):
            iStart = iTile*nNeuron_in_tile+15*8*1024
            iEnd = iTile*nNeuron_in_tile+16*8*1024
            input_I[iStart:iEnd] += x
        return np.int8(input_I)
    
    def update(self, inpS, inpE):
        # self.E2E.pron.refs['pre'].spike.value += inpS[:self.ne]
        self.E2E()
        self.E(inpE)
        return self.E.spike

    def dump(self,download_path,nStep,inpS=None,inpE=0,jit=False,save=True, txt=False): 
        inpS = np.zeros((nStep,self.ne)).astype(bool) if inpS == None else inpS
        V_init = np.expand_dims(self.E.V.value, axis=0)
        S_init = np.zeros((1, self.ne))
        wacc_init = np.zeros((1, self.ne))
    
        start = time.time()
        inpE = self.create_input_I(inpE)
        inpE = np.vstack([inpE] * nStep) 
        runner = bp.DSRunner(
            self, monitors=['E.spike','E.V','E2E.pron.syn.g'], jit=jit)
        _ = runner.run(inputs=[inpS, inpE])
        end = time.time()
        print(f"AVG_sim_time_per_step: {(end-start)/nStep*1000:.2f} ms")
        
        
        
        E_sps = runner.mon['E.spike']
        E_V = runner.mon['E.V']
        E2E = runner.mon['E2E.pron.syn.g']

        S = np.concatenate((S_init, E_sps), axis=0)
        V = np.concatenate((V_init, E_V), axis=0)
        #Do not need to scale as g keep constant between steps
        wacc1 = np.concatenate((wacc_init, E2E), axis=0)

        if save == True:
          download_path = f"{download_path}/soft_data"
          download_dir = Path(download_path)
          download_dir.mkdir(exist_ok=True,parents=True)
          np.save(download_dir / "N_V.npy", V)
          np.save(download_dir / "N_spike.npy", S)
          np.save(download_dir / "N_wacc1.npy", wacc1)
          
          test = BrainpyBase(self, inpE,{})
          conn_matrix = test.get_connection_matrix()
          cv = test.cv
          with open(f'{download_dir}/connection.pickle', 'wb') as handle:
              pickle.dump(conn_matrix, handle, protocol=pickle.HIGHEST_PROTOCOL)

        else:
          S = np.sum(S,axis=1)
          print(S)
        
        if txt == True:
          download_path = f"{download_path}/soft_data_txt"
          download_dir = Path(download_path)
          download_dir.mkdir(exist_ok=True,parents=True)        
          for iStep in range(nStep+1):
            np.savetxt(f"{download_path}/V_step_{iStep:03}.txt", V[iStep,:],fmt="%.6f")
            np.savetxt(f"{download_path}/S_step_{iStep:03}.txt", S[iStep,:],fmt="%.0f")

          # import matplotlib.pyplot as plt
          # plt.figure(figsize=(12, 4.5))
          # indices = np.arange(nStep)
          # ts = indices * bm.get_dt()
          # plt.subplot(121)
          # bp.visualize.raster_plot(ts, E_sps, show=False)
          # plt.subplot(122)
          # bp.visualize.raster_plot(ts, I_sps, show=True)
          # plt.savefig("tmp")
  
    def time_dump(self,download_path,nStep,inpS=None,inpE=0,jit=False,save=True, txt=False): 
        inpS = np.zeros((nStep,self.ne)).astype(bool) if inpS == None else inpS
      
        start = time.time()
        inpE = self.create_input_I(inpE)
        inpE = np.vstack([inpE] * nStep) 
        runner = bp.DSRunner(
            self, monitors=['E.spike','E.V','E2E.pron.syn.g'], jit=jit)
        _ = runner.run(inputs=[inpS, inpE])
        end = time.time()
        print(f"AVG_sim_time_per_step: {(end-start)/nStep*1000:.2f} ms")
        
        
        