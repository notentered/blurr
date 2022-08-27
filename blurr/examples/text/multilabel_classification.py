# AUTOGENERATED! DO NOT EDIT! File to edit: ../../../nbs/99d_text-examples-multilabel.ipynb.

# %% auto 0
__all__ = []

# %% ../../../nbs/99d_text-examples-multilabel.ipynb 5
import os, warnings

import datasets
from transformers import *
from transformers.utils import logging as hf_logging
from fastai.text.all import *
from fastai.callback.hook import _print_shapes


from ...text.data.core import *
from ...text.modeling.core import *
from ...text.utils import *
from ...utils import *


# %% ../../../nbs/99d_text-examples-multilabel.ipynb 7
# silence all the HF warnings
warnings.simplefilter("ignore")
hf_logging.set_verbosity_error()
