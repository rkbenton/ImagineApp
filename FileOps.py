import os

from DataManager import DataManager


class FileOps:

    def __init__(self, data_manager: DataManager):
        self.im_im_path = os.environ['IM_IM_PATH']
        self.data_manager = data_manager

    def count_local_files(self):
        """
        Recursively count all files and total sizes in directory defined by
        save_directory_path. We also return max_num_saved_files since that
        is germaine to the total file count.
        :return: a tuple of file_count, total_size, max_num_saved_files
        """
        file_count = 0
        total_size = 0
        config = self.data_manager.get_config()
        root_dir = os.path.join(self.im_im_path, config['save_directory_path'])
        for root, _, files in os.walk(root_dir):
            for file in files:
                full_path = os.path.join(root, file)
                file_count += 1
                total_size += os.path.getsize(full_path)
        return file_count, total_size, config['max_num_saved_files']
