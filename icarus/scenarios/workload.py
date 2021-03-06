"""Traffic workloads

Every traffic workload to be used with Icarus must be modelled as an iterable
class, i.e. a class with at least an `__init__` method (through which it is
initialized, with values taken from the configuration file) and an `__iter__`
method that is called to return a new event.

Each call to the `__iter__` method must return a 2-tuple in which the first
element is the timestamp at which the event occurs and the second is a
dictionary, describing the event, which must contain at least the three
following attributes:
 * receiver: The name of the node issuing the request 
 * content: The name of the content for which the request is issued
 * log: A boolean value indicating whether this request should be logged or not
   for measurement purposes.

Each workload must expose the `contents` attribute which is an iterable of
all content identifiers. This is needed for content placement.
"""
import random
import csv
import math

import networkx as nx

from icarus.tools import TruncatedZipfDist, DiscreteDist
from icarus.registry import register_workload

__all__ = [
        'YoutubetraceWorkload',
        'StationaryWorkload',
        'GlobetraffWorkload',
        'TraceDrivenWorkload'
           ]

@register_workload('YOUTUBETRACE')
class YoutubetraceWorkload(object):
    """This function generates events from the youtube traces

    Parameters
    ----------
    topology : fnss.Topology
        The topology to which the workload refers
    n_contents : int
        The number of content object
    num_clients : int
        Total number of requesting clients in original trace
    reqs_file : str
        Path of file containing requested contents
    timestamps_file : str
        Path of file containing timestamps of requested contents
    clients_file : str
        Path of file containing clients which requested the content
    n_warmup : int, optional
        The number of warmup requests (i.e. requests executed to fill cache but
        not logged)
    n_measured : int, optional
        The number of logged requests after the warmup

    Returns
    -------
    events : iterator
        Iterator of events. Each event is a 2-tuple where the first element is
        the timestamp at which the event occurs and the second element is a
        dictionary of event attributes.
    """
    def __init__(self, topology, n_contents, num_clients, reqs_file, timestamps_file, clients_file, unique_contents_file,
                    n_warmup=10 ** 5, n_measured=4 * 10 ** 5, **kwargs):
        self.receivers = [v for v in topology.nodes_iter()
                     if topology.node[v]['stack'][0] == 'receiver']
        self.buffering = 64 * 1024 * 1024
        self.n_contents = n_contents
        self.request_contents = []
        self.timestamps = []
        self.clients = []
        self.contents = []#range(1, n_contents + 1)
        self.probability = []
        with open('/home/adita/Greedy 08142017/youtube_traces/All traces/pdf', 'r') as f:
            for content in f:
                self.probability.append(float(content.rstrip()))
        with open(timestamps_file, 'r', buffering=self.buffering) as f:
            for content in f:
                self.timestamps.append(float(content.rstrip()))
        with open(reqs_file, 'r', buffering=self.buffering) as f:
            for content in f:
                self.request_contents.append(int(content.rstrip()))
        with open(clients_file, 'r', buffering=self.buffering) as f:
            for content in f:
                self.clients.append(int(content.rstrip()))
        with open(unique_contents_file, 'r', buffering=self.buffering) as f:
            for content in f:
                self.contents.append(int(content.rstrip()))
        self.n_warmup = n_warmup
        self.n_measured = n_measured
        self.num_clients = num_clients
        self.disc = DiscreteDist(self.probability)
        #print len(self.clients)

    def __iter__(self):
        req_counter = 0
        t_event = 0.0
        while req_counter < self.n_warmup + self.n_measured:

            """if req_counter == self.n_warmup + 25:
                self.probability = []
                with open('/home/adita/Greedy 08142017/youtube_traces/All traces/part2/pdf', 'r') as f:
                #with open('/home/adita/Greedy 08142017/youtube_traces/All traces/test/2/pdf', 'r') as f:
                    for content in f:
                        self.probability.append(float(content.rstrip()))
                self.disc = DiscreteDist(self.probability)

            elif req_counter == self.n_warmup + 50:
                self.probability = []
                with open('/home/adita/Greedy 08142017/youtube_traces/All traces/part3/pdf', 'r') as f:
                #with open('/home/adita/Greedy 08142017/youtube_traces/All traces/test/3/pdf', 'r') as f:
                    for content in f:
                        self.probability.append(float(content.rstrip()))
                self.disc = DiscreteDist(self.probability)"""

            if req_counter < self.n_warmup:
                receiver = random.choice(self.receivers)
                t_event += (random.expovariate(1.0))
                index = int(self.disc.rv())#np.searchsorted(self.probability,random_number)
                if index == 581527:#35130:
                    index = 581526#35129
                #print index
                content = self.contents[index]

            else:
                t_event = self.timestamps[req_counter-self.n_warmup]
                content = self.request_contents[req_counter-self.n_warmup]

                a = int(int(self.clients[req_counter-self.n_warmup])/(math.ceil(self.num_clients/len(self.receivers))))
                #print a
                #if a==8:
                    #a=7
                if a>=16:
                    a=15
                #print a
                receiver = 5#self.receivers[a] #self.receivers[int(int(self.clients[req_counter])/math.ceil(self.num_clients / len(self.receivers)))]
                #if req_counter > 2200000:
                    #print "\nRequest # %d, Index %d, Actual user %s, Simulator user %s, Requested content %s" %(req_counter, a, self.clients[req_counter-self.n_warmup], receiver, content)
            log = (req_counter >= self.n_warmup)
            event = {'receiver': receiver, 'content': content, 'log': log}
            #\"""if req_counter > self.n_warmup:
                #print "\n", req_counter, t_event, event\"""
            yield (t_event, event)
            req_counter += 1
        raise StopIteration()

    """def __iter__(self):
        req_counter = 0
        t_event = 0.0
        while req_counter < self.n_warmup + self.n_measured:
            if req_counter == 1:
                print "Receivers : ", self.receivers
            t_event = self.timestamps[req_counter]
            index = int(self.disc.rv())#np.searchsorted(self.probability,random_number)
            if index == 91243:
                index = 91242
            content = self.contents[index]
            
            a = int(int(self.clients[req_counter])/(math.ceil(self.num_clients / len(self.receivers))))
            if a==8:
                a=7
            receiver = self.receivers[a] #self.receivers[int(int(self.clients[req_counter])/math.ceil(self.num_clients / len(self.receivers)))]
            
            log = (req_counter >= self.n_warmup)
            event = {'receiver': receiver, 'content': content, 'log': log}
            
            yield (t_event, event)
            req_counter += 1
        raise StopIteration()"""


@register_workload('STATIONARY')
class StationaryWorkload(object):
    """This function generates events on the fly, i.e. instead of creating an 
    event schedule to be kept in memory, returns an iterator that generates
    events when needed.
    
    This is useful for running large schedules of events where RAM is limited
    as its memory impact is considerably lower.
    
    These requests are Poisson-distributed while content popularity is
    Zipf-distributed
    
    All requests are mapped to receivers uniformly unless a positive *beta*
    parameter is specified.
    
    If a *beta* parameter is specified, then receivers issue requests at
    different rates. The algorithm used to determine the requests rates for 
    each receiver is the following:
     * All receiver are sorted in decreasing order of degree of the PoP they
       are attached to. This assumes that all receivers have degree = 1 and are
       attached to a node with degree > 1
     * Rates are then assigned following a Zipf distribution of coefficient
       beta where nodes with higher-degree PoPs have a higher request rate 
    
    Parameters
    ----------
    topology : fnss.Topology
        The topology to which the workload refers
    n_contents : int
        The number of content object
    alpha : float
        The Zipf alpha parameter
    beta : float, optional
        Parameter indicating
    rate : float, optional
        The mean rate of requests per second
    n_warmup : int, optional
        The number of warmup requests (i.e. requests executed to fill cache but
        not logged)
    n_measured : int, optional
        The number of logged requests after the warmup
    
    Returns
    -------
    events : iterator
        Iterator of events. Each event is a 2-tuple where the first element is
        the timestamp at which the event occurs and the second element is a
        dictionary of event attributes.
    """
    def __init__(self, topology, n_contents, alpha, beta=0, rate=1.0,
                    n_warmup=10**5, n_measured=4*10**5, seed=None, **kwargs):
        if alpha < 0:
            raise ValueError('alpha must be positive')
        if beta < 0:
            raise ValueError('beta must be positive')
        self.receivers = [v for v in topology.nodes_iter()
                     if topology.node[v]['stack'][0] == 'receiver']
        self.zipf = TruncatedZipfDist(alpha, n_contents)
        self.n_contents = n_contents
        self.contents = range(1, n_contents + 1)
        self.alpha = alpha
        self.rate = rate
        self.n_warmup = n_warmup
        self.n_measured = n_measured
        random.seed(seed)
        self.beta = beta
        if beta != 0:
            degree = nx.degree(self.topology)
            self.receivers = sorted(self.receivers, key=lambda x: degree[iter(topology.edge[x]).next()], reverse=True)
            self.receiver_dist = TruncatedZipfDist(beta, len(self.receivers))
        
    def __iter__(self):
        req_counter = 0
        t_event = 0.0
        while req_counter < self.n_warmup + self.n_measured:
            t_event += (random.expovariate(self.rate))
            if self.beta == 0:
                receiver = random.choice(self.receivers)
            else:
                receiver = self.receivers[self.receiver_dist.rv()-1]
            content = int(self.zipf.rv())
            log = (req_counter >= self.n_warmup)
            event = {'receiver': receiver, 'content': content, 'log': log}
            yield (t_event, event)
            req_counter += 1
        raise StopIteration()


@register_workload('GLOBETRAFF')
class GlobetraffWorkload(object):
    """Parse requests from GlobeTraff workload generator
    
    All requests are mapped to receivers uniformly unless a positive *beta*
    parameter is specified.
    
    If a *beta* parameter is specified, then receivers issue requests at
    different rates. The algorithm used to determine the requests rates for 
    each receiver is the following:
     * All receiver are sorted in decreasing order of degree of the PoP they
       are attached to. This assumes that all receivers have degree = 1 and are
       attached to a node with degree > 1
     * Rates are then assigned following a Zipf distribution of coefficient
       beta where nodes with higher-degree PoPs have a higher request rate 
    
    Parameters
    ----------
    topology : fnss.Topology
        The topology to which the workload refers
    reqs_file : str
        The GlobeTraff request file
    contents_file : str
        The GlobeTraff content file
    beta : float, optional
        Spatial skewness of requests rates
        
    Returns
    -------
    events : iterator
        Iterator of events. Each event is a 2-tuple where the first element is
        the timestamp at which the event occurs and the second element is a
        dictionary of event attributes.
    """
    
    def __init__(self, topology, reqs_file, contents_file, beta=0, **kwargs):
        """Constructor"""
        if beta < 0:
            raise ValueError('beta must be positive')
        self.receivers = [v for v in topology.nodes_iter() 
                     if topology.node[v]['stack'][0] == 'receiver']
        self.n_contents = 0
        with open(contents_file, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for content, popularity, size, app_type in reader:
                self.n_contents = max(self.n_contents, content)
        self.n_contents += 1
        self.contents = range(self.n_contents)
        self.request_file = reqs_file
        self.beta = beta
        if beta != 0:
            degree = nx.degree(self.topology)
            self.receivers = sorted(self.receivers, key=lambda x: 
                                    degree[iter(topology.edge[x]).next()], 
                                    reverse=True)
            self.receiver_dist = TruncatedZipfDist(beta, len(self.receivers))
        
    def __iter__(self):
        with open(self.request_file, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for timestamp, content, size in reader:
                if self.beta == 0:
                    receiver = random.choice(self.receivers)
                else:
                    receiver = self.receivers[self.receiver_dist.rv()-1]
                event = {'receiver': receiver, 'content': content, 'size': size}
                yield (timestamp, event)
        raise StopIteration()

@register_workload('TRACE_DRIVEN')
class TraceDrivenWorkload(object):
    """Parse requests from a generic request trace.
    
    This workload requires two text files:
     * a requests file, where each line corresponds to a string identifying
       the content requested
     * a contents file, which lists all unique content identifiers appearing
       in the requests file.
       
    Since the trace do not provide timestamps, requests are scheduled according
    to a Poisson process of rate *rate*. All requests are mapped to receivers
    uniformly unless a positive *beta* parameter is specified.
    
    If a *beta* parameter is specified, then receivers issue requests at
    different rates. The algorithm used to determine the requests rates for 
    each receiver is the following:
     * All receiver are sorted in decreasing order of degree of the PoP they
       are attached to. This assumes that all receivers have degree = 1 and are
       attached to a node with degree > 1
     * Rates are then assigned following a Zipf distribution of coefficient
       beta where nodes with higher-degree PoPs have a higher request rate 
        
    Parameters
    ----------
    topology : fnss.Topology
        The topology to which the workload refers
    reqs_file : str
        The path to the requests file
    contents_file : str
        The path to the contents file
    n_contents : int
        The number of content object (i.e. the number of lines of contents_file)
    n_warmup : int
        The number of warmup requests (i.e. requests executed to fill cache but
        not logged)
    n_measured : int
        The number of logged requests after the warmup
    rate : float, optional
        The network-wide mean rate of requests per second
    beta : float, optional
        Spatial skewness of requests rates
        
    Returns
    -------
    events : iterator
        Iterator of events. Each event is a 2-tuple where the first element is
        the timestamp at which the event occurs and the second element is a
        dictionary of event attributes.
    """
    
    def __init__(self, topology, reqs_file, contents_file, n_contents,
                 n_warmup, n_measured, rate=1.0, beta=0, **kwargs):
        """Constructor"""
        if beta < 0:
            raise ValueError('beta must be positive')
        # Set high buffering to avoid one-line reads
        self.buffering = 64*1024*1024
        self.n_contents = n_contents
        self.n_warmup = n_warmup
        self.n_measured = n_measured
        self.reqs_file = reqs_file
        self.rate = rate
        self.receivers = [v for v in topology.nodes_iter() 
                          if topology.node[v]['stack'][0] == 'receiver']
        self.contents = []
        with open(contents_file, 'r', buffering=self.buffering) as f:
            for content in f:
                self.contents.append(content)
        self.beta = beta
        if beta != 0:
            degree = nx.degree(topology)
            self.receivers = sorted(self.receivers, key=lambda x:
                                    degree[iter(topology.edge[x]).next()],
                                    reverse=True)
            self.receiver_dist = TruncatedZipfDist(beta, len(self.receivers))
        
    def __iter__(self):
        req_counter = 0
        t_event = 0.0
        with open(self.reqs_file, 'r', buffering=self.buffering) as f:
            for content in f:
                t_event += (random.expovariate(self.rate))
                if self.beta == 0:
                    receiver = random.choice(self.receivers)
                else:
                    receiver = self.receivers[self.receiver_dist.rv()-1]
                log = (req_counter >= self.n_warmup)
                event = {'receiver': receiver, 'content': content, 'log': log}
                yield (t_event, event)
                req_counter += 1
                if(req_counter >= self.n_warmup + self.n_measured):
                    raise StopIteration()
            raise ValueError("Trace did not contain enough requests")
