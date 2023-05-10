import cv2
from time import time
from cv2 import (CAP_PROP_FOURCC, CAP_PROP_FPS, CAP_PROP_FRAME_COUNT,
                 CAP_PROP_FRAME_HEIGHT, CAP_PROP_FRAME_WIDTH,
                 CAP_PROP_POS_FRAMES, VideoWriter_fourcc)
import os.path as osp
import os
from collections import OrderedDict
from collections.abc import Iterable
from shutil import get_terminal_size
import sys


class Cache:

    def __init__(self, capacity):
        self._cache = OrderedDict()
        self._capacity = int(capacity)
        if capacity <= 0:
            raise ValueError('capacity must be a positive integer')

    @property
    def capacity(self):
        return self._capacity

    @property
    def size(self):
        return len(self._cache)

    def put(self, key, val):
        if key in self._cache:
            return
        if len(self._cache) >= self.capacity:
            self._cache.popitem(last=False)
        self._cache[key] = val

    def get(self, key, default=None):
        val = self._cache[key] if key in self._cache else default
        return val


class TimerError(Exception):

    def __init__(self, message):
        self.message = message
        super(TimerError, self).__init__(message)


class Timer:
    def __init__(self, start=True, print_tmpl=None):
        self._is_running = False
        self.print_tmpl = print_tmpl if print_tmpl else '{:.3f}'
        if start:
            self.start()

    @property
    def is_running(self):
        """bool: indicate whether the timer is running"""
        return self._is_running

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        print(self.print_tmpl.format(self.since_last_check()))
        self._is_running = False

    def start(self):
        """Start the timer."""
        if not self._is_running:
            self._t_start = time()
            self._is_running = True
        self._t_last = time()

    def since_start(self):
        """Total time since the timer is started.

        Returns (float): Time in seconds.
        """
        if not self._is_running:
            raise TimerError('timer is not running')
        self._t_last = time()
        return self._t_last - self._t_start

    def since_last_check(self):
        """Time since the last checking.

        Either :func:`since_start` or :func:`since_last_check` is a checking
        operation.

        Returns (float): Time in seconds.
        """
        if not self._is_running:
            raise TimerError('timer is not running')
        dur = time() - self._t_last
        self._t_last = time()
        return dur


class ProgressBar:
    """A progress bar which can print the progress."""

    def __init__(self, task_num=0, bar_width=50, start=True, file=sys.stdout):
        self.task_num = task_num
        self.bar_width = bar_width
        self.completed = 0
        self.file = file
        if start:
            self.start()

    @property
    def terminal_width(self):
        width, _ = get_terminal_size()
        return width

    def start(self):
        if self.task_num > 0:
            self.file.write(f'[{" " * self.bar_width}] 0/{self.task_num}, '
                            'elapsed: 0s, ETA:')
        else:
            self.file.write('completed: 0, elapsed: 0s')
        self.file.flush()
        self.timer = Timer()

    def update(self, num_tasks=1):
        assert num_tasks > 0
        self.completed += num_tasks
        elapsed = self.timer.since_start()
        if elapsed > 0:
            fps = self.completed / elapsed
        else:
            fps = float('inf')
        if self.task_num > 0:
            percentage = self.completed / float(self.task_num)
            eta = int(elapsed * (1 - percentage) / percentage + 0.5)
            msg = f'\r[{{}}] {self.completed}/{self.task_num}, ' \
                  f'{fps:.1f} task/s, elapsed: {int(elapsed + 0.5)}s, ' \
                  f'ETA: {eta:5}s'

            bar_width = min(self.bar_width,
                            int(self.terminal_width - len(msg)) + 2,
                            int(self.terminal_width * 0.6))
            bar_width = max(2, bar_width)
            mark_width = int(bar_width * percentage)
            bar_chars = '>' * mark_width + ' ' * (bar_width - mark_width)
            self.file.write(msg.format(bar_chars))
        else:
            self.file.write(
                f'completed: {self.completed}, elapsed: {int(elapsed + 0.5)}s,'
                f' {fps:.1f} tasks/s')
        self.file.flush()


class VideoReader:
    """Implemented by OpenMMLab in MMAction2 (https://github.com/open-mmlab/mmaction2)

    Video class with similar usage to a list object.

    This video warpper class provides convenient apis to access frames.
    There exists an issue of OpenCV's VideoCapture class that jumping to a
    certain frame may be inaccurate. It is fixed in this class by checking
    the position after jumping each time.
    Cache is used when decoding videos. So if the same frame is visited for
    the second time, there is no need to decode again if it is stored in the
    cache.
    """

    def __init__(self, filename, cache_capacity=10):
        # Check whether the video path is a url
        if not filename.startswith(('https://', 'http://')):
            self.check_file_exist(filename, 'Video file not found: ' + filename)
        self._vcap = cv2.VideoCapture(filename)
        assert cache_capacity > 0
        self._cache = Cache(cache_capacity)
        self._position = 0
        # get basic info
        self._width = int(self._vcap.get(CAP_PROP_FRAME_WIDTH))
        self._height = int(self._vcap.get(CAP_PROP_FRAME_HEIGHT))
        self._fps = self._vcap.get(CAP_PROP_FPS)
        self._frame_cnt = int(self._vcap.get(CAP_PROP_FRAME_COUNT))
        self._fourcc = self._vcap.get(CAP_PROP_FOURCC)

    @staticmethod
    def check_file_exist(filename, msg_tmpl='file "{}" does not exist'):
        if not osp.isfile(filename):
            raise FileNotFoundError(msg_tmpl.format(filename))

    @staticmethod
    def mkdir_or_exist(dir_name, mode=0o777):
        if dir_name == '':
            return
        dir_name = osp.expanduser(dir_name)
        os.makedirs(dir_name, mode=mode, exist_ok=True)

    @staticmethod
    def track_progress(func, tasks, bar_width=50, file=sys.stdout, **kwargs):
        """Track the progress of tasks execution with a progress bar.

        Tasks are done with a simple for-loop.

        Args:
            func (callable): The function to be applied to each task.
            tasks (list or tuple[Iterable, int]): A list of tasks or
                (tasks, total num).
            bar_width (int): Width of progress bar.

        Returns:
            list: The task results.
        """
        if isinstance(tasks, tuple):
            assert len(tasks) == 2
            assert isinstance(tasks[0], Iterable)
            assert isinstance(tasks[1], int)
            task_num = tasks[1]
            tasks = tasks[0]
        elif isinstance(tasks, Iterable):
            task_num = len(tasks)
        else:
            raise TypeError(
                '"tasks" must be an iterable object or a (iterator, int) tuple')
        prog_bar = ProgressBar(task_num, bar_width, file=file)
        results = []
        for task in tasks:
            results.append(func(task, **kwargs))
            prog_bar.update()
        prog_bar.file.write('\n')
        return results

    @property
    def vcap(self):
        """:obj:`cv2.VideoCapture`: The raw VideoCapture object."""
        return self._vcap

    @property
    def opened(self):
        """bool: Indicate whether the video is opened."""
        return self._vcap.isOpened()

    @property
    def width(self):
        """int: Width of video frames."""
        return self._width

    @property
    def height(self):
        """int: Height of video frames."""
        return self._height

    @property
    def resolution(self):
        """tuple: Video resolution (width, height)."""
        return (self._width, self._height)

    @property
    def fps(self):
        """float: FPS of the video."""
        return self._fps

    @property
    def frame_cnt(self):
        """int: Total frames of the video."""
        return self._frame_cnt

    @property
    def fourcc(self):
        """str: "Four character code" of the video."""
        return self._fourcc

    @property
    def position(self):
        """int: Current cursor position, indicating frame decoded."""
        return self._position

    def _get_real_position(self):
        return int(round(self._vcap.get(CAP_PROP_POS_FRAMES)))

    def _set_real_position(self, frame_id):
        self._vcap.set(CAP_PROP_POS_FRAMES, frame_id)
        pos = self._get_real_position()
        for _ in range(frame_id - pos):
            self._vcap.read()
        self._position = frame_id

    def read(self):
        """Read the next frame.

        If the next frame have been decoded before and in the cache, then
        return it directly, otherwise decode, cache and return it.

        Returns:
            ndarray or None: Return the frame if successful, otherwise None.
        """
        # pos = self._position
        if self._cache:
            img = self._cache.get(self._position)
            if img is not None:
                ret = True
            else:
                if self._position != self._get_real_position():
                    self._set_real_position(self._position)
                ret, img = self._vcap.read()
                if ret:
                    self._cache.put(self._position, img)
        else:
            ret, img = self._vcap.read()
        if ret:
            self._position += 1
        return img

    def get_frame(self, frame_id):
        """Get frame by index.

        Args:
            frame_id (int): Index of the expected frame, 0-based.

        Returns:
            ndarray or None: Return the frame if successful, otherwise None.
        """
        if frame_id < 0 or frame_id >= self._frame_cnt:
            raise IndexError(
                f'"frame_id" must be between 0 and {self._frame_cnt - 1}')
        if frame_id == self._position:
            return self.read()
        if self._cache:
            img = self._cache.get(frame_id)
            if img is not None:
                self._position = frame_id + 1
                return img
        self._set_real_position(frame_id)
        ret, img = self._vcap.read()
        if ret:
            if self._cache:
                self._cache.put(self._position, img)
            self._position += 1
        return img

    def current_frame(self):
        """Get the current frame (frame that is just visited).

        Returns:
            ndarray or None: If the video is fresh, return None, otherwise
                return the frame.
        """
        if self._position == 0:
            return None
        return self._cache.get(self._position - 1)

    def cvt2frames(self,
                   frame_dir,
                   file_start=0,
                   filename_tmpl='{:06d}.jpg',
                   start=0,
                   max_num=0,
                   show_progress=True):
        """Convert a video to frame images.

        Args:
            frame_dir (str): Output directory to store all the frame images.
            file_start (int): Filenames will start from the specified number.
            filename_tmpl (str): Filename template with the index as the
                placeholder.
            start (int): The starting frame index.
            max_num (int): Maximum number of frames to be written.
            show_progress (bool): Whether to show a progress bar.
        """
        self.mkdir_or_exist(frame_dir)
        if max_num == 0:
            task_num = self.frame_cnt - start
        else:
            task_num = min(self.frame_cnt - start, max_num)
        if task_num <= 0:
            raise ValueError('start must be less than total frame number')
        if start > 0:
            self._set_real_position(start)

        def write_frame(file_idx):
            img = self.read()
            if img is None:
                return
            filename = osp.join(frame_dir, filename_tmpl.format(file_idx))
            cv2.imwrite(filename, img)

        if show_progress:
            self.track_progress(write_frame, list(range(file_start, file_start + task_num)))
        else:
            for i in range(task_num):
                write_frame(file_start + i)

    def __len__(self):
        return self.frame_cnt

    def __getitem__(self, index):
        if isinstance(index, slice):
            return [
                self.get_frame(i)
                for i in range(*index.indices(self.frame_cnt))
            ]
        # support negative indexing
        if index < 0:
            index += self.frame_cnt
            if index < 0:
                raise IndexError('index out of range')
        return self.get_frame(index)

    def __iter__(self):
        self._set_real_position(0)
        return self

    def __next__(self):
        img = self.read()
        if img is not None:
            return img
        else:
            raise StopIteration

    next = __next__

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._vcap.release()
