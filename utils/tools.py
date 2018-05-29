import logging
import os
import shutil

logger = logging.getLogger(__name__)


def delete_and_rebuild_directory(directory_paths: list):
    """
    clear directories in directory_paths of all files by deleting and recreating
    """
    for dir in directory_paths:
        if os.path.exists(dir):
            shutil.rmtree(dir)
            logger.info('deleted directory: {}'.format(dir))
        os.makedirs(dir)
        logger.info('created directory: {}'.format(dir))