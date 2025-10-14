# Copyright (c) 2025 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import subprocess
import sys
import shlex
from copy import deepcopy
from typing import Any, Optional

from paddleformers.trainer import get_last_checkpoint
from paddleformers.utils.log import logger

from ..hparams import get_server_args, read_args
from ..utils.process import terminate_process_tree, is_valid_model_dir


def run_server(args: Optional[dict[str, Any]] = None) -> None:
    """Use fastdeploy for model service-oriented deployment"""
    args = read_args(args)
    model_args, generating_args, finetuning_args, server_args = get_server_args(args)

    server_model_path = model_args.model_name_or_path

    last_checkpoint = None
    if os.path.isdir(finetuning_args.output_dir):
        # Check if the output directory is a valid model directory (contains .safetensors or .pdparams files)
        if is_valid_model_dir(finetuning_args.output_dir):
            last_checkpoint = finetuning_args.output_dir
        # If not a model directory but still a valid path, try to find the latest checkpoint
        else:
            last_checkpoint = get_last_checkpoint(finetuning_args.output_dir)
    if last_checkpoint is not None:
        server_model_path = last_checkpoint
        logger.info(
            f"Checkpoint detected, launch server from {last_checkpoint} \
                    (Only Full checkpoint is supported)"
        )
    else:
        logger.info(
            f"No Checkpoint detected, launch server from {model_args.model_name_or_path}."
        )

    logger.info(
        "The optimal configuration for model deployment can be referred: https://github.com/PaddlePaddle/FastDeploy/tree/develop/docs/zh/optimal_deployment"
    )

    env = deepcopy(os.environ)
    if server_args.enable_mm:
        limit_mm_per_prompt = shlex.quote(server_args.limit_mm_per_prompt)
        command = (
            "python -m fastdeploy.entrypoints.openai.api_server "
            f"--model {server_model_path} "
            f"--tensor-parallel-size {finetuning_args.server_tp_degree} "
            f"--host {server_args.host} "
            f"--port {server_args.port} "
            f"--metrics-port {server_args.metrics_port} "
            f"--engine-worker-queue-port {server_args.engine_worker_queue_port} "
            f"--use-warmup {server_args.use_warmup} "
            f"--max-model-len {server_args.max_model_len} "
            f"--max-num-seqs {server_args.max_num_seqs} "
            f"--gpu-memory-utilization {server_args.gpu_memory_utilization} "
            f"--block-size {server_args.block_size} "
            f"--kv-cache-ratio {server_args.kv_cache_ratio} "
            f"--quantization {server_args.quantization} "
            f"--enable-mm "
            f"--limit-mm-per-prompt {limit_mm_per_prompt} "
            f"--reasoning-parser {server_args.reasoning_parser} "
            f"--enable-chunked-prefill "
            f"--max-num-batched-tokens {server_args.max_num_batched_tokens} "
        )
        if server_args.load_choices == "default_v1":
            command += "--load_choices default_v1 "
        command = shlex.split(command)
    else:
        command = (
            "python -m fastdeploy.entrypoints.openai.api_server "
            f"--model {server_model_path} "
            f"--tensor-parallel-size {finetuning_args.server_tp_degree} "
            f"--host {server_args.host} "
            f"--port {server_args.port} "
            f"--metrics-port {server_args.metrics_port} "
            f"--engine-worker-queue-port {server_args.engine_worker_queue_port} "
            f"--use-warmup {server_args.use_warmup} "
            f"--max-model-len {server_args.max_model_len} "
            f"--max-num-seqs {server_args.max_num_seqs} "
            f"--gpu-memory-utilization {server_args.gpu_memory_utilization} "
            f"--block-size {server_args.block_size} "
            f"--kv-cache-ratio {server_args.kv_cache_ratio} "
            f"--quantization {server_args.quantization} "
        )
        if server_args.load_choices == "default_v1":
            command += "--load_choices default_v1 "
        if server_args.reasoning_parser == "ernie_x1":
            command += "--reasoning-parser ernie_x1 "
        if server_args.tool_call_parser == "ernie_x1":
            command += "--tool-call-parser ernie_x1 "
        command = command.split()

    process = subprocess.Popen(
        command,
        env=env,
    )

    try:
        process.wait()
    except KeyboardInterrupt:
        print("\nReceived interrupt, terminating server...")
        terminate_process_tree(process.pid)
        sys.exit(1)
    except Exception as e:
        print(f"Server process failed: {e}")
        terminate_process_tree(process.pid)
        sys.exit(1)
    finally:
        sys.exit(process.returncode)
