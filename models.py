"""Builds the specified model:
1. inference() - Builds the model as far as is required for running the network
forward to make predictions.
2. cost() - Adds to the inference model the layers required to generate the cost function.
3. training() - Adds to the loss model the Ops required to generate and apply gradients.

This file is used by sr_nn.py and not meant to be run.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf


def inference(method, x, keep_prob, opt):
	""" Define the model up to where it may be used for inference.
	Args:
		method (str): model type
	Returns:
		y_pred: the predicted output patch (tensor)
	"""
	method = opt['method']
	n_h1 = opt['n_h1']
	n_h2 = opt['n_h2']
	n_h3 = opt['n_h3']
	upsampling_rate = opt['upsampling_rate']
	no_channels = opt['no_channels']

	if method == 'cnn_simple':
		h1_1 = conv3d(x, [3,3,3,no_channels,n_h1], [n_h1], 'conv_1')

		if opt['receptive_field_radius'] == 2:
			h1_2 = conv3d(tf.nn.relu(h1_1), [1,1,1,n_h1,n_h2], [n_h2], 'conv_2')
		elif opt['receptive_field_radius'] == 3:
			h1_2 = conv3d(tf.nn.relu(h1_1), [3,3,3,n_h1,n_h2], [n_h2], 'conv_2')
		elif opt['receptive_field_radius'] == 4:
			h1_2 = conv3d(tf.nn.relu(h1_1), [3,3,3,n_h1,n_h2], [n_h2], 'conv_2')
			h1_2 = conv3d(tf.nn.relu(h1_2), [3,3,3,n_h2,n_h2], [n_h2], 'conv_3')
		elif opt['receptive_field_radius'] == 5:
			h1_2 = conv3d(tf.nn.relu(h1_1), [3,3,3,n_h1,n_h2], [n_h2], 'conv_2')
			h1_2 = conv3d(tf.nn.relu(h1_2), [3,3,3,n_h2,n_h2], [n_h2], 'conv_3')
			h1_2 = conv3d(tf.nn.relu(h1_2), [3,3,3,n_h2,n_h2], [n_h2], 'conv_4')

		y_pred = conv3d(tf.nn.relu(h1_2),
						[3,3,3,n_h2,no_channels*(upsampling_rate**3)],
						[no_channels*(upsampling_rate**3)],
                        'conv_last')

	elif method == 'cnn_dropout':
		h1_1 = conv3d(x, [3, 3, 3, no_channels, n_h1], [n_h1], 'conv_1')

		if opt['receptive_field_radius'] == 2:
			h1_2 = conv3d(tf.nn.relu(h1_1), [1, 1, 1, n_h1, n_h2], [n_h2], 'conv_2')
		elif opt['receptive_field_radius'] == 3:
			h1_2 = conv3d(tf.nn.relu(h1_1), [3, 3, 3, n_h1, n_h2], [n_h2], 'conv_2')
		elif opt['receptive_field_radius'] == 4:
			h1_2 = conv3d(tf.nn.relu(h1_1), [3, 3, 3, n_h1, n_h2], [n_h2], 'conv_2')
			h1_2 = conv3d(tf.nn.dropout(tf.nn.relu(h1_2), keep_prob),
						  [3, 3, 3, n_h2, n_h2], [n_h2], 'conv_3')
		elif opt['receptive_field_radius'] == 5:
			h1_2 = conv3d(tf.nn.relu(h1_1), [3, 3, 3, n_h1, n_h2], [n_h2], 'conv_2')
			h1_2 = conv3d(tf.nn.dropout(tf.nn.relu(h1_2), keep_prob),
						  [3, 3, 3, n_h2, n_h2], [n_h2], 'conv_3')
			h1_2 = conv3d(tf.nn.dropout(tf.nn.relu(h1_2), keep_prob),
						  [3, 3, 3, n_h2, n_h2], [n_h2], 'conv_4')

		y_pred = conv3d(tf.nn.dropout(tf.nn.relu(h1_2), keep_prob),
						[3, 3, 3, n_h2, no_channels * (upsampling_rate ** 3)],
						[no_channels * (upsampling_rate ** 3)], 'conv_last')

	elif method == 'cnn_residual':
		h1 = tf.nn.relu(conv3d(x, [3,3,3,no_channels,n_h1], [n_h1], '1'))
		# Residual blocks:
		# todo: include BN
		h2 = residual_block(h1, n_h1, n_h1, 'res2')
		h3 = residual_block(h2, n_h1, n_h1, 'res3')
		# Output
		h4 = conv3d(h3, [3,3,3,n_h1,n_h2], [n_h2], '4')
		h5 = residual_block(h4, n_h2, n_h2, 'res5')
		h6 = residual_block(h5, n_h2, n_h2, 'res6')
		y_pred = conv3d(h6, [1,1,1,n_h2,no_channels*(upsampling_rate**3)],
							[no_channels*(upsampling_rate**3)], '7')
	else:
		raise ValueError('The chosen method not available ...')

	return y_pred

def residual_block(x, n_in, n_out, name):
	"""A residual block of constant spatial dimensions and 1x1 convs only"""
	b = tf.get_variable(name+'_2b', dtype=tf.float32, shape=[n_out],
						initializer=tf.constant_initializer(1e-2))
	assert n_out >= n_in
	
	h1 = conv3d(x, [1,1,1,n_in,n_out], [n_out], name+'1')
	h2 = conv3d(tf.nn.relu(h1), [1,1,1,n_out,n_out], None, name+'2')
	h3 = tf.pad(x, [[0,0],[0,0],[0,0],[0,0],[0,n_out-n_in]]) + h2
	return tf.nn.relu(tf.nn.bias_add(h3, b))

def get_weights(filter_shape, W_init=None, name=None):
	if W_init == None:
		# He/Xavier
		prod_length = len(filter_shape) - 1
		stddev = np.sqrt(2.0 / np.prod(filter_shape[:prod_length])) 
		W_init = tf.random_normal(filter_shape, stddev=stddev)
	return tf.Variable(W_init, name=name)

def conv3d(x, w_shape, b_shape=None, layer_name='', summary=False):
	"""Return the 3D convolution"""
	with tf.name_scope(layer_name):
		with tf.name_scope('weights'):
			w = get_weights(w_shape)
			variable_summaries(w, summary)

		if b_shape is not None:
			with tf.name_scope('biases'):
				b = tf.Variable(tf.constant(1e-2,dtype=tf.float32,shape=b_shape))
				variable_summaries(b, summary)

			# b = tf.get_variable('biases', dtype=tf.float32, shape=b_shape,
			#                    initializer=tf.constant_initializer(1e-2))
			with tf.name_scope('wxplusb'):
				z = tf.nn.conv3d(x, w, strides=(1, 1, 1, 1, 1), padding='VALID')
				z = tf.nn.bias_add(z, b)
				variable_summaries(z, summary)
		else:
			with tf.name_scope('wx'):
				z = tf.nn.conv3d(x, w, strides=(1, 1, 1, 1, 1), padding='VALID')
				variable_summaries(z, summary)
	return z

def scaled_prediction(method, x, keep_prob, transform, opt):
	x_mean = tf.constant(np.float32(transform['input_mean']), name='x_mean')
	x_std = tf.constant(np.float32(transform['input_std']), name='x_std')
	y_mean = tf.constant(np.float32(transform['output_mean']), name='y_mean')
	y_std = tf.constant(np.float32(transform['output_std']), name='y_std')
	# x_scaled = tf.div(tf.sub(x - transform['input_mean'), transform['input_std'])
	x_scaled = tf.div(tf.sub(x, x_mean), x_std)
	y = inference(method, x_scaled, keep_prob, opt)
	y_pred = tf.add(tf.mul(y_std, y), y_mean, name='y_pred')
	return y_pred


def variable_summaries(var, default=True):
	"""Attach a lot of summaries to a Tensor (for TensorBoard visualization)."""
	if default:
		with tf.name_scope('summaries'):
			mean = tf.reduce_mean(var)
			tf.summary.scalar('mean', mean)
			with tf.name_scope('stddev'):
				stddev = tf.sqrt(tf.reduce_mean(tf.square(var - mean)))
			tf.summary.scalar('stddev', stddev)
			tf.summary.scalar('max', tf.reduce_max(var))
			tf.summary.scalar('min', tf.reduce_min(var))
			tf.summary.histogram('histogram', var)