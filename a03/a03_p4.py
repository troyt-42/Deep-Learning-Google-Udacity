from __future__ import print_function
import numpy as np
import tensorflow as tf
from six.moves import cPickle as pickle
from six.moves import range

pickle_file = 'notMNIST.pickle'

with open(pickle_file, 'rb') as f:
  save = pickle.load(f)
  train_dataset = save['train_dataset']
  train_labels = save['train_labels']
  valid_dataset = save['valid_dataset']
  valid_labels = save['valid_labels']
  test_dataset = save['test_dataset']
  test_labels = save['test_labels']
  del save  # hint to help gc free up memory
  print('Training set', train_dataset.shape, train_labels.shape)
  print('Validation set', valid_dataset.shape, valid_labels.shape)
  print('Test set', test_dataset.shape, test_labels.shape)

image_size = 28
num_labels = 10

def reformat(dataset, labels):
  dataset = dataset.reshape((-1, image_size * image_size)).astype(np.float32)
  # Map 0 to [1.0, 0.0, 0.0 ...], 1 to [0.0, 1.0, 0.0 ...]
  labels = (np.arange(num_labels) == labels[:,None]).astype(np.float32)
  return dataset, labels

train_dataset, train_labels = reformat(train_dataset, train_labels)
valid_dataset, valid_labels = reformat(valid_dataset, valid_labels)
test_dataset, test_labels = reformat(test_dataset, test_labels)
print('Training set', train_dataset.shape, train_labels.shape)
print('Validation set', valid_dataset.shape, valid_labels.shape)
print('Test set', test_dataset.shape, test_labels.shape)

def accuracy(predictions, labels):
  return (100.0 * np.sum(np.argmax(predictions, 1) == np.argmax(labels, 1))
          / predictions.shape[0])

#1-Hidden Layer Neural Network
batch_size = 256
hidden_nodes = 1024
hidden_nodes_2 = 300
hidden_nodes_3 = 50
graph = tf.Graph()
with graph.as_default():

  # Input data. For the training data, we use a placeholder that will be fed
  # at run time with a training minibatch.
  tf_train_dataset = tf.placeholder(tf.float32,
                                    shape=(batch_size, image_size * image_size))
  tf_train_labels = tf.placeholder(tf.float32, shape=(batch_size, num_labels))
  tf_valid_dataset = tf.constant(valid_dataset)
  tf_test_dataset = tf.constant(test_dataset)
  
  # Variables.
  beta = 0.000001
  beta_2 = 0.0000005
  beta_3 = 0.0000001
  beta_4 = 0.00000005

  weights_1 = tf.Variable(
    tf.truncated_normal([image_size * image_size, hidden_nodes]))
  biases_1 = tf.Variable(tf.zeros([hidden_nodes]))
  regularization_1 = beta * tf.nn.l2_loss(weights_1)

  weights_2 = tf.Variable(
  	tf.truncated_normal([hidden_nodes, hidden_nodes_2]))
  biases_2 = tf.Variable(tf.zeros([hidden_nodes_2]))
  regularization_2 = beta_2 * tf.nn.l2_loss(weights_2)

  weights_3 = tf.Variable(
    tf.truncated_normal([hidden_nodes_2, hidden_nodes_3]))
  biases_3 = tf.Variable(tf.zeros([hidden_nodes_3]))
  regularization_3 = beta_3 * tf.nn.l2_loss(weights_3)

  weights_4 = tf.Variable(
    tf.truncated_normal([hidden_nodes_3, num_labels]))
  biases_4 = tf.Variable(tf.zeros([num_labels]))
  regularization_4 = beta_4 * tf.nn.l2_loss(weights_4)

  # Training computation.
  def forward_prop(inp):
  	h1 = tf.nn.relu(tf.matmul(inp, weights_1) + biases_1)
  	h2 = tf.nn.relu(tf.matmul(h1, weights_2) + biases_2)
  	h3 = tf.nn.relu(tf.matmul(h2, weights_3) + biases_3)
  	h4 = tf.matmul(h3, weights_4) + biases_4
  	return h4
  logits = forward_prop(tf_train_dataset)
  loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits, tf_train_labels) )
  
  # Optimizer.
  global_step = tf.Variable(0)  # count the number of steps taken.
  learning_rate = tf.train.exponential_decay(0.003, global_step, 1000, 0.99)
  optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(loss, global_step=global_step)
  
  # Predictions for the training, validation, and test data.
  train_prediction = tf.nn.softmax(logits)
  valid_prediction = tf.nn.softmax(forward_prop(tf_valid_dataset))
  test_prediction = tf.nn.softmax(forward_prop(tf_test_dataset))

num_steps = 10001

with tf.Session(graph=graph) as session:
  tf.initialize_all_variables().run()
  print("Initialized")
  for step in range(num_steps):
    # Pick an offset within the training data, which has been randomized.
    # Note: we could use better randomization across epochs.
    offset = (step * batch_size) % (train_labels.shape[0] - batch_size)
    # Generate a minibatch.
    batch_data = train_dataset[offset:(offset + batch_size), :]
    batch_labels = train_labels[offset:(offset + batch_size), :]
    # Prepare a dictionary telling the session where to feed the minibatch.
    # The key of the dictionary is the placeholder node of the graph to be fed,
    # and the value is the numpy array to feed to it.
    feed_dict = {tf_train_dataset : batch_data, tf_train_labels : batch_labels}
    _, l, predictions = session.run(
      [optimizer, loss, train_prediction], feed_dict=feed_dict)
    if (step % 500 == 0):
      print("Minibatch loss at step %d: %f" % (step, l))
      print("Minibatch accuracy: %.1f%%" % accuracy(predictions, batch_labels))
      print("Validation accuracy: %.1f%%" % accuracy(
        valid_prediction.eval(), valid_labels))
  print("Test accuracy: %.1f%%" % accuracy(test_prediction.eval(), test_labels))