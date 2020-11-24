import numpy as np
import random


def standardize(x, means, stddevs):
    return (x - means) / stddevs


def unstandardize(x, means, stddevs):
    return x * stddevs + means


def reduce_sample_y(data_y, args):
    ind = 1 if args.aggr_type == "Mean" else 0
    data_y = data_y[ind, None, args.parameters.index(args.pred_type), :, :, :]
    return data_y

def reduce_sample_x(data_x, args):
    op = np.mean if args.aggr_type == "Mean" else np.std
    data_x = np.concatenate([op(data_x, axis=1, keepdims=True),data_x[:,0,None,:,:,:,:]],axis=1)
    data_x = np.reshape(
                data_x,
                [
                    data_x.shape[0] * data_x.shape[1] * data_x.shape[2],
                    data_x.shape[3],
                    data_x.shape[4],
                    data_x.shape[5],
                ],
            )
    return data_x

def random_crop(data_x, data_y, args):
    max_lat = data_y.shape[-2] - args.crop_lat
    max_lon = data_y.shape[-1] - args.crop_lon
    lat = random.randint(0, max_lat)
    lon = random.randint(0, max_lon)
    data_x = data_x[:, :, lat : lat + args.crop_lat, lon : lon + args.crop_lon]
    data_y = data_y[:, :, lat : lat + args.crop_lat, lon : lon + args.crop_lon]
    return data_x, data_y


def horizontal_flip(data_x, data_y, args):
    if random.random() < 0.5:
        data_x = np.flip(data_x, -1)
        data_y = np.flip(data_y, -1)
    return data_x, data_y


def vertical_flip(data_x, data_y, args):
    if random.random() < 0.5:
        data_x = np.flip(data_x, -2)
        data_y = np.flip(data_y, -2)
    return data_x, data_y


def transpose(data_x, data_y, args):
    if random.random() < 0.5:
        data_x = data_x.transpose(0, 1, 3, 2)
        data_y = data_y.transpose(0, 1, 3, 2)
    return data_x, data_y
