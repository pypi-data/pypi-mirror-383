# -*- coding: utf-8 -*-
# file: memory_optimized_dataset.py
# Memory-optimized version of OmniDataset using lazy loading

import random
import warnings
from collections import Counter
import copy
import numpy as np
import torch
import tqdm
from transformers import BatchEncoding
from ..misc.utils import fprint, env_meta_info, RNA2StructureCache


class MemoryOptimizedOmniDataset(torch.utils.data.Dataset):
    """
    Memory-optimized version of OmniDataset that uses lazy loading.

    This class reduces memory usage by:
    1. Only storing raw examples, not preprocessed data
    2. Processing data on-demand in __getitem__
    3. Supporting multiprocessing through DataLoader
    4. Optionally caching frequently accessed items
    """

    def __init__(self, data_source, tokenizer, max_length=None, **kwargs):
        """
        Initialize the memory-optimized dataset.

        Args:
            data_source (str or list): Path to data file(s)
            tokenizer: Tokenizer for processing sequences
            max_length (int): Maximum sequence length
            **kwargs: Additional arguments including:
                - cache_size (int): Number of items to cache (default: 0)
                - precompute_structures (bool): Whether to precompute RNA structures
                - num_workers (int): Hint for DataLoader workers
        """
        super().__init__()

        # Basic setup
        self.metadata = env_meta_info()
        self.tokenizer = tokenizer
        self.label2id = kwargs.get("label2id", None)
        self.shuffle = kwargs.get("shuffle", True)
        self.structure_in = kwargs.get("structure_in", False)
        self.drop_long_seq = kwargs.get("drop_long_seq", False)
        self.cache_size = kwargs.get("cache_size", 0)
        self.precompute_structures = kwargs.get("precompute_structures", False)

        # Initialize RNA structure cache if needed
        if self.structure_in and not hasattr(self, "rna2structure"):
            self.rna2structure = RNA2StructureCache()

        # Setup label mappings
        if self.label2id is not None:
            self.id2label = {v: k for k, v in self.label2id.items()}

        # Setup max_length
        if max_length is not None:
            self.max_length = max_length
        elif (
            hasattr(self.tokenizer, "max_length")
            and self.tokenizer.max_length is not None
        ):
            self.max_length = self.tokenizer.max_length
        else:
            self.max_length = 512

        self.tokenizer.max_length = self.max_length

        # Load raw examples (not preprocessed data)
        self.examples = []
        if data_source is not None:
            fprint(f"Loading data from {data_source}...")
            self.load_data_source(data_source, **kwargs)
            self._preprocessing()

        # Optional: LRU cache for frequently accessed items
        self._cache = {}
        self._cache_order = []

        # Optional: precompute RNA structures to avoid repeated computation
        if self.structure_in and self.precompute_structures:
            self._precompute_rna_structures()

        # Store tokenization args for __getitem__
        import inspect

        tokenization_args = inspect.getfullargspec(self.tokenizer.encode).args
        self.tokenization_kwargs = {
            key: kwargs[key] for key in kwargs if key in tokenization_args
        }

        fprint(
            f"Memory-optimized dataset initialized with {len(self.examples)} examples"
        )

    def _precompute_rna_structures(self):
        """Precompute RNA structures to avoid repeated computation in __getitem__"""
        fprint("Precomputing RNA structures...")
        sequences = [ex.get("sequence", "") for ex in self.examples if "sequence" in ex]
        if sequences:
            structures = self.rna2structure.fold(sequences)
            for i, structure in enumerate(structures):
                if i < len(self.examples) and "sequence" in self.examples[i]:
                    self.examples[i]["_precomputed_structure"] = structure

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        """
        Get item with lazy processing and optional caching.

        This method:
        1. Checks cache first
        2. Processes raw example on-demand
        3. Optionally caches result
        4. Returns processed data ready for model
        """
        # Check cache first
        if self.cache_size > 0 and idx in self._cache:
            # Move to end of cache order (LRU)
            self._cache_order.remove(idx)
            self._cache_order.append(idx)
            return self._cache[idx]

        # Get raw example
        ex = self.examples[idx].copy()

        # Add RNA structure if needed
        if self.structure_in and "sequence" in ex:
            if "_precomputed_structure" in ex:
                structure = ex["_precomputed_structure"]
            else:
                structure = self.rna2structure.fold([ex["sequence"]])[0]
            ex["sequence"] = f"{ex['sequence']}{self.tokenizer.eos_token}{structure}"

        # Process the example
        prepared = self.prepare_input(ex, **self.tokenization_kwargs)

        # Handle long sequences
        if (
            self.drop_long_seq
            and prepared
            and len(prepared.get("input_ids", [])) > self.max_length
        ):
            # Return None for dropped sequences, DataLoader will handle filtering
            return None

        # Apply padding/truncation per-item
        if prepared:
            prepared = self._pad_and_truncate_item(prepared)

        # Cache if enabled
        if self.cache_size > 0 and prepared is not None:
            self._update_cache(idx, prepared)

        return prepared

    def _update_cache(self, idx, item):
        """Update LRU cache with new item"""
        if len(self._cache) >= self.cache_size:
            # Remove oldest item
            oldest_idx = self._cache_order.pop(0)
            del self._cache[oldest_idx]

        self._cache[idx] = copy.deepcopy(item)
        self._cache_order.append(idx)

    def _pad_and_truncate_item(self, item):
        """
        Pad and truncate a single item to max_length.
        More memory efficient than padding entire dataset.
        """
        if hasattr(self.tokenizer, "pad_token_id"):
            pad_token_id = self.tokenizer.pad_token_id
        else:
            pad_token_id = self.tokenizer.base_tokenizer.pad_token_id

        # Process each field in the item
        for key, value in item.items():
            if not isinstance(value, torch.Tensor):
                value = torch.as_tensor(value)

            # Determine target length and padding value
            if "label" in key:
                if value.ndim == 0:  # Scalar labels don't need padding
                    continue
                target_length = min(len(value), self.max_length)
                pad_value = -100
            else:
                target_length = self.max_length
                if key == "input_ids":
                    pad_value = pad_token_id
                elif key == "attention_mask":
                    pad_value = 0
                else:
                    pad_value = 0

            # Truncate if too long
            if len(value) > target_length:
                value = value[:target_length]

            # Pad if too short
            if len(value) < target_length:
                padding_length = target_length - len(value)
                if value.ndim == 1:
                    pad_tensor = torch.full(
                        (padding_length,), pad_value, dtype=value.dtype
                    )
                else:
                    pad_shape = (padding_length,) + value.shape[1:]
                    pad_tensor = torch.full(pad_shape, pad_value, dtype=value.dtype)
                value = torch.cat([value, pad_tensor], dim=0)

            item[key] = value

        return item

    def load_data_source(self, data_source, **kwargs):
        """Load raw examples from data source (same as original implementation)"""
        examples = []
        max_examples = kwargs.get("max_examples", None)
        if not isinstance(data_source, list):
            data_source = [data_source]

        for data_file in data_source:
            if data_file.endswith(".csv"):
                import pandas as pd

                df = pd.read_csv(data_file)
                for i in range(len(df)):
                    examples.append(df.iloc[i].to_dict())
            elif data_file.endswith(".json"):
                import json

                try:
                    with open(data_file, "r", encoding="utf8") as f:
                        file_examples = json.load(f)
                    if isinstance(file_examples, list):
                        examples.extend(file_examples)
                    else:
                        examples.append(file_examples)
                except:
                    with open(data_file, "r", encoding="utf8") as f:
                        lines = f.readlines()
                    for line in lines:
                        examples.append(json.loads(line.strip()))
            elif data_file.endswith(".parquet"):
                import pandas as pd

                df = pd.read_parquet(data_file)
                for i in range(len(df)):
                    examples.append(df.iloc[i].to_dict())
            # Add other file format support as needed...
            else:
                raise Exception(f"Unsupported file format: {data_file}")

        fprint(f"Loaded {len(examples)} examples from {data_source}")

        if self.shuffle:
            fprint("Shuffling examples...")
            random.shuffle(examples)

        if max_examples is not None:
            fprint(f"Limiting to {max_examples} examples...")
            examples = examples[:max_examples]

        self.examples = examples
        return examples

    def prepare_input(self, instance, **kwargs):
        """
        Prepare input for a single instance. Must be implemented by subclasses.

        Args:
            instance (dict): Raw example
            **kwargs: Tokenization arguments

        Returns:
            dict: Processed example ready for model
        """
        raise NotImplementedError("Subclasses must implement prepare_input method")

    def _preprocessing(self):
        """Optional preprocessing hook for subclasses"""
        pass

    def _postprocessing(self):
        """Optional postprocessing hook for subclasses"""
        pass

    def print_label_distribution(self):
        """Print label distribution by processing a sample of examples"""
        fprint("Computing label distribution...")
        labels = []
        sample_size = min(1000, len(self.examples))  # Sample for efficiency
        indices = random.sample(range(len(self.examples)), sample_size)

        for idx in tqdm.tqdm(indices, desc="Sampling labels"):
            try:
                item = self[idx]
                if item and "labels" in item:
                    label = item["labels"]
                    if isinstance(label, torch.Tensor):
                        if label.ndim == 0:
                            labels.append(int(label.item()))
                        else:
                            labels.extend(label.tolist())
                    else:
                        labels.append(int(label))
            except:
                continue

        if labels:
            label_counts = Counter(labels)
            total_samples = len(labels)

            fprint(f"\nLabel Distribution (sampled from {sample_size} examples):")
            fprint("-" * 50)
            for label, count in sorted(label_counts.items()):
                percentage = (count / total_samples) * 100
                label_name = (
                    self.id2label.get(label, str(label))
                    if hasattr(self, "id2label")
                    else str(label)
                )
                fprint(f"{label_name:<10}\t{count:<10}\t{percentage:.2f}%")
            fprint("-" * 50)
        else:
            fprint("No labels found in sampled data.")
