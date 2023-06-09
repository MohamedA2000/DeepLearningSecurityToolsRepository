import tensorflow as tf
import foolbox as fb
import numpy as np
import tensorflow_datasets as tfds
from tensorflow.python.ops.numpy_ops import np_config
from google.cloud import storage
import json
import functions_framework

# constants
BUCKET_NAME = "dlstr-bucket"


def preprocess_dataset(dataset, dataset_info):
    images = np.array([sample['image'] for sample in dataset])
    labels = np.array([sample['label'] for sample in dataset])

    # checks if the 'image' feature is of type 'INT'
    for feature in dataset_info['schema']['feature']:
        if feature['name'] == 'image' and feature['type'] == 'INT':
            images = tf.cast(images, tf.float32)
            break

    # checks the 'test' dataset with 'image' feature has a max value of 255
    stop = False
    for split in dataset_info['splits']:
        if split['name'] == 'test':
            for feature in split['statistics']['features']:
                if feature['name'] == 'image' and feature['numStats']['max'] == 255:
                    images /= 127.5
                    images -= 1.0
                    stop = True
                    break
        # breaks out of nested for loop
        if stop:
            break

    return images, labels


def l2_additive_uniform_noise_attack(model, model_lower_bound, model_upper_bound,
                                     images, labels, epsilons):
    model_bounds = (model_lower_bound, model_upper_bound)

    fmodel = fb.TensorFlowModel(model, model_bounds)

    attack = fb.attacks.L2AdditiveUniformNoiseAttack()

    raw, clipped, is_adv = attack(fmodel, images, labels, epsilons=epsilons)

    robust_accuracy = 1 - tf.math.reduce_mean(tf.cast(is_adv, tf.float32), axis=-1)
    robust_accuracy *= 100

    return robust_accuracy


def l2_clipping_aware_additive_uniform_noise_attack(model, model_lower_bound, model_upper_bound,
                                                    images, labels, epsilons):
    model_bounds = (model_lower_bound, model_upper_bound)

    fmodel = fb.TensorFlowModel(model, model_bounds)

    attack = fb.attacks.L2ClippingAwareAdditiveUniformNoiseAttack()

    raw, clipped, is_adv = attack(fmodel, images, labels, epsilons=epsilons)

    robust_accuracy = 1 - tf.math.reduce_mean(tf.cast(is_adv, tf.float32), axis=-1)
    robust_accuracy *= 100

    return robust_accuracy


def l2_repeated_additive_uniform_noise_attack(model, model_lower_bound, model_upper_bound,
                                              images, labels, epsilons):
    model_bounds = (model_lower_bound, model_upper_bound)

    fmodel = fb.TensorFlowModel(model, model_bounds)

    attack = fb.attacks.L2RepeatedAdditiveUniformNoiseAttack()

    raw, clipped, is_adv = attack(fmodel, images, labels, epsilons=epsilons)

    robust_accuracy = 1 - tf.math.reduce_mean(tf.cast(is_adv, tf.float32), axis=-1)
    robust_accuracy *= 100

    return robust_accuracy


def l2_clipping_aware_repeated_additive_uniform_noise_attack(model, model_lower_bound, model_upper_bound,
                                                             images, labels, epsilons):
    model_bounds = (model_lower_bound, model_upper_bound)

    fmodel = fb.TensorFlowModel(model, model_bounds)

    attack = fb.attacks.L2ClippingAwareRepeatedAdditiveUniformNoiseAttack()

    raw, clipped, is_adv = attack(fmodel, images, labels, epsilons=epsilons)

    robust_accuracy = 1 - tf.math.reduce_mean(tf.cast(is_adv, tf.float32), axis=-1)
    robust_accuracy *= 100

    return robust_accuracy


def linf_additive_uniform_noise_attack(model, model_lower_bound, model_upper_bound,
                                       images, labels, epsilons):
    model_bounds = (model_lower_bound, model_upper_bound)

    fmodel = fb.TensorFlowModel(model, model_bounds)

    attack = fb.attacks.LinfAdditiveUniformNoiseAttack()

    raw, clipped, is_adv = attack(fmodel, images, labels, epsilons=epsilons)

    robust_accuracy = 1 - tf.math.reduce_mean(tf.cast(is_adv, tf.float32), axis=-1)
    robust_accuracy *= 100

    return robust_accuracy


def linf_repeated_additive_uniform_noise_attack(model, model_lower_bound, model_upper_bound,
                                                images, labels, epsilons):
    model_bounds = (model_lower_bound, model_upper_bound)

    fmodel = fb.TensorFlowModel(model, model_bounds)

    attack = fb.attacks.LinfRepeatedAdditiveUniformNoiseAttack()

    raw, clipped, is_adv = attack(fmodel, images, labels, epsilons=epsilons)

    robust_accuracy = 1 - tf.math.reduce_mean(tf.cast(is_adv, tf.float32), axis=-1)
    robust_accuracy *= 100

    return robust_accuracy


@functions_framework.http
def attack_endpoint(request):
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return '', 204, headers

    request_json = request.get_json(silent=True)

    # enable numpy related methods
    np_config.enable_numpy_behavior()

    # model parameters
    model_name = request_json['model_name']
    dataset_name = request_json['dataset_name']

    # attack input parameters
    model_lower_bound = request_json['model_lower_bound']
    model_upper_bound = request_json['model_upper_bound']
    epsilon_min = request_json['epsilon_min']
    epsilon_max = request_json['epsilon_max']
    epsilon_step = request_json['epsilon_step']
    attack_types = request_json['attack_types']
    norms = request_json['norms']

    # get dataset metadata from bucket
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)
    file_obj = bucket.get_blob(f'{dataset_name}/dataset_info.json')
    dataset_info = json.loads(file_obj.download_as_string())

    # split the dataset into min(1%, 50)
    split_str = 'test'
    for i in dataset_info['splits']:
        if i['name'] == 'test':
            num_shards = sum(int(shard) for shard in i['shardLengths'])
            absolute = min(50, num_shards / 100)
            split_str = f'test[:{absolute}]'

    # load model from gcp bucket
    model = tf.keras.models.load_model(f'gs://{BUCKET_NAME}/{model_name}')

    # load dataset from gcp bucket
    builder = tfds.builder_from_directory(f'gs://{BUCKET_NAME}/{dataset_name}')
    dataset = builder.as_dataset(split=split_str)

    # extract images and labels
    images, labels = preprocess_dataset(dataset, dataset_info)
    epsilons = np.arange(epsilon_min, epsilon_max + epsilon_step, epsilon_step)

    response_body = {norm: {} for norm in norms}

    # run the attacks
    for attack_type in attack_types:
        for norm in norms:
            if norm == '2' and attack_type == 'additive':
                accuracy = l2_additive_uniform_noise_attack(model, model_lower_bound, model_upper_bound,
                                                            images, labels, epsilons)

                response_body[norm][attack_type] = {
                    'epsilons': epsilons.tolist(),
                    'accuracy': accuracy.tolist()
                }

            elif norm == '2' and attack_type == 'clipping-aware-additive':
                accuracy = l2_clipping_aware_additive_uniform_noise_attack(model, model_lower_bound, model_upper_bound,
                                                                           images, labels, epsilons)

                response_body[norm][attack_type] = {
                    'epsilons': epsilons.tolist(),
                    'accuracy': accuracy.tolist()
                }

            elif norm == '2' and attack_type == 'repeated-additive':
                accuracy = l2_repeated_additive_uniform_noise_attack(model, model_lower_bound, model_upper_bound,
                                                                     images, labels, epsilons)

                response_body[norm][attack_type] = {
                    'epsilons': epsilons.tolist(),
                    'accuracy': accuracy.tolist()
                }

            elif norm == '2' and attack_type == 'clipping-aware-repeated-additive':
                accuracy = l2_clipping_aware_repeated_additive_uniform_noise_attack(model, model_lower_bound,
                                                                                    model_upper_bound, images,
                                                                                    labels, epsilons)

                response_body[norm][attack_type] = {
                    'epsilons': epsilons.tolist(),
                    'accuracy': accuracy.tolist()
                }

            elif norm == 'inf' and attack_type == 'additive':
                accuracy = linf_additive_uniform_noise_attack(model, model_lower_bound, model_upper_bound, images,
                                                              labels, epsilons)

                response_body[norm][attack_type] = {
                    'epsilons': epsilons.tolist(),
                    'accuracy': accuracy.tolist()
                }

            elif norm == 'inf' and attack_type == 'repeated-additive':
                accuracy = l2_repeated_additive_uniform_noise_attack(model, model_lower_bound, model_upper_bound,
                                                                     images, labels, epsilons)

                response_body[norm][attack_type] = {
                    'epsilons': epsilons.tolist(),
                    'accuracy': accuracy.tolist()
                }

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    return response_body, 200, headers
