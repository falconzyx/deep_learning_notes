import os, sys, numpy as np, tensorflow as tf
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
import convnet

__package__ = 'convnet'
from . import network

from tensorflow.examples.tutorials.mnist import input_data

mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)

BATCH_SIZE = 250
FILENAME = os.path.basename(__file__)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SUMMARIES_DIR = SCRIPT_DIR
SAVE_PATH = SCRIPT_DIR + "/network.ckpt"

### configure devices for this eval script.
USE_DEVICE = '/gpu:1'
session_config = tf.ConfigProto(log_device_placement=True)
session_config.gpu_options.allow_growth = True
# this is required if want to use GPU as device.
# see: https://github.com/tensorflow/tensorflow/issues/2292
session_config.allow_soft_placement = True

if __name__ == "__main__":

    with tf.Graph().as_default() as g, tf.device(USE_DEVICE):
        # inference()
        input, logits = network.inference()
        labels, loss_op = network.loss(logits)
        train = network.training(loss_op, 1e-1)
        eval = network.evaluation(logits, labels)

        init = tf.initialize_all_variables()

        with tf.Session(config=session_config) as sess:
            # Merge all the summaries and write them out to /tmp/mnist_logs (by default)
            # to see the tensor graph, fire up the tensorboard with --logdir="./train"
            merged = tf.merge_all_summaries()
            train_writer = tf.train.SummaryWriter(SUMMARIES_DIR + '/convNet_train', sess.graph)
            test_writer = tf.train.SummaryWriter(SUMMARIES_DIR + '/convNet_test')

            saver = tf.train.Saver()

            sess.run(init)
            try:
                saver.restore(sess, SAVE_PATH)
            except ValueError:
                print('checkpoint file not found. Moving on to training.')
            for i in range(3000):

                batch_xs, batch_labels = mnist.train.next_batch(BATCH_SIZE)
                sess.run(train, feed_dict={
                    input: batch_xs,
                    labels: batch_labels
                })
                if i % 100 == 0:
                    output, loss_value, accuracy = sess.run([logits, loss_op, eval], feed_dict={
                        input: batch_xs,
                        labels: batch_labels
                    })
                    print("training accuracy is ", accuracy / BATCH_SIZE)

                if i % 500 == 0:
                    saver.save(sess, SAVE_PATH)
                    print('=> saved network in checkfile.')

            # now let's test!
            TEST_BATCH_SIZE = np.shape(mnist.test.labels)[0]
            output, loss_value, accuracy = sess.run([logits, loss_op, eval], feed_dict={
                input: mnist.test.images,
                labels: mnist.test.labels
            })
            print("MNIST Test accuracy is ", accuracy / TEST_BATCH_SIZE)