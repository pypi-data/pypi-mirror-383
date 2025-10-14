# -*- coding: utf-8 -*-
# File: abstract_dataset.py.ffi
# Time: 11:20 24/07/2025
# Author: YANG, HENG <hy345@exeter.ac.uk> (杨恒)
# Website: https://yangheng95.github.io
# GitHub: https://github.com/yangheng95
# HuggingFace: https://huggingface.co/yangheng
# Google Scholar: https://scholar.google.com/citations?user=NPq5a_0AAAAJ&hl=en
# Copyright (C) 2019-2025. All rights reserved.
# -*- coding: utf-8 -*-
# file: optimized_dataset.py
# time: 14:13 06/04/2024
# author: Optimized version with JSON storage and enhanced multiprocessing
# Copyright (C) 2019-2024. All Rights Reserved.

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
    安全的多进程样本处理函数，包含更好的错误处理和碱基N处理
    """
    import pickle
    import importlib

    try:
        # 重建tokenizer
        tokenizer = pickle.loads(tokenizer_state)

        # 动态导入数据集类并创建临时实例
        module = importlib.import_module(dataset_class_module)
        dataset_class = getattr(module, dataset_class_name)

        # 创建临时实例
        temp_instance = object.__new__(dataset_class)
        temp_instance.tokenizer = tokenizer
        temp_instance.max_length = max_length
        temp_instance.drop_long_seq = drop_long_seq

        # 设置实例属性
        for attr_name, attr_value in instance_attributes.items():
            setattr(temp_instance, attr_name, attr_value)

        prepare_input_func = getattr(temp_instance, prepare_input_func_name)

    except Exception as e:
        print(f"Error setting up processing environment: {e}")
        return []

    processed_data = []

    for example in examples_batch:
        try:
            # 处理碱基N的情况
            if "sequence" in example:
                sequence = example["sequence"]
                # 将N替换为随机碱基或保持不变（根据需求）
                if "N" in sequence:
                    # 选项1：将N替换为随机碱基
                    # sequence = sequence.replace('N', random.choice(['A', 'T', 'G', 'C']))

                    # 选项2：保持N不变，让tokenizer处理
                    # 大多数tokenizer都有处理未知字符的机制
                    pass

                example["sequence"] = sequence

            if hasattr(tokenizer, "max_length"):
                tokenizer.max_length = max_length
            else:
                tokenizer.base_tokenizer.max_length = max_length

            # 调用prepare_input函数
            prepared_input = prepare_input_func(example, **new_args)

            if not prepared_input:
                continue

            # 检查序列长度
            input_length = len(prepared_input.get("input_ids", []))
            if drop_long_seq and input_length > max_length:
                continue

            # 将numpy数组转换为Python原生类型以便JSON序列化
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
    递归地将数据转换为JSON兼容格式
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
    将JSON格式的数据转换回张量
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


class ThreadSafeDataset:
    """
    线程安全的数据集包装器
    """

    def __init__(self, data: List[Dict]):
        self.data = data
        self._lock = threading.RLock()

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        with self._lock:
            return self.data[idx]

    def append(self, item):
        with self._lock:
            self.data.append(item)

    def extend(self, items):
        with self._lock:
            self.data.extend(items)


class OmniDataset(torch.utils.data.Dataset):

    def __init__(self, data_source, tokenizer, max_length=None, **kwargs):
        """
        初始化优化的数据集

        Args:
            data_source: 数据源路径
            tokenizer: 分词器
            max_length: 最大序列长度
            **kwargs: 其他参数
                - storage_format: 'json' 或 'pickle' (默认'json')
                - n_base_strategy: 'random', 'mask', 'keep' (默认'keep')
                - use_threading: 是否使用线程而非进程 (默认False)
                - error_tolerance: 错误容忍度 (默认0.1)
        """
        super().__init__()

        # 基本设置
        self.data_source = data_source
        self.metadata = env_meta_info()
        self.tokenizer = tokenizer
        self.label2id = kwargs.get("label2id", None)
        self.shuffle = kwargs.get("shuffle", True)
        self.structure_in = kwargs.get("structure_in", False)
        self.drop_long_seq = kwargs.get("drop_long_seq", False)

        # 新的优化参数
        self.storage_format = kwargs.get("storage_format", "json")
        self.n_base_strategy = kwargs.get("n_base_strategy", "keep")
        self.use_threading = kwargs.get("use_threading", False)
        self.error_tolerance = kwargs.get("error_tolerance", 0.1)

        if self.structure_in and not hasattr(self, "rna2structure"):
            self.rna2structure = RNA2StructureCache()

        if self.label2id is not None:
            self.id2label = {v: k for k, v in self.label2id.items()}

        # 设置最大长度
        self._setup_max_length(max_length)

        # 初始化数据容器
        self.examples = []
        self.data = ThreadSafeDataset([])

        # 准备多进程环境
        self._setup_multiprocessing()

        # 加载和处理数据
        if self.data_source is not None:
            self._load_and_process_data(**kwargs)

    def _setup_max_length(self, max_length):
        """设置最大序列长度"""
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
        """设置多进程环境"""
        try:
            import pickle

            self.tokenizer_state = pickle.dumps(self.tokenizer)
        except Exception as e:
            fprint(f"Warning: Cannot serialize tokenizer for multiprocessing: {e}")
            self.tokenizer_state = None
            self.use_threading = True  # 回退到线程

    def _load_and_process_data(self, **kwargs):
        """加载和处理数据"""
        fprint(f"Loading data from {self.data_source}...")
        self.load_data_source(self.data_source, **kwargs)
        self._preprocessing()

        num_proc = kwargs.get("num_proc", 0)
        if not (num_proc > 1 and len(self.examples) > 1000):
            num_proc = 0

        # 缓存处理
        cache_key = self._get_cache_key(kwargs)
        if kwargs.get("cache", True) and num_proc:
            if self._load_from_cache(cache_key):
                return

        # 数据处理
        new_args = self._prepare_tokenization_args(kwargs)

        if num_proc:
            self._process_with_parallelization(new_args, num_proc, kwargs)
        else:
            fprint("Using single-threaded processing for data preparation...")
            self.data.data = self._process_examples_sequential(new_args)

        self._postprocessing()
        self._pad_and_truncate()

        # 保存缓存
        if kwargs.get("cache", True):
            self._save_to_cache(cache_key)

    def _get_cache_key(self, kwargs):
        """生成缓存键"""
        cache_string = f"{self.data_source}{kwargs}{self.tokenizer.__repr__()}{self.storage_format}"
        return sha256(cache_string.encode("utf-8")).hexdigest()

    def _load_from_cache(self, cache_key):
        """从缓存加载数据"""
        cache_file = f"og_data_cache_{cache_key}.{self.storage_format}"
        if os.path.exists(cache_file):
            try:
                if self.storage_format == "json":
                    with open(cache_file, "r", encoding="utf-8") as f:
                        cached_data = json.load(f)
                    self.data.data = [
                        convert_from_json_to_tensor(item) for item in cached_data
                    ]
                else:
                    import pickle

                    with open(cache_file, "rb") as f:
                        self.data.data = pickle.load(f)

                fprint(
                    f"Loaded cached dataset with hash tag {cache_key} for {self.data_source}."
                )
                self.metadata["cache"] = True
                self.metadata["cache_hash_tag"] = cache_key
                return True
            except Exception as e:
                fprint(f"Failed to load cache: {e}")
                return False
        return False

    def _save_to_cache(self, cache_key):
        """保存数据到缓存"""
        try:
            cache_file = f"og_data_cache_{cache_key}.{self.storage_format}"

            if self.storage_format == "json":
                # 转换为JSON兼容格式
                json_data = [
                    convert_to_json_compatible(item) for item in self.data.data
                ]
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
            else:
                import pickle

                with open(cache_file, "wb") as f:
                    pickle.dump(self.data.data, f)

            fprint(f"Cached processed dataset with hash tag {cache_key}")
            self.metadata["cache_hash_tag"] = cache_key
            self.metadata["cache"] = True
        except Exception as e:
            fprint(f"Failed to save cache: {e}")

    def _prepare_tokenization_args(self, kwargs):
        """准备分词参数"""
        import inspect

        new_args = {}
        tokenization_args = inspect.getfullargspec(self.tokenizer.encode).args
        for key in kwargs:
            if key in tokenization_args:
                new_args[key] = kwargs[key]
        return new_args

    def _process_with_parallelization(self, new_args, num_proc, kwargs):
        """使用并行处理数据"""
        batch_size = kwargs.get("batch_size", max(1, len(self.examples) // (num_proc)))
        num_proc = min(num_proc, len(self.examples) // batch_size, mp.cpu_count())

        if self.use_threading:
            fprint(
                f"Using multithreading with {num_proc} threads for data preparation..."
            )
            self.data.data = self._process_examples_threading(
                new_args, num_proc, batch_size
            )
        else:
            fprint(
                f"Using multiprocessing with {num_proc} workers for data preparation..."
            )
            self.data.data = self._process_examples_multiprocessing(
                new_args, num_proc, batch_size
            )

    def _process_examples_threading(self, new_args, num_threads, batch_size):
        """使用多线程处理样本"""
        chunks = [
            self.examples[i : i + batch_size]
            for i in range(0, len(self.examples), batch_size)
        ]
        processed_chunks = []

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for chunk in chunks:
                future = executor.submit(
                    self._process_chunk_sequential, chunk, new_args
                )
                futures.append(future)

            for future in tqdm.tqdm(as_completed(futures), total=len(futures)):
                try:
                    chunk_result = future.result()
                    processed_chunks.append(chunk_result)
                except Exception as e:
                    print(f"Error processing chunk: {e}")
                    continue

        return [item for sublist in processed_chunks for item in sublist]

    def _process_chunk_sequential(self, chunk, new_args):
        """顺序处理一个数据块"""
        processed_data = []

        for example in chunk:
            try:
                # 处理碱基N
                if "sequence" in example:
                    example["sequence"] = self._handle_n_bases(example["sequence"])

                prepared_input = self.prepare_input(example, **new_args)
                if prepared_input:
                    processed_data.append(prepared_input)

            except Exception as e:
                print(f"Error processing example: {e}")
                continue

        return processed_data

    def _handle_n_bases(self, sequence):
        """处理序列中的N碱基"""
        if "N" not in sequence:
            return sequence

        if self.n_base_strategy == "random":
            # 将N替换为随机碱基
            bases = ["A", "T", "G", "C"]
            return "".join(
                random.choice(bases) if base == "N" else base for base in sequence
            )
        elif self.n_base_strategy == "mask":
            # 将N替换为特殊mask token
            return sequence.replace("N", "[MASK]")
        else:
            # 保持N不变
            return sequence

    def _process_examples_multiprocessing(self, new_args, num_proc, batch_size):
        """使用多进程处理样本（优化版本）"""
        chunks = [
            self.examples[i : i + batch_size]
            for i in range(0, len(self.examples), batch_size)
        ]

        # 收集实例属性
        instance_attributes = {}
        for attr_name in ["drop_long_seq", "max_length", "n_base_strategy"]:
            if hasattr(self, attr_name):
                instance_attributes[attr_name] = getattr(self, attr_name)

        processed_chunks = []

        with ProcessPoolExecutor(max_workers=num_proc) as executor:
            futures = {
                executor.submit(
                    process_example_batch_safe,
                    chunk,
                    self.tokenizer_state,
                    self.max_length,
                    new_args,
                    "prepare_input",
                    self.drop_long_seq,
                    self.__class__.__module__,
                    self.__class__.__name__,
                    instance_attributes,
                ): chunk
                for chunk in chunks
            }

            successful_chunks = 0
            total_chunks = len(futures)

            for future in tqdm.tqdm(as_completed(futures), total=total_chunks):
                try:
                    chunk_result = future.result()
                    if chunk_result:  # 只添加非空结果
                        processed_chunks.append(chunk_result)
                        successful_chunks += 1
                except Exception as e:
                    print(f"Error processing chunk: {e}")
                    continue

            # 检查错误率
            error_rate = 1 - (successful_chunks / total_chunks)
            if error_rate > self.error_tolerance:
                fprint(
                    f"Warning: High error rate ({error_rate:.2%}) in multiprocessing. "
                    f"Consider reducing num_proc or using single-threaded processing."
                )

        return [item for sublist in processed_chunks for item in sublist]

    def _process_examples_sequential(self, new_args):
        """顺序处理样本"""
        processed_data = []
        errors = 0

        for example in tqdm.tqdm(self.examples):
            try:
                # 处理碱基N
                if "sequence" in example:
                    example["sequence"] = self._handle_n_bases(example["sequence"])

                if hasattr(self.tokenizer, "max_length"):
                    self.tokenizer.max_length = self.max_length
                else:
                    self.tokenizer.base_tokenizer.max_length = self.max_length

                prepared_input = self.prepare_input(example, **new_args)
                if not prepared_input:
                    continue

                if (
                    self.drop_long_seq
                    and len(prepared_input.get("input_ids", [])) > self.max_length
                ):
                    continue

                processed_data.append(prepared_input)

            except Exception as e:
                errors += 1
                print(f"Error processing example: {e}")
                continue

        error_rate = errors / len(self.examples) if self.examples else 0
        if error_rate > self.error_tolerance:
            fprint(
                f"Warning: High error rate ({error_rate:.2%}) in sequential processing."
            )

        return processed_data

    def load_data_source(self, data_source, **kwargs):
        """加载数据源（支持更多格式）"""
        examples = []
        max_examples = kwargs.get("max_examples", None)

        if not isinstance(data_source, list):
            data_source = [data_source]

        for source in data_source:
            if source.endswith(".csv"):
                examples.extend(self._load_csv(source))
            elif source.endswith(".json"):
                examples.extend(self._load_json(source))
            elif source.endswith(".parquet"):
                examples.extend(self._load_parquet(source))
            elif source.endswith((".npy", ".npz")):
                examples.extend(self._load_numpy(source))
            elif source.endswith((".fasta", ".fa", ".fna", ".ffn", ".faa", ".frn")):
                examples.extend(self._load_fasta(source))
            elif source.endswith((".fastq", ".fq")):
                examples.extend(self._load_fastq(source))
            elif source.endswith(".bed"):
                examples.extend(self._load_bed(source))
            elif source.endswith(".txt"):
                examples.extend(self._load_text(source))
            else:
                raise ValueError(f"Unsupported file format: {source}")

        fprint(f"Loaded {len(examples)} examples from {data_source}")

        if self.shuffle:
            fprint("Detected shuffle=True, shuffling the examples...")
            random.shuffle(examples)

        if max_examples is not None:
            fprint(f"Detected max_examples={max_examples}, truncating the examples...")
            examples = examples[:max_examples]

        self.examples = examples
        return examples

    def _load_csv(self, filepath):
        """加载CSV文件"""
        import pandas as pd

        df = pd.read_csv(filepath)
        return [row.to_dict() for _, row in df.iterrows()]

    def _load_json(self, filepath):
        """加载JSON文件"""
        try:
            with open(filepath, "r", encoding="utf8") as f:
                return json.load(f)
        except:
            # 处理JSONL格式
            examples = []
            with open(filepath, "r", encoding="utf8") as f:
                for line in f:
                    if line.strip():
                        examples.append(json.loads(line))
            return examples

    def _load_parquet(self, filepath):
        """加载Parquet文件"""
        import pandas as pd

        df = pd.read_parquet(filepath)
        return [row.to_dict() for _, row in df.iterrows()]

    def _load_numpy(self, filepath):
        """加载NumPy文件"""
        if filepath.endswith(".npy"):
            data = np.load(filepath, allow_pickle=True)
            if isinstance(data, np.ndarray):
                return [
                    {"sequence": item["sequence"], "label": item.get("label", None)}
                    for item in data
                ]
        else:  # .npz
            data = np.load(filepath, allow_pickle=True)
            examples = []
            for key in data.files:
                item = data[key]
                if isinstance(item, np.ndarray):
                    examples.extend(
                        [
                            {
                                "sequence": sub_item["sequence"],
                                "label": sub_item.get("label", None),
                            }
                            for sub_item in item
                        ]
                    )
            return examples
        raise ValueError("Unexpected data format in numpy file")

    def _load_fasta(self, filepath):
        """加载FASTA文件"""
        try:
            from Bio import SeqIO
        except ImportError:
            raise ImportError(
                "Biopython is required for FASTA parsing. Please install with 'pip install biopython'."
            )

        return [
            {
                "id": record.id,
                "sequence": str(record.seq),
                "description": record.description,
            }
            for record in SeqIO.parse(filepath, "fasta")
        ]

    def _load_fastq(self, filepath):
        """加载FASTQ文件"""
        try:
            from Bio import SeqIO
        except ImportError:
            raise ImportError(
                "Biopython is required for FASTQ parsing. Please install with 'pip install biopython'."
            )

        return [
            {
                "id": record.id,
                "sequence": str(record.seq),
                "quality": record.letter_annotations.get("phred_quality", []),
            }
            for record in SeqIO.parse(filepath, "fastq")
        ]

    def _load_bed(self, filepath):
        """加载BED文件"""
        import pandas as pd

        df = pd.read_csv(filepath, sep="\t", comment="#")
        return [row.to_dict() for _, row in df.iterrows()]

    def _load_text(self, filepath):
        """加载纯文本文件"""
        examples = []
        with open(filepath, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if line:
                    examples.append({"id": i, "sequence": line})
        return examples

    def save_to_json(self, filepath):
        """将数据集保存为JSON格式"""
        json_data = [convert_to_json_compatible(item) for item in self.data.data]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        fprint(f"Dataset saved to {filepath}")

    def load_from_json(self, filepath):
        """从JSON文件加载数据集"""
        with open(filepath, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        self.data.data = [convert_from_json_to_tensor(item) for item in json_data]
        fprint(f"Dataset loaded from {filepath}")

    def get_data_stats(self):
        """获取数据统计信息"""
        if not self.data.data:
            return {}

        stats = {
            "total_samples": len(self.data.data),
            "storage_format": self.storage_format,
            "n_base_strategy": self.n_base_strategy,
        }

        # 序列长度统计
        if "input_ids" in self.data.data[0]:
            lengths = [len(item["input_ids"]) for item in self.data.data]
            stats.update(
                {
                    "avg_seq_length": np.mean(lengths),
                    "min_seq_length": np.min(lengths),
                    "max_seq_length": np.max(lengths),
                    "std_seq_length": np.std(lengths),
                }
            )

        # 标签统计
        if "labels" in self.data.data[0]:
            labels = [item["labels"] for item in self.data.data]
            if isinstance(labels[0], (int, float)):
                stats["unique_labels"] = len(set(labels))
            else:
                stats["label_shape"] = np.array(labels[0]).shape

        return stats

    def prepare_input(self, instance, **kwargs):
        """准备输入数据 - 需要在子类中实现"""
        raise NotImplementedError(
            "The prepare_input() function should be implemented for your dataset."
        )

    def _preprocessing(self):
        """预处理数据"""
        for idx, ex in enumerate(self.examples):
            # 标准化序列字段名
            if "seq" in ex:
                ex["sequence"] = ex["seq"]
                del ex["seq"]
            if "text" in ex:
                ex["sequence"] = ex["text"]
                del ex["text"]

            if "sequence" not in ex:
                warnings.warn("The 'sequence' field is missing in the raw dataset.")

        # 添加结构信息
        if self.structure_in and self.examples and "sequence" in self.examples[0]:
            sequences = [ex["sequence"] for ex in self.examples]
            structures = self.rna2structure.fold(sequences)
            for idx, (sequence, structure) in enumerate(zip(sequences, structures)):
                self.examples[idx][
                    "sequence"
                ] = f"{sequence}{self.tokenizer.eos_token}{structure}"

    def _postprocessing(self):
        """后处理数据"""
        if not self.data.data:
            fprint(
                "Warning: No data found after processing. Check your data source and prepare_input method."
            )
            return

        for idx, ex in enumerate(self.data.data):
            if "label" in ex:
                ex["labels"] = ex["label"]

            if "labels" not in ex or ex["labels"] is None:
                ex["labels"] = torch.tensor([-100])

        # 打印标签分布
        if (
            self.data.data
            and "labels" in self.data.data[0]
            and isinstance(self.data.data[0]["labels"], torch.Tensor)
            and self.data.data[0]["labels"].dim() == 0
        ):
            self.print_label_distribution()

    def print_label_distribution(self):
        """打印标签分布"""
        if not self.data.data or "labels" not in self.data.data[0]:
            fprint("No labels found in the dataset.")
            return

        first_label = self.data.data[0]["labels"]
        if not isinstance(first_label, torch.Tensor) or first_label.ndim != 0:
            fprint("Warning: This method is only for scalar (0-dimensional) labels.")
            return

        if isinstance(first_label.item(), float):
            return

        labels = [int(d["labels"]) for d in self.data.data]
        label_counts = Counter(labels)
        total_samples = len(labels)
        sorted_counts = sorted(label_counts.items())

        fprint("\nLabel Distribution:")
        fprint("-" * 40)
        fprint(f"{'Label':<10}\t\t{'Count':<10}\t\t{'Percentage':<10}")
        fprint("-" * 40)

        for label, count in sorted_counts:
            percentage = (count / total_samples) * 100
            label_name = (
                self.id2label.get(label, str(label))
                if hasattr(self, "id2label")
                else str(label)
            )
            fprint(f"{label_name:<10}\t\t{count:<10}\t\t{percentage:.2f}%")

        fprint("-" * 40)
        fprint(f"Total samples: {total_samples}")

    def _pad_and_truncate(self, pad_value=0):
        """填充和截断序列"""
        if not self.data.data:
            return

        # 获取pad_token_id
        if hasattr(self.tokenizer, "pad_token_id"):
            pad_token_id = self.tokenizer.pad_token_id
        else:
            pad_token_id = self.tokenizer.base_tokenizer.pad_token_id

        # 计算最大长度
        max_input_length = max(
            torch.sum(torch.tensor(item["input_ids"]) != pad_token_id).item()
            for item in self.data.data
        )

        max_label_length = 0
        if "labels" in self.data.data[0]:
            max_label_length = max(
                (
                    len(item["labels"])
                    if isinstance(item["labels"], (list, torch.Tensor))
                    and len(torch.tensor(item["labels"]).shape) >= 1
                    else 0
                )
                for item in self.data.data
            )

        # 确定填充长度
        original_max_length = max(max_input_length, max_label_length)
        original_max_length = min(original_max_length, self.max_length)

        # 调整到8的倍数
        remainder = original_max_length % 8
        if remainder != 0:
            adjusted_max_length = original_max_length + (8 - remainder)
            adjusted_max_length = min(adjusted_max_length, self.max_length)
        else:
            adjusted_max_length = original_max_length

        max_length = adjusted_max_length

        fprint(f"Max sequence length updated -> Reset max_length={max_length}")

        # 填充和截断
        for item in self.data.data:
            for key, value in item.items():
                if not isinstance(value, torch.Tensor):
                    value = torch.tensor(value)

                # 确定填充长度
                if "label" in key:
                    if value.ndim == 0:
                        padding_length = 0
                    else:
                        padding_length = max_length - value.size(0)
                else:
                    padding_length = max_length - value.size(0)

                # 填充或截断
                if padding_length > 0:
                    # 确定填充值
                    if key == "input_ids":
                        _pad_value = pad_token_id
                    elif key == "attention_mask":
                        _pad_value = 0
                    elif "label" in key:
                        _pad_value = -100
                    else:
                        _pad_value = pad_value

                    # 构建填充张量
                    if value.ndim == 2:
                        pad_shape = (padding_length, value.size(1))
                    else:
                        pad_shape = (padding_length,)

                    pad_tensor = torch.full(pad_shape, _pad_value, dtype=value.dtype)
                    item[key] = torch.cat([value, pad_tensor], dim=0)
                elif padding_length < 0:
                    item[key] = value[:max_length]

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]

    def __iter__(self):
        for item in self.data.data:
            yield item
