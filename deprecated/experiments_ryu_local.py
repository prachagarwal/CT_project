"""Ryu: main experiments script"""

import tensorflow as tf

choose = input("Press 1 for training or 2 for reconstruction: ")

if choose == 1:
    from train import train_cnn

    # Options
    opt = {}

    # Network:
    opt['method'] = 'cnn_simple'
    opt['n_h1'] = 50
    opt['n_h2'] = 2*opt['n_h1']
    opt['n_h3'] = 10

    # Training
    opt['optimizer'] = tf.train.AdamOptimizer
    opt['dropout_rate'] = 0.0
    opt['learning_rate'] = 1e-3
    opt['L1_reg'] = 0.00
    opt['L2_reg'] = 1e-5
    opt['n_epochs'] = 200
    opt['batch_size'] = 12
    opt['validation_fraction'] = 0.5
    opt['shuffle'] = True
    opt['validation_fraction'] = 0.5
    opt['shuffle'] = True

    # Data/task:
    opt['cohort'] = 'Diverse'
    opt['no_subjects'] = 8
    opt['subsampling_rate'] = 1372
    opt['upsampling_rate'] = 2
    opt['input_radius'] = 5
    opt['receptive_field_radius'] = 2
    output_radius = ((2*opt['input_radius']-2*opt['receptive_field_radius']+1)//2)
    opt['output_radius'] = output_radius
    opt['no_channels'] = 6
    opt['transform_opt'] = 'scaling'  # preprocessing of input/output variables

    # Dir:
    opt['data_dir'] = '/Users/ryutarotanno/DeepLearning/Test_1/data/Training/IPMI/' # '../data/'
    opt['save_dir'] = '../models'
    opt['log_dir'] = '../log'

    train_cnn(opt)
elif choose==2:
    import reconstruct

    # Options
    opt = {}

    # Network:
    opt['method'] = 'cnn_simple'
    opt['n_h1'] = 50  # 64 # 50
    opt['n_h2'] = 2*opt['n_h1']
    opt['n_h3'] = 10  # 32 #10

    # Training
    opt['optimizer'] = tf.train.AdamOptimizer
    opt['dropout_rate'] = 0.0
    opt['learning_rate'] = 1e-3
    opt['L1_reg'] = 0.00
    opt['L2_reg'] = 1e-5
    opt['n_epochs'] = 200
    opt['batch_size'] = 125
    opt['validation_fraction'] = 0.5
    opt['shuffle'] = True
    opt['validation_fraction'] = 0.5
    opt['shuffle'] = True

    # Training data/task:
    opt['cohort'] = 'Diverse'
    opt['no_subjects'] = 8
    opt['subsampling_rate'] = 1372
    opt['upsampling_rate'] = 2
    opt['input_radius'] = 5
    opt['receptive_field_radius'] = 2
    output_radius = ((2 * opt['input_radius'] -
                      2 * opt['receptive_field_radius'] + 1) // 2)
    print("output radius is %i" % output_radius)
    opt['output_radius'] = output_radius
    opt['no_channels'] = 6
    opt['transform_opt'] = 'scaling'  # preprocessing of input/output variables

    # Dir:
    opt['data_dir'] = '/media/daniel/HDD/SuperRes/Training/IPMI/'  # '../data/'
    opt['save_dir'] = '../models'
    opt['recon_dir']= '../recon'

    opt['gt_dir'] = '/Users/ryutarotanno/DeepLearning/Test_1/data/HCP/'  # ground truth dir
    opt['subpath'] = 'T1w/Diffusion'
    opt['subject'] = '117324'

    opt['input_file_name'] = 'dt_b1000_lowres_' + str(opt['upsampling_rate']) + '_'


    reconstruct.sr_reconstruct(opt)

