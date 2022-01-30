import numpy as np
import random


def standardize(x, means, stddevs):
    return (x - means) / stddevs


def unstandardize(x, means, stddevs):
    return x * stddevs + means


def reduce_sample_y(data_y, args):
    """Crops longitude, latitude, selects the prediction parameter and pressure level for the ground truth.

    Args:
        data_y (np.array): Ground truth sample
        args (Object): Parsed arguments

    Returns:
        np.array: reduced ground truth
    """
    # crop to work with 5 pooling operations
    data_y = data_y[:, :, :, : args.max_lat, : args.max_lon]
    ind = 1 if args.aggr_type == "Mean" else 0
    if args.dims == 2:
        data_y = data_y[
            ind, None, args.parameters.index(args.pred_type), args.pred_plvl_used, :, :
        ]
    else:
        data_y = data_y[ind, None, args.parameters.index(args.pred_type), :, :, :]
    return data_y


def reduce_sample_x(
    data_x,
    args,
    means,
    stddevs,
):
    """Crops longitude, latitude, aggregates trajectories into mean and stddev, reshapes and standardizes the input data

    Args:
        data_x (np.array): input data
        args (Object): Parsed argumetns
        means (np.array): Means from LAS
        stddevs (np.array): Stddevs from LAS

    Returns:
        np.array: reduced input data
    """
    # For now plvl used only works with 2d data, can be scaled to be able to select 3d data later if needed
    # crop to work with 5 pooling operations
    data_x = data_x[:, :, :, :, : args.max_lat, : args.max_lon]

    op = np.mean if args.aggr_type == "Mean" else np.std
    stdized = (data_x[:, 0, None, :, :, :, :] - means) / stddevs #We standardize trajectory 0
    data_x = np.concatenate([op(data_x, axis=1, keepdims=True), stdized], axis=1) # concatenate  trajectory-0 with
    # spreads

    if args.dims == 2:

        data_x = data_x[:, :, :, args.plvl_used, :, :]

        data_x = np.reshape(
            data_x,
            [
                data_x.shape[0] * data_x.shape[1] * data_x.shape[2] * data_x.shape[3],
                data_x.shape[4],
                data_x.shape[5],
            ],
        )

    else:
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
    """Randomly crops both input and ground truth data to window size defined in args

    Args:
        data_x (np.array): input data
        data_y (np.array): ground truth data
        args (Object): parsed arguments

    Returns:
        (np.array, np.array): cropped data
    """
    max_lat = data_y.shape[-2] - args.crop_lat
    max_lon = data_y.shape[-1] - args.crop_lon
    lat = random.randint(0, max_lat)
    lon = random.randint(0, max_lon)
    if args.dims == 2:
        data_x = data_x[:, lat : lat + args.crop_lat, lon : lon + args.crop_lon]
        data_y = data_y[:, lat : lat + args.crop_lat, lon : lon + args.crop_lon]
    else:
        data_x = data_x[:, :, lat : lat + args.crop_lat, lon : lon + args.crop_lon]
        data_y = data_y[:, :, lat : lat + args.crop_lat, lon : lon + args.crop_lon]
    return data_x, data_y


def horizontal_flip(data_x, data_y, args):
    """Randomly performs a horizontal flip on both input and ground truth data

    Args:
        data_x (np.array): input data
        data_y (np.array): ground truth data
        args (Object): parsed arguments

    Returns:
        (np.array, np.array): flipped data
    """
    if random.random() < 0.5:
        data_x = np.flip(data_x, -1)
        data_y = np.flip(data_y, -1)
    return data_x, data_y


def vertical_flip(data_x, data_y, args):
    """Randomly performs a vertical flip on both input and ground truth data

    Args:
        data_x (np.array): input data
        data_y (np.array): ground truth data
        args (Object): parsed arguments

    Returns:
        (np.array, np.array): flipped data
    """
    if random.random() < 0.5:
        data_x = np.flip(data_x, -2)
        data_y = np.flip(data_y, -2)
    return data_x, data_y


def transpose(data_x, data_y, args):
    """Randomly transposes both input and ground truth data

    Args:
        data_x (np.array): input data
        data_y (np.array): ground truth data
        args (Object): parsed arguments

    Returns:
        (np.array, np.array): transposed data
    """
    if random.random() < 0.5:
        if args.dims == 2:
            data_x = data_x.transpose(0, 2, 1)
            data_y = data_y.transpose(0, 2, 1)
        else:
            data_x = data_x.transpose(0, 1, 3, 2)
            data_y = data_y.transpose(0, 1, 3, 2)
    return data_x, data_y
