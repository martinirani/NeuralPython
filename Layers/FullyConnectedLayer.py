import numpy as np
from AbstractLayer import AbstractLayer
from ..CostFunctions.LogLikelihood import LogLikelihood
from ..ActivationFunctions.Softmax import Softmax

class FullyConnectedLayer(AbstractLayer):
    def __init__(self, inputSize, nUnits, layerId, activationFunction, finalLayer = False):
        super(FullyConnectedLayer, self).__init__(1, inputSize, layerId)
        self.nUnits = nUnits
        self.activationFunction = activationFunction
        self.finalLayer = finalLayer
        # standardDeviation = 1.0 / np.sqrt(inputSize)
        self.weights = np.random.normal(0, 1.0 / inputSize, (nUnits, inputSize))
        self.biases = np.random.randn(nUnits)
        self.deltaWeights = []
        self.deltaBiases = []
        self.output = None

    def forward(self, x):
        self.z = np.dot(self.weights, x) + self.biases
        self.input = x
        result = self.activationFunction.function(self.z)
        if self.finalLayer:
            self.output = result
            return result

        return self.nextLayer.forward(result)

    def backward(self, dNext = None, desiredOutput = None, costFunction = None):
        if self.finalLayer:
            deltas = self.calculateDeltaOutputLayer(costFunction, desiredOutput)
        else:
            wNext = self.nextLayer.getWeights()
            # calcular deltas
            deltas = np.dot(wNext.transpose(), dNext) * \
                    self.activationFunction.derivative(self.z)
        # calcular delta biases
        deltaBiases = np.copy(deltas)

        # calcular delta pesos
        reshapedDelta = np.reshape(deltas, (self.nUnits, 1))
        reshapedInput = np.reshape(self.input, (self.inputSize, 1))
        deltaWeights =  np.dot(reshapedDelta, reshapedInput.transpose())

        # guardar deltas
        self.deltaWeights.append(deltaWeights)
        self.deltaBiases.append(deltaBiases)


        if type(self.previousLayer) == list:
            for l in self.previousLayer: l.backward(deltas)
        elif self.previousLayer != None:
            self.previousLayer.backward(deltas)

    def getWeights(self):
        return self.weights

    def getParameters(self):
        return self.biases, self.weights

    def calculateParameters(self):
        dWTotal = np.zeros(np.shape(self.weights))
        dBTotal = np.zeros(np.shape(self.biases))

        for dB, dw in zip(self.deltaBiases, self.deltaWeights):
            dBTotal += dB
            dWTotal += dw

        return dBTotal, dWTotal

    def updateParameters(self, biasesDelta, weightsDelta, regularization):
        self.biases -= biasesDelta
        self.weights -= weightsDelta + regularization.weightsDerivation(self.weights)
        self.deltaWeights = []
        self.deltaBiases = []

    def calculateDeltaOutputLayer(self, costFunction, desiredOutput):
        if isinstance(costFunction, LogLikelihood) \
        and isinstance(self.activationFunction, Softmax):
            return self.output - desiredOutput
        else:
            return costFunction.derivative(self.output, desiredOutput) * \
                            self.activationFunction.derivative(self.z, desiredOutput)

    def save(self, directory):
        baseFilename = directory + "fullyConnectedLayer" + str(self.layerId)
        np.save(open(baseFilename + "_biases.npy", "w"), self.biases)
        np.save(open(baseFilename + "_weights.npy", "w"), self.weights)

    def load(self, directory):
        biasesFile = directory + "fullyConnectedLayer" + str(self.layerId) + "_biases.npy"
        weightsFile = directory + "fullyConnectedLayer" + str(self.layerId) + "_weights.npy"

        self.biases = np.load(open(biasesFile))
        self.weights = np.load(open(weightsFile))









