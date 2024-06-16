import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

df = pd.read_csv(r"step.csv")

# Normalization
X = df[["max", "min", "humidity"]].values #28 days data, 23 unique user id steps
scaler = StandardScaler()
X = scaler.fit_transform(X)

y = df["steps"].values
y = y.reshape(y.shape[0],1)

print(X.shape)  # (644, 3)
print(y.shape) # (644, 1)

ones_x = np.ones((28*23, 1))
X_ = np.concatenate((ones_x, X), axis = 1) # (644, 4)

y = np.reshape(y,(y.shape[0]*y.shape[1], 1))
y = np.asfarray(y, float)
#define learning rate
alpha = 0.0001
#define the total number of iterations 
iters = 1000
#define initial weights
theta = np.array([[1.0,1.0,1.0,1.0]])

#compute the mean squared error
def computecost(X, y, theta):
    inner = np.power((np.matmul(X, theta.T) - y), 2)
    return np.sum(inner)/ (2* len(X))

#compute the gradient and update the cost
def gradientDescent(X, y, theta, alpha, iters):
    for i  in range(iters):
        theta = theta - (alpha/len(X)) *np.sum((X@theta.T-y) *X, axis = 0)
        cost = computecost(X, y, theta)
    return (theta, cost)

g,cost = gradientDescent(X_, y, theta, alpha, iters)
print(g, cost)
# g contains W0, W1, W2 and W3 in order

X1 = df[["max"]].values
X2 = df[["min"]].values
X3 = df[["humidity"]].values

### Steps = W0 + W1* Max + W2 * Min + W3 * Humidity
#y_pred = 343.31046642 + 12.71992071*X1 + 30.79605817*X2 -20.79486607*X3
#print("Max step:", y_pred.max(), ", Min step: ", y_pred.min())
