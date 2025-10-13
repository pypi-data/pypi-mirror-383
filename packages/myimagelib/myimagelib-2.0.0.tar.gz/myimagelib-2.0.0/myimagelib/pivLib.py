import numpy as np
import pandas as pd
import os
from scipy.io import savemat

def to_matrix(pivData):
    """
    Convert PIV data from DataFrame of (x, y, u, v) to four 2D matrices x, y, u, v.

    :param pivData: PIV data
    :type pivData: pandas.DataFrame
    :return: x, y, u, v -- 2D matrices

    >>> from myimagelib.pivLib import to_matrix
    >>> x, y, u, v = to_matrix(pivData)

    .. rubric:: Edit

    * Nov 17, 2022 -- Initial commit.
    """
    row = len(pivData.y.drop_duplicates())
    col = len(pivData.x.drop_duplicates())
    X = np.array(pivData.x).reshape((row, col))
    Y = np.array(pivData.y).reshape((row, col))
    U = np.array(pivData.u).reshape((row, col))
    V = np.array(pivData.v).reshape((row, col))
    return X, Y, U, V

def to_dataframe(x, y, u, v):
    """Convert PIV data from 2D numpy arrays to a pandas DataFrame [x, y, u, v].
    
    :param x: 2D numpy array of x-coordinates
    :param y: 2D numpy array of y-coordinates
    :param u: 2D numpy array of u-velocity components
    :param v: 2D numpy array of v-velocity components
    :return: pandas DataFrame with columns ['x', 'y', 'u', 'v']
    :rtype: pandas.DataFrame

    >>> from myimagelib.pivLib import to_dataframe
    >>> to_dataframe(x, y, u, v)

    .. rubric:: Edit

    * Mar 02, 2025 -- Initial commit.
    """
    df = pd.DataFrame()
    df["x"] = x.reshape(-1)
    df["y"] = y.reshape(-1)
    df["u"] = u.reshape(-1)
    df["v"] = v.reshape(-1)
    return df

class compact_PIV:
    """
    Compact PIV data structure. Instead of saving PIV data of each frame pair in separated text files, we can save them in a more compact form, where (x, y, mask) information are only saved once and only velocity informations are kept in 3D arrays. The data will be saved in a Matlab style .mat file, and the internal structure is a Python dictionary, with entries (x, y, labels, u, v, mask). Since here x, y, u, v are no longer the same shape, accessing PIV data from a specific frame becomes less straight forward. For example, when doing a quiver plot, one needs to call ``quiver(x, y, u[0], v[0]``, instead of ``quiver(x, y, u, v]``. This class is written to enable straightforward data access and saving. For a more detailed guide of using this class, see `compact_PIV tutorial <https://github.com/ZLoverty/mylib/blob/main/tests/compact_PIV.ipynb>`_. You can also download the notebook to run the code locally. Note that it requires you to download `myimagelib package <https://zloverty.github.io/mylib/usage.html>`_.

    .. rubric:: Syntax

    .. code-block:: python

       from myimagelib import readdata, compact_PIV

       # construct compact_PIV object from a folder containing PIV data
       folder = "path/to/piv/data" # folder containing .csv files
       l = readdata(folder, "csv")
       cpiv = compact_PIV(l)

       # get the data for one frame
       x, y, u, v = cpiv.get_frame(0)

       # save the data to a .mat file
       cpiv.to_mat("cpiv.mat")

       # Update mask
       from skimage.io import imread
       mask = imread("path/to/mask.tif")
       cpiv.update_mask(mask)

    .. rubric:: Edit

    * Jan 13, 2023 -- Add :py:func:`update_mask()`. The idea is that the original mask may include regions where image quality is bad, e.g. the bottom shadow region of droplet xz images. In this case, we usually realize the problem after performing the PIV. And to refine the PIV data, we want to update the mask to make it more conservative (i.e. mask out the bad quality region). Therefore, a method is needed to update the "mask" entry in a compact_PIV object. 
    """
    def __init__(self, data):
        """
        Initialize compact_PIV object from data.

        :param data: can be dict or pandas.DataFrame. If it's dict, set the value directly to self.data. If it's DataFrame, construct a dict from the DataFrame (filelist).
        """
        if isinstance(data, dict):
            self.data = data
            
        elif isinstance(data, pd.DataFrame):
            if "Name" in data and "Dir" in data:
                self.data = self._from_filelist(data)
            else:
                raise ValueError
        self.keys = self.data.keys()
    def get_frame(self, i, by="index"):
        """
        Get PIV data [x, y, u, v] for a specific frame. The frame can be specified by index or label. The default is by index. Index is from 0 to n-1, where n is the number of frames. Label is the filename originally used for constructing this data.
        """
        if by == "index":
            ind = i
        elif by == "label":
            ind = self.get_labels().index(i)
        u, v = self.data["u"][ind], self.data["v"][ind]
        if "mask" in self.data.keys():
            u[~self.data["mask"].astype("bool")] = np.nan
            v[~self.data["mask"].astype("bool")] = np.nan
        return self.data["x"], self.data["y"], u, v
    
    def __repr__(self):
        return str(self.data)
    
    def __getitem__(self, indices):
        return self.data[indices]
    
    def _from_filelist(self, filelist):
        """
        Construct dict data from filelist of conventional PIV data.

        :param filelist: return value of readdata.
        """
        compact_piv = {}
        pivData = pd.read_csv(filelist.at[0, "Dir"])
        x, y, u, v = to_matrix(pivData)
        # set x, y values
        compact_piv["x"] = x
        compact_piv["y"] = y
        # set mask value, if exists
        if "mask" in pivData:
            mask_bool = np.reshape(np.array(pivData["mask"]), x.shape)
            compact_piv["mask"] = mask_bool
        # set u, v values and label value
        ul, vl = [], []
        label = []
        for num, i in filelist.iterrows():
            label.append(i.Name)
            pivData = pd.read_csv(i.Dir)
            x, y, u, v = to_matrix(pivData)
            ul.append(u)
            vl.append(v)
        compact_piv["u"] = np.stack(ul)
        compact_piv["v"] = np.stack(vl)
        compact_piv["labels"] = label
        return compact_piv
    
    def get_labels(self): 
        """ 
        Returns filenames originally used for constructing this data.
        """
        return list(self.data["labels"])

    def to_mat(self, fname):
        """
        Save the compact_PIV data to a .mat file.
        """
        savemat(fname, self.data)

    def update_mask(self, mask_img):
        """
        Update mask in the compact_PIV object. The mask is a binary image, where large values denote valid region. This method will update the mask in the compact_PIV object, by setting the mask value to False where the mask_img value is small. If the "mask" field does not exist, create it can set the value by the provided ``mask_img``.
        """
        mask = mask_img > mask_img.mean()
        ind = mask[self.data["y"].astype("int"), self.data["x"].astype("int")].reshape(self.data["x"].shape)
        self.data["mask"] = ind

    def to_csv(self, folder):
        """
        Save as .csv files to given folder. This is the reverse of the condensing process. It is intended to complete partially finished .mat data.
        """
        for label in self.get_labels():
            x, y, u, v = self.get_frame(label, by="label")
            data = pd.DataFrame({"x": x.flatten(), "y": y.flatten(), "u": u.flatten(), "v": v.flatten()})
            data.to_csv(os.path.join(folder, "{}.csv".format(label)), index=False)

