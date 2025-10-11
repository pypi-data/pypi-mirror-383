import numpy as np

def sigmoid(x): return 1/(1+np.exp(-x))

X = np.array([0.5,0.3])
W1 = np.array([[0.4,0.2],[0.1,0.6]])
B1 = np.array([0.1,0.2])
W2 = np.array([0.3,0.7])
B2 = 0.5

H = sigmoid(np.dot(X,W1)+B1)
Y = sigmoid(np.dot(H,W2)+B2)

print("Hidden Layer:", H)
print("Output:", Y)
