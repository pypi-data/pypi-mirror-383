# myimagelib

myimagelib is an attempt to make the set of tools, e.g. image analysis and file I/O, __an installable package__. These code are initially just for my own convenience. As time goes on, they gradually become an integral part of my daily coding. When I share my code with friends, I always find it a problem when they cannot import in their local environment, and I have to ask them to download the code from my GitHub, or rewrite my code using packages that are already available on PyPI. This has been a PITA for a while, and I realize that it could be useful to make the code available on PyPI, too. So that my friends can download my code with a simple `pip install`. 

I understand that this package consists of code for many different purposes and they are not organized very nicely. It is only intended for people who are going to run my notebooks, but need the functions that I wrote earlier in this library. 

## Installation

```
pip install git+https://github.com/ZLoverty/mylib.git
```

## Examples of use

```python
>>> from myimagelib import show_progress
>>> show_progress(0.5, label="test", bar_length=40)
```
The result is:

```
test [####################--------------------] 50.0%
```

See [the documentation](https://zloverty.github.io/mylib/myImageLib.html) for more details!

## Versions

- 2.0.0: Move release_note.md to README.md; remove openpiv and matplotlib from dependencies; remove readdata, dirrec, PIV, apply_mask functions; start to use consistent versioning (last digit for bug fix, middle digit for added feature, first digit for major changes); no longer maintain the PyPI package, newer versions are only available from GitHub.
- 1.5.4: `imfindcircles()` now exclude overlap using `max_radius`; handle `nan` in `xy_bin`.
- 1.5.3: Fix a distance filter bug.
- 1.5.2: Improve `imfindcircles()` with new strong edge criterion and multi-stage detection.
- 1.5.1: Reorganize the documentation.
- 1.5.0: Lose weight project: the current package spreads very broadly. The reuse rates of most functions are quite low. Therefore, I'm planning to remove functions that are not useful any more, and figure out a focus of this package; remove `xcorr_funcs.py` and `fit_circle_utils.py`; add frequently used functions to `__init__.py`; clean up the imports; add a function `imfindcircles()` based on Atherton 1999
- 1.4.0: Implement doctest to test the code automatically; Add release note; Remove GitHub action that automatically builds docs. Instead build docs manually and upload to the "gh-pages" branch. See code notes for procedures; Add `update_mask` to `compact_PIV`; Add `to_csv` to `compact_PIV`; Handle NaN values in `to8bit`.
- 1.3.0: Fix the documentation. Due to the folder structure change, autodoc does not work correctly, and all the documentations currently are not working. Fix it in the next release. 
- 1.2.0: Reorganize the repo as a PyPI package and publish on PyPI.
- 1.1.0: All the functions and scripts that output PIV data should put PIV in a .mat container, which only save x, y, mask, labels in formation once, and save u, v as 3D arrays; The operations that based on \*.tif images should be transformed to work on raw images.

