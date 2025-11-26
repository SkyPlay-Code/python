import numpy as np # pyright: ignore[reportMissingImports]
class NeuralNetwork:
    # This is where all our code will go
    # Add this code inside the NeuralNetwork class, replacing 'pass'
    def __init__(self, input_size, hidden_size, output_size):
        """
        Initializes the neural network.

        Args:
          input_size: Number of neurons in the input layer (784 for our images)
          hidden_size: Number of neurons in the hidden layer (we can choose this, e.g., 128)
          output_size: Number of neurons in the output layer (10 for digits 0-9)
        """
        # These are the "hyperparameters" defining the network's architecture
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        # --- INITIALIZE WEIGHTS AND BIASES ---
        # We initialize weights with small random numbers.
        # This is crucial so the network can learn different things on each neuron.

        # Weights for connections between input and hidden layer (a matrix)
        self.W1 = np.random.randn(self.hidden_size, self.input_size) * np.sqrt(2. / self.input_size)

        # Biases for each neuron in the hidden layer (a vector)
        self.b1 = np.ones((self.hidden_size, 1)) * 0.01

        # Weights for connections between hidden and output layer (a matrix)
        self.W2 = np.random.randn(self.output_size, self.hidden_size) * np.sqrt(2. / self.hidden_size)

        # Biases for each neuron in the output layer (a vector)
        self.b2 = np.ones((self.output_size, 1)) * 0.01

    # Add these two methods inside the NeuralNetwork class, below __init__
    def sigmoid(self, z):
        """ The Sigmoid activation function. """
        return 1 / (1 + np.exp(-z))
    
    def sigmoid_derivative(self, z):
        """ The derivative of the Sigmoid function. """
        return self.sigmoid(z) * (1 - self.sigmoid(z))
    
    # Add this method inside the NeuralNetwork class

    def forward(self, X):
        """
        Performs the forward pass of the network.

        Args:
          X: The input data, a numpy array of shape (input_size, 1) for a single example.

        Returns:
          A2: The final output/prediction of the network.
          cache: A dictionary containing all intermediate values needed for backpropagation.
        """
        # --- From Input Layer to Hidden Layer ---
        # 1. Calculate the weighted sum
        # Z1 is the pre-activation values for the hidden layer
        Z1 = np.dot(self.W1, X) + self.b1

        # 2. Apply the activation function
        # A1 is the activated output of the hidden layer
        A1 = self.relu(Z1)

        # --- From Hidden Layer to Output Layer ---
        # 3. Calculate the next weighted sum
        # Z2 is the pre-activation values for the output layer
        Z2 = np.dot(self.W2, A1) + self.b2

        # 4. Apply the final activation function
        # A2 is the final output of the network, our prediction vector
        A2 = self.sigmoid(Z2)

        # We store these values because we'll need them for backpropagation
        cache = {
            "Z1": Z1,
            "A1": A1,
            "Z2": Z2,
            "A2": A2
        }

        return A2, cache
    
    # Add this method inside the NeuralNetwork class

    def backward(self, X, Y, cache):
        """
        Performs the backward pass and calculates the gradients (the "blame").

        Args:
          X: The input data from the forward pass.
          Y: The true label/correct answer for the input X.
          cache: The dictionary of intermediate values from the forward pass.

        Returns:
          grads: A dictionary containing the gradients for each weight and bias.
        """
        # Number of training examples (for now, just 1)
        m = X.shape[1] 

        # Retrieve activations from the cache
        A1 = cache['A1']
        A2 = cache['A2']
        Z1 = cache['Z1'] # We need the pre-activation value for the derivative

        # --- Backpropagation at the Output Layer ---
        # 1. Calculate the initial error. How different is our prediction (A2) from the truth (Y)?
        dZ2 = A2 - Y

        # 2. Calculate the gradient for W2. How much did W2 contribute to this error?
        # It's the output error (dZ2) multiplied by the activations of the previous layer (A1).
        dW2 = (1/m) * np.dot(dZ2, A1.T)

        # 3. Calculate the gradient for b2. This is just the sum of the error signal.
        db2 = (1/m) * np.sum(dZ2, axis=1, keepdims=True)

        # --- Backpropagation at the Hidden Layer ---
        # 4. "Propagate" the error backwards to the hidden layer.
        # We take the error from the output layer (dZ2) and map it back through the W2 weights.
        dA1 = np.dot(self.W2.T, dZ2)

        # 5. Adjust the hidden layer's error using the sigmoid derivative.
        # This step accounts for the activation function's role in the error.
        dZ1 = dA1 * self.relu_derivative(cache['Z1'])

        # 6. Calculate the gradient for W1.
        dW1 = (1/m) * np.dot(dZ1, X.T)

        # 7. Calculate the gradient for b1.
        db1 = (1/m) * np.sum(dZ1, axis=1, keepdims=True)

        # Store all our calculated gradients in a dictionary
        grads = {
            "dW1": dW1,
            "db1": db1,
            "dW2": dW2,
            "db2": db2
        }

        return grads
    
    # Add this method inside the NeuralNetwork class

    def update_parameters(self, grads, learning_rate):
        """
        Updates the weights and biases using the gradients and a learning rate.

        Args:
          grads: Dictionary of gradients calculated by the backward pass.
          learning_rate: A small number controlling how big of a step to take.
        """
        # The gradient descent update rule: parameter = parameter - learning_rate * gradient
        self.W1 = self.W1 - learning_rate * grads["dW1"]
        self.b1 = self.b1 - learning_rate * grads["db1"]
        self.W2 = self.W2 - learning_rate * grads["dW2"]
        self.b2 = self.b2 - learning_rate * grads["db2"]

    # Add these new methods to your class
    def relu(self, z):
        """ The ReLU activation function. """
        return np.maximum(0, z)

    def relu_derivative(self, z):
        """ The derivative of the ReLU function. """
        return z > 0
    

# --- Main execution block ---
if __name__ == "__main__":
    # 1. LOAD AND PREPARE THE DATA
    # ---------------------------------
    from tensorflow.keras.datasets import mnist # type: ignore
    import numpy as np # type: ignore

    print("Loading the MNIST dataset via Keras...")
    # This function downloads the data from a reliable Google-hosted source
    # It's already split into training and testing sets
    (X_train_orig, y_train), (X_test, y_test) = mnist.load_data()

    # Get the total number of images
    num_images = X_train_orig.shape[0]
    # Create a permutation of indices from 0 to num_images-1
    shuffled_indices = np.random.permutation(num_images)
    # Use these shuffled indices to reorder both the images and the labels
    X_train_shuffled = X_train_orig[shuffled_indices]
    y_train_shuffled = y_train[shuffled_indices]

    # Normalize and Reshape the training data
    # Normalize: convert pixels from 0-255 to 0-1
    # Reshape: flatten the 28x28 images into 784-element vectors
    # num_images = X_train_orig.shape[0]
    X_train = X_train_shuffled.reshape(num_images, -1) / 255.0

    # Transpose the data to match our network's expected input (features, num_examples)
    X_train = X_train.T

    # One-hot encode the training labels
    y_train_encoded = np.zeros((10, y_train_shuffled.shape[0]))
    for i in range(y_train_shuffled.shape[0]):
        y_train_encoded[y_train_shuffled[i], i] = 1

    print(f"Training data shape: {X_train.shape}")
    print(f"Training labels shape: {y_train_encoded.shape}")


    # 2. INITIALIZE THE NEURAL NETWORK
    # ---------------------------------
    input_size = 784  # 28x28 pixels
    hidden_size = 128 # You can experiment with this number
    output_size = 10  # Digits 0-9
    learning_rate = 0.1 # You can experiment with this, too
    epochs = 300     # An epoch is one full pass over the training data

    # Create the network
    nn = NeuralNetwork(input_size, hidden_size, output_size)
    print("Neural Network created. Starting training...")

    # 3. THE TRAINING LOOP
    # -----------------------
    for epoch in range(epochs):
        # a) FORWARD PASS: Make a prediction
        A2, cache = nn.forward(X_train)

        # We'll skip the complex cost calculation for simplicity, but we monitor it
        # The core logic is in backpropagation.
        
        # b) BACKWARD PASS: Calculate the "blame" (gradients)
        grads = nn.backward(X_train, y_train_encoded, cache)
        
        # c) UPDATE PARAMETERS: Nudge the weights and biases
        nn.update_parameters(grads, learning_rate)
        
        # d) Print progress (optional, but very helpful)
        if epoch % 10 == 0:
            # Calculate accuracy to see how we're doing
            predictions = np.argmax(A2, axis=0)
            correct_predictions = np.sum(predictions == y_train_shuffled)
            accuracy = correct_predictions / y_train_shuffled.shape[0] * 100
            print(f"Epoch {epoch}: Accuracy = {accuracy:.2f}%")

    print("Training finished!")