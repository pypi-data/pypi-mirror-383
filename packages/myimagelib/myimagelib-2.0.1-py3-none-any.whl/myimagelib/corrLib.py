import numpy as np
from skimage import io, util
import pandas as pd

def corrS(X, Y, U, V):
    """
    Compute the spatial autocorrelations of a velocity field.

    :param X,Y,U,V: the result of PIV analysis. Each is a 2D array. Use :py:func:`pivLib.read_piv` to construct thses arrays from PIV data files.
    :type X,Y,U,V: 2d arrays
    :return: x, y, CA, CV -- The angle autocorrelation (CA) and velocity autocorrelation (CV). x, y are the associated distances.

    .. note::

        We only consider half of the length in each dimension, so x, y are different from the input X, Y.

    >>> from myimagelib.corrLib import corrS
    >>> X, Y, CA, CV = corrS(x, y, u, v)

    .. rubric:: Edit

    * Dec 13, 2021 -- i) Replace all the ``mean()`` function to ``nanmean``, to handle masked PIV data. ii) Add doc string.
    * Dec 15, 2021 -- if norm ``vsqrt==0``, set it to np.nan to avoid divided by zero warning!
    * Dec 16, 2021 -- Shift the output X, Y origin to 0, 0, so that 0 distance will have the correlation function = 1. More intuitive.
    * Jan 05, 2023 -- Adapt myimagelib import style.
    """
    row, col = X.shape
    r = int(row/2)
    c = int(col/2)
    vsqrt = (U ** 2 + V ** 2) ** 0.5
    vsqrt[vsqrt==0] = np.nan # if norm is 0, set it to np.nan to avoid divided by zero warning!
    U = U - np.nanmean(U)
    V = V - np.nanmean(V)
    Ax = U / vsqrt
    Ay = V / vsqrt
    CA = np.ones((r, c))
    CV = np.ones((r, c))
    # pdb.set_trace()
    for xin in range(0, c):
        for yin in range(0, r):
            if xin != 0 or yin != 0:
                CA[yin, xin] = np.nanmean((Ax[0:row-yin, 0:col-xin] * Ax[yin:row, xin:col] + Ay[0:row-yin, 0:col-xin] * Ay[yin:row, xin:col]))
                CV[yin, xin] = np.nanmean((U[0:row-yin, 0:col-xin] * U[yin:row, xin:col] + V[0:row-yin, 0:col-xin] * V[yin:row, xin:col])) / (np.nanstd(U)**2+np.nanstd(V)**2)
    return X[0:r, 0:c] - X[0, 0], Y[0:r, 0:c] - Y[0, 0], CA, CV

def corrI(X, Y, I):
    """
    Compute pixel intensity spatial autocorrelation of an image.

    :param X: x coordinates of image pixels
    :type X: 2d array
    :param Y: y coordinates of image pixels
    :type Y: 2d array
    :param I: image
    :type I: 2d array
    :return: XI, YI, CI, where CI is the autocorrelation map and XI and YI are the corresponding coordinates.
    :rtype: 2d arrays
    """
    row, col = I.shape
    I = I - I.mean()
    # CI = np.ones(I.shape)
    r = int(row/2)
    c = int(col/2)
    CI = np.ones((r, c))
    XI = X[0: r, 0: c]
    YI = Y[0: r, 0: c]
    normalizer = I.std() ** 2
    for xin in range(0, int(col/2)):
        for yin in range(0, int(row/2)):
            if xin != 0 or yin != 0:
                I_shift_x = np.roll(I, xin, axis=1)
                I_shift = np.roll(I_shift_x, yin, axis=0)
                CI[yin, xin] = (I[yin:, xin:] * I_shift[yin:, xin:]).mean() / normalizer
    return XI, YI, CI

def divide_windows(img, windowsize=[20, 20], step=10):
    """
    Divide an image into windows with specified size and step. Size and step can be different, so that we generate a downsampled image with either overlap or gaps.

    >>> from myimagelib.corrLib import divide_windows
    >>> X, Y, I = divide_windows(img, windowsize=[20, 20], step=10)

    :param img: image
    :type img: 2d array
    :param windowsize: window size in x and y
    :type windowsize: list(int)
    :param step: distance between the centers of adjacent windows
    :type step: int
    :return: X,Y,I -- I is the downsampled image, while X, Y are the corresponding coordinates in x an y
    :rtype: 2d arrays
    """
    row, col = img.shape
    windowsize[0] = int(windowsize[0])
    windowsize[1] = int(windowsize[1])
    step = int(step)
    if isinstance(windowsize, list):
        windowsize = tuple(windowsize)
    X = np.array(range(0, col-windowsize[0], step))
    Y = np.array(range(0, row-windowsize[1], step))
    X, Y = np.meshgrid(X, Y)
    I = util.view_as_windows(img, windowsize, step=step).mean(axis=(2, 3))
    return X, Y, I

def distance_corr(X, Y, C):
    """ Convert 2d correlation matrix into 1d.

    :param X,Y: 2d coordinates, can be either 2d matrices or flattened matrices
    :param C: correlation matrix, can be either 2d matrices or flattened matrices
    :return: a DataFrame of ["R", "C"].

    >>> from myimagelib.corrLib import distance_corr
    >>> r_corr = distance_corr(X, Y, C)

    .. rubric:: Edit

    * Dec 16, 2021 -- (i) check input dimension, if it's 1, do not use `flatten`; (ii) add doc string
    """
    if len(X.shape) == 2:
        r_corr = pd.DataFrame({'R': (X.flatten()**2 + Y.flatten()**2) ** 0.5, 'C': C.flatten()}).sort_values(by='R')
    else:
        r_corr = pd.DataFrame({'R': (X**2 + Y**2) ** 0.5, 'C': C}).sort_values(by='R')
    return r_corr

def density_fluctuation(img_stack, boxsize=None, size_min=5, step=250):
    """
    Compute number fluctuations of an image stack (3D np.array, frame*h*w)

    :param img_stack: a stack of image, a 3D array
    :param boxsize: a list-like of integers, specify the subsystem size to look at. If None, generate a log spaced array within (size_min, L/2) (pixels), with 100 points
    :param size_min: the smallest box size
    :param step: step used when dividing image into windows

    :return: DataFrame of n and d, where n is box area (px^2) and d is total number fluctuations (box_area*dI)
    :rtype: ``pandas.DataFrame``

    >>> from myimagelib.corrLib import density_fluctuation
    >>> df = density_fluctuation(img_stack, boxsize=None, size_min=5, step=250)
    """
    L = min(img_stack.shape[1:3])
    if boxsize == None:
        boxsize = np.unique(np.floor(np.logspace(np.log10(size_min), np.log10(L/2), 100)))

    dI_list = []
    for bs in boxsize:
        I = divide_stack(img_stack, winsize=[bs, bs], step=step)
        dI = I.std(axis=0).mean() * bs ** 2
        dI_list.append(dI)

    return pd.DataFrame({'n': np.array(boxsize)**2, 'd': dI_list})

def local_df(img_folder, seg_length=50, winsize=50, step=25):
    """
    Compute local density fluctuations of given image sequence in img_folder

    :param img_folder: folder containing .tif image sequence
    :param seg_length: number of frames of each segment of video, for evaluating standard deviations
    :param winsize: window size
    :param step: step between adjacent windows

    :return: dict containing 't' and 'local_df', 't' is a list of time (frame), 'std' is a list of 2d array with local standard deviations corresponding to 't'
    :rtype: ``dict``

    >>> from myimagelib.corrLib import local_df
    >>> local_df = local_df(img_folder, seg_length=50, winsize=50, step=25)
    """

    l = readseq(img_folder)
    num_frames = len(l)
    assert(num_frames>seg_length)

    stdL = []
    tL = range(0, num_frames, seg_length)
    for n in tL:
        img_nums = range(n, min(n+seg_length, num_frames))
        l_sub = l.loc[img_nums]
        img_seq = []
        for num, i in l_sub.iterrows():
            img = io.imread(i.Dir)
            X, Y, I = divide_windows(img, windowsize=[50, 50], step=25)
            img_seq.append(I)
        img_stack = np.stack([img_seq], axis=0)
        img_stack = np.squeeze(img_stack)
        std = np.std(img_stack, axis=0)
        stdL.append(std)

    return {'t': tL, 'std': stdL}

def compute_energy_density(pivData, d=25*0.33, MPP=0.33):
    """
    Compute kinetic energy density in k space from piv data. The unit of the return value is [velocity] * [length], where [velocity] is the unit of pivData, and [length] is the unit of sample_spacing parameter. Note, the default value of sampling_spacing does not have any significance. It is just the most convenient value for my first application, and should be set with caution when a different magnification and PIV are used.

    :param pivData: 2D piv data, DataFrame of x, y, u, v
    :param d: sample spacing, in unit of microns
    :param MPP: microns per pixel

    :return: kinetic energy field in wavenumber (k) space

    .. rubric:: Test

    >>> pivData = pd.read_csv(r'E:\\moreData\\08032020\piv_imseq\\01\\3370-3371.csv')
    >>> compute_energy_density(pivData)

    .. rubric:: Edit

    :11020202:
        Add parameter sample_spacing, the distance between adjacent velocity (or data in general. The spacing is used to rescale the DFT so that it has a unit of [velocity] * [length]. In numpy.fft, the standard fft function is defined as

        .. math::

            A_k = \\sum\\limits^{n-1}_{m=0} a_m \\exp \\left[ -2\pi i \\frac{mk}{n} \\right]

        The unit of this Fourier Transform :math:`A_k` is clearly the same as :math:`a_m`. In order to get unit [velocity] * [length], and to make transform result consistent at different data density, I introduce sample_spacing :math:`d` as a modifier of the DFT. After this modification, the energy spectrum computed at various step size (of PIV) should give quantitatively similar results.

    :11042020:
        Replace the (* sample_spacing * sample_spacing) after v_fft with ( / row / col). This overwrites the edit I did on 11022020.

    :11112020: removed ( / row / col), add the area constant in energy_spectrum() function. Details can be found `here <https://zloverty.github.io/research/DF/blogs/energy_spectrum_2_methods_11112020.html>`_

    :11302020:
        *  Convert unit of velocity, add optional arg MPP (microns per pixel);
        * Add * d * d to both velocity FFT's to account for the missing length in default FFT algorithm;
        * The energy spectrum calculated by this function shows a factor of ~3 difference when comparing \int E(k) dk with v**2.sum()/2
    """

    row = len(pivData.y.drop_duplicates())
    col = len(pivData.x.drop_duplicates())
    U = np.array(pivData.u).reshape((row, col)) * MPP
    V = np.array(pivData.v).reshape((row, col)) * MPP

    u_fft = np.fft.fft2(U) * d * d
    v_fft = np.fft.fft2(V) * d * d

    E = (u_fft * u_fft.conjugate() + v_fft * v_fft.conjugate()) / 2

    return E

def compute_wavenumber_field(shape, d):
    """
    Compute the wave number field Kx and Ky, and magnitude field k.
    Note that this function works for even higher dimensional shape.

    :param shape: shape of the velocity field and velocity fft field, tuple
    :param d: sample spacing. This is the distance between adjacent samples, for example, velocities in PIV. The resulting frequency space has the unit which is inverse of the unit of d. The preferred unit of d is um.

    :return:
        * k -- wavenumber magnitude field
        * K -- wavenumber fields in given dimensions

    .. rubric:: Test

    >>> shape = (5, 5)
    >>> k, K = compute_wavenumber_field(shape, 0.2)

    .. rubric:: Edit

    :12022020: multiply 2pi to the wavenumber to account for the built-in 2pi in the fft method. This factor leads to a difference in the magnitude of 1D energy spectra.

        .. note:: The dimensionless wavenumber should remain unchanged.
    """

    for num, length in enumerate(shape):
        kx = np.fft.fftfreq(length, d=d)
        if num == 0:
            k = (kx,)
        else:
            k += (kx,)

    K = np.meshgrid(*k, indexing='ij')

    for num, k1 in enumerate(K):
        if num == 0:
            ksq = k1 ** 2
        else:
            ksq += k1 ** 2

    k_mag = ksq ** 0.5 * 2 * np.pi

    return k_mag, K

def energy_spectrum(pivData, d=25*0.33):
    """
    Compute energy spectrum (E vs k) from pivData.


    :param pivData: piv data
    :param d: sample spacing. This is the distance between adjacent samples, for example, velocities in PIV. The resulting frequency space has the unit which is inverse of the unit of d. The default unit of d is um.

    :return: energy spectrum, DataFrame (k, E)
    :rtype: ``pandas.DataFrame``

    >>> from myimagelib import energy_spectrum
    >>> es = energy_spectrum(pivData, d=25*0.33)

    .. rubric:: Edit

    * Oct 19, 2020 -- add argument d as sample spacing
    * Nov 11, 2020 -- add area constant, see details `here <https://zloverty.github.io/research/DF/blogs/energy_spectrum_2_methods_11112020.html>`_
    * Nov 30, 2020 -- The energy spectrum calculated by this function shows a factor of ~3 difference when comparing \int E(k) dk with v**2.sum()/2
    """

    row = len(pivData.y.drop_duplicates())
    col = len(pivData.x.drop_duplicates())

    E = compute_energy_density(pivData, d) / (row * d * col * d)
    k, K = compute_wavenumber_field(E.shape, d)

    ind = np.argsort(k.flatten())
    k_plot = k.flatten()[ind]
    E_plot = E.real.flatten()[ind]

    es = pd.DataFrame(data={'k': k_plot, 'E': E_plot})

    return es

def autocorr1d(x, t):
    """Compute the temporal autocorrelation of a 1-D signal.

    :param x: 1-D signal,
    :param t: the corresponding time of the signal, should be np.array 1d
    :return: DataFrame of (corr, t), where corr is the autocorrelation and t is the time lag.
    :rtype: ``pandas.DataFrame``

    >>> from myimagelib import autocorr1d
    >>> corr = autocorr1d(x, t)

    .. rubric:: Edit

    * July 27, 2022 -- Handle time series with missing values.
    """
    if any(np.isnan(x)):
        xn = x - np.nanmean(x)
        x2 = np.nanmean(xn * xn)
        c_list = []
        for s in range(0, len(xn)//2):
            xx = np.roll(xn, shift=s)
            xx[:s] = np.nan
            c_list.append(np.nanmean(xn * xx ))
        corr = np.array(c_list) / x2
    else:
        xn = x - np.nanmean(x)
        corr = np.correlate(xn, xn, mode="same")[len(xn)//2:] / np.inner(xn, xn)
    lagt = (t - t[0])[:len(corr)]
    return corr, lagt

def vacf_piv(vstack, dt, mode="direct"):
    """
    Compute averaged vacf from PIV data. This is a wrapper of function autocorr_t(), adding the averaging over all the velocity spots.

    :param vstack: a 2-D np array of velocity data. axis-0 is time and axes-1,2 are spots in velocity field. Usually, this stack can be constracted by ``np.stack(u_list)`` and then reshape to flatten axes 1 and 2.
    :param dt: time between two data points
    :param mode: the averaging method, can be ``"direct"`` or ``"weighted"``. ``"weighted"`` will use mean velocity as the averaging weight, whereas ``"direct"`` uses 1.
    :return: DataFrame of (corr, t)

    .. rubric:: Edit

    * Oct 26, 2022 -- add condition :code:`x.sum() != 0`, avoids nan in all-zero columns.
    """
    # rearrange vstack
    assert(len(vstack.shape)==3)
    stack_r = vstack.reshape((vstack.shape[0], -1)).T
    # compute autocorrelation
    corr_list = []
    weight = 1
    normalizer = 0
    for x in stack_r:
        if np.isnan(x.sum()) == False and x.sum() != 0: # masked out part has velocity as nan, which cannot be used for correlation computation
            if mode == "weighted":
                weight = abs(x).mean()
            normalizer += weight
            corr = autocorr1d(x) * weight
            corr_list.append(corr)
            print(x.sum(), corr.sum())
    corr_mean = np.stack(corr_list, axis=0).sum(axis=0) / normalizer

    return pd.DataFrame({"c": corr_mean, "t": np.arange(len(corr_mean)) * dt}).set_index("t")
