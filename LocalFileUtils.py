import os
import re

from ImImConfigManager import ImImConfigManager


class LocalFileUtils:
    RATING_PATTERN = re.compile(r' r\[(\d\.\d)\]')

    def __init__(self, imim_config_mgr: ImImConfigManager):
        self.im_im_path = os.environ['IM_IM_PATH']
        self.data_manager = imim_config_mgr

    def count_local_files(self, start_dir_name=None):
        """
        Recursively count all files and total sizes in directory defined by
        save_directory_path. We also return max_num_saved_files since that
        is germaine to the total file count. Alternatively, we can look
        at a subdirectory if start_dir_name is passed, e.g. "st_patricks".
        :param start_dir_name: must be the name of a subdirectory of
        the save_directory_path, e.g. "creative". It will create the
        directory if it doesn't exist.' If start_dir_name is None,
        which is the default, we look recursively. from the save_directory_path,
        i.e. image_out.
        :return: a tuple of file_count, total_size_bytes, num_unrated_images, max_num_saved_files,
        each of which is an integer.
        """
        file_count = 0
        total_size = 0
        unrated_images = 0
        config = self.data_manager.get_config()
        if start_dir_name is None:
            root_dir = os.path.join(self.im_im_path, config['save_directory_path'])
        else:
            root_dir = os.path.join(self.im_im_path, config['save_directory_path'], start_dir_name)
            os.makedirs(root_dir, exist_ok=True)
        for root, _, files in os.walk(root_dir):
            for file in files:
                full_path = os.path.join(root, file)
                file_count += 1
                total_size += os.path.getsize(full_path)
                if self.is_image_file(full_path):
                    if not self.is_file_rated(full_path):
                        unrated_images += 1
        return file_count, total_size, unrated_images, config['max_num_saved_files']

    def is_file_rated(self, filepath: str) -> bool:
        result: bool = False
        if os.path.isfile(filepath) and self.is_image_file(filepath):
            result = self.RATING_PATTERN.search(filepath)
        return result

    @staticmethod
    def sizeof_fmt(num, suffix="B"):
        """
        Format bytes to human-friendly string.
        Found on https://stackoverflow.com/questions/1094841/get-a-human-readable-version-of-a-file-size
        Sample usage:
        ```
        >>> sizeof_fmt(168963795964)
        '157.4GiB'
        ```
        :param num:
        :param suffix:
        :return:
        """
        for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
            if abs(num) < 1024.0:
                return f"{num:3.1f}{unit}{suffix}"
            num /= 1024.0
        return f"{num:.1f}Yi{suffix}"

    @staticmethod
    def is_image_file(file_path: str) -> bool:
        """
        Returns True if the file_path points to an image file,
        determined by its file extension.
        """
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
        ext = os.path.splitext(file_path)[1].lower()
        return ext in image_extensions
