import os
import cv2
import wandb
import numpy as np
from glob import glob
import tensorflow as tf
import tensorflow_addons as tfa
from wandb.keras import WandbCallback
from sklearn.model_selection import train_test_split


os.environ['WANDB_API_KEY'] = '0a94ef68f2a7a8b709671d6ef76e61580d20da7f'


def get_compile_datasets(
        datasets_path: str
):
    inputs_path, targets_data = [], []
    for idx, dataset_name in enumerate(os.listdir(datasets_path)):
        images_path = glob(f'{datasets_path}/{dataset_name}/*.[pj][pn][g]')
        targets = np.zeros((len(images_path), class_count))
        targets[:, idx] = targets[:, idx] + 1
        targets_data.extend(targets)
        inputs_path.extend(images_path)
    return inputs_path, targets_data


def get_compile_datasets_uno(
        datasets_path: str
):
    inputs_path, targets_data = [], []
    for idx, dataset_name in enumerate(os.listdir(datasets_path)):
        images_path = glob(f'{datasets_path}/{dataset_name}/*.[pj][pn][g]')
        targets = np.zeros(len(images_path))
        if dataset_name != 'Norma':
            targets[:] = 1
        targets_data.extend(targets)
        inputs_path.extend(images_path)
    return inputs_path, targets_data


class DataSequence(tf.keras.utils.Sequence):
    def __init__(self, x_set, y_set, img_height, img_width, num_channels, batch_size):
        self.x, self.y = x_set, y_set
        self.height, self.width, self.channels = img_height, img_width, num_channels
        self.batch_size = batch_size

    def __len__(self):
        return int(np.ceil(len(self.x) / self.batch_size))

    def __getitem__(self, idx):
        paths = self.x[idx * self.batch_size:(idx + 1) * self.batch_size]
        labels = self.y[idx * self.batch_size:(idx + 1) * self.batch_size]
        imgs = self._processing(paths=paths)

        batch_sample = imgs, np.array(labels)
        return batch_sample

    def _processing(self, paths):
        hu_batch = np.zeros(shape=(len(paths), self.height, self.width, self.channels), dtype=np.float32)
        for idx, path in enumerate(paths):
            img_string = tf.io.read_file(path)
            img_input = tf.image.decode_png(img_string, channels=self.channels)

            s = max(img_input.shape[0], img_input.shape[1])
            new_images = np.zeros((s, s, 3))
            new_images[:img_input.shape[0], :img_input.shape[1], :] = img_input

            img_resized = tf.image.resize(images=new_images, size=(self.height, self.width))
            img_norm = img_resized / 255.0
            img_output = tf.reshape(tensor=img_norm, shape=(self.height, self.width, self.channels))

            img_output = tf.image.stateless_random_brightness(image=img_output, max_delta=0.3, seed=(1, 2))
            img_output = tf.image.random_flip_left_right(img_output)
            img_output = tf.image.random_flip_up_down(img_output)
            img_output = tf.image.random_saturation(img_output, 5, 10)
            img_output = tf.image.random_jpeg_quality(img_output, 75, 95)

            # num_samples = int(tf.shape(img_output)[0])
            degrees = tf.random.stateless_uniform(
                shape=[1], minval=-45, maxval=45, seed=(1, 2)
            )
            degrees = degrees * 0.017453292519943295  # convert the angle in degree to radians

            img_output = tfa.image.rotate(img_output, degrees)

            hu_batch[idx] = img_output

        return hu_batch


def get_model(
        input_shape,
        output_shape,
):
    # tl_model = tf.keras.applications.MobileNetV2(
    tl_model = tf.keras.applications.Xception(
        weights='imagenet',
        include_top=False,
        input_tensor=None,
        input_shape=input_shape,
        pooling=None,
    )
    tl_model.trainable = False
    for layer in tl_model.layers[-10:]:
        layer.trainable = True
    x = tl_model.output
    x = tf.keras.layers.Dropout(rate=0.5)(x)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dense(2048, activation='relu')(x)
    x = tf.keras.layers.Dropout(rate=0.5)(x)
    # x_0 = tf.keras.layers.Dense(1, activation='sigmoid')(x)
    # x_1 = tf.keras.layers.Dense(1, activation='sigmoid')(x)
    # x_2 = tf.keras.layers.Dense(1, activation='sigmoid')(x)
    # x_3 = tf.keras.layers.Dense(1, activation='sigmoid')(x)
    # x_4 = tf.keras.layers.Dense(1, activation='sigmoid')(x)
    x = tf.keras.layers.Dense(output_shape, activation='sigmoid')(x)
    # model = tf.keras.Model(EfficientNetB0.input, [x_0, x_1, x_2, x_3, x_4])
    model = tf.keras.Model(tl_model.input, x)
    model.summary()
    return model


if __name__ == '__main__':
    # class_ = ['DR+LKS', 'Norm', 'NPDR', 'PDR', 'PrePDR']
    class_ = ['Norma', 'Pathologic']
    class_count = len(class_)
    batch_size = 64
    epochs = 75
    img_height, img_width, num_channels = 448, 448, 3
    model_name = 'model_test'
    program_type = 'train'
    if program_type == 'train':
        if class_count > 2:
            inputs_path, targets_data = get_compile_datasets('../Datasets/eyes')
        else:
            inputs_path, targets_data = get_compile_datasets_uno('../../Datasets/SibGMU/eyes')
        if not os.path.exists(f'models/{model_name}'):
            os.makedirs(f'models/{model_name}')

        x_train, x_val, y_train, y_val = train_test_split(inputs_path, targets_data, test_size=0.1, random_state=11)

        ds_train = DataSequence(x_set=x_train, y_set=y_train, img_height=img_height, img_width=img_width,
                                batch_size=batch_size, num_channels=num_channels)
        ds_val = DataSequence(x_set=x_val, y_set=y_val, img_height=img_height, img_width=img_width,
                              batch_size=batch_size, num_channels=num_channels)

        model = get_model(
            input_shape=(img_height, img_width, num_channels),
            output_shape=class_count if class_count > 2 else 1,
        )

        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.00012),
            loss=tf.keras.losses.BinaryCrossentropy(from_logits=False, label_smoothing=0),
            # loss=tf.keras.losses.CategoricalCrossentropy(from_logits=False, label_smoothing=0),
            metrics=[
                tf.keras.metrics.TruePositives(name='tp'),
                tf.keras.metrics.FalsePositives(name='fp'),
                tf.keras.metrics.TrueNegatives(name='tn'),
                tf.keras.metrics.FalseNegatives(name='fn'),
                tf.keras.metrics.BinaryAccuracy(name='accuracy'),
                tf.keras.metrics.Precision(name='precision'),
                tf.keras.metrics.Recall(name='recall'),
                tf.keras.metrics.AUC(name='auc'),
                tf.keras.metrics.AUC(name='prc', curve='PR'),
            ]
        )
        csv_logger = tf.keras.callbacks.CSVLogger(os.path.join(f'models/{model_name}', 'logs.csv'), separator=',', append=False)
        wandb_config = dict(input_size=(img_height, img_width, num_channels),
                            batch_size=batch_size)
        from datetime import datetime
        wandb.init(project='eyes classification',
                   dir=f'models/{model_name}',
                   name=model_name + ' - ' + str(datetime.now())[:16],
                   config=wandb_config,
                   sync_tensorboard=True)

        wb = WandbCallback(monitor='val_loss',
                           mode='min',
                           save_weights_only=False,
                           save_model=False,
                           log_evaluation=False,
                           verbose=1)
        callbacks = [csv_logger, wb]

        class_weight = {
            0: 1.0,
            1: 2.15,
        }
        n_cpu = os.cpu_count()
        model.fit(
            x=ds_train,
            epochs=epochs,
            verbose=1,
            class_weight=class_weight,
            validation_data=ds_val,
            callbacks=callbacks,
            workers=n_cpu,
        )
        model.save(f'inference_models/{model_name}/save_model/')

    if program_type == 'test':
        model = tf.saved_model.load(f'models/{model_name}/save_model/')
        for idx, dataset_name in enumerate(os.listdir('../../Глаза')):
            img_path = glob(f'../Глаза/{dataset_name}/*')[0]
            input_img = cv2.imread(img_path)
            img = cv2.cvtColor(input_img.copy(), cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (224, 224))
            img = img / 255
            res = model([img])[0]
            res = np.array(res)
            res = res * 100
            res_new = [round(r, 3) for r in res]
            input_img = cv2.resize(input_img, (512, 512))
            input_img = cv2.putText(
                input_img,
                f'Norm: {str(res_new[1])} DR+LKS: {str(res_new[0])} NPDR: {str(res_new[2])} PDR: {str(res_new[3])} PrePDR: {str(res_new[4])}',
                (20, 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (100, 0, 255),
                1,
                cv2.LINE_AA,
            )
            input_img = cv2.putText(
                input_img,
                f'{class_[idx]}',
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (100, 255, 0),
                1,
                cv2.LINE_AA,
            )
            # cv2.imshow('res', input_img)
            # cv2.waitKey()
            cv2.imwrite(f'result{idx}.png', input_img)



