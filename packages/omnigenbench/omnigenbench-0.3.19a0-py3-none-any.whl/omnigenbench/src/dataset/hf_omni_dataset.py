# -*- coding: utf-8 -*-
# file: hf_omni_dataset.py
# time: 24/07/2025
# author: Refactored to inherit from HuggingFace datasets.Dataset
# Copyright (C) 2019-2025. All Rights Reserved.
"""
Specialized dataset classes for OmniGenome framework that inherit from HuggingFace datasets.Dataset.

This module provides specialized dataset classes for various genomic tasks,
inheriting from the refactored `HFOmniDataset` that now inherits from datasets.Dataset.
These classes handle data preparation for token classification, sequence classification,
token regression, and sequence regression, while preserving all custom behaviors like padding.
"""
import json

import numpy as np
import torch

from ..abc.hf_abstract_dataset import HFOmniDataset
from ..misc.utils import fprint
from ... import __name__, __version__


class HFOmniDatasetForTokenClassification(HFOmniDataset):
    """
    Dataset class specifically designed for token classification tasks in genomics.
    Now inherits from HuggingFace datasets.Dataset while preserving custom behaviors.

    This class extends the refactored `HFOmniDataset` to provide functionalities for preparing
    input sequences and their corresponding token-level labels. It's designed for tasks where
    each token in a sequence needs to be classified independently.

    Attributes:
        metadata: Dictionary containing dataset metadata including library information
        label2id: Mapping from label strings to integer IDs
    """

    def __init__(self, data_source, tokenizer, max_length=None, **kwargs):
        """
        Initialize the dataset for token classification.

        Args:
            data_source: Path to the data file or a list of paths.
                        Supported formats depend on the `HFOmniDataset` implementation.
            tokenizer: The tokenizer instance to use for converting sequences into
                      tokenized inputs.
            max_length: The maximum sequence length for tokenization. Sequences longer
                       than this will be truncated. If None, a default or tokenizer's
                       max length will be used.
            **kwargs: Additional keyword arguments to be stored in the dataset's metadata.
        """
        super(HFOmniDatasetForTokenClassification, self).__init__(
            data_source, tokenizer, max_length, **kwargs
        )

        self.metadata.update(
            {
                "library_name": __name__,
                "omnigenbench_version": __version__,
                "task": "genome_token_classification",
            }
        )
        for key, value in kwargs.items():
            self.metadata[key] = value

    def prepare_input(self, instance, **kwargs):
        """
        Prepare a single data instance for token classification.

        This method handles both string sequences and dictionary instances
        containing sequence and label information. It tokenizes the input
        sequence and prepares token-level labels for classification.

        Args:
            instance: A single data instance. Can be a string representing the sequence
                     or a dictionary with 'seq'/'sequence' and 'labels'/'label' keys.
            **kwargs: Additional keyword arguments for tokenization, such as 'padding'
                     and 'truncation'.

        Returns:
            dict: A dictionary of tokenized inputs, including 'input_ids', 'attention_mask',
                  and 'labels' (tensor of token-level labels).

        Raises:
            Exception: If the input instance format is unknown or if a dictionary
                      instance does not contain a 'seq' or 'sequence' key.
        """
        labels = None
        if isinstance(instance, str):
            sequence = instance
        elif isinstance(instance, dict):
            sequence = (
                instance.get("seq", None)
                if "seq" in instance
                else instance.get("sequence", None)
            )
            label = instance.get("label", None)
            labels = instance.get("labels", None)
            labels = labels if labels is not None else label
            if not sequence:
                raise Exception(
                    "The input instance must contain a 'seq' or 'sequence' key."
                )
        else:
            raise Exception("Unknown instance format.")

        tokenized_inputs = self.tokenizer(
            sequence,
            padding=kwargs.get("padding", "do_not_pad"),
            truncation=kwargs.get("truncation", True),
            max_length=self.max_length,
            return_tensors="pt",
        )
        for col in tokenized_inputs:
            tokenized_inputs[col] = tokenized_inputs[col].squeeze()

        if labels is not None:
            # Handle token-level labels
            if isinstance(labels, (list, tuple)):
                # Truncate labels to match tokenized sequence length minus special tokens
                labels = list(labels)[: self.max_length - 2]
                # Add labels for special tokens ([CLS] and [SEP])
                labels = (
                    [-100]
                    + [self.label2id.get(str(label), -100) for label in labels]
                    + [-100]
                )
            else:
                # Single label for the entire sequence (broadcast to all tokens)
                label_id = self.label2id.get(str(labels), -100)
                labels = [-100] + [label_id] * (self.max_length - 2) + [-100]

        # Ensure labels tensor has the same length as input_ids
        if labels is not None:
            input_length = len(tokenized_inputs["input_ids"])
            if len(labels) > input_length:
                labels = labels[:input_length]
            elif len(labels) < input_length:
                labels = labels + [-100] * (input_length - len(labels))

        tokenized_inputs["labels"] = (
            torch.tensor(labels) if labels is not None else torch.tensor([-100])
        )
        return tokenized_inputs

    def load_data_source(self, data_source, **kwargs):
        """
        Load data from various sources for token classification.

        Supports loading from files (JSON, JSONL, CSV, NPY) or direct data structures.
        """
        max_examples = kwargs.get("max_examples", None)

        if isinstance(data_source, str):
            if data_source.endswith(".json"):
                with open(data_source, "r", encoding="utf-8") as f:
                    data = json.load(f)
            elif data_source.endswith(".jsonl"):
                data = []
                with open(data_source, "r", encoding="utf-8") as f:
                    for line in f:
                        data.append(json.loads(line.strip()))
            elif data_source.endswith(".npy"):
                data = np.load(data_source, allow_pickle=True)
                if isinstance(data, np.ndarray):
                    data = data.tolist()
            else:
                raise ValueError(f"Unsupported file format: {data_source}")
        elif isinstance(data_source, (list, tuple)):
            data = list(data_source)
        else:
            raise ValueError(f"Unsupported data source type: {type(data_source)}")

        if max_examples:
            data = data[:max_examples]

        self.examples = data
        fprint(f"Loaded {len(self.examples)} examples from {data_source}")


class HFOmniDatasetForSequenceClassification(HFOmniDataset):
    """
    Dataset class for sequence classification tasks in genomics.
    Now inherits from HuggingFace datasets.Dataset while preserving custom behaviors.

    This class extends the refactored `HFOmniDataset` to prepare input sequences and their
    corresponding sequence-level labels. It's designed for tasks where the entire sequence
    needs to be classified into one of several categories.

    Attributes:
        metadata: Dictionary containing dataset metadata including library information
        label2id: Mapping from label strings to integer IDs
    """

    def __init__(self, data_source, tokenizer, max_length=None, **kwargs):
        """
        Initialize the dataset for sequence classification.

        Args:
            data_source: Path to the data file or a list of paths.
                        Supported formats depend on the `HFOmniDataset` implementation.
            tokenizer: The tokenizer instance to use for converting sequences into
                      tokenized inputs.
            max_length: The maximum sequence length for tokenization. Sequences longer
                       than this will be truncated. If None, a default or tokenizer's
                       max length will be used.
            **kwargs: Additional keyword arguments to be stored in the dataset's metadata.
        """
        super(HFOmniDatasetForSequenceClassification, self).__init__(
            data_source, tokenizer, max_length, **kwargs
        )

        self.metadata.update(
            {
                "library_name": __name__,
                "omnigenbench_version": __version__,
                "task": "genome_sequence_classification",
            }
        )
        for key, value in kwargs.items():
            self.metadata[key] = value

    def prepare_input(self, instance, **kwargs):
        """
        Prepare a single data instance for sequence classification.

        This method handles both string sequences and dictionary instances
        containing sequence and label information. It tokenizes the input
        sequence and prepares sequence-level labels for classification.

        Args:
            instance: A single data instance. Can be a string representing the sequence
                     or a dictionary with 'seq'/'sequence' and 'labels'/'label' keys.
            **kwargs: Additional keyword arguments for tokenization, such as 'padding'
                     and 'truncation'.

        Returns:
            dict: A dictionary of tokenized inputs, including 'input_ids', 'attention_mask',
                  and 'labels' (tensor of sequence-level labels).

        Raises:
            Exception: If the input instance format is unknown or if a dictionary
                      instance does not contain a 'label' or 'labels' key, or if
                      the label is not an integer.
        """
        labels = -100
        if isinstance(instance, str):
            sequence = instance
        elif isinstance(instance, dict):
            sequence = (
                instance.get("seq", None)
                if "seq" in instance
                else instance.get("sequence", None)
            )
            label = instance.get("label", None)
            labels = instance.get("labels", None)
            labels = labels if labels is not None else label
        else:
            raise Exception("Unknown instance format.")

        tokenized_inputs = self.tokenizer(
            sequence,
            padding=kwargs.get("padding", "do_not_pad"),
            truncation=kwargs.get("truncation", True),
            max_length=self.max_length,
            return_tensors="pt",
        )
        for col in tokenized_inputs:
            tokenized_inputs[col] = tokenized_inputs[col].squeeze()

        if labels is not None:
            if isinstance(labels, (list, tuple)):
                # Multi-label classification
                if self.label2id:
                    # Convert string labels to ids
                    label_ids = [
                        self.label2id.get(str(label), -100) for label in labels
                    ]
                    tokenized_inputs["labels"] = torch.tensor(label_ids)
                else:
                    tokenized_inputs["labels"] = torch.tensor(labels)
            else:
                # Single label classification
                if not isinstance(labels, (int, float)):
                    raise Exception(
                        "The label must be an integer or float for sequence classification."
                    )
                if self.label2id:
                    labels = self.label2id.get(str(labels), -100)
                tokenized_inputs["labels"] = torch.tensor(labels)
        else:
            tokenized_inputs["labels"] = torch.tensor(-100)

        return tokenized_inputs

    def load_data_source(self, data_source, **kwargs):
        """
        Load data from various sources for sequence classification.

        Supports loading from files (JSON, JSONL, CSV, NPY) or direct data structures.
        """
        max_examples = kwargs.get("max_examples", None)

        if isinstance(data_source, str):
            if data_source.endswith(".json"):
                with open(data_source, "r", encoding="utf-8") as f:
                    data = json.load(f)
            elif data_source.endswith(".jsonl"):
                data = []
                with open(data_source, "r", encoding="utf-8") as f:
                    for line in f:
                        data.append(json.loads(line.strip()))
            elif data_source.endswith(".npy"):
                data = np.load(data_source, allow_pickle=True)
                if isinstance(data, np.ndarray):
                    data = data.tolist()
            else:
                raise ValueError(f"Unsupported file format: {data_source}")
        elif isinstance(data_source, (list, tuple)):
            data = list(data_source)
        else:
            raise ValueError(f"Unsupported data source type: {type(data_source)}")

        if max_examples:
            data = data[:max_examples]

        self.examples = data
        fprint(f"Loaded {len(self.examples)} examples from {data_source}")


class HFOmniDatasetForTokenRegression(HFOmniDataset):
    """
    Dataset class for token regression tasks in genomics.
    Now inherits from HuggingFace datasets.Dataset while preserving custom behaviors.

    This class extends the refactored `HFOmniDataset` to prepare input sequences and their
    corresponding token-level regression targets. It's designed for tasks where each token
    in a sequence needs to be assigned a continuous value.

    Attributes:
        metadata: Dictionary containing dataset metadata including library information
    """

    def __init__(self, data_source, tokenizer, max_length=None, **kwargs):
        """
        Initialize the dataset for token regression.

        Args:
            data_source: Path to the data file or a list of paths.
                        Supported formats depend on the `HFOmniDataset` implementation.
            tokenizer: The tokenizer instance to use for converting sequences into
                      tokenized inputs.
            max_length: The maximum sequence length for tokenization. Sequences longer
                       than this will be truncated. If None, a default or tokenizer's
                       max length will be used.
            **kwargs: Additional keyword arguments to be stored in the dataset's metadata.
        """
        super(HFOmniDatasetForTokenRegression, self).__init__(
            data_source, tokenizer, max_length, **kwargs
        )

        self.metadata.update(
            {
                "library_name": __name__,
                "omnigenbench_version": __version__,
                "task": "genome_token_regression",
            }
        )
        for key, value in kwargs.items():
            self.metadata[key] = value

    def prepare_input(self, instance, **kwargs):
        """
        Prepare a single data instance for token regression.

        This method handles both string sequences and dictionary instances
        containing sequence and regression target information. It tokenizes
        the input sequence and prepares token-level regression targets.

        Args:
            instance: A single data instance. Can be a string representing the sequence
                     or a dictionary with 'seq'/'sequence' and 'labels'/'label' keys.
            **kwargs: Additional keyword arguments for tokenization, such as 'padding'
                     and 'truncation'.

        Returns:
            dict: A dictionary of tokenized inputs, including 'input_ids', 'attention_mask',
                  and 'labels' (tensor of token-level regression targets).

        Raises:
            Exception: If the input instance format is unknown or if a dictionary
                      instance does not contain a 'seq' or 'sequence' key.
        """
        labels = None
        if isinstance(instance, str):
            sequence = instance
        elif isinstance(instance, dict):
            sequence = (
                instance.get("seq", None)
                if "seq" in instance
                else instance.get("sequence", None)
            )
            label = instance.get("label", None)
            labels = instance.get("labels", None)
            labels = labels if labels is not None else label
            if not sequence:
                raise Exception(
                    "The input instance must contain a 'seq' or 'sequence' key."
                )
        else:
            raise Exception("Unknown instance format.")

        tokenized_inputs = self.tokenizer(
            sequence,
            padding=kwargs.get("padding", "do_not_pad"),
            truncation=kwargs.get("truncation", True),
            max_length=self.max_length,
            return_tensors="pt",
        )
        for col in tokenized_inputs:
            tokenized_inputs[col] = tokenized_inputs[col].squeeze()

        if labels is not None:
            # Handle token-level regression labels
            if isinstance(labels, (list, tuple)):
                # Ensure labels match sequence length
                labels = list(labels)[
                    : self.max_length - 2
                ]  # Account for special tokens
                labels = (
                    [-100.0] + [float(label) for label in labels] + [-100.0]
                )  # Add padding for special tokens
            else:
                # Single value for the entire sequence
                labels = [-100.0] + [float(labels)] * (self.max_length - 2) + [-100.0]

            # Ensure labels tensor has the same length as input_ids
            input_length = len(tokenized_inputs["input_ids"])
            if len(labels) > input_length:
                labels = labels[:input_length]
            elif len(labels) < input_length:
                labels = labels + [-100.0] * (input_length - len(labels))

        tokenized_inputs["labels"] = (
            torch.tensor(labels, dtype=torch.float32)
            if labels is not None
            else torch.tensor([-100.0])
        )
        return tokenized_inputs

    def load_data_source(self, data_source, **kwargs):
        """
        Load data from various sources for token regression.

        Supports loading from files (JSON, JSONL, CSV, NPY) or direct data structures.
        """
        max_examples = kwargs.get("max_examples", None)

        if isinstance(data_source, str):
            if data_source.endswith(".json"):
                with open(data_source, "r", encoding="utf-8") as f:
                    data = json.load(f)
            elif data_source.endswith(".jsonl"):
                data = []
                with open(data_source, "r", encoding="utf-8") as f:
                    for line in f:
                        data.append(json.loads(line.strip()))
            elif data_source.endswith(".npy"):
                data = np.load(data_source, allow_pickle=True)
                if isinstance(data, np.ndarray):
                    data = data.tolist()
            else:
                raise ValueError(f"Unsupported file format: {data_source}")
        elif isinstance(data_source, (list, tuple)):
            data = list(data_source)
        else:
            raise ValueError(f"Unsupported data source type: {type(data_source)}")

        if max_examples:
            data = data[:max_examples]

        self.examples = data
        fprint(f"Loaded {len(self.examples)} examples from {data_source}")


class HFOmniDatasetForSequenceRegression(HFOmniDataset):
    """
    Dataset class for sequence regression tasks in genomics.
    Now inherits from HuggingFace datasets.Dataset while preserving custom behaviors.

    This class extends the refactored `HFOmniDataset` to prepare input sequences and their
    corresponding sequence-level regression targets. It's designed for tasks where the
    entire sequence needs to be assigned a continuous value.

    Attributes:
        metadata: Dictionary containing dataset metadata including library information
    """

    def __init__(self, data_source, tokenizer, max_length=None, **kwargs):
        """
        Initialize the dataset for sequence regression.

        Args:
            data_source: Path to the data file or a list of paths.
                        Supported formats depend on the `HFOmniDataset` implementation.
            tokenizer: The tokenizer instance to use for converting sequences into
                      tokenized inputs.
            max_length: The maximum sequence length for tokenization. Sequences longer
                       than this will be truncated. If None, a default or tokenizer's
                       max length will be used.
            **kwargs: Additional keyword arguments to be stored in the dataset's metadata.
        """
        super(HFOmniDatasetForSequenceRegression, self).__init__(
            data_source, tokenizer, max_length, **kwargs
        )

        self.metadata.update(
            {
                "library_name": __name__,
                "omnigenbench_version": __version__,
                "task": "genome_sequence_regression",
            }
        )
        for key, value in kwargs.items():
            self.metadata[key] = value

    def prepare_input(self, instance, **kwargs):
        """
        Prepare a single data instance for sequence regression.

        This method handles both string sequences and dictionary instances
        containing sequence and regression target information. It tokenizes
        the input sequence and prepares sequence-level regression targets.

        Args:
            instance: A single data instance. Can be a string representing the sequence
                     or a dictionary with 'seq'/'sequence' and 'labels'/'label' keys.
            **kwargs: Additional keyword arguments for tokenization, such as 'padding'
                     and 'truncation'.

        Returns:
            dict: A dictionary of tokenized inputs, including 'input_ids', 'attention_mask',
                  and 'labels' (tensor of sequence-level regression targets).

        Raises:
            Exception: If the input instance format is unknown or if a dictionary
                      instance does not contain a 'seq' or 'sequence' key.
        """
        labels = -100.0
        if isinstance(instance, str):
            sequence = instance
        elif isinstance(instance, dict):
            sequence = (
                instance.get("seq", None)
                if "seq" in instance
                else instance.get("sequence", None)
            )
            label = instance.get("label", None)
            labels = instance.get("labels", None)
            labels = labels if labels is not None else label
            if not sequence:
                raise Exception(
                    "The input instance must contain a 'seq' or 'sequence' key."
                )
        else:
            raise Exception("Unknown instance format.")

        tokenized_inputs = self.tokenizer(
            sequence,
            padding=kwargs.get("padding", "do_not_pad"),
            truncation=kwargs.get("truncation", True),
            max_length=self.max_length,
            return_tensors="pt",
        )
        for col in tokenized_inputs:
            tokenized_inputs[col] = tokenized_inputs[col].squeeze()

        if labels is not None:
            if isinstance(labels, (list, tuple)):
                # Multi-target regression
                tokenized_inputs["labels"] = torch.tensor(
                    [float(label) for label in labels], dtype=torch.float32
                )
            else:
                # Single target regression
                tokenized_inputs["labels"] = torch.tensor(
                    float(labels), dtype=torch.float32
                )
        else:
            tokenized_inputs["labels"] = torch.tensor(-100.0, dtype=torch.float32)

        return tokenized_inputs

    def load_data_source(self, data_source, **kwargs):
        """
        Load data from various sources for sequence regression.

        Supports loading from files (JSON, JSONL, CSV, NPY) or direct data structures.
        """
        max_examples = kwargs.get("max_examples", None)

        if isinstance(data_source, str):
            if data_source.endswith(".json"):
                with open(data_source, "r", encoding="utf-8") as f:
                    data = json.load(f)
            elif data_source.endswith(".jsonl"):
                data = []
                with open(data_source, "r", encoding="utf-8") as f:
                    for line in f:
                        data.append(json.loads(line.strip()))
            elif data_source.endswith(".npy"):
                data = np.load(data_source, allow_pickle=True)
                if isinstance(data, np.ndarray):
                    data = data.tolist()
            else:
                raise ValueError(f"Unsupported file format: {data_source}")
        elif isinstance(data_source, (list, tuple)):
            data = list(data_source)
        else:
            raise ValueError(f"Unsupported data source type: {type(data_source)}")

        if max_examples:
            data = data[:max_examples]

        self.examples = data
        fprint(f"Loaded {len(self.examples)} examples from {data_source}")
