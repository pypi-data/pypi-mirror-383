import numpy as np

X = np.array([[0,0],[0,1],[1,0],[1,1]])
y = np.array([[0],[1],[1],[0]])

def sigmoid(x):
    return 1/(1+np.exp(-x))

np.random.seed(1)
weights = 2*np.random.random((2,1)) - 1

for _ in range(10000):
    layer0 = X
    layer1 = sigmoid(np.dot(layer0, weights))
    error = y - layer1
    adjustments = error * layer1 * (1-layer1)
    weights += np.dot(layer0.T, adjustments)

print('Output after training:')
print(layer1)
