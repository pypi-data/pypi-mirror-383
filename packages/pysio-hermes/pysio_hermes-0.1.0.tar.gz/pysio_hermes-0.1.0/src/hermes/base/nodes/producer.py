############
#
# Copyright (c) 2024 Maxim Yudayev and KU Leuven eMedia Lab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Created 2024-2025 for the KU Leuven AidWear, AidFOG, and RevalExo projects
# by Maxim Yudayev [https://yudayev.com].
#
# ############

from abc import abstractmethod
import threading
import zmq
import math

from hermes.utils.msgpack_utils import serialize
from hermes.utils.dict_utils import *
from hermes.utils.zmq_utils import *

from hermes.base.stream import Stream
from hermes.base.storage import Storage
from hermes.base.delay_estimator import DelayEstimator
from hermes.base.nodes import Node
from hermes.base.nodes.producer_interface import ProducerInterface


############################################################
############################################################
# An abstract class to interface with a particular sensor.
#   i.e. a superclass for DOTs, Pupil Core, or Camera class.
############################################################
############################################################
class Producer(ProducerInterface, Node):
  def __init__(self,
               host_ip: str,
               stream_out_spec: dict,
               logging_spec: dict,
               sampling_rate_hz: float = float('nan'),
               port_pub: str = PORT_BACKEND,
               port_sync: str = PORT_SYNC_HOST,
               port_killsig: str = PORT_KILL,
               transmit_delay_sample_period_s: float = float('nan')) -> None:
    super().__init__(host_ip=host_ip,
                     port_sync=port_sync,
                     port_killsig=port_killsig)
    self._sampling_rate_hz = sampling_rate_hz
    self._sampling_period = 1/sampling_rate_hz
    self._port_pub = port_pub
    self._is_continue_capture = True
    self._transmit_delay_sample_period_s = transmit_delay_sample_period_s
    self._publish_fn = lambda tag, **kwargs: None

    # Data structure for keeping track of data
    self._stream: Stream = self.create_stream(stream_out_spec)

    # Create the DataLogger object
    self._logger = Storage(self._log_source_tag(), **logging_spec)

    # Launch datalogging thread with reference to the Stream object.
    self._logger_thread = threading.Thread(target=self._logger, args=(OrderedDict([(self._log_source_tag(), self._stream)]),))
    self._logger_thread.start()

    # Conditional creation of the transmission delay estimate thread.
    if not math.isnan(self._transmit_delay_sample_period_s):
      self._delay_estimator = DelayEstimator(self._transmit_delay_sample_period_s)
      self._delay_thread = threading.Thread(target=self._delay_estimator, 
                                            kwargs={
                                              'ping_fn': self._ping_device,
                                              'publish_fn': lambda time_s, delay_s: 
                                                self._publish(tag="%s.connection"%self._log_source_tag(),
                                                              time_s=time_s,
                                                              data={"%s-connection"%self._log_source_tag(): {
                                                                'transmission_delay': delay_s
                                                              }})
                                            })
      self._delay_thread.start()


  # Common method to save and publish the captured sample
  # NOTE: best to deal with data structure (threading primitives) AFTER handing off packet to ZeroMQ.
  #   That way network thread can alrady start processing the packet.
  def _publish(self, tag: str, **kwargs) -> None:
    self._publish_fn(tag, **kwargs)


  # Initialize backend parameters specific to Producer.
  def _initialize(self):
    super()._initialize()
    # Socket to publish sensor data and log
    self._pub: zmq.SyncSocket = self._ctx.socket(zmq.PUB)
    self._pub.connect("tcp://%s:%s" % (DNS_LOCALHOST, self._port_pub))
    self._connect()


  # Launch data streaming from the device.
  def _activate_data_poller(self) -> None:
    self._poller.register(self._pub, zmq.POLLOUT)

  
  # Process custom event first, then Node generic (killsig).
  def _on_poll(self, poll_res):
    if self._pub in poll_res[0]:
      self._process_data()
    super()._on_poll(poll_res)


  def _on_sync_complete(self) -> None:
    self._publish_fn = self._store_and_broadcast
    self._keep_samples()


  def _store_and_broadcast(self, tag: str, **kwargs) -> None:
    # Get serialized object to send over ZeroMQ.
    msg = serialize(**kwargs)
    # Send the data packet on the PUB socket.
    self._pub.send_multipart([tag.encode('utf-8'), msg])
    # Store the captured data into the data structure.
    self._stream.append_data(**kwargs)


  def _trigger_stop(self):
    self._is_continue_capture = False
    self._stop_new_data()


  # Send 'END' empty packet and label Node as done to safely finish and exit the process and its threads.
  def _send_end_packet(self) -> None:
    self._pub.send_multipart([("%s.data" % self._log_source_tag()).encode('utf-8'), CMD_END.encode('utf-8')])
    self._is_done = True


  # Cleanup sensor specific resources, then Producer generics, then Node generics.
  @abstractmethod
  def _cleanup(self) -> None:
    # Indicate to Logger to wrap up and exit.
    self._logger.cleanup()
    if not math.isnan(self._transmit_delay_sample_period_s):
      self._delay_estimator.cleanup()
    # Before closing the PUB socket, wait for the 'BYE' signal from the Broker.
    self._sync.send_multipart([self._log_source_tag().encode('utf-8'), CMD_EXIT.encode('utf-8')]) 
    host, cmd = self._sync.recv_multipart() # no need to read contents of the message.
    print("%s received %s from %s." % (self._log_source_tag(),
                                       cmd.decode('utf-8'),
                                       host.decode('utf-8')),
                                       flush=True)
    self._pub.close()
    # Join on the logging background thread last, so that all things can finish in parallel.
    self._logger_thread.join()
    if not math.isnan(self._transmit_delay_sample_period_s):
      self._delay_thread.join()
    super()._cleanup()
