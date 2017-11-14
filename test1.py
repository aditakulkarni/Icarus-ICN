import numpy as np

probability = []
with open('/home/adita/Greedy 08142017/youtube_traces/trace 1/probabilities_not_sorted', 'r') as f:
    for content in f:
        probability.append(float(content.rstrip()))
pdf = np.asarray(probability)
print len(pdf)
