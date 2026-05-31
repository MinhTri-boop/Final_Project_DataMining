import numpy as np
from active_semi_supervised_clustering.semi_supervised.labeled_data.kmeans import COPKMeans

X = np.random.rand(10, 2)
ml = [(0, 1), (2, 3)]
cl = [(0, 2)]

clusterer = COPKMeans(n_clusters=2)
clusterer.fit(X, ml=ml, cl=cl)
print(clusterer.labels_)
