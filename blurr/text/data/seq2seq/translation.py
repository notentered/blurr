# AUTOGENERATED! DO NOT EDIT! File to edit: ../../../../nbs/22_text-data-seq2seq-translation.ipynb.

# %% auto 0
__all__ = ['TranslationPreprocessor']

# %% ../../../../nbs/22_text-data-seq2seq-translation.ipynb 5
import warnings
from typing import Optional

import numpy as np
import pandas as pd

from datasets import Dataset
from fastai.data.block import DataBlock
from transformers import AutoModelForSeq2SeqLM, PreTrainedTokenizerBase
from transformers.utils import logging as hf_logging

from .core import Seq2SeqBatchTokenizeTransform, Seq2SeqPreprocessor, Seq2SeqTextBlock
from ...utils import get_hf_objects


# %% ../../../../nbs/22_text-data-seq2seq-translation.ipynb 7
# silence all the HF warnings
warnings.simplefilter("ignore")
hf_logging.set_verbosity_error()

# %% ../../../../nbs/22_text-data-seq2seq-translation.ipynb 17
class TranslationPreprocessor(Seq2SeqPreprocessor):
    def __init__(
        self,
        # A Hugging Face tokenizer
        hf_tokenizer: PreTrainedTokenizerBase,
        # The number of examples to process at a time
        batch_size: int = 1000,
        # The unique identifier in the dataset
        id_attr: Optional[str] = None,
        # The attribute holding the text to translate
        text_attr: str = "original_text",
        # The maximum length (# of tokens) allowed for inputs. Will default to the max length allowed
        # by the model if not provided
        max_input_tok_length: Optional[int] = None,
        # The attribute holding the summary
        target_text_attr: str = "translated_text",
        # The maximum length (# of tokens) allowed for targets
        max_target_tok_length: Optional[int] = None,
        # The attribute that should be created if your are processing individual training and validation
        # datasets into a single dataset, and will indicate to which each example is associated
        is_valid_attr: Optional[str] = "is_valid",
        # Tokenization kwargs that will be applied with calling the tokenizer
        tok_kwargs: dict = {},
    ):
        # we need to use the offset mappings to get back at the raw text from its tokenized representation
        tok_kwargs = {**tok_kwargs, "return_offsets_mapping": True}

        super().__init__(
            hf_tokenizer, batch_size, text_attr, max_input_tok_length, target_text_attr, max_target_tok_length, is_valid_attr, tok_kwargs
        )

        self.id_attr = id_attr

    def process_df(self, training_df: pd.DataFrame, validation_df: Optional[pd.DataFrame] = None):
        df = super().process_df(training_df, validation_df)

        # process df in mini-batches
        final_df = pd.DataFrame()
        for g, batch_df in df.groupby(np.arange(len(df)) // self.batch_size):
            final_df = final_df.append(self._process_df_batch(batch_df))

        final_df.reset_index(drop=True, inplace=True)
        return final_df

    def process_hf_dataset(self, training_ds: Dataset, validation_ds: Optional[Dataset] = None):
        ds = super().process_hf_dataset(training_ds, validation_ds)
        return Dataset.from_pandas(self.process_df(pd.DataFrame(ds)))

    # ----- utility methods -----
    def _process_df_batch(self, batch_df):
        batch_df.reset_index(drop=True, inplace=True)

        # grab our inputs and targets batch encoding objects
        inputs, targets = self._tokenize_function(batch_df.to_dict(orient="list"))

        # add are processed text and target texts to the batched DataFrame
        for txt_seq_idx, (txt_attr, batch_enc) in enumerate(zip([self.text_attr, self.target_text_attr], [inputs, targets])):
            if txt_attr is None:
                break

            char_idxs = []
            for idx, offset_mapping in enumerate(batch_enc["offset_mapping"]):
                text_offsets = [offset_mapping[i] for i, seq_id in enumerate(batch_enc.sequence_ids(idx))]
                char_idxs.append([min(text_offsets)[0], max(text_offsets)[1]])

            batch_df = pd.concat(
                [batch_df, pd.DataFrame(char_idxs, columns=[f"{txt_attr}_start_char_idx", f"{txt_attr}_end_char_idx"])], axis=1
            )
            batch_df.insert(
                0,
                f"proc_{txt_attr}",
                batch_df.apply(lambda r: r[txt_attr][r[f"{txt_attr}_start_char_idx"] : r[f"{txt_attr}_end_char_idx"] + 1], axis=1),
            )

        return batch_df

