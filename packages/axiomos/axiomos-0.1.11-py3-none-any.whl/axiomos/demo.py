def softmax_demo():
    import numpy as np
    x = np.array([[1.0, 2.0, 3.0]])
    e = np.exp(x - np.max(x))
    s = e / e.sum(axis=1, keepdims=True)
    print("Softmax demo:", s)
