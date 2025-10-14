# -*- coding: utf-8 -*-
# file: hf_abstract_dataset.py
# time: 24/07/2025
# author: Refactored to inherit from datasets.Dataset
# Copyright (C) 2019-2025. All Rights Reserved.

import os
import json
import random
import warnings
from collections import Counter
from hashlib import sha256
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from functools import partial
import threading
from typing import Dict, List, Any, Optional, Union

import numpy as np
import torch
import tqdm
from datasets import Dataset, DatasetDict
from transformers import BatchEncoding

from ..misc.utils import fprint, env_meta_info, RNA2StructureCache


def process_example_batch_safe(
    examples_batch: List[Dict],
    tokenizer_state: bytes,
    max_length: int,
    new_args: Dict,
    prepare_input_func_name: str,
    drop_long_seq: bool,
    dataset_class_module: str,
    dataset_class_name: str,
    instance_attributes: Dict[str, Any],
) -> List[Dict]:
    """
    Safe multiprocessing function for processing example batches with better error handling and N base handling
    """
    import pickle
    import importlib

    try:
        # Rebuild tokenizer
        tokenizer = pickle.loads(tokenizer_state)

        # Dynamically import dataset class and create temporary instance
        module = importlib.import_module(dataset_class_module)
        dataset_class = getattr(module, dataset_class_name)

        # Create temporary instance
        temp_instance = object.__new__(dataset_class)
        temp_instance.tokenizer = tokenizer
        temp_instance.max_length = max_length
        temp_instance.drop_long_seq = drop_long_seq

        # Set instance attributes
        for attr_name, attr_value in instance_attributes.items():
            setattr(temp_instance, attr_name, attr_value)

        prepare_input_func = getattr(temp_instance, prepare_input_func_name)

    except Exception as e:
        print(f"Error setting up processing environment: {e}")
        return []

    processed_data = []

    for example in examples_batch:
        try:
            # Handle N bases
            if "sequence" in example:
                sequence = example["sequence"]
                # Handle N bases - keep them as is and let tokenizer handle them
                if "N" in sequence:
                    # Option 1: Replace N with random bases
                    # sequence = sequence.replace('N', random.choice(['A', 'T', 'G', 'C']))
                    # Option 2: Keep N as is (most tokenizers handle unknown characters)
                    pass

                example["sequence"] = sequence

            if hasattr(tokenizer, "max_length"):
                tokenizer.max_length = max_length
            else:
                tokenizer.base_tokenizer.max_length = max_length

            # Call prepare_input function
            prepared_input = prepare_input_func(example, **new_args)

            if not prepared_input:
                continue

            # Check sequence length
            input_length = len(prepared_input.get("input_ids", []))
            if drop_long_seq and input_length > max_length:
                continue

            # Convert numpy arrays to Python native types for JSON serialization
            for key, value in prepared_input.items():
                if isinstance(value, np.ndarray):
                    prepared_input[key] = value.tolist()
                elif isinstance(value, torch.Tensor):
                    prepared_input[key] = value.tolist()

            processed_data.append(prepared_input)

        except Exception as e:
            print(f"Error processing example: {e}")
            continue

    return processed_data


def convert_to_json_compatible(data: Any) -> Any:
    """
    Recursively convert data to JSON compatible format
    """
    if isinstance(data, (np.ndarray, torch.Tensor)):
        return data.tolist()
    elif isinstance(data, dict):
        return {key: convert_to_json_compatible(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_to_json_compatible(item) for item in data]
    elif isinstance(data, (np.integer, np.floating)):
        return data.item()
    else:
        return data


def convert_from_json_to_tensor(data: Any) -> Any:
    """
    Convert JSON format data back to tensors
    """
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if isinstance(value, list) and key in [
                "input_ids",
                "attention_mask",
                "labels",
            ]:
                result[key] = torch.tensor(value)
            else:
                result[key] = convert_from_json_to_tensor(value)
        return result
    elif isinstance(data, list):
        return [convert_from_json_to_tensor(item) for item in data]
    else:
        return data


class HFOmniDataset(Dataset):
    """
    Refactored HFOmniDataset that inherits from HuggingFace datasets.Dataset
    while preserving all custom behaviors including padding, multiprocessing, and chunked caching.
    """

    def __init__(self, data_source, tokenizer, max_length=None, **kwargs):
        """
        Initialize the optimized dataset that inherits from datasets.Dataset

        Args:
            data_source: Data source path
            tokenizer: Tokenizer
            max_length: Maximum sequence length
            **kwargs: Other parameters
                - storage_format: 'json' or 'pickle' (default 'json')
                - n_base_strategy: 'random', 'mask', 'keep' (default 'keep')
                - use_threading: Whether to use threading instead of processes (default False)
                - error_tolerance: Error tolerance (default 0.1)
                - cache: Whether to use caching (default True)
                - num_proc: Number of processes for parallel processing (default 0)
                - cache_chunk_size: Size of each cache chunk (default 10000)
        """
        # Initialize basic settings
        self.data_source = data_source
        self.metadata = env_meta_info()
        self.tokenizer = tokenizer
        self.label2id = kwargs.get("label2id", None)
        self.shuffle = kwargs.get("shuffle", True)
        self.structure_in = kwargs.get("structure_in", False)
        self.drop_long_seq = kwargs.get("drop_long_seq", False)

        # New optimization parameters
        self.storage_format = kwargs.get("storage_format", "json")
        self.n_base_strategy = kwargs.get("n_base_strategy", "keep")
        self.use_threading = kwargs.get("use_threading", False)
        self.error_tolerance = kwargs.get("error_tolerance", 0.1)
        self.cache_chunk_size = kwargs.get(
            "cache_chunk_size", 10000
        )  # New parameter for chunk size

        if self.structure_in and not hasattr(self, "rna2structure"):
            self.rna2structure = RNA2StructureCache()

        if self.label2id is not None:
            self.id2label = {v: k for k, v in self.label2id.items()}

        # Setup max length
        self._setup_max_length(max_length)

        # Initialize data containers
        self.examples = []
        self._processed_data = []

        # Setup multiprocessing environment
        self._setup_multiprocessing()

        # Load and process data
        if self.data_source is not None:
            self._load_and_process_data(**kwargs)

        # Initialize the parent Dataset class with processed data
        # Convert processed data to HuggingFace Dataset format
        if self._processed_data:
            data_dict = self._convert_to_hf_format(self._processed_data)
            super().__init__(data_dict)
        else:
            # Initialize empty dataset
            super().__init__({})

    def _convert_to_hf_format(self, processed_data: List[Dict]) -> Dict[str, List]:
        """
        Convert processed data to HuggingFace Dataset format
        """
        if not processed_data:
            return {}

        # Get all keys from the first item
        keys = set()
        for item in processed_data:
            keys.update(item.keys())

        # Create dictionary with lists for each key
        hf_data = {key: [] for key in keys}

        for item in processed_data:
            for key in keys:
                if key in item:
                    # Convert tensors to lists for HuggingFace Dataset
                    value = item[key]
                    if isinstance(value, torch.Tensor):
                        value = value.tolist()
                    elif isinstance(value, np.ndarray):
                        value = value.tolist()
                    hf_data[key].append(value)
                else:
                    # Fill missing keys with None or appropriate default
                    if key == "labels":
                        hf_data[key].append(-100)
                    else:
                        hf_data[key].append(None)

        return hf_data

    def _setup_max_length(self, max_length):
        """Setup maximum sequence length"""
        if max_length is not None:
            fprint(
                f"Detected max_length={max_length} in the dataset, using it as the max_length."
            )
            self.max_length = max_length
        elif (
            hasattr(self.tokenizer, "max_length")
            and self.tokenizer.max_length is not None
        ):
            fprint(
                f"Detected max_length={self.tokenizer.max_length} from the tokenizer."
            )
            self.max_length = self.tokenizer.max_length
        else:
            fprint(f"No max_length detected, using default max_length=512.")
            self.max_length = 512

        self.tokenizer.max_length = self.max_length

    def _setup_multiprocessing(self):
        """Setup multiprocessing environment"""
        try:
            import pickle

            self.tokenizer_state = pickle.dumps(self.tokenizer)
        except Exception as e:
            fprint(f"Warning: Cannot serialize tokenizer for multiprocessing: {e}")
            self.tokenizer_state = None
            self.use_threading = True  # Fallback to threading

    def _load_and_process_data(self, **kwargs):
        """Load and process data"""
        fprint(f"Loading data from {self.data_source}...")
        self.load_data_source(self.data_source, **kwargs)
        self._preprocessing()

        num_proc = kwargs.get("num_proc", 0)
        if not (num_proc > 1 and len(self.examples) > 1000):
            num_proc = 0

        # Cache handling
        cache_key = self._get_cache_key(kwargs)
        if kwargs.get("cache", True) and num_proc:
            if self._load_from_cache(cache_key):
                return

        # Data processing
        new_args = self._prepare_tokenization_args(kwargs)

        if num_proc:
            self._process_with_parallelization(new_args, num_proc, kwargs)
        else:
            fprint("Using single-threaded processing for data preparation...")
            self._processed_data = self._process_examples_sequential(new_args)

        self._postprocessing()

        # Save cache
        if kwargs.get("cache", True):
            self._save_to_cache(cache_key)

    def _get_cache_key(self, kwargs):
        """Generate cache key"""
        cache_string = f"{self.data_source}{kwargs}{self.tokenizer.__repr__()}{self.storage_format}"
        return sha256(cache_string.encode("utf-8")).hexdigest()

    def _get_cache_dir(self, cache_key):
        """Get cache directory path"""
        cache_dir = f"og_data_cache_{cache_key}"
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir

    def _load_from_cache(self, cache_key):
        """Load data from cache - supports chunked loading"""
        cache_dir = self._get_cache_dir(cache_key)
        metadata_file = os.path.join(cache_dir, "metadata.json")

        if os.path.exists(metadata_file):
            try:
                # Load metadata
                with open(metadata_file, "r", encoding="utf-8") as f:
                    cache_metadata = json.load(f)

                num_chunks = cache_metadata.get("num_chunks", 1)
                chunk_size = cache_metadata.get("chunk_size", len(self.examples))

                # Load all chunks
                all_data = []
                for chunk_idx in range(num_chunks):
                    chunk_file = os.path.join(
                        cache_dir, f"chunk_{chunk_idx}.{self.storage_format}"
                    )
                    if not os.path.exists(chunk_file):
                        fprint(f"Missing chunk {chunk_idx}, cache incomplete")
                        return False

                    if self.storage_format == "json":
                        with open(chunk_file, "r", encoding="utf-8") as f:
                            chunk_data = json.load(f)
                        chunk_data = [
                            convert_from_json_to_tensor(item) for item in chunk_data
                        ]
                    else:
                        import pickle

                        with open(chunk_file, "rb") as f:
                            chunk_data = pickle.load(f)

                    all_data.extend(chunk_data)

                self._processed_data = all_data
                fprint(
                    f"Loaded cached dataset from {num_chunks} chunks with hash tag {cache_key}"
                )
                return True

            except Exception as e:
                fprint(f"Failed to load chunked cache: {e}")
                return False

        # Fallback to old single-file cache
        cache_file = f"og_data_cache_{cache_key}.{self.storage_format}"
        if os.path.exists(cache_file):
            try:
                if self.storage_format == "json":
                    with open(cache_file, "r", encoding="utf-8") as f:
                        cached_data = json.load(f)
                    self._processed_data = [
                        convert_from_json_to_tensor(item) for item in cached_data
                    ]
                else:
                    import pickle

                    with open(cache_file, "rb") as f:
                        self._processed_data = pickle.load(f)

                fprint(
                    f"Loaded {len(self._processed_data)} examples from cache: {cache_file}"
                )
                return True
            except Exception as e:
                fprint(f"Error loading cache: {e}")
                return False
        return False

    def _save_to_cache(self, cache_key):
        """Save data to cache - supports chunked saving"""
        try:
            total_items = len(self._processed_data)

            # If data is small, use single file cache
            if total_items <= self.cache_chunk_size:
                return self._save_to_single_cache(cache_key)

            # Use chunked cache for large datasets
            cache_dir = self._get_cache_dir(cache_key)
            num_chunks = (
                total_items + self.cache_chunk_size - 1
            ) // self.cache_chunk_size

            # Save chunked data
            for chunk_idx in range(num_chunks):
                start_idx = chunk_idx * self.cache_chunk_size
                end_idx = min(start_idx + self.cache_chunk_size, total_items)
                chunk_data = self._processed_data[start_idx:end_idx]

                chunk_file = os.path.join(
                    cache_dir, f"chunk_{chunk_idx}.{self.storage_format}"
                )

                if self.storage_format == "json":
                    json_data = [
                        convert_to_json_compatible(item) for item in chunk_data
                    ]
                    with open(chunk_file, "w", encoding="utf-8") as f:
                        json.dump(json_data, f, ensure_ascii=False)
                else:
                    import pickle

                    with open(chunk_file, "wb") as f:
                        pickle.dump(chunk_data, f)

            # Save metadata
            metadata = {
                "num_chunks": num_chunks,
                "chunk_size": self.cache_chunk_size,
                "total_items": total_items,
                "storage_format": self.storage_format,
                "created_at": (
                    os.path.getctime(cache_dir) if os.path.exists(cache_dir) else None
                ),
            }

            metadata_file = os.path.join(cache_dir, "metadata.json")
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            fprint(
                f"Cached processed dataset in {num_chunks} chunks with hash tag {cache_key}"
            )

        except Exception as e:
            fprint(f"Failed to save chunked cache: {e}")
            # Fallback to single file cache
            self._save_to_single_cache(cache_key)

    def _save_to_single_cache(self, cache_key):
        """Save to single file cache (fallback method)"""
        try:
            cache_file = f"og_data_cache_{cache_key}.{self.storage_format}"

            if self.storage_format == "json":
                data_to_save = [
                    convert_to_json_compatible(item) for item in self._processed_data
                ]
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            else:
                import pickle

                with open(cache_file, "wb") as f:
                    pickle.dump(self._processed_data, f)

            fprint(f"Saved {len(self._processed_data)} examples to cache: {cache_file}")
        except Exception as e:
            fprint(f"Error saving cache: {e}")

    def _prepare_tokenization_args(self, kwargs):
        """Prepare tokenization arguments"""
        new_args = {}
        for key in ["padding", "truncation", "return_tensors"]:
            if key in kwargs:
                new_args[key] = kwargs[key]
        return new_args

    def _process_examples_sequential(self, new_args):
        """Process examples sequentially"""
        processed_data = []
        for example in tqdm.tqdm(self.examples, desc="Processing examples"):
            try:
                processed_input = self.prepare_input(example, **new_args)
                if processed_input:
                    processed_data.append(processed_input)
            except Exception as e:
                fprint(f"Error processing example: {e}")
                continue
        return processed_data

    def _process_with_parallelization(self, new_args, num_proc, kwargs):
        """Process data with parallelization"""
        if not self.tokenizer_state:
            fprint(
                "Tokenizer cannot be serialized, falling back to sequential processing"
            )
            self._processed_data = self._process_examples_sequential(new_args)
            return

        batch_size = max(1, len(self.examples) // (num_proc * 4))
        batches = [
            self.examples[i : i + batch_size]
            for i in range(0, len(self.examples), batch_size)
        ]

        instance_attributes = {
            "label2id": self.label2id,
            "max_length": self.max_length,
            "structure_in": self.structure_in,
        }
        if hasattr(self, "rna2structure"):
            instance_attributes["rna2structure"] = self.rna2structure

        process_func = partial(
            process_example_batch_safe,
            tokenizer_state=self.tokenizer_state,
            max_length=self.max_length,
            new_args=new_args,
            prepare_input_func_name="prepare_input",
            drop_long_seq=self.drop_long_seq,
            dataset_class_module=self.__class__.__module__,
            dataset_class_name=self.__class__.__name__,
            instance_attributes=instance_attributes,
        )

        processed_data = []
        executor_class = (
            ThreadPoolExecutor if self.use_threading else ProcessPoolExecutor
        )

        with executor_class(max_workers=num_proc) as executor:
            futures = [executor.submit(process_func, batch) for batch in batches]

            for future in tqdm.tqdm(
                as_completed(futures), total=len(futures), desc="Processing batches"
            ):
                try:
                    batch_result = future.result()
                    processed_data.extend(batch_result)
                except Exception as e:
                    fprint(f"Error processing batch: {e}")

        self._processed_data = processed_data

    def _preprocessing(self):
        """Override this method for custom preprocessing"""
        pass

    def _postprocessing(self):
        """Override this method for custom postprocessing"""
        pass

    def load_data_source(self, data_source, **kwargs):
        """
        Load data from source - implement in subclasses
        """
        raise NotImplementedError("Subclasses must implement load_data_source method")

    def prepare_input(self, instance, **kwargs):
        """
        Prepare input for a single instance - implement in subclasses
        """
        raise NotImplementedError("Subclasses must implement prepare_input method")

    def custom_collate_fn(self, batch):
        """
        Custom collate function that preserves padding behavior
        """
        # Convert batch items back to tensors if needed
        processed_batch = []
        for item in batch:
            processed_item = {}
            for key, value in item.items():
                if key in ["input_ids", "attention_mask", "labels"]:
                    if not isinstance(value, torch.Tensor):
                        processed_item[key] = torch.tensor(value)
                    else:
                        processed_item[key] = value
                else:
                    processed_item[key] = value
            processed_batch.append(processed_item)

        # Apply custom padding logic
        return self._apply_custom_padding(processed_batch)

    def _apply_custom_padding(self, batch):
        """
        Apply custom padding logic - override in subclasses if needed
        """
        if not batch:
            return {}

        # Find max length in the batch
        max_length = max(len(item["input_ids"]) for item in batch)

        # Pad all sequences to max length
        padded_batch = {}
        for key in batch[0].keys():
            if key in ["input_ids", "attention_mask"]:
                pad_value = 0
            elif key == "labels":
                pad_value = -100
            else:
                # For other keys, just stack without padding
                padded_batch[key] = [item[key] for item in batch]
                continue

            padded_tensors = []
            for item in batch:
                tensor = item[key]
                if len(tensor) < max_length:
                    padding = [pad_value] * (max_length - len(tensor))
                    if isinstance(tensor, torch.Tensor):
                        padding_tensor = torch.tensor(padding, dtype=tensor.dtype)
                        padded_tensor = torch.cat([tensor, padding_tensor])
                    else:
                        padded_tensor = torch.tensor(tensor + padding)
                else:
                    padded_tensor = tensor[:max_length]
                padded_tensors.append(padded_tensor)

            padded_batch[key] = torch.stack(padded_tensors)

        return padded_batch

    def to_torch_dataset(self):
        """
        Convert to PyTorch Dataset for compatibility with existing code
        """
        return TorchDatasetWrapper(self)


class TorchDatasetWrapper(torch.utils.data.Dataset):
    """
    Wrapper to make HuggingFace Dataset compatible with PyTorch DataLoader
    """

    def __init__(self, hf_dataset):
        self.hf_dataset = hf_dataset

    def __len__(self):
        return len(self.hf_dataset)

    def __getitem__(self, idx):
        item = self.hf_dataset[idx]
        # Convert lists back to tensors
        processed_item = {}
        for key, value in item.items():
            if key in ["input_ids", "attention_mask", "labels"] and isinstance(
                value, list
            ):
                processed_item[key] = torch.tensor(value)
            else:
                processed_item[key] = value
        return processed_item
