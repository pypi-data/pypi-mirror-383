# -*- coding: utf-8 -*-
import argparse

ARGS_DEFAULT = {
        'cfg_file_path': 'config.yaml',
        'dataset_name': "ACM",
        'pretrain': False,
        'flag': "TRAIN",
        'eval_each': False,
        'drop_edge': 0.0,
        'drop_feature': 0.0,
        'add_edge': 0.0,
        'add_noise': 0.0,
        'rounds': 10,
    }


def parse_arguments(dataset_name: str = "ACM", arg_config: dict = None) -> argparse.Namespace:
    """Parse arguments.

    Args:
        dataset_name (str): Dataset name.
        arg_config (dict): Custom arguments.

    Returns:
        argparse.Namespace: Arguments.
    """
    ARGS_DEFAULT['dataset_name'] = dataset_name
    if arg_config is not None:
        ARGS_DEFAULT.update(arg_config)
    parser = argparse.ArgumentParser()
    for arg_name, arg_default in ARGS_DEFAULT.items():
        arg_type = type(arg_default)
        if arg_type == bool:
            parser.add_argument(f'-{arg_name}', dest=arg_name, action='store_true', default=False)
        else:
            parser.add_argument(f'--{arg_name}', type=arg_type, default=arg_default)
    args = parser.parse_args()
    args.dataset_name = args.dataset_name.upper()
    return args
