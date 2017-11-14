"""Implementations of all caching and routing strategies
"""
from __future__ import division
import random
import abc
import collections
import math

import networkx as nx
import numpy as np
import csv

from icarus.registry import register_strategy
from icarus.util import iround
from icarus.util import inheritdoc, multicast_tree, path_links
import icarus

loop_count = 200000
warm_up_count = 1000000
caches = [0,1,2,6,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,29]

__all__ = [
       'Strategy',
       'Hybrid',
       'Optimal2Caching',
       'Hashrouting',
       'HashroutingSymmetric',
       'HashroutingAsymmetric',
       'HashroutingMulticast',
       'HashroutingHybridAM',
       'HashroutingHybridSM',
       'NoCache',
       'Edge',
       'LeaveCopyEverywhere',
       'CharacteristicTime',
       'CharacteristicTimeLCE',
       'OptimalCaching',
       'LeaveCopyDown',
       'CacheLessForMore',
       'RandomBernoulli',
       'RandomChoice',
       'NearestReplicaRouting',
           ]

#TODO: Implement BaseOnPath to reduce redundant code
#TODO: In Hashrouting, implement request routing phase under in single function

class Strategy(object):
    """Base strategy imported by all other strategy classes"""
    
    __metaclass__ = abc.ABCMeta

    def __init__(self, view, controller, **kwargs):
        """Constructor
        
        Parameters
        ----------
        view : NetworkView
            An instance of the network view
        controller : NetworkController
            An instance of the network controller
        kwargs : keyworded arguments, optional
            Additional strategy parameters
        """
        self.view = view
        self.controller = controller
        
    @abc.abstractmethod
    def process_event(self, time, receiver, content, log):
        """Process an event received from the simulation engine.
        
        This event is processed by executing relevant actions of the network
        controller, potentially based on the current status of the network
        retrieved from the network view.
        
        Parameters
        ----------
        time : int
            The timestamp of the event
        receiver : any hashable type
            The receiver node requesting a content
        content : any hashable type
            The content identifier requested by the receiver
        log : bool
            Indicates whether the event must be registered by the data
            collectors attached to the network.
        """
        raise NotImplementedError('The selected strategy must implement '
                                  'a process_event method')

@register_strategy('HYBRID')
class Hybrid(Strategy):
    """Hybrid strategy.
    
    This strategy is combination of static and dynamic caching.
    """

    @inheritdoc(Strategy)
    def __init__(self, view, controller, **kwargs):
        super(Hybrid, self).__init__(view, controller)
	self.count = 1
	self.scount = 0
	self.dcount = 0
	self.hit = 0
	self.hop = 0
	self.core = 0
	self.custodian = 0
	self.alpha = kwargs['alpha']
	self.network_cache = kwargs['network_cache']
	n = 581527
	self.cache_size = iround(n * self.network_cache)
        #self.static_cache_size = iround(self.cache_size*2.5*33/100)
        self.static_cache_size = iround(self.cache_size*0.99009901)
        self.dynamic_cache_size = self.cache_size - self.static_cache_size
	self.link = []
	self.load = []
        self.hits = [None] * 581527
        self.caches = [0,1,2,6,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,29]
        self.sources = [10]

        print "HYBRID"
        print "Static Cache Size:", self.static_cache_size
        print "Dynamic Cache Size:", self.dynamic_cache_size


    @inheritdoc(Strategy)
    def process_event(self, time, receiver, content, log):
	source = self.view.content_source(content)
        """for v in self.caches:
            if self.count > warm_up_count+1467699:
                if not self.view.static_cache_dump(v) == None:
                    print "Static Cache Dump of ", v, self.count,len(self.view.static_cache_dump(v))
                if not self.view.dynamic_cache_dump(v) == None:
                    print "Dynamic Cache Dump of ", v, self.count,len(self.view.dynamic_cache_dump(v))"""

        if self.count == 1:
            """name = '/home/adita/Greedy 08142017/Adita/WIDE/581527-1/matrix'+str(iround(self.cache_size/2)) #WIDE
            f1 = open(name,'r')
            columns = []
            rec = []
            cont = []
            for f in f1:
                columns = f.split(' ')
                columns = [col.strip() for col in columns]
                rec.append(int(columns[0]))
                cont.append(int(columns[1])+1)
            #serving_node = 10
            for r1 in range(len(rec)):                
                self.controller.start_session(time, receiver, cont[r1], log, False)
                serving_node = rec[r1]
                self.controller.put_static_content(serving_node)
                self.controller.end_session(False)"""

            name = '/home/adita/Greedy 08142017/youtube_traces/All traces/sorted_cont'
            f1 = open(name,'r')
            columns = []
            cont = []
            for f in f1:
                #columns = f.split(' ')
                columns = f.strip()
                cont.append(int(columns))

            """l1 =[7, 8, 9, 10, 11, 12, 13, 14]
            l2 =[3, 4, 5, 6]
            l3 =[1, 2]
            name1 = '/home/adita/Greedy 08142017/Adita/icarus-0.5.0/Tree Caching/l1'+str(self.static_cache_size)+'.0'
            f2 = open(name1,'r')
            name2 = '/home/adita/Greedy 08142017/Adita/icarus-0.5.0/Tree Caching/l2'+str(self.static_cache_size)+'.0'
            f3 = open(name2,'r')
            name3 = '/home/adita/Greedy 08142017/Adita/icarus-0.5.0/Tree Caching/l3'+str(self.static_cache_size)+'.0'
            f4 = open(name3,'r')
            columns = []
            cont = []
            for f in f2:
                #columns = f.split(' ')
                columns = f.strip()
                cont.append(int(columns))

            for l in l1:
                for c in cont:                
                    self.controller.start_session(time, receiver, c, log, False)
                    serving_node = l
                    self.controller.put_static_content(serving_node)
                    self.controller.end_session(False)

            cont = []
            for f in f3:
                #columns = f.split(' ')
                columns = f.strip()
                cont.append(int(columns))

            for l in l2:
                for c in cont:                
                    self.controller.start_session(time, receiver, c, log, False)
                    serving_node = l
                    self.controller.put_static_content(serving_node)
                    self.controller.end_session(False)

            cont = []
            for f in f4:
                #columns = f.split(' ')
                columns = f.strip()
                cont.append(int(columns))

            for l in l3:
                for c in cont:                
                    self.controller.start_session(time, receiver, c, log, False)
                    serving_node = l
                    self.controller.put_static_content(serving_node)
                    self.controller.end_session(False)"""
                    

            #serving_node = 10
            for r1 in range(self.static_cache_size):                
                self.controller.start_session(time, receiver, cont[r1], log, False)
                serving_node = 6#rec[r1]
                self.controller.put_static_content(serving_node)
                self.controller.end_session(False)


        path = self.view.shortest_path(receiver, source)

        # Route requests to original source and queries caches on the path
        self.controller.start_session(time, receiver, content, log)
        for u, v in path_links(path):
            self.controller.forward_request_hop(u, v)
            if self.view.has_cache(v):
                if self.controller.get_static_content(v):
                    serving_node = v
               	    self.scount += 1
                    #print '\nS Hit Hyb: Request # %d, Serving node %d, Content %d, Receiver %d, Source %d, Path %s' % (self.count, serving_node, content, receiver, source, path)
                    break
                elif self.controller.get_dynamic_content(v):
                    serving_node = v
               	    self.dcount += 1
                    #print '\nD Hit Hyb: Request # %d, Serving node %d, Content %d, Receiver %d, Source %d, Path %s' % (self.count, serving_node, content, receiver, source, path)
                    break

            # No cache hits, get content from source
            self.controller.get_dynamic_content(v)
            serving_node = v
        # Return content
	hopcount = len(self.view.shortest_path(receiver, serving_node))
        path = list(reversed(self.view.shortest_path(receiver, serving_node)))

        if self.count >= warm_up_count+1467699:# and ( not (serving_node == 10)):
            print self.scount, self.dcount
            #print '\nHyb: Request # %d, Serving node %d, Content %d, Receiver %d, Source %d, Path %s' % (self.count, serving_node, content, receiver, source, path)

        for u, v in path_links(path):
            self.controller.forward_content_hop(u, v)
            if self.view.has_cache(v):
                # insert content
                self.controller.put_dynamic_content(v)

        """copied = False
        for u, v in path_links(path):
            self.controller.forward_content_hop(u, v)
            if not copied and v != receiver and self.view.has_cache(v):
                self.controller.put_dynamic_content(v)
                copied = True"""
        self.count += 1
        self.controller.end_session()


@register_strategy('OPTIMAL2')
class Optimal2Caching(Strategy):

    @inheritdoc(Strategy)
    def __init__(self, view, controller, **kwargs):
        super(Optimal2Caching, self).__init__(view, controller)
	self.alpha = kwargs['alpha']
	self.network_cache = kwargs['network_cache']
	self.count=1
	self.hit=0
	self.hop=0
	self.core = 0
	self.custodian = 0

        self.change_counter = 1
        self.name_counter = 2

	alpha = self.alpha
	name = str(alpha)
	name2 = name.replace(".","")
	self.num = 581527
	n = 581527
	self.cache_size = iround(n * self.network_cache)
	name3 = str(self.cache_size)
	name5 = name3.replace(".0","")
	self.name4 = str.join('%s'%name2,'%s'%name5)
	self.link = []
	self.load = []
        self.actual_cont = []
        self.hits = [None] * 581527
        self.delay = 0
        self.sources = [10]
        self.caches = [0,1,2,6,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,29] #WIDE
	self.receivers = [27, 28, 3, 5, 4, 7, 9, 8, 11, 13, 12, 15, 14, 17, 16, 19, 18] #WIDE
        print "Opt2"

    @inheritdoc(Strategy)
    def process_event(self, time, receiver, content, log):
	source = self.view.content_source(content)

        if self.count == 1:
            name = '/home/adita/Greedy 08142017/youtube_traces/All traces/sorted_cont'
            f1 = open(name,'r')
            l1 =[7, 8, 9, 10, 11, 12, 13, 14]
            l2 =[3, 4, 5, 6]
            l3 =[1, 2]
            name1 = '/home/adita/Greedy 08142017/Adita/icarus-0.5.0/Tree Caching/l1'+str(self.cache_size)
            f2 = open(name1,'r')
            name2 = '/home/adita/Greedy 08142017/Adita/icarus-0.5.0/Tree Caching/l2'+str(self.cache_size)
            f3 = open(name2,'r')
            name3 = '/home/adita/Greedy 08142017/Adita/icarus-0.5.0/Tree Caching/l3'+str(self.cache_size)
            f4 = open(name3,'r')
            columns = []
            cont = []
            for f in f2:
                #columns = f.split(' ')
                columns = f.strip()
                cont.append(int(columns))

            for l in l1:
                for c in cont:                
                    self.controller.start_session(time, receiver, c, log, False)
                    serving_node = l
                    self.controller.put_content(serving_node)
                    self.controller.end_session(False)

            cont = []
            for f in f3:
                #columns = f.split(' ')
                columns = f.strip()
                cont.append(int(columns))

            for l in l2:
                for c in cont:                
                    self.controller.start_session(time, receiver, c, log, False)
                    serving_node = l
                    self.controller.put_content(serving_node)
                    self.controller.end_session(False)

            cont = []
            for f in f4:
                #columns = f.split(' ')
                columns = f.strip()
                cont.append(int(columns))

            for l in l3:
                for c in cont:                
                    self.controller.start_session(time, receiver, c, log, False)
                    serving_node = l
                    self.controller.put_content(serving_node)
                    self.controller.end_session(False)

            """columns = []
            rec = []
            cont = []
            for f in f1:
                #columns = f.split(' ')
                columns = f.strip()
                cont.append(int(columns))
            #serving_node = 10
            for r1 in range(self.cache_size):                
                self.controller.start_session(time, receiver, cont[r1], log, False)
                serving_node = 6#rec[r1]
                self.controller.put_content(serving_node)
                self.controller.end_session(False)"""

        path = self.view.shortest_path(receiver, source)
        """for v in self.caches:
            if self.count > warm_up_count:# or self.count == warm_up_count+500000 or self.count == warm_up_count+1400000:
                if not self.view.cache_dump(v) == None:
                    print "Prev Opt Cache Dump of ", v, self.count, len(self.view.cache_dump(v))"""

        # Route requests to original source and queries caches on the path

        if self.count > warm_up_count:
            self.controller.start_session(time, receiver, content, log)
            for u, v in path_links(path):
                self.controller.forward_request_hop(u, v)
                if self.view.has_cache(v):
                    if self.controller.get_content(v):
                        serving_node = v
                        if v not in self.sources:
                            self.hit += 1
                            self.hits[int(content)-1] = self.count
                        break
                # No cache hits, get content from source
                self.controller.get_content(v)
                serving_node = v
            if self.count >= warm_up_count+1467699:# and ( not (serving_node == 10)):
                print self.hit, len(self.view.cache_dump(6))
            # Return content
            path = list(reversed(self.view.shortest_path(receiver, serving_node)))
            for i in range(0,len(path)-1):
	        u = path[i]
	        v = path[i+1]
                self.controller.forward_content_hop(u, v)

            self.count += 1
       	    self.controller.end_session()
        else:
            self.count += 1



class Hashrouting(Strategy):
    """Base class for all hash-routing implementations. Hash-routing
    implementations are described in [1]_.
        
    References
    ----------
    .. [1] L. Saino, I. Psaras and G. Pavlou, Hash-routing Schemes for
    Information-Centric Networking, in Proceedings of ACM SIGCOMM ICN'13
    workshop. Available:
    https://www.ee.ucl.ac.uk/~lsaino/publications/hashrouting-icn13.pdf
    
    """

    @inheritdoc(Strategy)
    def __init__(self, view, controller, **kwargs):
        super(Hashrouting, self).__init__(view, controller)
        self.cache_nodes = view.cache_nodes()
        # Allocate results of hash function to caching nodes 
        self.cache_assignment = dict((i, self.cache_nodes[i]) 
                                      for i in range(len(self.cache_nodes)))

    def authoritative_cache(self, content):
        """Return the authoritative cache node for the given content
        
        Parameters
        ----------
        content : any hashable type
            The identifier of the content
            
        Returns
        -------
        authoritative_cache : any hashable type
            The node on which the authoritative cache is deployed
        """
        return self.cache_assignment[self.hash(content)]

    def hash(self, content):
        """Return a hash code of the content for hash-routing purposes
        
        
        Parameters
        ----------
        content : any hashable type
            The identifier of the content
            
        Returns
        -------
        hash : int
            The hash code of the content
        """
        #TODO: This hash function needs revision because it does not return
        # equally probably hash codes
        n = len(self.cache_nodes)
        h = content % n
        return h if (content/n) % 2 == 0 else (n - h - 1)


@register_strategy('HR_SYMM')
class HashroutingSymmetric(Hashrouting):
    """Hash-routing with symmetric routing (HR SYMM)
    """

    @inheritdoc(Strategy)
    def __init__(self, view, controller, **kwargs):
        super(HashroutingSymmetric, self).__init__(view, controller)
	self.count = 0
	self.hit = 0
	self.hop = 0
	self.alpha = kwargs['alpha']
	self.network_cache = kwargs['network_cache']

    @inheritdoc(Strategy)
    def process_event(self, time, receiver, content, log):
        # get all required data
        source = self.view.content_source(content)
        cache = self.authoritative_cache(content)
        # handle (and log if required) actual request
        self.controller.start_session(time, receiver, content, log)
        # Forward request to authoritative cache
        self.controller.forward_request_path(receiver, cache)
	self.count+=1
        if self.controller.get_content(cache):
            # We have a cache hit here
            self.controller.forward_content_path(cache, receiver)
	    hopcount = len(self.view.shortest_path(receiver, cache))
	    if self.count>100000:
	    	self.hit+=1
		self.hop+=hopcount
        else:
            # Cache miss: go all the way to source
            self.controller.forward_request_path(cache, source)
            if not self.controller.get_content(source):
                raise RuntimeError('The content is not found the expected source')
	    hopcount1 = len(self.view.shortest_path(source, cache))
	    hopcount2 = len(self.view.shortest_path(cache, receiver))
	    hopcount = hopcount1 + hopcount2
	    if self.count>100000:
		self.hop+=hopcount
            self.controller.forward_content_path(source, cache)
            # Insert in cache
            self.controller.put_content(cache)
            # Forward to receiver
            self.controller.forward_content_path(cache, receiver)
	if self.count == 200000:
	    fo = open("hr.txt", "a")
	    fo.write('%s, ' % self.alpha)
	    fo.write('%s:' % self.network_cache)
	    fo.write(' %d' % self.hit)
	    fo.write("\t")
	    fo.write(' %d' % self.hop)
	    fo.write("\n")
	    fo.close()
        self.controller.end_session() 


@register_strategy('HR_ASYMM')
class HashroutingAsymmetric(Hashrouting):
    """Hash-routing with asymmetric routing (HR ASYMM) 
    """

    @inheritdoc(Strategy)
    def __init__(self, view, controller, **kwargs):
        super(HashroutingAsymmetric, self).__init__(view, controller)
        
    @inheritdoc(Strategy)
    def process_event(self, time, receiver, content, log):
        # get all required data
        source = self.view.content_source(content)
        cache = self.authoritative_cache(content)
        # handle (and log if required) actual request
        self.controller.start_session(time, receiver, content, log)
        # Forward request to authoritative cache
        self.controller.forward_request_path(receiver, cache)
        if self.controller.get_content(cache):
            # We have a cache hit here
            self.controller.forward_content_path(cache, receiver)
        else:
            # Cache miss: go all the way to source
            self.controller.forward_request_path(cache, source)
            if not self.controller.get_content(source):
                raise RuntimeError('The content was not found at the expected source')   
            if cache in self.view.shortest_path(source, receiver):
                # Forward to cache
                self.controller.forward_content_path(source, cache)
                # Insert in cache
                self.controller.put_content(cache)
                # Forward to receiver
                self.controller.forward_content_path(cache, receiver)
            else:
                # Forward to receiver straight away
                self.controller.forward_content_path(source, receiver)
        self.controller.end_session()


@register_strategy('HR_MULTICAST')
class HashroutingMulticast(Hashrouting):
    """
    Hash-routing implementation with multicast delivery of content packets.
    
    In this strategy, if there is a cache miss, when contant packets return in
    the domain, the packet is multicast, one copy being sent to the
    authoritative cache and the other to the receiver. If the cache is on the
    path from source to receiver, this strategy behaves as a normal symmetric
    hash-routing strategy.
    """

    @inheritdoc(Strategy)
    def __init__(self, view, controller, **kwargs):
        super(HashroutingMulticast, self).__init__(view, controller)
        # map id of content to node with cache responsibility

    @inheritdoc(Strategy)
    def process_event(self, time, receiver, content, log):
        # get all required data
        source = self.view.content_source(content)
        cache = self.authoritative_cache(content)
        # handle (and log if required) actual request
        self.controller.start_session(time, receiver, content, log)
        # Forward request to authoritative cache
        self.controller.forward_request_path(receiver, cache)
        if self.controller.get_content(cache):
            # We have a cache hit here
            self.controller.forward_content_path(cache, receiver)
        else:
            # Cache miss: go all the way to source
            self.controller.forward_request_path(cache, source)
            if not self.controller.get_content(source):
                raise RuntimeError('The content is not found the expected source') 
            if cache in self.view.shortest_path(source, receiver):
                self.controller.forward_content_path(source, cache)
                # Insert in cache
                self.controller.put_content(cache)
                # Forward to receiver
                self.controller.forward_content_path(cache, receiver)
            else:
                # Multicast
                cache_path = self.view.shortest_path(source, cache)
                recv_path = self.view.shortest_path(source, receiver)
                
                # find what is the node that has to fork the content flow
                for i in range(1, min([len(cache_path), len(recv_path)])):
                    if cache_path[i] != recv_path[i]:
                        fork_node = cache_path[i-1]
                        break
                else: fork_node = cache
                self.controller.forward_content_path(source, fork_node, main_path=True)
                self.controller.forward_content_path(fork_node, receiver, main_path=True)
                self.controller.forward_content_path(fork_node, cache, main_path=False)
                self.controller.put_content(cache)
        self.controller.end_session()


@register_strategy('HR_HYBRID_AM')
class HashroutingHybridAM(Hashrouting):
    """
    Hash-routing implementation with hybrid asymmetric-multicast delivery of
    content packets.
    
    In this strategy, if there is a cache miss, when content packets return in
    the domain, the packet is delivered to the receiver following the shortest
    path. If the additional number of hops required to send a copy to the
    authoritative cache is below a specific fraction of the network diameter,
    then one copy is sent to the authoritative cache as well. If the cache is
    on the path from source to receiver, this strategy behaves as a normal
    symmetric hash-routing strategy.
    """

    @inheritdoc(Strategy)
    def __init__(self, view, controller, max_stretch=0.2):
        super(HashroutingHybridAM, self).__init__(view, controller)
        self.max_stretch = nx.diameter(view.topology()) * max_stretch

    @inheritdoc(Strategy)
    def process_event(self, time, receiver, content, log):
        # get all required data
        source = self.view.content_source(content)
        cache = self.authoritative_cache(content)
        # handle (and log if required) actual request
        self.controller.start_session(time, receiver, content, log)
        # Forward request to authoritative cache
        self.controller.forward_request_path(receiver, cache)
        if self.controller.get_content(cache):
            # We have a cache hit here
            self.controller.forward_content_path(cache, receiver)
        else:
            # Cache miss: go all the way to source
            self.controller.forward_request_path(cache, source)
            if not self.controller.get_content(source):
                raise RuntimeError('The content was not found at the expected source') 
            
            if cache in self.view.shortest_path(source, receiver):
                # Forward to cache
                self.controller.forward_content_path(source, cache)
                # Insert in cache
                self.controller.put_content(cache)
                # Forward to receiver
                self.controller.forward_content_path(cache, receiver)
            else:
                # Multicast
                cache_path = self.view.shortest_path(source, cache)
                recv_path = self.view.shortest_path(source, receiver)
                
                # find what is the node that has to fork the content flow
                for i in range(1, min([len(cache_path), len(recv_path)])):
                    if cache_path[i] != recv_path[i]:
                        fork_node = cache_path[i-1]
                        break
                else: fork_node = cache
                self.controller.forward_content_path(source, receiver, main_path=True)
                # multicast to cache only if stretch is under threshold
                if len(self.view.shortest_path(fork_node, cache)) - 1 < self.max_stretch:
                    self.controller.forward_content_path(fork_node, cache, main_path=False)
                    self.controller.put_content(cache)
        self.controller.end_session()
        

@register_strategy('HR_HYBRID_SM')
class HashroutingHybridSM(Hashrouting):
    """
    Hash-routing implementation with hybrid symmetric-multicast delivery of
    content packets.
    
    In this implementation, the edge router receiving a content packet decides
    whether to deliver the packet using multicast or symmetric hash-routing
    based on the total cost for delivering the Data to both cache and receiver
    in terms of hops.
    """

    @inheritdoc(Strategy)
    def __init__(self, view, controller, **kwargs):
        super(HashroutingHybridSM, self).__init__(view, controller)

    @inheritdoc(Strategy)
    def process_event(self, time, receiver, content, log):
        # get all required data
        source = self.view.content_source(content)
        cache = self.authoritative_cache(content)
        # handle (and log if required) actual request
        self.controller.start_session(time, receiver, content, log)
        # Forward request to authoritative cache
        self.controller.forward_request_path(receiver, cache)
        if self.controller.get_content(cache):
            # We have a cache hit here
            self.controller.forward_content_path(cache, receiver)
        else:
            # Cache miss: go all the way to source
            self.controller.forward_request_path(cache, source)
            if not self.controller.get_content(source):
                raise RuntimeError('The content is not found the expected source') 
            
            if cache in self.view.shortest_path(source, receiver):
                self.controller.forward_content_path(source, cache)
                # Insert in cache
                self.controller.put_content(cache)
                # Forward to receiver
                self.controller.forward_content_path(cache, receiver)
            else:
                # Multicast
                cache_path = self.view.shortest_path(source, cache)
                recv_path = self.view.shortest_path(source, receiver)
                
                # find what is the node that has to fork the content flow
                for i in range(1, min([len(cache_path), len(recv_path)])):
                    if cache_path[i] != recv_path[i]:
                        fork_node = cache_path[i-1]
                        break
                else: fork_node = cache
                
                symmetric_path_len = len(self.view.shortest_path(source, cache)) + \
                                     len(self.view.shortest_path(cache, receiver)) - 2
                multicast_path_len = len(self.view.shortest_path(source, fork_node)) + \
                                     len(self.view.shortest_path(fork_node, cache)) + \
                                     len(self.view.shortest_path(fork_node, receiver)) - 3
                
                self.controller.put_content(cache)
                # If symmetric and multicast have equal cost, choose symmetric
                # because of easier packet processing
                if symmetric_path_len <= multicast_path_len: # use symmetric delivery
                    # Symmetric delivery
                    self.controller.forward_content_path(source, cache, main_path=True)
                    self.controller.forward_content_path(cache, receiver, main_path=True)
                else:
                    # Multicast delivery
                    self.controller.forward_content_path(source, receiver, main_path=True)
                    self.controller.forward_content_path(fork_node, cache, main_path=False)
                self.controller.end_session()


@register_strategy('NO_CACHE')
class NoCache(Strategy):
    """Strategy without any caching
    
    This corresponds to the traffic in a normal TCP/IP network without any
    CDNs or overlay caching, where all content requests are served by the 
    original source.
    """

    @inheritdoc(Strategy)
    def __init__(self, view, controller, **kwargs):
        super(NoCache, self).__init__(view, controller)
    
    @inheritdoc(Strategy)
    def process_event(self, time, receiver, content, log):
        # get all required data
        source = self.view.content_source(content)
        path = self.view.shortest_path(receiver, source)
        # Route requests to original source
        self.controller.start_session(time, receiver, content, log)
        self.controller.forward_request_path(receiver, source)
        self.controller.get_content(source)
        # Route content back to receiver
        path = list(reversed(path))
        self.controller.forward_content_path(source, receiver, path)
        self.controller.end_session()


@register_strategy('EDGE')
class Edge(Strategy):
    """Edge caching strategy.
    
    In this strategy only a cache at the edge is looked up before forwarding
    a content request to the original source.
    
    In practice, this is like an LCE but it only queries the first cache it
    finds in the path. It is assumed to be used with a topology where each
    PoP has a cache but it simulates a case where the cache is actually further
    down the access network and it is not looked up for transit traffic passing
    through the PoP but only for PoP-originated requests.
    """

    @inheritdoc(Strategy)
    def __init__(self, view, controller):
        super(Edge, self).__init__(view, controller)

    @inheritdoc(Strategy)
    def process_event(self, time, receiver, content, log):
        # get all required data
        source = self.view.content_source(content)
        path = self.view.shortest_path(receiver, source)
        # Route requests to original source and queries caches on the path
        self.controller.start_session(time, receiver, content, log)
        edge_cache = None
        for u, v in path_links(path):
            self.controller.forward_request_hop(u, v)
            if self.view.has_cache(v):
                edge_cache = v
                if self.controller.get_content(v):
                    serving_node = v
                else:
                    # Cache miss, get content from source
                    self.controller.forward_request_path(v, source)
                    self.controller.get_content(source)
                    serving_node = source
                break
        else:
            # No caches on the path at all, get it from source
            self.controller.get_content(v)
            serving_node = v
            
        # Return content
        path = list(reversed(self.view.shortest_path(receiver, serving_node)))
        self.controller.forward_content_path(serving_node, receiver, path)
        if serving_node == source:
            self.controller.put_content(edge_cache)
        self.controller.end_session()


@register_strategy('LCE')
class LeaveCopyEverywhere(Strategy):
    """Leave Copy Everywhere (LCE) strategy.
    
    In this strategy a copy of a content is replicated at any cache on the
    path between serving node and receiver.
    """

    @inheritdoc(Strategy)
    def __init__(self, view, controller, **kwargs):
        super(LeaveCopyEverywhere, self).__init__(view, controller)
	self.count = 0
	self.hit = 0
	self.hop = 0
	self.core = 0
	self.custodian = 0
	self.alpha = kwargs['alpha']
	self.network_cache = kwargs['network_cache']
	self.link = []
	self.load = []
        self.hits = [None] * 581527
        self.caches = [0,1,2,6,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,29]
        self.sources = [10]
        #self.caches = [4, 55, 10, 21, 18, 49, 14, 35, 37, 22, 58, 20, 29, 59, 39, 31, 34, 36, 15, 46] #GARR

        self.conts = []
        f1 = open('/home/adita/Greedy 08142017/youtube_traces/All traces/f15','r')
        for f in f1:
            self.conts.append(int(f.rstrip()))
        print "LCE"
	"""receivers = [27, 28, 3, 5, 4, 7, 9, 8, 11, 13, 12, 15, 14, 17, 16, 19, 18] #WIDE
	sources = [10]#, 6, 20, 21, 22]#WIDE
        print "Shortest Paths:"#, self.network_cache
        for i in range(len(receivers)):
            for j in range(len(sources)):
                print self.view.shortest_path(receivers[i], sources[j])"""


    @inheritdoc(Strategy)
    def process_event(self, time, receiver, content, log):
	source = self.view.content_source(content)
        #caches = [0,1,2,6,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,29]
        """for v in self.caches:
            if self.count > warm_up_count and self.count == 2331056:#warm_up_count+500000 or self.count == warm_up_count+1400000:
                if not self.view.cache_dump(v) == None:
                    print "LCE Cache Dump of ", v, self.count,(self.view.cache_dump(v))"""

        path = self.view.shortest_path(receiver, source)
	nodes = [27, 28, 3, 5, 4, 7, 9, 8, 11, 13, 12, 15, 14, 17, 16, 19, 18] #WIDE
	#nodes = [26, 20, 21, 11, 10, 19, 18, 37] #GEANT
	#nodes = [54, 42, 48, 60, 52, 53, 24, 25, 26, 27, 23, 47, 28, 1, 0, 3, 2, 5, 8, 51, 11, 13, 12, 16, 19, 30, 50] #GARR
	custodian = [10]#, 6, 20, 21, 22]#WIDE
	#custodian = [4, 2, 34, 22, 29]#GEANT
	#custodian = [55, 37, 14, 35, 34]#GARR
	"""fo=open('path.txt','a')
	for i in range(len(nodes)):
	    node = nodes[i]
	    for j in range(len(custodian)):
		cust = custodian[j]
		path = self.view.shortest_path(node, cust)
		fo.write('%s:'%path)
	   	fo.write("\n")
	fo.close()"""
        # Route requests to original source and queries caches on the path
        self.controller.start_session(time, receiver, content, log)
        for u, v in path_links(path):
            self.controller.forward_request_hop(u, v)
            if self.view.has_cache(v):
                if self.controller.get_content(v):
                    serving_node = v
                    if v not in self.sources and self.count > warm_up_count and content in self.conts:
                        self.hit += 1
                        self.hits[int(content)-1] = self.count
                    break
            # No cache hits, get content from source
            self.controller.get_content(v)
            serving_node = v
        # Return content
	hopcount = len(self.view.shortest_path(receiver, serving_node))
        path = list(reversed(self.view.shortest_path(receiver, serving_node)))
        """for i in range(len(path)-1):
            print "LCE Link delay of %d - %d : %d" % (path[i], path[i+1], self.view.link_delay(path[i], path[i+1]))"""
        #if self.count > warm_up_count and ( not (serving_node == 10)):
            #print '\nLCE: Request # %d, Serving node %d, Content %d, Receiver %d, Source %d, Path %s' % (self.count, serving_node, content, receiver, source, path)
        for u, v in path_links(path):
            self.controller.forward_content_hop(u, v)
            if self.view.has_cache(v):
                # insert content
                self.controller.put_content(v)

        if self.count == warm_up_count + 1467699:
            c = 0
            d = 0
            #f1 = open('LCE_hits15','w')
            for x in self.hits:
                c += 1
                if not x == None:
                    #f1.write(str(c)+" "+str(x)+"\n")
                    d+=1
            print "LCE hits:",d, self.hit
        self.count += 1
        self.controller.end_session()



@register_strategy('OPTIMAL')
class OptimalCaching(Strategy):

    @inheritdoc(Strategy)
    def __init__(self, view, controller, **kwargs):
        super(OptimalCaching, self).__init__(view, controller)
	self.alpha = kwargs['alpha']
	self.network_cache = kwargs['network_cache']
	self.count=1
	self.hit=0
	self.hop=0
	self.core = 0
	self.custodian = 0

        self.change_counter = 1
        self.name_counter = 2

	alpha = self.alpha
	name = str(alpha)
	#print name
	name2 = name.replace(".","")
	#print name2
	self.num = 581527
	n = 581527
	#n = 66410
	#n = 35744
	self.cache_size = iround(n * self.network_cache)
	name3 = str(self.cache_size)
	#print name3
	name5 = name3.replace(".0","")
	#print name5
	self.name4 = str.join('%s'%name2,'%s'%name5)
	#print name4
	self.cache_mat = np.loadtxt(open('/home/adita/Greedy 08142017/Adita/GARR/All 1 lac/1/part1/%s.csv'%self.name4,"rb"),delimiter=",")
	#self.cache_mat = np.loadtxt(open('/home/adita/Greedy 08142017/Adita/WIDE/test/1/%s.csv'%self.name4,"rb"),delimiter=",")
	self.link = []
	self.load = []
        self.actual_cont = []
        self.hits = [None] * 581527
        self.delay = 0
        self.caches = [0,1,2,6,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,29] #WIDE
	self.receivers = [27, 28, 3, 5, 4, 7, 9, 8, 11, 13, 12, 15, 14, 17, 16, 19, 18] #WIDE
        #self.caches = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 14, 15, 16, 17, 22, 23, 24, 25, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 38, 39] #GEANT
	#self.receivers = [10, 11, 18, 19, 20, 21, 26, 37] #GEANT 
        #self.caches = [4, 55, 10, 21, 18, 49, 14, 35, 37, 22, 58, 20, 29, 59, 39, 31, 34, 36, 15, 46] #GARR
        #self.receivers = [1, 7, 8, 9, 11, 12, 19, 26, 28, 30, 32, 33, 41, 42, 43, 47, 48, 50, 53, 57, 60] #GARR

        self.conts = []
        f1 = open('/home/adita/Greedy 08142017/youtube_traces/All traces/f15','r')
        for f in f1:
            self.conts.append(int(f.rstrip()))
        print "Opt"
	self.sources = [10]#, 6]#, 20, 21, 22]#WIDE
        print "Shortest Paths:"#, self.network_cache
        for i in range(len(self.receivers)):
            for j in range(len(self.sources)):
                print self.view.shortest_path(self.receivers[i], self.sources[j])


    @inheritdoc(Strategy)
    def process_event(self, time, receiver, content, log):
	source = self.view.content_source(content)
        path = self.view.shortest_path(receiver, source)
        """for v in self.caches:
            if self.count > warm_up_count:# or self.count == warm_up_count+500000 or self.count == warm_up_count+1400000:
                if not self.view.cache_dump(v) == None:
                    print "Prev Opt Cache Dump of ", v, self.count, len(self.view.cache_dump(v))"""

        # Route requests to original source and queries caches on the path

#################changed 09052017
        if self.count == 1:
            name = '/home/adita/Greedy 08142017/Adita/GARR/All 1 lac/1/part1/matrix'+str(self.cache_size) #WIDE
            #name = '/home/adita/Greedy 08142017//Adita/WIDE/10939-1/matrix'+str(self.cache_size) #WIDE
            #name = '/home/adita/Greedy 08142017/Adita/icarus-0.5.0/GEANTmatrix'+str(self.cache_size) #GEANT
            f1 = open(name,'r')
            columns = []
            rec = []
            cont = []
            for f in f1:
                columns = f.split(' ')
                columns = [col.strip() for col in columns]
                rec.append(int(columns[0]))
                cont.append(int(columns[1])+1)
            #serving_node = 10
            for r1 in range(len(rec)):                
                self.controller.start_session(time, receiver, cont[r1], log, False)
                serving_node = rec[r1]
                self.controller.put_content(serving_node)
                self.controller.end_session(False)

        if self.change_counter == 100000 and self.count > warm_up_count and self.name_counter < 16:
            file_name = '/home/adita/Greedy 08142017/Adita/GARR/All 1 lac/1/part'+str(self.name_counter)
            self.cache_mat = np.loadtxt(open(file_name+'/%s.csv'%self.name4,"rb"),delimiter=",")
            #self.cache_mat = np.loadtxt(open('/home/adita/Greedy 08142017/Adita/WIDE/test/2/%s.csv'%self.name4,"rb"),delimiter=",")
            name = '/home/adita/Greedy 08142017/Adita/GARR/All 1 lac/1/part'+str(self.name_counter)+'/matrix'+str(self.cache_size) #WIDE
            #name = '/home/adita/Greedy 08142017//Adita/WIDE/10939-1/matrix'+str(self.cache_size) #WIDE
            #name = '/home/adita/Greedy 08142017/Adita/icarus-0.5.0/GEANTmatrix'+str(self.cache_size) #GEANT
            self.actual_cont = []
            if self.name_counter >= 2:
                with open('/home/adita/Greedy 08142017/youtube_traces/All 1 lac/part'+str(self.name_counter)+'/unique_cont', 'r') as f:
                    for content in f:
                        self.actual_cont.append(int(content.rstrip()))
            f1 = open(name,'r')
            columns = []
            rec = []
            cont = []
            for f in f1:
                columns = f.split(' ')
                columns = [col.strip() for col in columns]
                rec.append(int(columns[0]))
                if self.name_counter >= 2:
                    #print int(columns[1]), len(self.actual_cont)
                    cont.append(self.actual_cont[int(columns[1])])
                else:
                    cont.append(int(columns[1])+1)
            #serving_node = 10
            for r1 in range(len(rec)):                
                self.controller.start_session(time, receiver, cont[r1], log, False)
                serving_node = rec[r1]
                self.controller.put_content(serving_node)
                self.controller.end_session(False)
            print self.name_counter, self.count, self.change_counter
            self.change_counter = 0
            self.name_counter += 1

            #for v in self.caches:
                #print "New Opt Cache Dump of ", v,self.view.cache_dump(v)
            #self.count += 1
        #else:
#################
        if self.count > warm_up_count:
            self.controller.start_session(time, receiver, content, log)
            for u, v in path_links(path):
                self.controller.forward_request_hop(u, v)
                if self.view.has_cache(v):
                    if self.controller.get_content(v):
                        serving_node = v
                        if v not in self.sources and content in self.conts:
                            self.hit += 1
                            self.hits[int(content)-1] = self.count
                        break
                # No cache hits, get content from source
                self.controller.get_content(v)
                serving_node = v
            # Return content
            path = list(reversed(self.view.shortest_path(receiver, serving_node)))
            #for i in range(len(path)-1):
                #print "Opt Link delay of %d - %d : %d" % (path[i], path[i+1], self.view.link_delay(path[i], path[i+1]))
                #self.delay = self.delay + self.view.link_delay(path[i], path[i+1])
            #if self.count == 248335:
                #print "\nDelay:", self.delay
            #if self.count > warm_up_count and ( not (serving_node == 10)):
                #print '\nOpt: Request # %d, Serving node %d, Content %d, Receiver %d, Source %d, Path %s' % (self.count, serving_node, content, receiver, source, path)
            for i in range(0,len(path)-1):
	        u = path[i]
	        v = path[i+1]
                cache_row = self.cache_mat[v][:]
                self.controller.forward_content_hop(u, v)
                self.delay = self.delay + self.view.link_delay(u, v)
                if self.name_counter-1 >= 2 and self.name_counter-1 < 16:
                    #print "Buggg", self.name_counter-1, content, self.count
                    if not isinstance(content,int):
                        content = content.rstrip()
                    if cache_row[int(self.actual_cont.index(int(content)))] == 1:
                        self.controller.put_content(v)
                else:
                    #print "Bugggg",content,self.count,self.change_counter
                    if cache_row[int(content-1)] == 1:
                        self.controller.put_content(v)
                #print v, cache_row[int(content-1)]
            self.change_counter += 1

            if self.count == warm_up_count + 1467699:
                c = 0
                d = 0
                #f1 = open('Opt_hits15','w')
                for x in self.hits:
                    c += 1
                    if not x == None:
                        #f1.write(str(c)+" "+str(x)+"\n")
                        d += 1
                print "Opt hits:",d, self.hit
            self.count += 1
            #for v in self.caches:
                #print "New Opt Cache Dump of ", v,self.view.cache_dump(v)
       	    self.controller.end_session()
        else:
            #self.change_counter += 1
            self.count += 1


@register_strategy('CTR')
class CharacteristicTime(Strategy):
    """Characteristic time (Ch_time) strategy.
    
    In this strategy a copy of a content is replicated at any cache on the
    path between serving node and receiver. A information is maintained 
    """
    @inheritdoc(Strategy)
    def __init__(self, view, controller, symm_paths=True, **kwargs):
        super(CharacteristicTime, self).__init__(view, controller)
        self.symm_paths = symm_paths
	self.alpha = kwargs['alpha']
	self.network_cache = kwargs['network_cache']
	
    @inheritdoc(Strategy)
    def process_event(self, time, receiver, content, log):
	t2 = time
	z1 = 0
	z4 = 0
	global index2
	global source
	global a
	global d
	global c
	global e
	global s1
	global path
	alpha = self.alpha
	#n_s = self.network_cache
	n = 10000
	cache_size = 10000 * self.network_cache * 21
	# get all required data
	z = receiver
	s4 = self.view.content_source(content)
	if t2 < 0.35:
	    a =  [[0 for x in range(2)] for x in range(1500)]
	    d =  [[0 for x in range(2)] for x in range(1500)]
	    c =  [[0 for x in range(2)] for x in range(1500)]
	    e =  [[0 for x in range(2)] for x in range(1500)]
	    content_id = a[z][:]
	    cache_id = e[z][:]
	    charac_time = d[z][:]
	    rec_time = c[z][:]
	    rec_node = receiver
	    x = rec_node-1
	    if content in content_id:
	        index_id = []
	        char_time1 = []
	        for i in range (0,len(content_id)):
		    if content_id[i] == content:
		       index_id.append(i)
		       xd = rec_time[i]+charac_time[i]
		       char_time1.append(xd)
	        char_time = max(char_time1)
		index1 = char_time1.index(char_time)
	        t1 = time
	        if t1 < char_time:
	            index3 = index_id[index1]
	            s1 = cache_id[index3]
		    #fo = open("ctr.txt", "a")
	    	    #fo.write('%d' % s1)
	            #fo.write("\n")
	            #fo.close()
		    if self.view.cache_lookup(s1,content):
			#fo = open("ctr_use.txt", "a")
	    	        #fo.write('%d' % s1)
	                #fo.write("\n")
	                #fo.close()
		        path = self.view.shortest_path(receiver, s1)
		    else:
	                path = self.view.shortest_path(receiver, s4)
	    else:
		r = random.uniform(0, 1.0)
		if r >= 0:
		    plen = []
		    sou1 = self.view.content_locations(content)
		    sou = list(sou1)
		    sou.remove(s4)
		    if sou:
		        for i in range (0,len(sou)):
		            pl = self.view.shortest_path(receiver, sou[i])
		            plen.append(pl)
		        ind = plen.index(min(plen))
		        sour = sou[ind]
		        #fo = open("neighbor.txt", "a")
	    	        #fo.write('%d' % sour)
	                #fo.write("\n")
	                #fo.close()
		        if self.view.cache_lookup(sour,content):
		            gain = len(self.view.shortest_path(receiver,sour)) - len(self.view.shortest_path(receiver,s4))
		            #fo = open("neighbor_gain.txt", "a")
	    	            #fo.write('%d' % gain)
	                    #fo.write("\n")
	                    #fo.close()
			    if gain < 0:
		                path = self.view.shortest_path(receiver, sour)
		            else:
	                        path = self.view.shortest_path(receiver, s4)
		    else:
	                path = self.view.shortest_path(receiver, s4)
		else:
	            path = self.view.shortest_path(receiver, s4)
	    index2 = charac_time.index(min(charac_time))
            # Route requests to original source and queries caches on the path
            self.controller.start_session(time, receiver, content, log)
	    b = time
            for hop in range(1, len(path)):
                u = path[hop - 1]
                v = path[hop]
                self.controller.forward_request_hop(u, v)
                if self.view.has_cache(v):
                    if self.controller.get_content(v):
                        serving_node = v
			z4=1
                        break
                # No cache hits, get content from source
		v = self.view.content_source(content)
		self.controller.get_content(v)
            	serving_node = v
            # Return content
            path = list(reversed(path[:hop + 1])) if self.symm_paths \
                            else self.view.shortest_path(serving_node, receiver)
        # Leave a copy of the content only in the cache one level down the hit
        # caching node
            copied = False
            for u, v in path_links(path):
                self.controller.forward_content_hop(u, v)
                if not copied and v != receiver and self.view.has_cache(v):
                    self.controller.put_content(v)
                    copied = True
	    self.controller.end_session()
            if s4 is not serving_node:
	       content_id[index2] = content
	       cache_id[index2] = serving_node
	       pdf = icarus.TruncatedZipfDist(alpha,n).pdf
	       charac_time1 = icarus.che_characteristic_time(pdf,cache_size,content)
	       #c_time1 = icarus.che_characteristic_time(pdf,cache_size)
	       #charac_time1 = c_time1[0]
	       charac_time[index2] = charac_time1
	       rec_time[index2] = b
	       a[z][:] = content_id
	       d[z][:] = charac_time
	       c[z][:] = rec_time
	       e[z][:] = cache_id
	else:
	    content_id = a[z][:]
	    cache_id = e[z][:]
	    charac_time = d[z][:]
	    rec_time = c[z][:]
	    rec_node = receiver
	    x = rec_node-1
	    if content in content_id:
	        index_id = []
	        char_time1 = []
	        for i in range (0,len(content_id)):
		    if content_id[i] == content:
		       index_id.append(i)
		       xd = rec_time[i]+charac_time[i]
		       char_time1.append(xd)
	        char_time = max(char_time1)
		index1 = char_time1.index(char_time)
	        t1 = time
	        if t1 < char_time:
	            index3 = index_id[index1]
	            s1 = cache_id[index3]
		    #fo = open("ctr.txt", "a")
	    	    #fo.write('%d' % s1)
	            #fo.write("\n")
	            #fo.close()
		    if self.view.cache_lookup(s1,content):
			#fo = open("ctr_use.txt", "a")
	    	        #fo.write('%d' % s1)
	                #fo.write("\n")
	                #fo.close()
		        path = self.view.shortest_path(receiver, s1)
		    else:
	                path = self.view.shortest_path(receiver, s4)
	    else:
		r = random.uniform(0, 1.0)
		if r >= 0:
		    plen = []
		    sou1 = self.view.content_locations(content)
		    sou = list(sou1)
		    sou.remove(s4)
		    if sou:
		        for i in range (0,len(sou)):
		            pl = self.view.shortest_path(receiver, sou[i])
		            plen.append(pl)
		        ind = plen.index(min(plen))
		        sour = sou[ind]
		        #fo = open("neighbor.txt", "a")
	    	        #fo.write('%d' % sour)
	                #fo.write("\n")
	                #fo.close()
		        if self.view.cache_lookup(sour,content):
		            gain = len(self.view.shortest_path(receiver,sour)) - len(self.view.shortest_path(receiver,s4))
		            #fo = open("neighbor_gain.txt", "a")
	    	            #fo.write('%d' % gain)
	                    #fo.write("\n")
	                    #fo.close()
			    if gain < 0:
		                path = self.view.shortest_path(receiver, sour)
		            else:
	                        path = self.view.shortest_path(receiver, s4)
		    else:
	                path = self.view.shortest_path(receiver, s4)
		else:
	            path = self.view.shortest_path(receiver, s4)
	    index2 = charac_time.index(min(charac_time))
            # Route requests to original source and queries caches on the path
            self.controller.start_session(time, receiver, content, log)
	    b = time
            for hop in range(1, len(path)):
                u = path[hop - 1]
                v = path[hop]
                self.controller.forward_request_hop(u, v)
                if self.view.has_cache(v):
                    if self.controller.get_content(v):
                        serving_node = v
			z4=1
                        break
                # No cache hits, get content from source
		v = self.view.content_source(content)
                self.controller.get_content(v)
            	serving_node = v
            # Return content
            path = list(reversed(path[:hop + 1])) if self.symm_paths \
                            else self.view.shortest_path(serving_node, receiver)
        # Leave a copy of the content only in the cache one level down the hit
        # caching node
            copied = False
            for u, v in path_links(path):
                self.controller.forward_content_hop(u, v)
                if not copied and v != receiver and self.view.has_cache(v):
                    self.controller.put_content(v)
                    copied = True
	    self.controller.end_session()
            if s4 is not serving_node:
	       content_id[index2] = content
	       cache_id[index2] = serving_node
	       pdf = icarus.TruncatedZipfDist(alpha,n).pdf
	       charac_time1 = icarus.che_characteristic_time(pdf,cache_size,content)
	       #c_time1 = icarus.che_characteristic_time(pdf,cache_size)
	       #charac_time1 = c_time1[0]
	       charac_time[index2] = charac_time1
	       rec_time[index2] = b
	       a[z][:] = content_id
	       d[z][:] = charac_time
	       c[z][:] = rec_time
	       e[z][:] = cache_id
	    

@register_strategy('CTR_LCE')
class CharacteristicTimeLCE(Strategy):
    """Characteristic time (Ch_time) strategy.
    
    In this strategy a copy of a content is replicated at any cache on the
    path between serving node and receiver. A information is maintained 
    """
    @inheritdoc(Strategy)
    def __init__(self, view, controller, symm_paths=True, **kwargs):
        super(CharacteristicTimeLCE, self).__init__(view, controller)
        self.symm_paths = symm_paths
	self.alpha = kwargs['alpha']
	self.network_cache = kwargs['network_cache']
	self.count=0
	self.hit=0
	
    @inheritdoc(Strategy)
    def process_event(self, time, receiver, content, log):
	t2 = time
	z1 = 0
	z4 = 0
	global index2
	global source
	global a
	global d
	global c
	global e
	global s1
	global path
	alpha = self.alpha
	#n_s = self.network_cache
	n = 10000
	cache_size = 10000 * self.network_cache * 21
	# get all required data
	z = receiver
	s4 = self.view.content_source(content)
	if t2 < 0.35:
	    a =  [[0 for x in range(2)] for x in range(300)]
	    d =  [[0 for x in range(2)] for x in range(300)]
	    c =  [[0 for x in range(2)] for x in range(300)]
	    e =  [[0 for x in range(2)] for x in range(300)]
	    content_id = a[z][:]
	    cache_id = e[z][:]
	    charac_time = d[z][:]
	    rec_time = c[z][:]
	    rec_node = receiver
	    x = rec_node-1
	    if content in content_id:
	        index_id = []
	        char_time1 = []
	        for i in range (0,len(content_id)):
		    if content_id[i] == content:
		       index_id.append(i)
		       xd = rec_time[i]+charac_time[i]
		       char_time1.append(xd)
	        char_time = max(char_time1)
		index1 = char_time1.index(char_time)
	        t1 = time
	        if t1 < char_time:
	            index3 = index_id[index1]
	            s1 = cache_id[index3]
		    #fo = open("ctr.txt", "a")
	    	    #fo.write('%d' % s1)
	            #fo.write("\n")
	            #fo.close()
		    if self.view.cache_lookup(s1,content):
			#fo = open("ctr_use.txt", "a")
	    	        #fo.write('%d' % s1)
	                #fo.write("\n")
	                #fo.close()
		        path = self.view.shortest_path(receiver, s1)
		    else:
	                path = self.view.shortest_path(receiver, s4)
	    else:
		r = random.uniform(0, 1.0)
		if r >= 0:
		    plen = []
		    sou1 = self.view.content_locations(content)
		    sou = list(sou1)
		    sou.remove(s4)
		    if sou:
		        for i in range (0,len(sou)):
		            pl = self.view.shortest_path(receiver, sou[i])
		            plen.append(pl)
		        ind = plen.index(min(plen))
		        sour = sou[ind]
		        #fo = open("neighbor.txt", "a")
	    	        #fo.write('%d' % sour)
	                #fo.write("\n")
	                #fo.close()
		        if self.view.cache_lookup(sour,content):
		            gain = len(self.view.shortest_path(receiver,sour)) - len(self.view.shortest_path(receiver,s4))
		            #fo = open("neighbor_gain.txt", "a")
	    	            #fo.write('%d' % gain)
	                    #fo.write("\n")
	                    #fo.close()
			    path = self.view.shortest_path(receiver, sour)
		        else:
	                    path = self.view.shortest_path(receiver, s4)
		    else:
	                path = self.view.shortest_path(receiver, s4)
		else:
	            path = self.view.shortest_path(receiver, s4)
	    index2 = charac_time.index(min(charac_time))
            # Route requests to original source and queries caches on the path
            self.controller.start_session(time, receiver, content, log)
	    b = time
            for hop in range(1, len(path)):
                u = path[hop - 1]
                v = path[hop]
                self.controller.forward_request_hop(u, v)
                if self.view.has_cache(v):
                    if self.controller.get_content(v):
                        serving_node = v
			z4=1
                        break
                # No cache hits, get content from source
		v = self.view.content_source(content)
		self.controller.get_content(v)
            	serving_node = v
            # Return content
            path = list(reversed(path[:hop + 1])) if self.symm_paths \
                            else self.view.shortest_path(serving_node, receiver)
        # Leave a copy of the content only in the cache one level down the hit
        # caching node
            for u, v in path_links(path):
                self.controller.forward_content_hop(u, v)
            	if self.view.has_cache(v):
                # insert content
                    self.controller.put_content(v)
	    self.count+=1
	    if self.count>100000:
	    	self.hit+=len(self.view.shortest_path(receiver, serving_node))
	    if self.count%200000==0:
	    	fo = open("ctr.txt", "a")
	    	fo.write('%s, ' % self.alpha)
	    	fo.write('%s:' % self.network_cache)
	    	fo.write(' %d' % self.hit)
	    	fo.write("\n")
	    	fo.close()
	    self.controller.end_session()
            if s4 is not serving_node:
	       content_id[index2] = content
	       cache_id[index2] = serving_node
	       pdf = icarus.TruncatedZipfDist(alpha,n).pdf
	       charac_time1 = icarus.che_characteristic_time(pdf,cache_size,content)
	       #c_time1 = icarus.che_characteristic_time(pdf,cache_size)
	       #charac_time1 = c_time1[0]
	       charac_time[index2] = charac_time1
	       rec_time[index2] = b
	       a[z][:] = content_id
	       d[z][:] = charac_time
	       c[z][:] = rec_time
	       e[z][:] = cache_id
	else:
	    content_id = a[z][:]
	    cache_id = e[z][:]
	    charac_time = d[z][:]
	    rec_time = c[z][:]
	    rec_node = receiver
	    x = rec_node-1
	    if content in content_id:
	        index_id = []
	        char_time1 = []
	        for i in range (0,len(content_id)):
		    if content_id[i] == content:
		       index_id.append(i)
		       xd = rec_time[i]+charac_time[i]
		       char_time1.append(xd)
	        char_time = max(char_time1)
		index1 = char_time1.index(char_time)
	        t1 = time
	        if t1 < char_time:
	            index3 = index_id[index1]
	            s1 = cache_id[index3]
		    #fo = open("ctr.txt", "a")
	    	    #fo.write('%d' % s1)
	            #fo.write("\n")
	            #fo.close()
		    if self.view.cache_lookup(s1,content):
			#fo = open("ctr_use.txt", "a")
	    	        #fo.write('%d' % s1)
	                #fo.write("\n")
	                #fo.close()
		        path = self.view.shortest_path(receiver, s1)
		    else:
	                path = self.view.shortest_path(receiver, s4)
	    else:
		r = random.uniform(0, 1.0)
		if r >= 0:
		    plen = []
		    sou1 = self.view.content_locations(content)
		    sou = list(sou1)
		    sou.remove(s4)
		    if sou:
		        for i in range (0,len(sou)):
		            pl = self.view.shortest_path(receiver, sou[i])
		            plen.append(pl)
		        ind = plen.index(min(plen))
		        sour = sou[ind]
		        #fo = open("neighbor.txt", "a")
	    	        #fo.write('%d' % sour)
	                #fo.write("\n")
	                #fo.close()
		        if self.view.cache_lookup(sour,content):
		            gain = len(self.view.shortest_path(receiver,sour)) - len(self.view.shortest_path(receiver,s4))
		            #fo = open("neighbor_gain.txt", "a")
	    	            #fo.write('%d' % gain)
	                    #fo.write("\n")
	                    #fo.close()
			    path = self.view.shortest_path(receiver, sour)
		        else:
	                    path = self.view.shortest_path(receiver, s4)
		    else:
	                path = self.view.shortest_path(receiver, s4)
		else:
	            path = self.view.shortest_path(receiver, s4)
	    index2 = charac_time.index(min(charac_time))
            # Route requests to original source and queries caches on the path
            self.controller.start_session(time, receiver, content, log)
	    b = time
            for hop in range(1, len(path)):
                u = path[hop - 1]
                v = path[hop]
                self.controller.forward_request_hop(u, v)
                if self.view.has_cache(v):
                    if self.controller.get_content(v):
                        serving_node = v
			z4=1
                        break
                # No cache hits, get content from source
		v = self.view.content_source(content)
                self.controller.get_content(v)
            	serving_node = v
            # Return content
            path = list(reversed(path[:hop + 1])) if self.symm_paths \
                            else self.view.shortest_path(serving_node, receiver)
        # Leave a copy of the content only in the cache one level down the hit
        # caching node
            for u, v in path_links(path):
                self.controller.forward_content_hop(u, v)
            	if self.view.has_cache(v):
                # insert content
                    self.controller.put_content(v)
	    self.count+=1
	    if self.count>100000:
	    	self.hit+=len(self.view.shortest_path(receiver, serving_node))
	    if self.count%200000==0:
	    	fo = open("ctr.txt", "a")
	    	fo.write('%s, ' % self.alpha)
	    	fo.write('%s:' % self.network_cache)
	    	fo.write(' %d' % self.hit)
	    	fo.write("\n")
	    	fo.close()
	    self.controller.end_session()
            if s4 is not serving_node:
	       content_id[index2] = content
	       cache_id[index2] = serving_node
	       pdf = icarus.TruncatedZipfDist(alpha,n).pdf
	       charac_time1 = icarus.che_characteristic_time(pdf,cache_size,content)
	       #c_time1 = icarus.che_characteristic_time(pdf,cache_size)
	       #charac_time1 = c_time1[0]
	       charac_time[index2] = charac_time1
	       rec_time[index2] = b
	       a[z][:] = content_id
	       d[z][:] = charac_time
	       c[z][:] = rec_time
	       e[z][:] = cache_id
	    










@register_strategy('LCD')
class LeaveCopyDown(Strategy):
    """Leave Copy Down (LCD) strategy.
    
    According to this strategy, one copy of a content is replicated only in
    the caching node you hop away from the serving node in the direction of
    the receiver. This strategy is described in [2]_.
    
    Rereferences
    ------------
    ..[2] N. Laoutaris, H. Che, i. Stavrakakis, The LCD interconnection of LRU
          caches and its analysis. 
          Available: http://cs-people.bu.edu/nlaout/analysis_PEVA.pdf 
    """

    @inheritdoc(Strategy)
    def __init__(self, view, controller, **kwargs):
        super(LeaveCopyDown, self).__init__(view, controller)
	self.count = 0
	self.hit = 0
	self.hop = 0
	self.core = 0
	self.custodian = 0
	self.alpha = kwargs['alpha']
	self.network_cache = kwargs['network_cache']
	self.link = []
        self.hits = [None] * 581527
	self.load = []
	self.sources = [10]
        self.caches = [4, 55, 10, 21, 18, 49, 14, 35, 37, 22, 58, 20, 29, 59, 39, 31, 34, 36, 15, 46] #GARR
        print "LCD"

    @inheritdoc(Strategy)
    def process_event(self, time, receiver, content, log):
        # get all required data
        source = self.view.content_source(content)
        path = self.view.shortest_path(receiver, source)
        #caches = [0,1,2,6,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,29]
        """for v in self.caches:
            if self.count == warm_up_count or self.count == warm_up_count+500000 or self.count == warm_up_count+1400000:
                if not self.view.cache_dump(v) == None:
                    print "LCD Cache Dump of ", v, self.count,len(self.view.cache_dump(v))"""
	# Route requests to original source and queries caches on the path
        self.controller.start_session(time, receiver, content, log)
###############################################################################################changed####08292017
        """if self.count < loop_count:
            for u, v in path_links(path):
                self.controller.forward_request_hop(u, v)
                if self.view.has_cache(v):
                    if self.controller.get_content(v):
                        serving_node = v
                        break
                # No cache hits, get content from source
                self.controller.get_content(v)
                serving_node = v
            # Return content
	    hopcount = len(self.view.shortest_path(receiver, serving_node))
            path = list(reversed(self.view.shortest_path(receiver, serving_node)))
            #if self.count > print_count:
                #print '\nLCD: Request # %d, Serving node %d, Content %d, Receiver %d, Source %d, Path %s' % (self.count, serving_node, content, receiver, source, path)
            for u, v in path_links(path):
                self.controller.forward_content_hop(u, v)
                if self.view.has_cache(v):
                    # insert content
                    self.controller.put_content(v)"""
        if self.count < 0:
            pass

        else:
            for u, v in path_links(path):
                self.controller.forward_request_hop(u, v)
                if self.view.has_cache(v):
                    if self.controller.get_content(v):
                        serving_node = v
                        if v not in self.sources and self.count > warm_up_count:
                            self.hits[int(content)-1] = self.count
                        break
            else:
                # No cache hits, get content from source
                self.controller.get_content(v)
                serving_node = v
            # Return content
	    hopcount = len(self.view.shortest_path(receiver, serving_node))
            path = list(reversed(self.view.shortest_path(receiver, serving_node)))
            #if self.count > print_count:
                #print '\nLCD: Request # %d, Serving node %d, Content %d, Receiver %d, Source %d, Path %s' % (self.count, serving_node, content, receiver, source, path)
            # Leave a copy of the content only in the cache one level down the hit
            # caching node
            copied = False
            for u, v in path_links(path):
                self.controller.forward_content_hop(u, v)
                if not copied and v != receiver and self.view.has_cache(v):
                    self.controller.put_content(v)
                    copied = True

        if self.count == warm_up_count + 1467699:
            c = 0
            d = 0
            #f1 = open('LCD_hits200All','w')
            for x in self.hits:
                c += 1
                if not x == None:
                    #f1.write(str(c)+" "+str(x)+"\n")
                    d+=1
            print "LCD hits:",d

        self.count += 1
        self.controller.end_session()


@register_strategy('PROB_CACHE')
class ProbCache(Strategy):
    """ProbCache strategy [4]_
    
    This strategy caches content objects probabilistically on a path with a
    probability depending on various factors, including distance from source
    and destination and caching space available on the path.
    
    This strategy was originally proposed in [3]_ and extended in [4]_. This
    class implements the extended version described in [4]_. In the extended
    version of ProbCache the :math`x/c` factor of the ProbCache equation is
    raised to the power of :math`c`.
    
    References
    ----------
    ..[3] I. Psaras, W. Chai, G. Pavlou, Probabilistic In-Network Caching for
          Information-Centric Networks, in Proc. of ACM SIGCOMM ICN '12
          Available: http://www.ee.ucl.ac.uk/~uceeips/prob-cache-icn-sigcomm12.pdf
    ..[4] I. Psaras, W. Chai, G. Pavlou, In-Network Cache Management and
          Resource Allocation for Information-Centric Networks, IEEE
          Transactions on Parallel and Distributed Systems, 22 May 2014
          Available: http://doi.ieeecomputersociety.org/10.1109/TPDS.2013.304
    """

    @inheritdoc(Strategy)
    def __init__(self, view, controller, t_tw=10, **kwargs):
        super(ProbCache, self).__init__(view, controller)
        self.t_tw = t_tw
        self.cache_size1 = view.cache_nodes(size=True)
	self.count = 0
	self.sources = [10]
	self.hit = 0
	self.hop = 0
	self.core = 0
	self.custodian = 0
	self.alpha = kwargs['alpha']
	self.network_cache = kwargs['network_cache']
	self.link = []
	self.load = []
        self.hits = [None] * 581527
        self.caches = [4, 55, 10, 21, 18, 49, 14, 35, 37, 22, 58, 20, 29, 59, 39, 31, 34, 36, 15, 46] #GARR
        print "PC"
    
    @inheritdoc(Strategy)
    def process_event(self, time, receiver, content, log):
        # get all required data
        source = self.view.content_source(content)
        path = self.view.shortest_path(receiver, source)
        #caches = [0,1,2,6,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,29]
        """for v in self.caches:
            if self.count == warm_up_count or self.count == warm_up_count+500000 or self.count == warm_up_count+1400000:
                if not self.view.cache_dump(v) == None:
                    print "Prob Cache Cache Dump of ", v, self.count,len(self.view.cache_dump(v))"""
        # Route requests to original source and queries caches on the path
        self.controller.start_session(time, receiver, content, log)
###############################################################################################changed####08312017
        """if self.count < loop_count:
            for u, v in path_links(path):
                self.controller.forward_request_hop(u, v)
                if self.view.has_cache(v):
                    if self.controller.get_content(v):
                        serving_node = v
                        break
                # No cache hits, get content from source
                self.controller.get_content(v)
                serving_node = v
            # Return content
	    hopcount = len(self.view.shortest_path(receiver, serving_node))
            path = list(reversed(self.view.shortest_path(receiver, serving_node)))
            if self.count > print_count:
                print '\nProb: Request # %d, Serving node %d, Content %d, Receiver %d, Source %d, Path %s' % (self.count, serving_node, content, receiver, source, path)
            for u, v in path_links(path):
                self.controller.forward_content_hop(u, v)
                if self.view.has_cache(v):
                    # insert content
                    self.controller.put_content(v)"""
        if self.count < 0:
            pass

        else:
            for hop in range(1, len(path)):
                u = path[hop - 1]
                v = path[hop]
                self.controller.forward_request_hop(u, v)
                if self.view.has_cache(v):
                    if self.controller.get_content(v):
                        serving_node = v
                        if v not in self.sources and self.count > warm_up_count:
                            self.hits[int(content)-1] = self.count
                        break
            else:
                # No cache hits, get content from source
                self.controller.get_content(v)
                serving_node = v
            # Return content
	    hopcount = len(self.view.shortest_path(receiver, serving_node))
            path = list(reversed(self.view.shortest_path(receiver, serving_node)))
            #if self.count > print_count:
                #print '\nProb: Request # %d, Serving node %d, Content %d, Receiver %d, Source %d, Path %s' % (self.count, serving_node, content, receiver, source, path)
            c = len([v for v in path if self.view.has_cache(v)])
            x = 0.0
            for hop in range(1, len(path)):
                u = path[hop - 1]
                v = path[hop]    
                N = sum([self.cache_size1[n] for n in path[hop - 1:]
                         if n in self.cache_size1])
                if v in self.cache_size1:
                    x += 1
                self.controller.forward_content_hop(u, v)
                if v != receiver and v in self.cache_size1:
                    # The (x/c) factor raised to the power of "c" according to the
                    # extended version of ProbCache published in IEEE TPDS
                    prob_cache = float(N)/(self.t_tw * self.cache_size1[v])*(x/c)**c
                    if random.random() < prob_cache:
                        self.controller.put_content(v)

        if self.count == warm_up_count + 1467699:
            c = 0
            d = 0
            #f1 = open('PC_hits200All','w')
            for x in self.hits:
                c += 1
                if not x == None:
                    #f1.write(str(c)+" "+str(x)+"\n")
                    d+=1
            print "PC hits:",d

        self.count += 1
        self.controller.end_session()


@register_strategy('CL4M')
class CacheLessForMore(Strategy):
    """Cache less for more strategy [5]_.
    
    References
    ----------
    ..[5] W. Chai, D. He, I. Psaras, G. Pavlou, Cache Less for More in
          Information-centric Networks, in IFIP NETWORKING '12
          Available: http://www.ee.ucl.ac.uk/~uceeips/centrality-networking12.pdf
    """

    @inheritdoc(Strategy)
    def __init__(self, view, controller, use_ego_betw=False, **kwargs):
        super(CacheLessForMore, self).__init__(view, controller)
	self.count = 0
	self.hit = 0
	self.hop = 0
	self.core = 0
	self.custodian = 0
	self.sources = [10]
	self.alpha = kwargs['alpha']
	self.network_cache = kwargs['network_cache']
	self.link = []
	self.load = []
        self.hits = [None] * 581527
        self.caches =  [4, 55, 10, 21, 18, 49, 14, 35, 37, 22, 58, 20, 29, 59, 39, 31, 34, 36, 15, 46] #GARR
        print "CL4M"
        topology = view.topology()
        if use_ego_betw:
            self.betw = dict((v, nx.betweenness_centrality(nx.ego_graph(topology, v))[v])
                             for v in topology.nodes_iter())
        else:
            self.betw = nx.betweenness_centrality(topology)
    
    @inheritdoc(Strategy)
    def process_event(self, time, receiver, content, log):
        # get all required data
        source = self.view.content_source(content)
        path = self.view.shortest_path(receiver, source)
        #caches = [0,1,2,6,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,29]
        """for v in self.caches:
            if self.count == warm_up_count or self.count == warm_up_count+500000 or self.count == warm_up_count+1400000:
                if not self.view.cache_dump(v) == None:
                    print "CL4M Cache Dump of ", v, self.count,len(self.view.cache_dump(v))"""
        # Route requests to original source and queries caches on the path
        self.controller.start_session(time, receiver, content, log)
###############################################################################################changed####08312017
        """if self.count < loop_count:
            for u, v in path_links(path):
                self.controller.forward_request_hop(u, v)
                if self.view.has_cache(v):
                    if self.controller.get_content(v):
                        serving_node = v
                        break
                # No cache hits, get content from source
                self.controller.get_content(v)
                serving_node = v
            # Return content
	    hopcount = len(self.view.shortest_path(receiver, serving_node))
            path = list(reversed(self.view.shortest_path(receiver, serving_node)))
            #if self.count > print_count:
                #print '\nCL4M: Request # %d, Serving node %d, Content %d, Receiver %d, Source %d, Path %s' % (self.count, serving_node, content, receiver, source, path)
            for u, v in path_links(path):
                self.controller.forward_content_hop(u, v)
                if self.view.has_cache(v):
                    # insert content
                    self.controller.put_content(v)"""
        if self.count < 0:
            pass

        else:
            for u, v in path_links(path):
                self.controller.forward_request_hop(u, v)
                if self.view.has_cache(v):
                    if self.controller.get_content(v):
                        serving_node = v
                        if v not in self.sources and self.count > warm_up_count:
                            self.hits[int(content)-1] = self.count
                        break
            # No cache hits, get content from source
            else:
                self.controller.get_content(v)
                serving_node = v
            # Return content
	    hopcount = len(self.view.shortest_path(receiver, serving_node))
            path = list(reversed(self.view.shortest_path(receiver, serving_node)))
            #if self.count > print_count:
                #print '\nCL4M: Request # %d, Serving node %d, Content %d, Receiver %d, Source %d, Path %s' % (self.count, serving_node, content, receiver, source, path)
            # get the cache with maximum betweenness centrality
            # if there are more than one cache with max betw then pick the one
            # closer to the receiver
            max_betw = -1
            designated_cache = None
            for v in path[1:]:
                if self.view.has_cache(v):
                    if self.betw[v] >= max_betw:
                        max_betw = self.betw[v]
                        designated_cache = v
            # Forward content
            for u, v in path_links(path):
                self.controller.forward_content_hop(u, v)
                if v == designated_cache:
                    self.controller.put_content(v)


        if self.count == warm_up_count + 1467699:
            c = 0
            d = 0
            #f1 = open('CL4M_hits200All','w')
            for x in self.hits:
                c += 1
                if not x == None:
                    #f1.write(str(c)+" "+str(x)+"\n")
                    d+=1
            print "CL4M hits:",d

        self.count += 1
        self.controller.end_session()  
        

@register_strategy('NRR')
class NearestReplicaRouting(Strategy):
    """Ideal Nearest Replica Routing (NRR) strategy.
    
    In this strategy, a request is forwarded to the topologically close node
    holding a copy of the requested item. This strategy is ideal, as it is
    implemented assuming that each node knows the nearest replica of a content
    without any signalling
    
    On the return path, content can be caching according to a variety of
    metacaching policies. LCE and LCD are currently supported.
    """

    @inheritdoc(Strategy)
    def __init__(self, view, controller, metacaching, **kwargs):
        super(NearestReplicaRouting, self).__init__(view, controller)
        if metacaching not in ('LCE', 'LCD'):
            raise ValueError("Metacaching policy %s not supported" % metacaching)
        self.metacaching = metacaching
        
    @inheritdoc(Strategy)
    def process_event(self, time, receiver, content, log):
        # get all required data
        locations = self.view.content_locations(content)
        nearest_replica = min(locations, 
                              key=lambda s: sum(self.view.shortest_path(receiver, s)))
        # Route request to nearest replica
        self.controller.start_session(time, receiver, content, log)
        self.controller.forward_request_path(receiver, nearest_replica)
        self.controller.get_content(nearest_replica)
        # Now we need to return packet and we have options
        path = list(reversed(self.view.shortest_path(receiver, nearest_replica)))
        if self.metacaching == 'LCE':
            for u, v in path_links(path):
                self.controller.forward_content_hop(u, v)
                if self.view.has_cache(v) and not self.view.cache_lookup(v, content):
                    self.controller.put_content(v)
        elif self.metacaching == 'LCD':
            copied = False
            for u, v in path_links(path):
                self.controller.forward_content_hop(u, v)
                if not copied and v != receiver and self.view.has_cache(v):
                    self.controller.put_content(v)
                    copied = True
        else:
            raise ValueError('Metacaching policy %s not supported'
                             % self.metacaching)
        self.controller.end_session()


@register_strategy('RAND_BERNOULLI')
class RandomBernoulli(Strategy):
    """Bernoulli random cache insertion.
    
    In this strategy, a content is randomly inserted in a cache on the path
    from serving node to receiver with probability *p*.
    """

    @inheritdoc(Strategy)
    def __init__(self, view, controller, p=0.2, **kwargs):
        super(RandomBernoulli, self).__init__(view, controller)
        self.p = p
    
    @inheritdoc(Strategy)
    def process_event(self, time, receiver, content, log):
        # get all required data
        source = self.view.content_source(content)
        path = self.view.shortest_path(receiver, source)
        # Route requests to original source and queries caches on the path
        self.controller.start_session(time, receiver, content, log)
        for u, v in path_links(path):
            self.controller.forward_request_hop(u, v)
            if self.view.has_cache(v):
                if self.controller.get_content(v):
                    serving_node = v
                    break
        else:
            # No cache hits, get content from source
            self.controller.get_content(v)
            serving_node = v
        # Return content
        path =  list(reversed(self.view.shortest_path(receiver, serving_node)))
        for u, v in path_links(path):
            self.controller.forward_content_hop(u, v)
            if v != receiver and self.view.has_cache(v):
                if random.random() < self.p:
                    self.controller.put_content(v)
        self.controller.end_session()

@register_strategy('RAND_CHOICE')
class RandomChoice(Strategy):
    """Random choice strategy
    
    This strategy stores the served content exactly in one single cache on the
    path from serving node to receiver selected randomly.
    """

    @inheritdoc(Strategy)
    def __init__(self, view, controller, **kwargs):
        super(RandomChoice, self).__init__(view, controller)
	self.count = 0
	self.hit = 0
	self.hop = 0
	self.core = 0
	self.custodian = 0
	self.alpha = kwargs['alpha']
	self.network_cache = kwargs['network_cache']
	self.load = []
	self.link = []
        self.caches =  [4, 55, 10, 21, 18, 49, 14, 35, 37, 22, 58, 20, 29, 59, 39, 31, 34, 36, 15, 46] #GARR
    
    @inheritdoc(Strategy)
    def process_event(self, time, receiver, content, log):
        # get all required data
        source = self.view.content_source(content)
        path = self.view.shortest_path(receiver, source)
        #caches = [0,1,2,6,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,29]
        """for v in self.caches:
            if self.count == warm_up_count or self.count == warm_up_count+500000 or self.count == warm_up_count+1400000:
                if not self.view.cache_dump(v) == None:
                    print "RAND Cache Dump of ", v, self.count,len(self.view.cache_dump(v))"""
        # Route requests to original source and queries caches on the path
        self.controller.start_session(time, receiver, content, log)
        for u, v in path_links(path):
            self.controller.forward_request_hop(u, v)
            if self.view.has_cache(v):
                if self.controller.get_content(v):
                    serving_node = v
                    break
        else:
            # No cache hits, get content from source
            self.controller.get_content(v)
            serving_node = v
        # Return content
	hopcount = len(self.view.shortest_path(receiver, serving_node))
        path =  list(reversed(self.view.shortest_path(receiver, serving_node)))
        caches = [v for v in path[1:-1] if self.view.has_cache(v)]
        designated_cache = random.choice(caches) if len(caches) > 0 else None
        for u, v in path_links(path):
            self.controller.forward_content_hop(u, v)
            if v == designated_cache:
                self.controller.put_content(v)
        self.controller.end_session() 
