import os
import numpy as np
import pandas as pd
import psutil
from skimage import io
import time
import shutil
from nd2reader import ND2Reader
import cv2
from scipy.ndimage import gaussian_filter
from skimage.feature import peak_local_max
from sklearn.cluster import DBSCAN

def to8bit(img):
    """
    Auto adjust the contrast of an image and convert it to 8-bit. The input image dtype can be float or int of any bit-depth. The function handles spuriously bright pixels by clipping the image with the 5-sigma rule (inspired by processing active nematics data). The function also works with images containing NaN values.

    :param img: mono image of any dtype
    :type img: 2D numpy.array
    :return: 8-bit image with contrast enhanced.
    :rtype: 2D numpy.array (uint8)

    >>> from myimagelib import to8bit
    >>> img8 = to8bit(img)

    .. rubric:: Edit

    * Feb 27, 2023 -- change ``img.max()`` to ``np.nanmax(img)`` to handle NaN values. 
    * Mar 16, 2023 -- use mean and std to infer upper bound. This makes the function more stable to images with spurious pixels with extremely large intensity. 
    * Mar 17, 2023 -- using upper bound that is smaller than the maximal pixel intensity causes dark "patches" in the rescaled images due to the data type change to "uint8". The solution is to ``clip`` the images with the determined bounds first, then apply the data type conversion. In this way, the over exposed pixels will just reach the saturation value 255.
    * Feb 27, 2025 -- convert the image to float32 before processing, to avoid overflow when the image is of int8 type when performing clipping.
    * Oct 12, 2025 -- add a tiny number to both numerator and denominator, so that the rescaling is never invalid. E.g. for a uniform image, `maxx-minn=0` will now be the tiny number `eps`.
    """

    img = img.astype('float32')
    mean = np.nanmean(img)
    std = np.nanstd(img)
    maxx = min(mean + 5 * std, np.nanmax(img))
    minn = np.nanmin(img)
    img.clip(minn, maxx, out=img)
    eps = np.finfo(np.float32).tiny
    img8 = (img - minn + eps) / (maxx - minn + eps) * 255
    return img8.astype('uint8')

def bestcolor(n):
    """
    A good colormap for categorical data plots. Color Universal Design (CUD) colorblind-safe.

    :param n: integer from 0 to 9, specifying the index of the color in the list
    :type n: int
    :return: the hex code of the specified color
    :rtype: str

    >>> from myimagelib import bestcolor
    >>> bestcolor(0)
    """
    # colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    colors = ["#377eb8", "#ff7f00", "#4daf4a", "#f781bf", "#a65628", "#984ea3", "#999999", "#e41a1c", "#dede00"]
    return colors[n]

def wowcolor(n):
    """
    WOW class color scheme, used in my density fluctuations paper. I used to think these colors are aesthetically pleasing, but now I feel they are too saturated and cause eye fatigue easily. Therefore I would avoid using these colors in future publications.

    :param n: integer from 0 to 9, specifying the index of the color in the list
    :type n: int
    :return: the hex code of the specified color
    :rtype: str
    """
    colors = ['#C41F3B', '#A330C9', '#FF7D0A', '#A9D271', '#40C7EB',
              '#00FF96', '#F58CBA', '#FFF569', '#0070DE', '#8787ED',
              '#C79C6E', '#BBBBBB', '#1f77b4', '#ff7f0e', '#2ca02c',
              '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
              '#bcbd22', '#17becf']
    return colors[n]

def imfindcircles(img, radius, edge_width=10, smooth_window=11, nIter=1):
    """
    Find circles in images. The algorithm is based on Hough Transform and the idea of `Atherton and Kerbyson 1999 <https://www.sciencedirect.com/science/article/pii/S0262885698001607>`_, using the edge orientation information to improve the performance on noisy images. See `step-by-step phase code find circles <../tests/find_circles.html>`_ for more details about this method.

    :param img: Input image. Note that it has to be grayscale and 8-bit, otherwise the function will raise an error.
    :type img: numpy array
    :param radius: Radius of circles to detect. A list of 2 values, [minimum, maximum].
    :type radius: list
    :param edge_width: An estimated with of the edge in pixels. Default is 10.
    :type edge_width: int
    :param smooth_window: Size of the Gaussian window for smoothing the image / gradient field / accumulator. Default is 11.
    :type smooth_window: int
    :param nIter: Number of iterations for multi-stage detection. Default is 1. When nIter > 1, the function will run the detection multiple times with different radius ranges. This is useful when the circles have different sizes.
    :type nIter: int
    :return: DataFrame with columns [x, y, r] for the centers and radii of detected circles.
    :rtype: pandas.DataFrame

    >>> from myimagelib import imfindcircles
    >>> circles = imfindcircles(img, [50, 120])
    >>> circles = imfindcircles(img, [50, 120], edge_width=5)
    >>> circles = imfindcircles(img, [50, 120], edge_width=5, smooth_window=5)
    >>> circles = imfindcircles(img, [50, 120], edge_width=5, smooth_window=5, nIter=4)

    .. rubric:: Edit
    
    * Feb 27, 2025 -- Initial commit.
    * Feb 28, 2025 -- (i) Add `smooth_window` argument, include the preprocessing step in this function to simplify the code on the user side; (ii) determine step size adaptively.
    * Mar 04, 2025 -- Smooth the score before locating the peak.
    * Mar 05, 2025 -- (i) Implement multi-stage detection. Add `nIter` argument to determine the number of iterations. (ii) Use threshold of magnitude (magnitude > mean + 2*std) to determine the strong edges.
    """

    assert(img.ndim == 2), "Input image must be grayscale"
    assert(img.dtype == np.uint8), "Input image must be 8-bit"

    # Loop through radius values, updating accumulator
    min_radius, max_radius = radius
    # estimate smooth sigma for score
    sigma = edge_width / 100 * (max_radius - min_radius) / 3
    # make sure the window size is odd
    s = smooth_window // 2 * 2 + 1 

    # preprocess the image
    # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(5, 5))
    # img = clahe.apply(img)
    img = cv2.GaussianBlur(img, (s, s), 0)

    # Compute image gradients (Sobel)
    grad_x = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)

    # smooth the gradient images
    grad_x = cv2.GaussianBlur(grad_x, (s, s), 0)
    grad_y = cv2.GaussianBlur(grad_y, (s, s), 0)

    # Compute gradient magnitude and direction
    magnitude = np.sqrt(grad_x**2 + grad_y**2)
    direction = np.arctan2(grad_y, grad_x) + np.pi
    
    # Thresholding for strong edges
    # strong_edges = cv2.Canny(img, 100, 150) > 0
    strong_edges = magnitude > magnitude.mean() + 2 * magnitude.std()

    def imfindcircles_one(magnitude, direction, strong_edges, min_radius, max_radius, sigma):
        # Create accumulator using vectorized voting
        height, width = magnitude.shape
        accumulator = np.zeros_like(img, dtype=np.float32)
        # Get indices of strong edge points
        y_idx, x_idx = np.where(strong_edges)
        theta = direction[y_idx, x_idx]
        # Precompute cosine and sine values for efficiency
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)
        
        for r in np.linspace(min_radius, max_radius, 10):  # Step size of 5 for performance
            x_shift = (r * cos_theta).astype(np.int32)
            y_shift = (r * sin_theta).astype(np.int32)
            xc = x_idx - x_shift
            yc = y_idx - y_shift
            # Validity check
            valid = (xc >= 0) & (xc < width) & (yc >= 0) & (yc < height)
            accumulator[yc[valid], xc[valid]] += magnitude[y_idx[valid], x_idx[valid]]

        # Apply Gaussian smoothing to accumulator
        accumulator_smooth = gaussian_filter(accumulator, sigma=(min_radius//10)*2+1)
        # Find local maxima
        centers = peak_local_max(accumulator_smooth, min_distance=int(max_radius), threshold_abs=0.1)

        radii = []
        scores = []
        angles = np.linspace(0, 2*np.pi, 20) # 8 angles
        for y, x in centers:
            radius_votes = []
            scores_tmp = []
            for r in np.linspace(min_radius, max_radius, 100):
                dx, dy = (r * np.cos(angles)).astype(int), (r * np.sin(angles)).astype(int)
                if (0 <= x + dx).all() and (x + dx < width).all() \
                    and (0 <= y + dy).all and (y + dy < height).all(): # validity check
                    score = magnitude[y + dy, x + dx].mean() 
                    radius_votes.append(r)
                    scores_tmp.append(score)
            if scores_tmp:
                scores_smooth = gaussian_filter(scores_tmp, sigma=sigma)
                best_radius = radius_votes[np.argmax(scores_smooth)]
                radii.append(best_radius)
                scores.append(np.max(scores_smooth))
            else:
                radii.append(0)
                scores.append(0)

        # construct the dataframe for centers and radii
        df = pd.DataFrame(centers, columns=["y", "x"])
        df["r"] = radii
        df["score"] = scores

        # keep only the circles with radius > 0
        df = df[df["r"] > 0]

        return df

    if nIter > 1:
        min_r, max_r = radius
        ranges, step = np.linspace(min_r, max_r, num=nIter, endpoint=False, retstep=True)
        df_list = []
        for min_radius in ranges:
            max_radius = min_radius + step
            df_tmp = imfindcircles_one(magnitude, direction, strong_edges, \
                min_radius, max_radius, sigma)
            df_list.append(df_tmp)
        df = pd.concat(df_list).reset_index(drop=True)
    else:
        df = imfindcircles_one(magnitude, direction, strong_edges, min_radius, max_radius
        , sigma)
        return df.drop(columns=["score"])

    # filter overlapping circles
    # Define the threshold distance
    threshold_distance = min_r
    # Apply DBSCAN clustering
    db = DBSCAN(eps=threshold_distance, min_samples=1).fit(df[['x', 'y']])
    df['cluster'] = db.labels_
    # construct a new dataframe to store the final result
    g_list = []
    for c, g in df.groupby("cluster"):
        g = g.loc[[g['score'].idxmax()]]
        if len(g) > 1:
            print(c, len(g))
        g_list.append(g)
    df_final = pd.concat(g_list)

    return df_final.drop(columns=["cluster", "score"])

def show_progress(progress, label='', bar_length=60):
    """
    Display a progress bar in command line environment, which looks like

    .. code-block:: console

      label [##############-----------] 62%

    This is a useful tool for tracking work progress in a batch processing task on a server.

    :param progress: the progress of the work. It is a number between 0 and 1, where 0 is start and 1 is finish
    :type progress: float
    :param label: a string to put before the progress bar. It can be the name of the work, or the actual number of files that have been processed, and so on. Default to :code:`''`.
    :type label: str
    :param bar_length: length of the progress bar, in the unit of characters. Default to :code:`60`.
    :type bar_length: int
    :return: None

    >>> from myimagelib import show_progress
    >>> show_progress(0.5, label='Processing')
    >>> show_progress(0.75, label='Processing', bar_length=80)
    """
    N_finish = int(progress*bar_length)
    N_unfinish = bar_length - N_finish
    print('{0} [{1}{2}] {3:.1f}%'.format(label, '#'*N_finish, '-'*N_unfinish, progress*100), end="\r")


def xy_bin(xo, yo, n=100, mode='log', bins=None):
    """
    Bin x, y data on log or linear scale. This is used when the data is too dense to be plotted directly. The function will bin the data and return the means in each bin.

    :param xo: input x
    :param yo: input y
    :param n: points after binning
    :param mode: ``"lin"`` or ``"log"``, scale to bin the data
    :param bins: set the bins to bin data together

    :return: binned x, and mean y in the bins.
    :rtype: 2-tuple of array-likes

    >>> from myimagelib import xy_bin
    >>> x, y = xy_bin(xo, yo, n=100)
    >>> x, y = xy_bin(xo, yo, n=100, mode='lin')
    >>> x, y = xy_bin(xo, yo, bins=np.linspace(0, 100)')

    .. rubric:: Edit

    * Nov 04, 2020 -- Change function name to ``xy_bin``, to incorporate the mode parameter, so that the function can do both log space binning and linear space binning.
    * Nov 17, 2020 -- add bins kwarg, allow user to enter custom bins.
    * Dec 16, 2021 -- fix divided by 0 issue.
    * Nov 14, 2022 -- Move from ``corrLib`` to ``myImageLib``.
    * Apr 01, 2025 -- Remove nan before binning, to avoid all-nan yb.
    """
    df = pd.DataFrame({"xo": xo, "yo": yo})
    df.dropna(inplace=True)
    xo = df.xo.values
    yo = df.yo.values
    if bins is None:
        if mode == 'log':
            x = np.logspace(np.log10(xo[xo>0].min()), np.log10(xo.max()), n+1)
        elif mode == 'lin':
            x = np.linspace(xo.min(), xo.max(), n+1)
    else:
        x = np.sort(bins)
    top = np.histogram(xo, x, weights=yo)[0]
    bot = np.histogram(xo, x)[0]
    ind = bot > 0
    xb = ((x[1:] + x[:-1]) / 2)[ind]
    yb = top[ind] / bot[ind]
    return xb, yb




class rawImage:
    """
    Convert raw images (e.g. nd2) to tif sequences. Throughout my research, I have mostly worked with two raw image formats: *\*.nd2* and *\*.raw*. Typically, they are tens of GB large, and are not feasible to load into the memory of a PC as a whole. Therefore, the starting point of my workflow is to convert raw images into sequences of *\*.tif* images. 
    
    This class is designed to have a unified interface for different raw image formats. The class is initialized with the directory of a raw image file, and the :py:func:`extract_tif` method will convert the raw image to tif sequences. The tif sequences are saved in a subfolder named *raw* and *8-bit* under the folder where the raw image file is located.
    
    .. code-block:: python

       from myimagelib import rawImage
       file_dir = "path/to/your/file.nd2"
       img = rawImage(file_dir)
       img.extract_tif()
    """

    def __init__(self, file_dir):
        """
        Construct rawImage object using the file directory.
        """
        self.file = file_dir
        self.type = os.path.splitext(self.file)[1]
        if self.type == ".nd2":
            with ND2Reader(self.file) as images:
                self.images = images
        elif self.type == ".raw":
            pass
        else:
            raise ValueError
    def __repr__(self):
        """Ideally, I can see some general informations about this image. For example, the number of frames and the frame size. Frame rate would also be helpful."""
        repr_str = "source file: {0}\nimage shape: {1}".format(self.file, self.images.shape)
        return repr_str
    def extract_tif(self):
        """Extract tif sequence from raw image files."""
        file, ext = os.path.splitext(self.file)
        if ext == ".raw":
            self._extract_raw()
        elif ext == ".nd2":
            self._extract_nd2()
        else:
            raise ValueError("Unrecognized image format {}".format(ext))
    def _extract_raw(self, cutoff=None):
        """Extract tif sequence from *\*.raw* file.
        :param cutoff: number of images to extract

        .. rubric:: Edit

        * Dec 07, 2022: fix progress bar error.
        """
        # read info from info_file
        folder, file = os.path.split(self.file)
        info_file = os.path.join(folder, "RawImageInfo.txt")
        if os.path.exists(info_file):
            fps, h, w = self.read_raw_image_info(info_file)
        else:
            print("Info file missing!")

        # create output folders, skip if both folders exist
        save_folder = folder
        out_raw_folder = os.path.join(save_folder, 'raw')
        out_8_folder = os.path.join(save_folder, '8-bit')
        if os.path.exists(out_raw_folder) and os.path.exists(out_8_folder):
            print(time.asctime() + " // {} tif folders exists, skipping".format(self.file))
            return None
        if os.path.exists(out_raw_folder) == False:
            os.makedirs(out_raw_folder)
        if os.path.exists(out_8_folder) == False:
            os.makedirs(out_8_folder)

        # check disk
        if self._disk_capacity_check() == False:
            raise SystemError("No enough disk capacity!")

        # calculate buffer size based on available memory, use half of it
        file_size = os.path.getsize(self.file)
        avail_mem = psutil.virtual_memory().available
        unit_size = (h * w + 2) * 2 # the size of a single unit in bytes (frame# + image)
        buffer_size = ((avail_mem // 2) // unit_size) * unit_size # integer number of units
        remaining_size = file_size

        # print("Memory information:")
        # print("Available memory: {:.1f} G".format(avail_mem / 2 ** 30))
        # print("File size: {:.1f} G".format(file_size / 2 ** 30))
        # print("Buffer size: {:.1f} G".format(buffer_size / 2 ** 30))

        # read the binary files, in partitions if needed
        num = 0
        n_images = int(file_size // unit_size)
        t0 = time.monotonic()
        while remaining_size > 0:
            # load np.array from buffer
            if remaining_size > buffer_size:
                read_size = buffer_size
            else:
                read_size = remaining_size
            with open(self.file, "rb") as f:
                f.seek(-remaining_size, 2) # offset bin file reading, counting remaining size from EOF
                bytestring = f.read(read_size)
                a = np.frombuffer(bytestring, dtype=np.uint16)
            remaining_size -= read_size

            # manipulate the np.array
            assert(a.shape[0] % (h*w+2) == 0)
            num_images = a.shape[0] // (h*w+2)
            img_in_row = a.reshape(num_images, h*w+2)
            labels = img_in_row[:, :2] # not in use currently
            images = img_in_row[:, 2:]
            images_reshape = images.reshape(num_images, h, w)

            # save the image sequence
            for label, img in zip(labels, images_reshape):
                # num = label[0] + label[1] * 2 ** 16 + 1 # convert image label to uint32 to match the info in StagePosition.txt
                io.imsave(os.path.join(save_folder, 'raw', '{:05d}.tif'.format(num)), img, check_contrast=False)
                io.imsave(os.path.join(save_folder, '8-bit', '{:05d}.tif'.format(num)), to8bit(img), check_contrast=False)
                t1 = time.monotonic() - t0
                show_progress((num+1 / n_images), label="{:.1f} frame/s".format(num / t1))
                num += 1
                if cutoff is not None:
                    if num > cutoff:
                        return None

    def read_raw_image_info(self, info_file):
        """
        Read image info, such as fps and image dimensions, from *\*.RawImageInfo.txt*.
        Helper function of :py:func:`myImageLib.rawImage.extract_raw`.
        """
        with open(info_file, 'r') as f:
            a = f.read()
        fps, h, w = a.split('\n')[0:3]
        return int(fps), int(h), int(w)

    def _extract_nd2(self):
        """
        Extract tif sequence from *\*.nd2* file.
        """
        # check disk
        if self._disk_capacity_check() == False:
            raise SystemError("No enough disk capacity!")

        folder, file = os.path.split(self.file)
        name, ext = os.path.splitext(file)
        saveDir = os.path.join(folder, name, 'raw')
        saveDir8 = os.path.join(folder, name, '8-bit')
        if os.path.exists(saveDir) == False:
            os.makedirs(saveDir)
        if os.path.exists(saveDir8) == False:
            os.makedirs(saveDir8)
        t0 = time.monotonic()
        with ND2Reader(self.file) as images:
            n_images = len(images)
            for num, image in enumerate(images):
                io.imsave(os.path.join(saveDir8, '{:05d}.tif'.format(num)), to8bit(image))
                io.imsave(os.path.join(saveDir, '%05d.tif' % num), image, check_contrast=False)
                t1 = time.monotonic() - t0
                show_progress((num+1) / n_images, label="{:.1f} frame/s".format(num/t1))

    def _disk_capacity_check(self):
        """Check if the capacity of disk is larger than twice of the file size.
        Args:
        file -- directory of the (.nd2) file being converted
        Returns:
        flag -- bool, True if capacity is enough."""
        d = os.path.split(self.file)[0]
        fs = os.path.getsize(self.file) / 2**30
        ds = shutil.disk_usage(d)[2] / 2**30
        print("File size {0:.1f} GB, Disk size {1:.1f} GB".format(fs, ds))
        return ds > 2 * fs

