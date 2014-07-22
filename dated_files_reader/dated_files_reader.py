import pickle
import datetime
import os.path as path

default_date_format = '%Y/%m/%d'


class DatedFilesReader:
    """To only be used in a with block. This class will read a file up to
    the current date and will store progress information into a specified
    checkpoint file."""
    def __init__(self, checkpoint_filename):
        self.checkpoint_filename = checkpoint_filename

    def __enter__(self):
        """Only load checkpoint data when used in a with block"""
        self.checkpoints = pickle.load(open(self.checkpoint_filename, 'rb')) \
            if path.isfile(self.checkpoint_filename) else {}
        return self

    def __exit__(self, type, value, traceback):
        """Serialize pickled object when exiting the with block"""
        pickle.dump(self.checkpoints, open(self.checkpoint_filename, 'wb'))

    def read_file(self, filename_template, from_date=datetime.date.today(),
                  date_fmt=default_date_format, force_date=False):
        """Returns the lines in a file using previous checkpoint data and
        reading up until the most recent data"""
        if not (hasattr(self, 'checkpoints') or '{date}' in filename_template):
            return
        elif filename_template in self.checkpoints and not force_date:
            date, offset = self.checkpoints[filename_template]
        else:
            date = from_date
            offset = 0
        cur_date = date
        while cur_date <= datetime.date.today():
            with open(filename_template.format(
                    date=cur_date.strftime(date_fmt))) as f:
                if cur_date != date:
                    date = cur_date
                    offset = 0
                else:
                    f.seek(offset)
                for line in f:
                    offset += len(line)
                    yield line.strip()
                cur_date += datetime.timedelta(days=1)
        self.checkpoints[filename_template] = (date, offset)
