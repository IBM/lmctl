import logging.config
import yaml
import shutil
from pkg_resources import resource_string
from pathlib import Path
from datetime import datetime

def log_dir() -> Path:
  return Path.home().joinpath('.lmctl').joinpath('logs')

def setup_logging(default_level=logging.INFO):

  logging_config = resource_string("lmctl.utils", 'logging.yaml')

  if logging_config is not None:
    config = yaml.safe_load(logging_config)
    log_dir_path = log_dir()
    log_dir_path.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir_path.joinpath('cli.log')
    config['handlers']['file_handler']['filename'] = str(log_file_path)
    logging.config.dictConfig(config)
    notify_user_if_existing_log_file_in_current_dir(new_log_dir_path=log_dir_path)
  else:
    logging.basicConfig(level=default_level)	


def notify_user_if_existing_log_file_in_current_dir(new_log_dir_path):
  existing_log = Path('lmctl.log')
  if existing_log.exists():
    backup_log_path = Path('lmctl.log.delete')
    existing_log.rename(backup_log_path)
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    with open(backup_log_path, 'a') as f:
      f.write(f'-------------{dt_string}-----------------\n')
      f.write(f'Logs moved to: {new_log_dir_path}\n')
      f.write(f'Delete this file\n')
      f.write(f'-----------------------------------------\n')
    