import logging
import os
import shutil

logger = logging.getLogger(__name__)


def delete_and_rebuild_directory(directory_path: str):
    """
    clear directory of all files
    """
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)
        logger.info('deleted directory: {}'.format(directory_path))
    os.makedirs(directory_path)
    logger.info('created directory: {}'.format(directory_path))