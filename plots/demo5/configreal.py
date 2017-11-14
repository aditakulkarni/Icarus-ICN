"""This module contains all configuration information used to run simulations.

Overview
========

This reference configuration file is divided into two parts.
The first part lists generic simulation parameters such as number of processes
to use, logging configuration and so on.
The second part builds an "experiment queue", i.e. a queue of configuration
parameters each representing one single experiment.

Each element of the queue must be an instance of the icarus.util.Tree class,
which is an object modelling a tree of hierarchically organized configuration
parameters. Alternatively nested dictionaries can be used instead of trees. In
this case Icarus will convert them to trees at runtime. It is however suggested
to use Tree objects because they provide methods that simplify the definition
of experiments.  

Experiment definition syntax
============================

This figure below represents the parameter structure accepted by Icarus:

 |
 |--- topology
 |        |----- name
 |        |----- topology arg 1
 |        |----- topology arg 2
 |        |----- ..............
 |        |----- topology arg N
 |
 |--- workload
 |        |----- name
 |        |----- workload arg 1
 |        |----- workload arg 2
 |        |----- ..............
 |        |----- workload arg N
 |
 |--- cache_placement
 |        |----- name
 |        |----- cache_placement arg 1
 |        |----- cache_placement arg 2
 |        |----- ......................
 |        |----- cache_placement arg N
 |
 |--- content_placement
 |        |----- name
 |        |----- content_placement arg 1
 |        |----- content_placement arg 2
 |        |----- .......................
 |        |----- content_placement arg N
 |
 |--- strategy
 |        |----- name
 |        |----- strategy arg 1
 |        |----- strategy arg 2
 |        |----- ..............
 |        |----- strategy arg N
 |
 |--- cache_policy
 |        |----- name
 |        |----- cache_policy arg 1
 |        |----- cache_policy arg 2
 |        |----- ..................
 |        |----- cache_policy arg N
 |


Here below are listed all components currently provided by Icarus and lists
all parameters for each of them

topology
--------

Path topology
 * name: PATH
 * args:
    * n: number of nodes

Tree topology
 * name: TREE
 * args:
    * h: height
    * k: branching factor
    
RocketFuel topologies
 * name: ROCKET_FUEL
 * args:
     * asn: ASN of topology selected (see resources/README.md for further info)
     * source_ratio: ratio of nodes to which attach a content source
     * ext_delay: delay of interdomain links

Internet Topology Zoo topologies 
 * name: GARR, GEANT, TISCALI, WIDE, GEANT_2, GARR_2, TISCALI_2
 * args: None


workload
--------

Stationary Zipf workload
 * name: STATIONARY
 * args:
    * alpha : float, the Zipf alpha parameter
    * n_contents: number of content objects
    * n_warmup: number of warmup requests
    * n_measured: number of measured requests
    * rate: requests rate

GlobeTraff workload
 * name: GLOBETRAFF
 * args:
    * reqs_file: the path to a GlobeTraff request file
    * contents_file: the path to a GlobeTraff content file

Trace-driven workload
 * name: TRACE_DRIVEN
 * args:
    * reqs_file: the path to the requests file
    * contents_file: the path to the contents file
    * n_contents: number of content objects
    * n_warmup: number of warmup requests
    * n_measured: number of measured requests


content_placement
-----------------
Uniform (content uniformly distributed among servers)
 * name: UNIFORM 
 * args: None 


cache_placement
---------------
 * name:
    * UNIFORM -> cache space uniformly spread across caches
    * CONSOLIDATED -> cache space consolidated among nodes with top betweenness centrality
    * BETWEENNESS_CENTRALITY -> cache space assigned to all candidate nodes proportionally to their betweenness centrality
    * DEGREE -> cache space assigned to all candidate nodes proportionally to their degree
 * args
    * For all:
       * network_cache: overall network cache (in number of entries) as fraction of content catalogue 
    * For CONSOLIDATED
       * spread: The fraction of top centrality nodes on which caches are deployed (optional, default: 0.5)


strategy
--------
 * name:
    * LCE             ->  Leave Copy Everywhere
    * NO_CACHE        ->  No caching, shorest-path routing
    * HR_SYMM         ->  Symmetric hash-routing
    * HR_ASYMM        ->  Asymmetric hash-routing
    * HR_MULTICAST    ->  Multicast hash-routing
    * HR_HYBRID_AM    ->  Hybrid Asymm-Multicast hash-routing
    * HR_HYBRID_SM    ->  Hybrid Symm-Multicast hash-routing
    * CL4M            ->  Cache less for more
    * PROB_CACHE      ->  ProbCache
    * LCD             ->  Leave Copy Down
    * RAND_CHOICE     ->  Random choice: cache in one random cache on path
    * RAND_BERNOULLI  ->  Random Bernoulli: cache randomly in caches on path
 * args:
    * For PROB_CACHE
       * t_tw : float, optional, default=10. The ProbCache t_tw parameter
    * For HR_HYBRID_AM
       * max_stretch: float, optional, default=0.2.
         The max detour stretch for selecting multicast 


cache_policy
------------
 * name:
    * LRU   -> Least Recently Used
    * SLRU  -> Segmeted Least Recently Used
    * LFU   -> Least Frequently Used
    * NULL  -> No cache
    * RAND  -> Random eviction
    * FIFO  -> First In First Out
 * args:
    * For SLRU:
       * segments: int, optional, default=2. Number of segments 


desc
----
string describing the experiment (used to print on screen progress information)

Further info
============

To get further information about the models implemented in the simulator you
can inspect the source code which is well organized and documented:
 * Topology implementations are located in ./icarus/scenarios/topology.py
 * Cache placement implementations are located in
   ./icarus/scenarios/cacheplacement.py
 * Caching and routing strategies located in ./icarus/models/strategy.py
 * Cache eviction policy implementations are located in ./icarus/models/cache.py
"""
from multiprocessing import cpu_count
from collections import deque
import copy
from icarus.util import Tree

############################## GENERAL SETTINGS ##############################

# Level of logging output
# Available options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = 'INFO'

# If True, executes simulations in parallel using multiple processes
# to take advantage of multicore CPUs
PARALLEL_EXECUTION = True

# Number of processes used to run simulations in parallel.
# This option is ignored if PARALLEL_EXECUTION = False
N_PROCESSES = cpu_count()

# Granularity of caching.
# Currently, only OBJECT is supported
CACHING_GRANULARITY = 'OBJECT'

# Format in which results are saved.
# Result readers and writers are located in module ./icarus/results/readwrite.py
# Currently only PICKLE is supported 
RESULTS_FORMAT = 'PICKLE'

# Number of times each experiment is replicated
# This is necessary for extracting confidence interval of selected metrics
N_REPLICATIONS = 1

# List of metrics to be measured in the experiments
# The implementation of data collectors are located in ./icaurs/execution/collectors.py
# Remove collectors not needed
DATA_COLLECTORS = [
           'LATENCY',           # Measure request and response latency (based on static link delays)
           #'LINK_LOAD',         # Measure link loads
                   ]


########################## EXPERIMENTS CONFIGURATION ##########################

# Default experiment values, i.e. values shared by all experiments

#N_CLIENTS = 5047
#N_CLIENTS = 20838
N_CLIENTS = 39852#22659#989#734#4519

# Number of content objects
#N_CONTENTS = 35744
#N_CONTENTS = 66410
#N_CONTENTS = 91243
N_CONTENTS = 581527#341028#89125#10939#9688#35130

# Number of content requests generated to pre-populate the caches
# These requests are not logged
#N_WARMUP_REQUESTS = 30000#54793
N_WARMUP_REQUESTS = 900000#248336

# Number of content requests that are measured after warmup
#N_MEASURED_REQUESTS = 24792
N_MEASURED_REQUESTS = 1467700#14785#12838#52021

# Number of requests per second (over the whole network)
REQ_RATE = 1

# Cache eviction policy
CACHE_POLICY = 'LRU'

# Zipf alpha parameter, remove parameters not needed
ALPHA = [0.8]
#ALPHA = [0.6, 0.8, 1.1]
# Total size of network cache as a fraction of content population
# Remove sizes not needed
#NETWORK_CACHE = [0.000586462,0.001466155,0.002932311,0.005864621,0.008796932]#,0.011729242] #341028
#NETWORK_CACHE = [0.002244039,0.005610098,0.011220196,0.022440393,0.033660589]
#NETWORK_CACHE = [0.022440393,0.028050491,0.033660589,0.039270687] #89125
NETWORK_CACHE = [0.001719611,0.003439221,0.005158832,0.006878442] #581527 #0.000085981,0.000171961,0.000257942,0.000343922,
#NETWORK_CACHE = [0.001423285,0.00284657,0.004269855,0.00569314,0.007116425]#35130
#NETWORK_CACHE = [0.004570802,0.009141603,0.013712405,0.018283207,0.022854009]#10939
#NETWORK_CACHE = [0.005161024,0.010322048,0.015483072,0.020644096,0.02580512]#9688
#NETWORK_CACHE = [0.001096,0.001644,0.002193,0.00274] #[0.00548] 91243
#NETWORK_CACHE = [0.002798,0.004199,0.0056,0.006995]
#NETWORK_CACHE = [0.00075, 0.0015, 0.00226, 0.003012, 0.003765]#66410
#NETWORK_CACHE = [0.005, 0.01, 0.015, 0.02, 0.025]

# List of topologies tested
# Topology implementations are located in ./icarus/scenarios/topology.py
# Remove topologies not needed
TOPOLOGIES =  [
        'GARR',
        #'GEANT',
        #'WIDE'
        #'TEST'
              ]

# List of caching and routing strategies
# The code is located in ./icarus/models/strategy.py
# Remove strategies not needed
STRATEGIES = [
#     'CTR',		# Characteristic Time
     'OPTIMAL',		# Optimal Caching
#     'CTR_LCE',
     'LCE',             # Leave Copy Everywhere
#     'NO_CACHE',        # No caching, shortest-path routing
#     'HR_SYMM',         # Symmetric hash-routing
#     'HR_ASYMM',        # Asymmetric hash-routing
#     'HR_MULTICAST',    # Multicast hash-routing
#     'HR_HYBRID_AM',    # Hybrid Asymm-Multicast hash-routing
#     'HR_HYBRID_SM',    # Hybrid Symm-Multicast hash-routing
     'CL4M',            # Cache less for more
     'PROB_CACHE',      # ProbCache
     'LCD',             # Leave Copy Down
#     'RAND_CHOICE',     # Random choice: cache in one random cache on path
#     'RAND_BERNOULLI',  # Random Bernoulli: cache randomly in caches on path
             ]

EXPERIMENT_QUEUE = deque()

# Build a default experiment configuration which is going to be used by all
# experiments of the campaign
default = Tree()
default['workload'] = {'name':       'YOUTUBETRACE',
                       'n_contents': N_CONTENTS,
                       'n_warmup':   N_WARMUP_REQUESTS,
                       'n_measured': N_MEASURED_REQUESTS,
                       'num_clients' : N_CLIENTS,
                       'reqs_file': '/home/adita/Greedy 08142017/youtube_traces/All traces/requests',
                       'timestamps_file': '/home/adita/Greedy 08142017/youtube_traces/All traces/timestamps',
                       'clients_file': '/home/adita/Greedy 08142017/youtube_traces/All traces/clients',
                       'unique_contents_file': '/home/adita/Greedy 08142017/youtube_traces/All traces/unique_contents',
			}
default['cache_placement']['name'] = 'UNIFORM'
default['content_placement']['name'] = 'UNIFORM'
default['cache_policy']['name'] = CACHE_POLICY

# Create experiments multiplexing all desired parameters
for alpha in ALPHA:
    for strategy in STRATEGIES:
        for topology in TOPOLOGIES:
            for network_cache in NETWORK_CACHE:
                experiment = copy.deepcopy(default)
                #experiment['workload']['alpha'] = alpha
                experiment['strategy']['name'] = strategy
		experiment['strategy']['alpha'] = alpha
		experiment['strategy']['network_cache'] = network_cache
                experiment['topology']['name'] = topology
                experiment['cache_placement']['network_cache'] = network_cache
                experiment['desc'] = "Alpha: %s, strategy: %s, topology: %s, network cache: %s" \
                                     % (str(alpha), strategy, topology, str(network_cache))
                EXPERIMENT_QUEUE.append(experiment)
