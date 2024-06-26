"""
DeepLearning Assignment1 - Implementation of a simple neural network “from scratch”
Authors: Or Gindes & Roei Zaady
"""
import numpy as np
from typing import Tuple, List, Dict, Any

np.random.seed(2)
EPSILON = 1e-6


# 2.a
def linear_backward(dZ: np.ndarray, cache: Tuple, l2_regularization: bool = False) -> Tuple:
    """
    Computes the linear part of the backward propagation process of a single layer
    :param dZ: The gradient of the cost with respect to the linear output of the current layer
    :param cache: Tuple of values (A_prev, W, b) coming from the forward propagation in the current layer
    :param l2_regularization: boolean - indicates if l2 regularization should be used
    :return: dA_prev - Gradient of the cost with respect to the activation (of the previous layer l-1), same shape as A_prev
    :return: dW - Gradient of the cost with respect to W (current layer l), same shape as W
    :return: db - Gradient of the cost with respect to b (current layer l), same shape as b
    """
    A_prev, W, b = cache
    m = A_prev.shape[1]
    dW = 1 / m * np.dot(dZ, A_prev.T) + ((EPSILON / m) * W if l2_regularization else 0)
    # not sure about dividing with m
    db = 1 / m * np.sum(dZ, axis=1, keepdims=True)
    dA_prev = np.dot(W.T, dZ)
    return dA_prev, dW, db


# 2.b
def linear_activation_backward(dA: np.ndarray, cache: Tuple, activation: str, l2_regularization: bool = False) -> Tuple:
    """
    Compute the backward propagation for the LINEAR->ACTIVATION layer.
    The function first computes dZ and then applies the linear_backward function
    :param dA: post activation gradient of the current layer
    :param cache:  cache contains both the linear and the activations cache
    :param activation: The activation function to be used (a string, either “softmax” or “relu”)
    :param l2_regularization: boolean - indicates if l2 regularization should be used
    :return: dA_prev – Gradient of the cost with respect to the activation (of the previous layer l-1), same shape as A_prev
    :return: dW – Gradient of the cost with respect to W (current layer l), same shape as W
    :return: db – Gradient of the cost with respect to b (current layer l), same shape as b
    """
    linear_cache, activation_cache = cache
    if activation == 'relu':
        back_activation = relu_backward
    elif activation == 'softmax':
        back_activation = softmax_backward
    else:
        raise ValueError(f"activation {activation} isn't implemented")
    dZ = back_activation(dA, activation_cache)
    dA_prev, dW, db = linear_backward(dZ, linear_cache, l2_regularization)
    return dA_prev, dW, db


# 2.c
def relu_backward(dA: np.ndarray, activation_cache: Dict) -> np.ndarray:
    """
    Compute backward propagation for a ReLU unit
    :param dA: the post-activation gradient
    :param activation_cache: contains Z (stored during the forward propagation)
    :return: dZ – gradient of the cost with respect to Z
    """
    Z = activation_cache["Z"]
    dZ = np.where(Z > 0, dA, np.zeros_like(dA))
    return dZ


# 2.d
def softmax_backward(dA: np.ndarray, activation_cache: Dict) -> np.ndarray:
    """
    Compute backward propagation for a ReLU unit
    :param dA: the post-activation gradient
    :param activation_cache: contains Z (stored during the forward propagation)
    :return: dZ – gradient of the cost with respect to Z
    """
    dZ = dA - activation_cache["Y"]
    return dZ


# 2.e
def L_model_backward(AL: np.ndarray, Y: np.ndarray, caches: List, l2_regularization: bool = False) -> Dict[str, Any]:
    """
    Computes the backward propagation process for the entire network.
    The backpropagation for the softmax function should be done only once, as only the output layers
    uses it and the RELU should be done iteratively over all the remaining layers of the network.
    :param AL: the probabilities vector, the output of the forward propagation (L_model_forward)
    :param Y: the true labels vector (the "ground truth" - true classifications)
    :param caches: list of caches containing for each layer: a) the linear cache; b) the activation cache
    :param l2_regularization: boolean - indicates if l2 regularization should be used
    :return: Grads - a dictionary with the gradients
             grads["dA" + str(l)] = ...
             grads["dW" + str(l)] = ...
             grads["db" + str(l)] = ...
    """
    grads = dict()
    n_layers = len(caches)

    for l in reversed(range(n_layers)):
        current_cache = caches[l]
        current_cache[-1] = {"Z": current_cache[-1]}
        if l == n_layers - 1:
            current_cache[-1].update({"Y": Y})
            dA_prev, dW, db = linear_activation_backward(AL, current_cache, "softmax", l2_regularization)
        else:
            dA = dA_prev
            dA_prev, dW, db = linear_activation_backward(dA, current_cache, "relu", l2_regularization)

        grads["dA" + str(l)] = dA_prev
        grads["dw" + str(l)] = dW
        grads["db" + str(l)] = db

    return grads


# 2.f
def update_parameters(parameters: Dict, grads: Dict, learning_rate: float) -> Dict:
    """
    Updates parameters using gradient descent
    :param parameters: a python dictionary containing the DNN architecture’s parameters
    :param grads: a python dictionary containing the gradients (generated by L_model_backward)
    :param learning_rate: the learning rate used to update the parameters (the “alpha”)
    :return: parameters – the updated values of the parameters object provided as input
    """
    for layer, (layer_weights, layer_biases) in parameters.items():
        # Update weights
        parameters[layer][0] = layer_weights - learning_rate * grads["dw" + layer.split('_')[-1]]
        # Update biases
        parameters[layer][1] = layer_biases - learning_rate * grads["db" + layer.split('_')[-1]]
    return parameters


