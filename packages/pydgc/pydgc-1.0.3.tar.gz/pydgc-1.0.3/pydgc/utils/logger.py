# -*- coding: utf-8 -*-
import os
import time
import logging
import numpy as np

from rich.table import Table
from torch import Tensor

from . import count_parameters
from rich.console import Console
from rich.logging import RichHandler


def get_formatted_time():
    """Get formatted time.

    Returns:
        str: Formatted time in the format of 'YYYY-MM-DD HH-MM-SS'.
    """
    current_time = time.localtime()
    time_format = "%Y-%m-%d %H-%M-%S"
    formatted_time = time.strftime(time_format, current_time)
    return formatted_time


def create_logger(logger_name, log_mode='both', log_file_path=None, encoding='utf-8'):
    """Create logger.

    Args:
        logger_name (str): Used to name logger.
        log_mode (str, optional): Print mode. Options: [file, stdout, both]. Defaults to 'both'.
        log_file_path (str, optional): If print output to file, you must specify file path. Defaults to None.
        encoding (str, optional): Encoding mode, 'utf-8' for default. Defaults to 'utf-8'.

    Returns:
        Logger: Logger.
    """
    if log_mode != 'stdout' and log_file_path is None:
        raise ValueError("log_file_path must be specified when print output to log file!")
    logging.root.handlers = []
    logging_cfg = {'level': logging.INFO, 'format': '%(message)s'}
    h_stdout = RichHandler(show_path=False,
                           keywords=["Random seed",
                                     "Round", "Epoch", "Loss",
                                     "ACC", "NMI", "ARI", "F1", "HOM", "COM", "PUR", "SC", "GRE",
                                     "Time cost"])
    dir_ = os.path.dirname(log_file_path)
    if not os.path.exists(dir_):
        os.makedirs(dir_)
    if log_mode == 'file':
        h_file = logging.FileHandler(log_file_path, encoding=encoding)
        logging_cfg['handlers'] = [h_file]
    elif log_mode == 'stdout':
        logging_cfg['handlers'] = [h_stdout]
    elif log_mode == 'both':
        h_file = logging.FileHandler(log_file_path, encoding=encoding)
        logging_cfg['handlers'] = [h_file, h_stdout]
    else:
        raise ValueError('Print option not supported, options: file, stdout, both')
    logging.basicConfig(**logging_cfg)
    return Logger(name=logger_name)


class Logger(object):
    """Logger.

    Args:
        name (str): Name of logger.
    """

    def __init__(self, name):
        self.logger = logging.getLogger(name)

    def info(self, message):
        """Info level log.

        Args:
            message (str): Log message.
        """
        self.logger.info(message)

    def error(self, message):
        """Error level log.

        Args:
            message (str): Log message.
        """
        self.logger.error(message)

    def debug(self, message):
        """Debug level log.

        Args:
            message (str): Log message.
        """
        self.logger.debug(message)

    def warning(self, message):
        """Warning level log.

        Args:
            message (str): Log message.
        """
        self.logger.warning(message)

    def flag(self, message):
        """Print flag to partition different parts above and below.

        Args:
            message (str): Log message.
        """
        self.logger.info(f"{'*' * 40}{message}{'*' * 40}")

    @staticmethod
    def table(results_dir: str, dataset_name: str, results_dict: dict, decimal: int = 4):
        """Create table.

        Args:
            results_dir (str): Results directory.
            dataset_name (str): Dataset name.
            results_dict (dict): Results dictionary.
            decimal (int, optional): Decimal. Defaults to 4.
        """
        table = Table(title=f"Clustering Results on Dataset {dataset_name}")
        if type(next(iter(results_dict.values()))) in [float, int, np.float32, np.float64, np.int32, np.int64]:
            table.add_column("Metric", justify="right", style="cyan", no_wrap=True)
            table.add_column("Value", justify="right", style="green", no_wrap=True)
            for key, value in results_dict.items():
                table.add_row(key, str(round(value, decimal)))
        else:
            table.add_column("Metric", justify="right", style="cyan", no_wrap=True)
            rounds = len(next(iter(results_dict.values())))
            for i in range(rounds):
                table.add_column(f"{i + 1}", justify="right", style="green", no_wrap=True)
            table.add_column("Avg.", justify="right", style="green", no_wrap=True)
            table.add_column("Std.", justify="right", style="green", no_wrap=True)
            for key, values in results_dict.items():
                table.add_row(key, *[str(round(value, decimal)) for value in values],
                              str(round(np.mean(values), decimal)),
                              str(round(np.std(values), decimal)))
        with open(os.path.join(results_dir, "results.txt"), "a+") as report_file:
            console = Console(file=report_file)
            console.print(get_formatted_time())
            console.print(table)
        console = Console()
        console.print(table)

    def loss(self, epoch, loss, decimal: int = 6):
        """Loss level log.

        Args:
            epoch (int): Epoch.
            loss (float): Loss.
            decimal (int, optional): Decimal. Defaults to 6.
        """
        if isinstance(loss, Tensor):
            loss = loss.item()
        self.logger.info(f"Epoch: {epoch:0>4d}, Loss: {round(loss, decimal):0>.{decimal}f}")

    def model_info(self, model):
        """Model info level log.

        Args:
            model (nn.Module): Model.
        """
        self.logger.info(model)
        self.logger.info(f"Parameters: {count_parameters(model)} MB")
