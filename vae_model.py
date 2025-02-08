import tensorflow as tf
from tensorflow import keras
from keras import layers, Model
from keras import backend as K

class VAELoss(layers.Layer):
    def __init__(self, **kwargs):
        super(VAELoss, self).__init__(**kwargs)

    def vae_loss(self, inputs, outputs, z_mean, z_log_var):
        reconstruction_loss = tf.reduce_mean(tf.square(inputs - outputs), axis=-1)
        kl_loss = -0.5 * tf.reduce_mean(1 + z_log_var - tf.square(z_mean) - tf.exp(z_log_var), axis=-1)
        return reconstruction_loss + kl_loss

    def call(self, inputs):
        inputs, outputs, z_mean, z_log_var = inputs
        loss = self.vae_loss(inputs, outputs, z_mean, z_log_var)
        self.add_loss(loss)
        return outputs

def build_vae(input_dim, latent_dim=2):
    """
    Build a Variational Autoencoder (VAE)
    :param input_dim: Dimension of input features
    :param latent_dim: Dimension of latent space
    :return: Tuple of (VAE model, Encoder model)
    """
    
    # Encoder
    inputs = layers.Input(shape=(input_dim,))
    
    h = layers.Dense(64, activation='relu')(inputs)
    
    z_mean = layers.Dense(latent_dim, name='z_mean')(h)
    
    z_log_var = layers.Dense(latent_dim, name='z_log_var')(h)

    # Sampling layer
    def sampling(args):
        z_mean, z_log_var = args
        batch = tf.shape(z_mean)[0]
        epsilon = tf.random.normal(shape=(batch, latent_dim), mean=0., stddev=1.0)
        return z_mean + tf.exp(0.5 * z_log_var) * epsilon
    
    z = layers.Lambda(sampling, output_shape=(latent_dim,), name='z')([z_mean, z_log_var])

    # Decoder
    decoder_h = layers.Dense(64, activation='relu')
    
    decoder_outputs = layers.Dense(input_dim, activation='linear')
    
    h_decoded = decoder_h(z)
    
    outputs = decoder_outputs(h_decoded)

    # Create VAE model with custom loss
    vae_layer = VAELoss()([inputs, outputs, z_mean, z_log_var])
    
    vae = Model(inputs, vae_layer)
    
    vae.compile(optimizer='adam')

    # Separate encoder model
    encoder = Model(inputs, z_mean)

    return vae, encoder