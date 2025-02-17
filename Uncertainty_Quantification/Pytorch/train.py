from argparse import ArgumentParser
import loader
import random
from models import unet3d, resnet2d_simple
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks.early_stopping import EarlyStopping

YEARS = [str(i) for i in range(1999, 2018)]


def main():

    # Set reproducability seed
    random.seed(42)

    parser = ArgumentParser()
    parser = Trainer.add_argparse_args(parser)

    parser.add_argument(
        "--model_name",
        type=str,
        default="resnet2d_simple",
        help="{3DUNet,resnet2d_simple}",
    )

    # To pull the model name
    temp_args, _ = parser.parse_known_args()

    parser.add_argument(
        "--data_directory",
        type=str,
        default="/users/petergro/RSTA_DATA",
        help="Pass your data directoy here",
    )
    parser.add_argument(
        "--parameters",
        nargs="+",
        default=[
            "Temperature",
            "SpecHum",
            "VertVel",
            "U",
            "V",
            "Geopotential",
            "Divergence",
        ],
        help="The parameters that will be used",
    )
    parser.add_argument(
        "--augmentation",
        nargs="+",
        default=[
            # "RandomCrop",
            # "RandomHorizontalFlip",
            # "RandomVerticalFlip",
            # "Transpose",
        ],
        help='["RandomCrop","RandomHorizontalFlip","RandomVerticalFlip","Transpose"]',
    )
    parser.add_argument(
        "--max_lat",
        type=int,
        default=352,
        help="Maximum latitude used as crop limit to allow for down and upscaling",
    )
    parser.add_argument(
        "--max_lon",
        type=int,
        default=704,
        help="Maximum longitude used as crop limit to allow for down and upscaling",
    )
    parser.add_argument(
        "--pressure_levels",
        nargs="+",
        default=[500, 850],
        help="What pressure levels are available",
    )
    parser.add_argument(
        "--dims",
        type=int,
        default=2,
        help="How many dimensions are we predicting in, 2 or 3",
    )
    parser.add_argument(
        "--plvl_used",
        nargs="+",
        default=1,
        help="if --dims is 2, which pressure level are we predicting (index)",
    )
    parser.add_argument(
        "--time_steps",
        nargs="+",
        default=[0, 24, 48],
        help="List of timesteps that are available to use",
    )
    parser.add_argument(
        "--perturbations",
        nargs="+",
        default=[0, 1, 2, 3, 4],
        help="What are the perturbation numbers that we are using",
    )
    parser.add_argument(
        "--crop_lon",
        type=int,
        default=256,
        help="What is the crop size in longitude points for the random crop",
    )
    parser.add_argument(
        "--crop_lat",
        type=int,
        default=256,
        help="What is the crop size in latitude points for the random crop",
    )
    parser.add_argument("--batch_size", type=int, default=8, help="The batch size")
    parser.add_argument(
        "--base_lr",
        type=float,
        default=1e-6,
        help="Base learning rate for the cyclical learning rate scheduler",
    )
    parser.add_argument(
        "--max_lr",
        type=float,
        default=1e-2,
        help="Maximum learning rate for the cyclical learning rate scheduler",
    )
    parser.add_argument(
        "--num_workers",
        type=int,
        default=8,
        help="Set the number of dataloader workers",
    )
    parser.add_argument(
        "--grad_accumulation",
        type=int,
        default=1,
        help="How many gradient passes should be accumulated",
    )
    parser.add_argument(
        "--pred_type",
        type=str,
        default="Temperature",
        help="Which parameter is being predicted",
    )
    parser.add_argument("--aggr_type", type=str, default="Spread", help="Spread | Mean")
    parser.add_argument(
        "--std_folder",
        type=str,
        default="/users/petergro/std",
        help="Folder with the means.npy and stddevs.npy files generated in the data generation",
    )
    parser.add_argument(
        "--fix_split",
        type=bool,
        default=True,
        help="Whether the train, val, test split are random or fixed",
    )

    # if temp_args.model_name == "3DUNet":
    #    parser = 3dunet.add_model_specific_args(parser)

    args = parser.parse_args()

    # Adapt the sample split
    year_dict = {}
    if args.fix_split:
        year_dict["test"] = [YEARS[0], YEARS[-1]]
        year_dict["val"] = [YEARS[1], YEARS[-2]]
        year_dict["train"] = [
            i for e, i in enumerate(YEARS) if 1 < e < (len(YEARS) - 1)
        ]
    else:
        random.shuffle(YEARS)
        year_dict["test"] = [YEARS[0], YEARS[-1]]
        year_dict["val"] = [YEARS[1], YEARS[-2]]
        year_dict["train"] = [
            i for e, i in enumerate(YEARS) if 1 < e < (len(YEARS) - 1)
        ]

    if args.model_name == "3DUNet":
        model = unet3d(
            sample_nr=len(
                loader.WeatherDataset(args, step="train", year_dict=year_dict)
            )
            // args.batch_size,
            base_lr=args.base_lr,
            max_lr=args.max_lr,
            in_channels=len(args.parameters)
            * len(args.time_steps)
            * 2,  # 2 because we use either the mean or the std + the unperturbed trajectory as input
            out_channels=1,  # output temperature only
            args=args,
        )
    elif args.model_name == "resnet2d_simple":
        model = resnet2d_simple(
            sample_nr=(
                len(loader.WeatherDataset(args, step="train", year_dict=year_dict))
                // args.batch_size
            ),
            base_lr=args.base_lr,
            max_lr=args.max_lr,
            in_channels=len(args.parameters)
            * len(args.time_steps)
            * 2,  # 2 because we use either the mean or the std + the unperturbed trajectory as input
            out_channels=1,  # output temperature only
            args=args,
        )

    # --min_epochs 1 --max_epochs 30 --gpus 2 --accelerator ddp --accumulate_grad_batches 1 --resume_from_checkpoint None
    trainer = Trainer.from_argparse_args(args)

    dm = loader.WDatamodule(args, year_dict=year_dict)
    dm.setup(args)

    trainer.fit(model, dm.train, dm.val)

    result = trainer.test(test_dataloaders=dm.test)
    print(result)


if __name__ == "__main__":
    main()
