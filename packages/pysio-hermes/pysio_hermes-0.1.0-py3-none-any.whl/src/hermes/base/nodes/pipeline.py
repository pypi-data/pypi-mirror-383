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

from hermes.utils.node_utils import search_node_class
from hermes.utils.msgpack_utils import deserialize, serialize
from hermes.utils.dict_utils import *
from hermes.utils.zmq_utils import *

from hermes.base.stream import Stream
from hermes.base.storage import Storage
from hermes.base.nodes import Node
from hermes.base.nodes.pipeline_interface import PipelineInterface
from hermes.base.nodes.producer_interface import ProducerInterface


##############################################################
##############################################################
# An abstract class to interface with a data-producing worker.
#   i.e. a superclass for AI worker, controllable GUI, etc.
##############################################################
##############################################################
class Pipeline(PipelineInterface, Node):
  def __init__(self,
               host_ip: str,
               stream_out_spec: dict,
               stream_in_specs: list[dict],
               logging_spec: dict,
               port_pub: str = PORT_BACKEND,
               port_sub: str = PORT_FRONTEND,
               port_sync: str = PORT_SYNC_HOST,
               port_killsig: str = PORT_KILL) -> None:
    super().__init__(host_ip=host_ip,
                     port_sync=port_sync,
                     port_killsig=port_killsig)
    self._port_pub = port_pub
    self._port_sub = port_sub
    self._is_continue_produce = True
    self._is_more_data_in = True
    self._publish_fn = lambda tag, **kwargs: None

    # Data structure for keeping track of the Pipeline's output data.
    self._out_stream: Stream = self.create_stream(stream_out_spec)

    # Instantiate all desired Streams that the Pipeline will process.
    self._in_streams: OrderedDict[str, Stream] = OrderedDict()
    self._poll_data_fn = self._poll_data_packets
    self._is_producer_ended: OrderedDict[str, bool] = OrderedDict()

    for stream_spec in stream_in_specs:
      module_name: str = stream_spec['package']
      class_name: str = stream_spec['stream_name']
      specs: dict = stream_spec['settings']
      # Create the stream datastructure.
      class_type: type[ProducerInterface] | type[PipelineInterface] = search_node_class(module_name, class_name) # type: ignore
      class_object: Stream = class_type.create_stream(specs)
      self._in_streams.setdefault(class_type._log_source_tag(), class_object)
      self._is_producer_ended.setdefault(class_type._log_source_tag(), False)

    # Create the Logger object.
    self._logger = Storage(self._log_source_tag(), **logging_spec)

    # Launch datalogging thread with reference to the Stream objects, to save Pipeline's outputs and inputs.
    self._logger_thread = threading.Thread(target=self._logger,
                                           args=(OrderedDict([
                                             (self._log_source_tag(), self._out_stream),
                                             *list(self._in_streams.items())
                                             ]),))
    self._logger_thread.start()


  # Initialize backend parameters specific to Pipeline.
  def _initialize(self):
    super()._initialize()

    # Socket to publish processed data and log.
    self._pub: zmq.SyncSocket = self._ctx.socket(zmq.PUB)
    self._pub.connect("tcp://%s:%s" % (DNS_LOCALHOST, self._port_pub))

    # Socket to subscribe to other Producers.
    self._sub: zmq.SyncSocket = self._ctx.socket(zmq.SUB)
    self._sub.connect("tcp://%s:%s" % (DNS_LOCALHOST, self._port_sub))
    
    # Subscribe to topics for each mentioned local and remote streamer
    for tag in self._in_streams.keys():
      self._sub.subscribe(tag)


  # Launch data receiving and result producing.
  def _activate_data_poller(self) -> None:
    self._poller.register(self._sub, zmq.POLLIN)


  # Process custom event first, then Node generic (killsig).
  def _on_poll(self, poll_res):
    if self._sub in poll_res[0]:
      # Receiving a modality packet, process until all data sources sent 'END' packet.
      self._poll_data_fn()
    super()._on_poll(poll_res)


  def _on_sync_complete(self) -> None:
    self._publish_fn = self._store_and_broadcast


  # Gets called every time one of the requestes modalities produced new data.
  # In normal operation mode, all messages are 2-part.
  def _poll_data_packets(self) -> None:
    topic, payload = self._sub.recv_multipart()
    msg = deserialize(payload)
    topic_tree: list[str] = topic.decode('utf-8').split('.')
    self._in_streams[topic_tree[0]].append_data(**msg)
    self._process_data(topic=topic_tree[0], msg=msg)


  # When system triggered a safe exit, Pipeline gets a mix of normal 2-part messages
  #   and 3-part 'END' message from each Producer that safely exited.
  #   It's more efficient to dynamically switch the callback instead of checking every message.
  def _poll_ending_data_packets(self) -> None:
    # Process until all data sources sent 'END' packet.
    topic, payload = self._sub.recv_multipart()
    # 'END' empty packet from a Producer.
    if CMD_END.encode('utf-8') in payload:
      topic_tree: list[str] = topic.decode('utf-8').split('.')
      self._is_producer_ended[topic_tree[0]] = True
      if all(list(self._is_producer_ended.values())):
        self._is_more_data_in = False
        # If triggered to stop and no more available data, send empty 'END' packet and join.
        # not self._is_more_data_in and not self._is_continue_produce
        self._send_end_packet()
    # Regular data packets.
    else:
      msg = deserialize(payload)
      topic_tree: list[str] = topic.decode('utf-8').split('.')
      self._in_streams[topic_tree[0]].append_data(**msg)
      self._process_data(topic=topic_tree[0], msg=msg)


  def _publish(self, tag: str, **kwargs) -> None:
    self._publish_fn(tag, **kwargs)


  # Common method to save and publish the captured sample
  # NOTE: best to deal with data structure (threading primitives) AFTER handing off packet to ZeroMQ
  def _store_and_broadcast(self, tag: str, **kwargs) -> None:
    # Get serialized object to send over ZeroMQ.
    msg = serialize(**kwargs)
    # Send the data packet on the PUB socket.
    self._pub.send_multipart([tag.encode('utf-8'), msg])
    # Store the captured data into the data structure.
    self._out_stream.append_data(**kwargs)


  def _trigger_stop(self):
    self._poll_data_fn = self._poll_ending_data_packets
    self._is_continue_produce = False
    self._stop_new_data()


  # Send 'END' empty packet and label Node as done to safely finish and exit the process and its threads.
  def _send_end_packet(self) -> None:
    self._pub.send_multipart([("%s.data" % self._log_source_tag()).encode('utf-8'), b'', CMD_END.encode('utf-8')])
    self._is_done = not self._is_more_data_in and not self._is_continue_produce


  @abstractmethod
  def _cleanup(self) -> None:
    # Indicate to Logger to wrap up and exit.
    self._logger.cleanup()
    # Before closing the PUB socket, wait for the 'BYE' signal from the Broker.
    self._sync.send_multipart([self._log_source_tag().encode('utf-8'), CMD_EXIT.encode('utf-8')]) 
    host, cmd = self._sync.recv_multipart() # no need to read contents of the message.
    print("%s received %s from %s." % (self._log_source_tag(),
                                       cmd.decode('utf-8'),
                                       host.decode('utf-8')),
                                       flush=True)
    self._pub.close()
    self._sub.close()
    # Join on the logging background thread last, so that all things can finish in parallel.
    self._logger_thread.join()
    super()._cleanup()
