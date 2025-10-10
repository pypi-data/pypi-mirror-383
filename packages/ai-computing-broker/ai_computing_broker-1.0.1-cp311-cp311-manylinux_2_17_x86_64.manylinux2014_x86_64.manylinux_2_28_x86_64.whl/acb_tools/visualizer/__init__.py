import plotly.express as px
import pandas as pd
import sys
from dataclasses import dataclass, field
import os
import csv
import argparse
from multiprocessing import Pool


@dataclass
class RatioInfo:
    job_uuid: str = ""
    overhead_ratio: float = 0.0
    acceleration_rate: float = 0.0


@dataclass
class StatsInfo:
    time: list[float] = field(default_factory=list)
    call_num: int = 0
    average: float = 0.0
    std_deviation: float = 0.0


@dataclass
class OverheadInfo:
    time: list[float] = field(default_factory=list)
    ratio: float = 0.0


def add_df_item(df_data, calltime, qual_name, job_uuid, elapsed_time, finish):
    """create dataframe item and add created dataframe to designated dataframe.

    Args:
        df_data: pandas dataframe to add
        calltime: "calltime" info of added dataframe item
        qual_name: "qual_name" info of added dataframe item
        job_uuid: "job_uuid" info of added dataframe item
        finish: "finish" info of added dataframe item

    """
    add_dict = {
        "calltime": calltime,
        "qual_name": qual_name,
        "args": "nan",
        "kwargs": "nan",
        "job_uuid": job_uuid,
        "elapsed_time": elapsed_time,
        "model_size_mb": "nan",
        "class": "nan",
        "gpu_memory_mb": "nan",
        "exception": "nan",
        "finish": finish,
    }
    df_item = pd.DataFrame(data=add_dict, index=[0])
    added_df_data = pd.concat([df_data, df_item])
    return added_df_data


def read_file(input_file: str):
    """read log file and create dataframe.

    Args:
        input_file: log file obtained by logging module(history.py)

    """
    json_file = open(input_file, "r")
    df_jsonl = pd.read_json(json_file, orient="records", lines=True)

    df_jsonl["calltime"] = pd.to_datetime(df_jsonl["calltime"], format="ISO8601")
    df_jsonl["finish"] = df_jsonl["calltime"] + pd.to_timedelta(df_jsonl["elapsed_time"], unit="s")
    df_jsonl_other = df_jsonl[df_jsonl["qual_name"] != "main"]
    df_jsonl_main = df_jsonl[df_jsonl["qual_name"] == "main"]
    sorted_df_jsonl = pd.concat([df_jsonl_main, df_jsonl_other])

    return sorted_df_jsonl


def calc_average(job_info):
    """calculate average time and standard deviation for each function and process.

    Args:
        job_info: analyzed job information(processing-time, call count)

    """
    for key in job_info:
        if key != "overhead" and key != "acceleration_rate" and key != "proc_time" and key != "job_uuid":
            if job_info[key].call_num:
                job_info[key].average = sum(job_info[key].time) / job_info[key].call_num
                time_values = pd.DataFrame(job_info[key].time)
                job_info[key].std_deviation = time_values[0].std(ddof=0)
            else:
                job_info[key].average = "No Data"


def calc_ratio(target_time, all_time):
    """calcurate ratio from two variables.

    Args:
        target_time: numerator of the ratio
        all_time: denominator of the ratio

    """
    if all_time != "No Data" and all_time != 0.0 and target_time != "No Data":
        ratio = target_time / all_time
    else:
        ratio = "No Data"
    return ratio


def create_job_info_file(fname):
    """create csv file to save analyzed job information.

    Args:
        fname: csv file to save analyzed job information

    """
    header1 = [
        "",
        "time",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "call_num",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "average",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "std_deviation",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "overhead_ratio",
        "accelaration_ratio",
    ]
    header2 = [
        "job_uuid",
        "proc",
        "overhead",
        "init",
        "finalize",
        "on_train_end",
        "load_checkpoint",
        "on_device_begin",
        "on_device_end",
        "on_epoch_begin",
        "on_epoch_end",
        "on_train_epoch_start",
        "on_train_epoch_end",
        "on_train_batch_start",
        "on_train_batch_end",
        "move_tensor",
        "move_model",
        "before_init",
        "after_finalize",
        "preproc",
        "prepostproc",
        "postproc",
        "keras_proc",
        "cpu_learning_predict",
        "gpu_learning_predict",
        "learning_predict",
        "update_state_dict",
        "save_checkpoint",
        "reboot",
        "ask_restart",
        "cleanup_device_resource",
        "init",
        "finalize",
        "on_train_end",
        "load_checkpoint",
        "on_device_begin",
        "on_device_end",
        "on_epoch_begin",
        "on_epoch_end",
        "on_train_epoch_start",
        "on_train_epoch_end",
        "on_train_batch_start",
        "on_train_batch_end",
        "move_tensor",
        "move_model",
        "before_init",
        "after_finalize",
        "preproc",
        "prepostproc",
        "postproc",
        "keras_proc",
        "cpu_learning_predict",
        "gpu_learning_predict",
        "learning_predict",
        "update_state_dict",
        "save_checkpoint",
        "reboot",
        "ask_restart",
        "cleanup_device_resource",
        "init",
        "finalize",
        "on_train_end",
        "load_checkpoint",
        "on_device_begin",
        "on_device_end",
        "on_epoch_begin",
        "on_epoch_end",
        "on_train_epoch_start",
        "on_train_epoch_end",
        "on_train_batch_start",
        "on_train_batch_end",
        "move_tensor",
        "move_model",
        "before_init",
        "after_finalize",
        "preproc",
        "prepostproc",
        "postproc",
        "keras_proc",
        "cpu_learning_predict",
        "gpu_learning_predict",
        "learning_predict",
        "update_state_dict",
        "save_checkpoint",
        "reboot",
        "ask_restart",
        "cleanup_device_resource",
        "init",
        "finalize",
        "on_train_end",
        "load_checkpoint",
        "on_device_begin",
        "on_device_end",
        "on_epoch_begin",
        "on_epoch_end",
        "on_train_epoch_start",
        "on_train_epoch_end",
        "on_train_batch_start",
        "on_train_batch_end",
        "move_tensor",
        "move_model",
        "before_init",
        "after_finalize",
        "preproc",
        "prepostproc",
        "postproc",
        "keras_proc",
        "cpu_learning_predict",
        "gpu_learning_predict",
        "learning_predict",
        "update_state_dict",
        "save_checkpoint",
        "reboot",
        "ask_restart",
        "cleanup_device_resource",
        "",
        "",
    ]
    with open(fname, "w") as f:
        writer = csv.writer(f)
        writer.writerow(header1)
        writer.writerow(header2)


def record_job_info(job_info, fname):
    """save analyzed job information in csv file.

    Args:
        job_info: analyzed job information
        fname: csv file to save analyzed job information

    """
    record = [
        job_info["job_uuid"],
        job_info["proc_time"],
        sum(job_info["overhead"].time),
        sum(job_info["__init__"].time),
        sum(job_info["finalize"].time),
        sum(job_info["on_train_end"].time),
        sum(job_info["load_checkpoint"].time),
        sum(job_info["on_device_begin"].time),
        sum(job_info["on_device_end"].time),
        sum(job_info["on_epoch_begin"].time),
        sum(job_info["on_epoch_end"].time),
        sum(job_info["on_train_epoch_start"].time),
        sum(job_info["on_train_epoch_end"].time),
        sum(job_info["on_train_batch_start"].time),
        sum(job_info["on_train_batch_end"].time),
        sum(job_info["move_tensor_to_device"].time),
        sum(job_info["move_models_to_device"].time),
        sum(job_info["before_init"].time),
        sum(job_info["after_finalize"].time),
        sum(job_info["preproc"].time),
        sum(job_info["prepostproc"].time),
        sum(job_info["postproc"].time),
        sum(job_info["keras_proc"].time),
        sum(job_info["cpu_learn_predict"].time),
        sum(job_info["gpu_learn_predict"].time),
        sum(job_info["learn_predict"].time),
        sum(job_info["update_state_dict"].time),
        sum(job_info["save_checkpoint"].time),
        sum(job_info["reboot"].time),
        sum(job_info["ask_restart"].time),
        sum(job_info["cleanup_device_resource"].time),
        job_info["__init__"].call_num,
        job_info["finalize"].call_num,
        job_info["on_train_end"].call_num,
        job_info["load_checkpoint"].call_num,
        job_info["on_device_begin"].call_num,
        job_info["on_device_end"].call_num,
        job_info["on_epoch_begin"].call_num,
        job_info["on_epoch_end"].call_num,
        job_info["on_train_epoch_start"].call_num,
        job_info["on_train_epoch_end"].call_num,
        job_info["on_train_batch_start"].call_num,
        job_info["on_train_batch_end"].call_num,
        job_info["move_tensor_to_device"].call_num,
        job_info["move_models_to_device"].call_num,
        job_info["before_init"].call_num,
        job_info["after_finalize"].call_num,
        job_info["preproc"].call_num,
        job_info["prepostproc"].call_num,
        job_info["postproc"].call_num,
        job_info["keras_proc"].call_num,
        job_info["cpu_learn_predict"].call_num,
        job_info["gpu_learn_predict"].call_num,
        job_info["learn_predict"].call_num,
        job_info["update_state_dict"].call_num,
        job_info["save_checkpoint"].call_num,
        job_info["reboot"].call_num,
        job_info["ask_restart"].call_num,
        job_info["cleanup_device_resource"].call_num,
        job_info["__init__"].average,
        job_info["finalize"].average,
        job_info["on_train_end"].average,
        job_info["load_checkpoint"].average,
        job_info["on_device_begin"].average,
        job_info["on_device_end"].average,
        job_info["on_epoch_begin"].average,
        job_info["on_epoch_end"].average,
        job_info["on_train_epoch_start"].average,
        job_info["on_train_epoch_end"].average,
        job_info["on_train_batch_start"].average,
        job_info["on_train_batch_end"].average,
        job_info["move_tensor_to_device"].average,
        job_info["move_models_to_device"].average,
        job_info["before_init"].average,
        job_info["after_finalize"].average,
        job_info["preproc"].average,
        job_info["prepostproc"].average,
        job_info["postproc"].average,
        job_info["keras_proc"].average,
        job_info["cpu_learn_predict"].average,
        job_info["gpu_learn_predict"].average,
        job_info["learn_predict"].average,
        job_info["update_state_dict"].average,
        job_info["save_checkpoint"].average,
        job_info["reboot"].average,
        job_info["ask_restart"].average,
        job_info["cleanup_device_resource"].average,
        job_info["__init__"].std_deviation,
        job_info["finalize"].std_deviation,
        job_info["on_train_end"].std_deviation,
        job_info["load_checkpoint"].std_deviation,
        job_info["on_device_begin"].std_deviation,
        job_info["on_device_end"].std_deviation,
        job_info["on_epoch_begin"].std_deviation,
        job_info["on_epoch_end"].std_deviation,
        job_info["on_train_epoch_start"].std_deviation,
        job_info["on_train_epoch_end"].std_deviation,
        job_info["on_train_batch_start"].std_deviation,
        job_info["on_train_batch_end"].std_deviation,
        job_info["move_tensor_to_device"].std_deviation,
        job_info["move_models_to_device"].std_deviation,
        job_info["before_init"].std_deviation,
        job_info["after_finalize"].std_deviation,
        job_info["preproc"].std_deviation,
        job_info["prepostproc"].std_deviation,
        job_info["postproc"].std_deviation,
        job_info["keras_proc"].std_deviation,
        job_info["cpu_learn_predict"].std_deviation,
        job_info["gpu_learn_predict"].std_deviation,
        job_info["learn_predict"].std_deviation,
        job_info["update_state_dict"].std_deviation,
        job_info["save_checkpoint"].std_deviation,
        job_info["reboot"].std_deviation,
        job_info["ask_restart"].std_deviation,
        job_info["cleanup_device_resource"].std_deviation,
        job_info["overhead"].ratio,
        job_info["acceleration_rate"],
    ]
    with open(fname, "a") as f:
        writer = csv.writer(f)
        writer.writerow(record)


def analyze_pytorch_mp(df):
    """analyze dataframe generated from PyTorch log file.


    Args:
        df: pandas dataframe generated from log file

    """
    gpu_total_use_time = 0
    job_id = df["job_uuid"].unique()
    work_df = df.copy()
    end_begin_start = None
    init_begin_start = None
    local_max_end = pd.Timestamp(0)
    local_min_start = pd.Timestamp(sys.maxsize)
    last_event_end_time = None
    last_finalize_end_time = None
    last_event = None
    calltime = None
    job_info = {
        "before_init": StatsInfo(),
        "__init__": StatsInfo(),
        "finalize": StatsInfo(),
        "on_train_end": StatsInfo(),
        "load_checkpoint": StatsInfo(),
        "move_tensor_to_device": StatsInfo(),
        "move_models_to_device": StatsInfo(),
        "on_device_begin": StatsInfo(),
        "on_device_end": StatsInfo(),
        "on_epoch_begin": StatsInfo(),
        "on_epoch_end": StatsInfo(),
        "on_train_epoch_start": StatsInfo(),
        "on_train_epoch_end": StatsInfo(),
        "on_train_batch_start": StatsInfo(),
        "on_train_batch_end": StatsInfo(),
        "cpu_learn_predict": StatsInfo(),
        "gpu_learn_predict": StatsInfo(),
        "learn_predict": StatsInfo(),
        "preproc": StatsInfo(),
        "prepostproc": StatsInfo(),
        "postproc": StatsInfo(),
        "keras_proc": StatsInfo(),
        "before_init_time": StatsInfo(),
        "after_finalize": StatsInfo(),
        "update_state_dict": StatsInfo(),
        "save_checkpoint": StatsInfo(),
        "reboot": StatsInfo(),
        "ask_restart": StatsInfo(),
        "cleanup_device_resource": StatsInfo(),
        "overhead": OverheadInfo(),
        "acceleration_rate": 0.0,
        "proc_time": 0.0,
        "job_uuid": "",
    }
    for _, data in work_df.iterrows():
        local_min_start = min(local_min_start, data["calltime"])
        local_max_end = max(local_max_end, data["finish"])
        prefix_name = data["qual_name"].split(".")[0]
        if prefix_name == "main":
            continue
        func_name = data["qual_name"].split(".")[1]
        if func_name not in job_info:
            print("unknown event: ", func_name)
            continue
        if (
            prefix_name == "PyTorchAdaptiveGPUAllocator"
            or prefix_name == "NoopAdaptiveGPUAllocator"
            or prefix_name == "PyTorchAutomaticAdaptiveGPUAllocator"
        ):
            job_info[func_name].time.append(data["elapsed_time"])
            job_info[func_name].call_num += 1
            if func_name == "on_device_begin":
                last_event = "on_device_begin"
                calltime = data["finish"]
                if init_begin_start is not None:
                    elapsed_time = (data["calltime"] - init_begin_start).total_seconds()
                    job_info["preproc"].time.append(elapsed_time)
                    job_info["preproc"].call_num += 1
                    df = add_df_item(
                        df,
                        calltime=init_begin_start,
                        qual_name="CPU process(preprocess)",
                        job_uuid=job_id,
                        elapsed_time=elapsed_time,
                        finish=data["calltime"],
                    )
                    init_begin_start = None
                if end_begin_start is not None:
                    elapsed_time = (data["calltime"] - end_begin_start).total_seconds()
                    job_info["prepostproc"].time.append(elapsed_time)
                    job_info["prepostproc"].call_num += 1
                    df = add_df_item(
                        df,
                        calltime=end_begin_start,
                        qual_name="CPU process(pre/postprocess)",
                        job_uuid=job_id,
                        elapsed_time=elapsed_time,
                        finish=data["calltime"],
                    )
                    end_begin_start = None
                last_event_end_time = data["finish"]
            elif func_name == "on_device_end":
                last_event = "on_device_end"
                finish = data["calltime"]
                end_begin_start = data["finish"]
                if calltime is not None:
                    learn_predict_time = (finish - calltime).total_seconds()
                    if "last_gpu_id" in data:
                        if str(data["last_gpu_id"]) == "CPU":
                            qual_name = "CPU process(learn/predict)"
                            job_info["cpu_learn_predict"].time.append(learn_predict_time)
                            job_info["cpu_learn_predict"].call_num += 1
                        else:
                            qual_name = "GPU process(learn/predict)"
                            job_info["gpu_learn_predict"].time.append(learn_predict_time)
                            job_info["gpu_learn_predict"].call_num += 1
                            gpu_total_use_time += learn_predict_time
                    elif "gpu_memory_mb" in data:
                        if str(data["gpu_memory_mb"]) == "nan":
                            qual_name = "CPU process(learn/predict)"
                            job_info["cpu_learn_predict"].time.append(learn_predict_time)
                            job_info["cpu_learn_predict"].call_num += 1
                        else:
                            qual_name = "GPU process(learn/predict)"
                            job_info["gpu_learn_predict"].time.append(learn_predict_time)
                            job_info["gpu_learn_predict"].call_num += 1
                            gpu_total_use_time += learn_predict_time
                    else:
                        qual_name = "learn/predict process (cannot get GPU info)"
                        job_info["learn_predict"].time.append(learn_predict_time)
                        job_info["learn_predict"].call_num += 1
                    df = add_df_item(
                        df,
                        calltime=calltime,
                        qual_name=qual_name,
                        job_uuid=job_id,
                        elapsed_time=learn_predict_time,
                        finish=finish,
                    )
            elif func_name == "__init__" and prefix_name == "NoopAdaptiveGPUAllocator":
                init_begin_start = data["finish"]
                if last_event_end_time is not None:
                    start_time = last_event_end_time
                else:
                    start_time = local_min_start
                elapsed_time = (data["calltime"] - start_time).total_seconds()
                job_info["before_init"].time.append(elapsed_time)
                job_info["before_init"].call_num += 1
                df = add_df_item(
                    df,
                    calltime=start_time,
                    qual_name="CPU allocated(before Init)",
                    job_uuid=job_id,
                    elapsed_time=elapsed_time,
                    finish=data["calltime"],
                )
            elif func_name == "finalize" and prefix_name != "NoopAdaptiveGPUAllocator":
                last_finalize_end_time = data["finish"]
                if last_event_end_time is not None:
                    start_time = last_event_end_time
                else:
                    start_time = end_begin_start
                elapsed_time = (data["calltime"] - start_time).total_seconds()
                job_info["postproc"].time.append(elapsed_time)
                job_info["postproc"].call_num += 1
                df = add_df_item(
                    df,
                    calltime=start_time,
                    qual_name="CPU process(postprocess)",
                    job_uuid=job_id,
                    elapsed_time=elapsed_time,
                    finish=data["calltime"],
                )
            elif func_name == "finalize" and prefix_name == "NoopAdaptiveGPUAllocator":
                last_finalize_end_time = data["finish"]
                if last_event_end_time is not None:
                    start_time = last_event_end_time
                else:
                    start_time = end_begin_start
                elapsed_time = (data["calltime"] - start_time).total_seconds()
                if last_event == "on_device_end":
                    job_info["postproc"].time.append(elapsed_time)
                    job_info["postproc"].call_num += 1
                    df = add_df_item(
                        df,
                        calltime=start_time,
                        qual_name="CPU process(postprocess)",
                        job_uuid=job_id,
                        elapsed_time=elapsed_time,
                        finish=data["calltime"],
                    )
                elif last_event == "on_device_begin":
                    job_info["gpu_learn_predict"].time.append(elapsed_time)
                    job_info["gpu_learn_predict"].call_num += 1
                    gpu_total_use_time += elapsed_time
                    df = add_df_item(
                        df,
                        calltime=start_time,
                        qual_name="GPU process(learn/predict)",
                        job_uuid=job_id,
                        elapsed_time=elapsed_time,
                        finish=data["calltime"],
                    )

        else:
            if func_name != "on_device_begin" and func_name != "on_device_end":
                job_info[func_name].time.append(data["elapsed_time"])
                job_info[func_name].call_num += 1
            if func_name == "__init__":
                init_begin_start = data["finish"]
                if last_event_end_time is not None:
                    start_time = last_event_end_time
                else:
                    start_time = local_min_start
                elapsed_time = (data["calltime"] - start_time).total_seconds()
                job_info["before_init"].time.append(elapsed_time)
                job_info["before_init"].call_num += 1
                df = add_df_item(
                    df,
                    calltime=start_time,
                    qual_name="CPU allocated(before Init)",
                    job_uuid=job_id,
                    elapsed_time=elapsed_time,
                    finish=data["calltime"],
                )
            if func_name == "finalize":
                last_finalize_end_time = data["finish"]
        last_event_end_time = data["finish"]

    job_info["proc_time"] = (local_max_end - local_min_start).total_seconds()
    job_info["job_uuid"] = job_id[0][0:7]

    if last_finalize_end_time is not None and local_max_end != last_finalize_end_time:
        elapsed_time = (local_max_end - last_finalize_end_time).total_seconds()
        job_info["after_finalize"].time.append(elapsed_time)
        job_info["after_finalize"].call_num += 1
        df = add_df_item(
            df,
            calltime=last_finalize_end_time,
            qual_name="CPU allocated(after Finalize)",
            job_uuid=job_id,
            elapsed_time=elapsed_time,
            finish=local_max_end,
        )
    job_info["overhead"].time.append(
        sum(job_info["__init__"].time)
        + sum(job_info["finalize"].time)
        + sum(job_info["on_device_begin"].time)
        + sum(job_info["on_device_end"].time)
        + sum(job_info["move_tensor_to_device"].time)
    )
    calc_average(job_info)
    job_info["overhead"].ratio = calc_ratio(sum(job_info["overhead"].time), job_info["proc_time"])
    job_info["acceleration_rate"] = calc_ratio(
        job_info["cpu_learn_predict"].average, job_info["gpu_learn_predict"].average
    )

    df = df[df["qual_name"] != "main"]

    return df, local_max_end, local_min_start, gpu_total_use_time, job_info


def analyze_tensorflow_mp(df):
    """analyze dataframe generated from TensorFlow log file.

    Args:
        df: pandas dataframe generated from TensorFlow log file

    """
    gpu_total_use_time = 0
    job_id = df["job_uuid"].unique()
    work_df = df.copy()
    end_begin_start = None
    init_begin_start = None
    local_max_end = pd.Timestamp(0)
    local_min_start = pd.Timestamp(sys.maxsize)
    last_event_end_time = None
    last_finalize_end_time = None
    calltime = None
    prev_event = "start"
    job_info = {
        "before_init": StatsInfo(),
        "__init__": StatsInfo(),
        "finalize": StatsInfo(),
        "on_train_end": StatsInfo(),
        "load_checkpoint": StatsInfo(),
        "move_tensor_to_device": StatsInfo(),
        "move_models_to_device": StatsInfo(),
        "on_device_begin": StatsInfo(),
        "on_device_end": StatsInfo(),
        "on_epoch_begin": StatsInfo(),
        "on_epoch_end": StatsInfo(),
        "on_train_epoch_start": StatsInfo(),
        "on_train_epoch_end": StatsInfo(),
        "on_train_batch_start": StatsInfo(),
        "on_train_batch_end": StatsInfo(),
        "cpu_learn_predict": StatsInfo(),
        "gpu_learn_predict": StatsInfo(),
        "learn_predict": StatsInfo(),
        "preproc": StatsInfo(),
        "prepostproc": StatsInfo(),
        "postproc": StatsInfo(),
        "keras_proc": StatsInfo(),
        "before_init_time": StatsInfo(),
        "after_finalize": StatsInfo(),
        "update_state_dict": StatsInfo(),
        "save_checkpoint": StatsInfo(),
        "reboot": StatsInfo(),
        "ask_restart": StatsInfo(),
        "cleanup_device_resource": StatsInfo(),
        "overhead": OverheadInfo(),
        "acceleration_rate": 0.0,
        "proc_time": 0.0,
        "job_uuid": "",
    }
    for _, data in work_df.iterrows():
        local_min_start = min(local_min_start, data["calltime"])
        local_max_end = max(local_max_end, data["finish"])
        prefix_name = data["qual_name"].split(".")[0]
        if prefix_name == "main":
            continue
        func_name = data["qual_name"].split(".")[1]
        if func_name not in job_info:
            print("unknown event: ", func_name)
            continue
        if prefix_name == "TensorflowAdaptiveGPUAllocator":
            # func_name is init or save_checkpoint
            job_info[func_name].time.append(data["elapsed_time"])
            job_info[func_name].call_num += 1
            if func_name == "__init__":
                init_begin_start = data["finish"]
                end_begin_start = None
                if last_event_end_time is not None:
                    start_time = last_event_end_time
                else:
                    start_time = local_min_start
                elapsed_time = (data["calltime"] - start_time).total_seconds()
                if prev_event == "on_device_begin" or prev_event == "on_device_end" or prev_event == "finalize":
                    job_info["reboot"].time.append(elapsed_time)
                    job_info["reboot"].call_num += 1
                    df = add_df_item(
                        df,
                        calltime=start_time,
                        qual_name="Reboot",
                        job_uuid=job_id,
                        elapsed_time=elapsed_time,
                        finish=data["calltime"],
                    )
                else:
                    job_info["before_init"].time.append(elapsed_time)
                    job_info["before_init"].call_num += 1
                    df = add_df_item(
                        df,
                        calltime=start_time,
                        qual_name="CPU allocated(before Init)",
                        job_uuid=job_id,
                        elapsed_time=elapsed_time,
                        finish=data["calltime"],
                    )
                last_event_end_time = data["finish"]
            prev_event = func_name
        else:
            if func_name != "__init__":
                job_info[func_name].time.append(data["elapsed_time"])
                job_info[func_name].call_num += 1
                prev_event = func_name

                if func_name == "finalize":
                    last_finalize_end_time = data["finish"]
                    if last_event_end_time is not None:
                        start_time = last_event_end_time
                    else:
                        start_time = end_begin_start
                    elapsed_time = (data["calltime"] - start_time).total_seconds()

                    job_info["postproc"].time.append(elapsed_time)
                    job_info["postproc"].call_num += 1
                    df = add_df_item(
                        df,
                        calltime=start_time,
                        qual_name="CPU process(postprocess)",
                        job_uuid=job_id,
                        elapsed_time=elapsed_time,
                        finish=data["calltime"],
                    )

                last_event_end_time = data["finish"]
            if func_name == "on_device_begin":
                calltime = data["finish"]
                if init_begin_start is not None:
                    elapsed_time = (data["calltime"] - init_begin_start).total_seconds()
                    job_info["preproc"].time.append(elapsed_time)
                    job_info["preproc"].call_num += 1
                    df = add_df_item(
                        df,
                        calltime=init_begin_start,
                        qual_name="CPU process(preprocess)",
                        job_uuid=job_id,
                        elapsed_time=elapsed_time,
                        finish=data["calltime"],
                    )
                    init_begin_start = None
                if end_begin_start is not None:
                    elapsed_time = (data["calltime"] - end_begin_start).total_seconds()
                    job_info["prepostproc"].time.append(elapsed_time)
                    job_info["prepostproc"].call_num += 1
                    df = add_df_item(
                        df,
                        calltime=end_begin_start,
                        qual_name="CPU process(pre/postprocess)",
                        job_uuid=job_id,
                        elapsed_time=elapsed_time,
                        finish=data["calltime"],
                    )
                    end_begin_start = None
            elif func_name == "on_device_end":
                finish = data["calltime"]
                end_begin_start = data["finish"]
                init_begin_start = None
                if calltime is not None:
                    learn_predict_time = (finish - calltime).total_seconds()
                    if "last_gpu_id" in data:
                        if str(data["last_gpu_id"]) == "CPU":
                            qual_name = "CPU process(learn/predict)"
                            job_info["cpu_learn_predict"].time.append(learn_predict_time)
                            job_info["cpu_learn_predict"].call_num += 1
                        else:
                            qual_name = "GPU process(learn/predict)"
                            job_info["gpu_learn_predict"].time.append(learn_predict_time)
                            job_info["gpu_learn_predict"].call_num += 1
                            gpu_total_use_time += learn_predict_time
                    elif "gpu_memory_mb" in data:
                        if str(data["gpu_memory_mb"]) == "nan":
                            qual_name = "CPU process(learn/predict)"
                            job_info["cpu_learn_predict"].time.append(learn_predict_time)
                            job_info["cpu_learn_predict"].call_num += 1
                        else:
                            qual_name = "GPU process(learn/predict)"
                            job_info["gpu_learn_predict"].time.append(learn_predict_time)
                            job_info["gpu_learn_predict"].call_num += 1
                            gpu_total_use_time += learn_predict_time
                    else:
                        qual_name = "learn/predict process (cannot get GPU info)"
                        job_info["learn_predict"].time.append(learn_predict_time)
                        job_info["learn_predict"].call_num += 1
                    df = add_df_item(
                        df,
                        calltime=calltime,
                        qual_name=qual_name,
                        job_uuid=job_id,
                        elapsed_time=learn_predict_time,
                        finish=finish,
                    )

    job_info["proc_time"] = (local_max_end - local_min_start).total_seconds()
    job_info["job_uuid"] = job_id[0][0:7]

    if last_finalize_end_time is not None and local_max_end != last_finalize_end_time:
        elapsed_time = (local_max_end - last_finalize_end_time).total_seconds()
        job_info["after_finalize"].time.append(elapsed_time)
        job_info["after_finalize"].call_num += 1
        df = add_df_item(
            df,
            calltime=last_finalize_end_time,
            qual_name="CPU allocated(after Finalize)",
            job_uuid=job_id,
            elapsed_time=elapsed_time,
            finish=local_max_end,
        )
    job_info["overhead"].time.append(
        sum(job_info["__init__"].time)
        + sum(job_info["finalize"].time)
        + sum(job_info["on_device_begin"].time)
        + sum(job_info["on_device_end"].time)
        + sum(job_info["move_tensor_to_device"].time)
    )
    calc_average(job_info)
    job_info["overhead"].ratio = calc_ratio(sum(job_info["overhead"].time), job_info["proc_time"])
    job_info["acceleration_rate"] = calc_ratio(
        job_info["cpu_learn_predict"].average, job_info["gpu_learn_predict"].average
    )

    df = df[df["qual_name"] != "main"]

    return df, local_max_end, local_min_start, gpu_total_use_time, job_info


def analyze_keras_mp(df):
    """analyze dataframe generated from Keras log file.

    Args:
        df: pandas dataframe generated from Keras log file

    """
    gpu_total_use_time = 0
    job_id = df["job_uuid"].unique()
    work_df = df.copy()
    end_begin_start = None
    init_begin_start = None
    local_max_end = pd.Timestamp(0)
    local_min_start = pd.Timestamp(sys.maxsize)
    last_event_end_time = None
    last_finalize_end_time = None
    calltime = None
    prev_event = "start"
    job_info = {
        "before_init": StatsInfo(),
        "__init__": StatsInfo(),
        "finalize": StatsInfo(),
        "on_train_end": StatsInfo(),
        "load_checkpoint": StatsInfo(),
        "move_tensor_to_device": StatsInfo(),
        "move_models_to_device": StatsInfo(),
        "on_device_begin": StatsInfo(),
        "on_device_end": StatsInfo(),
        "on_epoch_begin": StatsInfo(),
        "on_epoch_end": StatsInfo(),
        "on_train_epoch_start": StatsInfo(),
        "on_train_epoch_end": StatsInfo(),
        "on_train_batch_start": StatsInfo(),
        "on_train_batch_end": StatsInfo(),
        "cpu_learn_predict": StatsInfo(),
        "gpu_learn_predict": StatsInfo(),
        "learn_predict": StatsInfo(),
        "preproc": StatsInfo(),
        "prepostproc": StatsInfo(),
        "postproc": StatsInfo(),
        "keras_proc": StatsInfo(),
        "before_init_time": StatsInfo(),
        "after_finalize": StatsInfo(),
        "update_state_dict": StatsInfo(),
        "save_checkpoint": StatsInfo(),
        "reboot": StatsInfo(),
        "ask_restart": StatsInfo(),
        "cleanup_device_resource": StatsInfo(),
        "overhead": OverheadInfo(),
        "acceleration_rate": 0.0,
        "proc_time": 0.0,
        "job_uuid": "",
    }
    for _, data in work_df.iterrows():
        local_min_start = min(local_min_start, data["calltime"])
        local_max_end = max(local_max_end, data["finish"])
        prefix_name = data["qual_name"].split(".")[0]
        if prefix_name == "main":
            continue
        func_name = data["qual_name"].split(".")[1]
        if func_name not in job_info:
            print("unknown event: ", func_name)
            continue
        if prefix_name == "TensorflowAdaptiveGPUAllocator":
            # func_name is init or save_checkpoint
            job_info[func_name].time.append(data["elapsed_time"])
            job_info[func_name].call_num += 1
            if func_name == "__init__":
                init_begin_start = data["finish"]
                if last_event_end_time is not None:
                    start_time = last_event_end_time
                else:
                    start_time = local_min_start
                elapsed_time = (data["calltime"] - start_time).total_seconds()
                if prev_event == "on_epoch_begin" or prev_event == "on_train_end":
                    job_info["reboot"].time.append(elapsed_time)
                    job_info["reboot"].call_num += 1
                    df = add_df_item(
                        df,
                        calltime=start_time,
                        qual_name="Reboot",
                        job_uuid=job_id,
                        elapsed_time=elapsed_time,
                        finish=data["calltime"],
                    )
                else:
                    job_info["before_init"].time.append(elapsed_time)
                    job_info["before_init"].call_num += 1
                    df = add_df_item(
                        df,
                        calltime=start_time,
                        qual_name="CPU allocated(before Init)",
                        job_uuid=job_id,
                        elapsed_time=elapsed_time,
                        finish=data["calltime"],
                    )
                last_event_end_time = data["finish"]
            prev_event = func_name
        elif prefix_name == "AGATFCallback":
            job_info[func_name].time.append(data["elapsed_time"])
            job_info[func_name].call_num += 1
            prev_event = func_name
            if func_name == "on_train_end" or func_name == "on_epoch_end":
                last_finalize_end_time = data["finish"]
                last_event_end_time = data["finish"]
        else:  # prefix_name == "AdaptiveGPUAllocator":
            if func_name != "__init__":
                job_info[func_name].time.append(data["elapsed_time"])
                job_info[func_name].call_num += 1
                prev_event = func_name

                if func_name == "finalize":
                    last_finalize_end_time = data["finish"]
                    if last_event_end_time is not None:
                        start_time = last_event_end_time
                    else:
                        start_time = end_begin_start
                    elapsed_time = (data["calltime"] - start_time).total_seconds()

                    if job_info["reboot"].call_num == 0:
                        job_info["postproc"].time.append(elapsed_time)
                        job_info["postproc"].call_num += 1
                        df = add_df_item(
                            df,
                            calltime=start_time,
                            qual_name="CPU process(post process)",
                            job_uuid=job_id,
                            elapsed_time=elapsed_time,
                            finish=data["calltime"],
                        )
                    else:
                        job_info["keras_proc"].time.append(elapsed_time)
                        job_info["keras_proc"].call_num += 1
                        df = add_df_item(
                            df,
                            calltime=start_time,
                            qual_name="CPU process(Keras process)",
                            job_uuid=job_id,
                            elapsed_time=elapsed_time,
                            finish=data["calltime"],
                        )

                    last_event_end_time = data["finish"]
                if func_name == "on_device_begin":
                    calltime = data["finish"]
                    if init_begin_start is not None:
                        elapsed_time = (data["calltime"] - init_begin_start).total_seconds()
                        job_info["preproc"].time.append(elapsed_time)
                        job_info["preproc"].call_num += 1
                        df = add_df_item(
                            df,
                            calltime=init_begin_start,
                            qual_name="CPU process(preprocess)",
                            job_uuid=job_id,
                            elapsed_time=elapsed_time,
                            finish=data["calltime"],
                        )
                        init_begin_start = None
                    if end_begin_start is not None:
                        elapsed_time = (data["calltime"] - end_begin_start).total_seconds()
                        job_info["prepostproc"].time.append(elapsed_time)
                        job_info["prepostproc"].call_num += 1
                        df = add_df_item(
                            df,
                            calltime=end_begin_start,
                            qual_name="CPU process(pre/postprocess)",
                            job_uuid=job_id,
                            elapsed_time=elapsed_time,
                            finish=data["calltime"],
                        )
                        end_begin_start = None
                    last_event_end_time = data["finish"]
                elif func_name == "on_device_end":
                    finish = data["calltime"]
                    end_begin_start = data["finish"]
                    if calltime is not None:
                        learn_predict_time = (finish - calltime).total_seconds()
                        if "last_gpu_id" in data:
                            if str(data["last_gpu_id"]) == "CPU":
                                qual_name = "CPU process(learn/predict)"
                                job_info["cpu_learn_predict"].time.append(learn_predict_time)
                                job_info["cpu_learn_predict"].call_num += 1
                            else:
                                qual_name = "GPU process(learn/predict)"
                                job_info["gpu_learn_predict"].time.append(learn_predict_time)
                                job_info["gpu_learn_predict"].call_num += 1
                                gpu_total_use_time += learn_predict_time
                        elif "gpu_memory_mb" in data:
                            if str(data["gpu_memory_mb"]) == "nan":
                                qual_name = "CPU process(learn/predict)"
                                job_info["cpu_learn_predict"].time.append(learn_predict_time)
                                job_info["cpu_learn_predict"].call_num += 1
                            else:
                                qual_name = "GPU process(learn/predict)"
                                job_info["gpu_learn_predict"].time.append(learn_predict_time)
                                job_info["gpu_learn_predict"].call_num += 1
                                gpu_total_use_time += learn_predict_time
                        else:
                            qual_name = "learn/predict process (cannot get GPU info)"
                            job_info["learn_predict"].time.append(learn_predict_time)
                            job_info["learn_predict"].call_num += 1
                        df = add_df_item(
                            df,
                            calltime=calltime,
                            qual_name=qual_name,
                            job_uuid=job_id,
                            elapsed_time=learn_predict_time,
                            finish=finish,
                        )
                    last_event_end_time = data["finish"]

    job_info["proc_time"] = (local_max_end - local_min_start).total_seconds()
    job_info["job_uuid"] = job_id[0][0:7]

    if last_finalize_end_time is not None and local_max_end != last_finalize_end_time:
        elapsed_time = (local_max_end - last_finalize_end_time).total_seconds()
        job_info["after_finalize"].time.append(elapsed_time)
        job_info["after_finalize"].call_num += 1
        df = add_df_item(
            df,
            calltime=last_finalize_end_time,
            qual_name="CPU allocated(after Finalize)",
            job_uuid=job_id,
            elapsed_time=elapsed_time,
            finish=local_max_end,
        )
    job_info["overhead"].time.append(
        sum(job_info["__init__"].time)
        + sum(job_info["finalize"].time)
        + sum(job_info["on_device_begin"].time)
        + sum(job_info["on_device_end"].time)
        + sum(job_info["move_tensor_to_device"].time)
    )
    calc_average(job_info)
    job_info["overhead"].ratio = calc_ratio(sum(job_info["overhead"].time), job_info["proc_time"])
    job_info["acceleration_rate"] = calc_ratio(
        job_info["cpu_learn_predict"].average, job_info["gpu_learn_predict"].average
    )

    df = df[df["qual_name"] != "main"]

    return df, local_max_end, local_min_start, gpu_total_use_time, job_info


def analyze_lightning_mp(df):
    """analyze dataframe generated from PyTorch Lightning log file.

    Args:
        df: pandas dataframe generated from PyTorch Lightning log file

    """
    gpu_total_use_time = 0
    job_id = df["job_uuid"].unique()
    work_df = df.copy()
    end_begin_start = None
    init_begin_start = None
    local_max_end = pd.Timestamp(0)
    local_min_start = pd.Timestamp(sys.maxsize)
    last_event_end_time = None
    last_finalize_end_time = None
    calltime = None
    prev_event = "start"
    job_info = {
        "before_init": StatsInfo(),
        "__init__": StatsInfo(),
        "finalize": StatsInfo(),
        "on_train_end": StatsInfo(),
        "load_checkpoint": StatsInfo(),
        "move_tensor_to_device": StatsInfo(),
        "move_models_to_device": StatsInfo(),
        "on_device_begin": StatsInfo(),
        "on_device_end": StatsInfo(),
        "on_epoch_begin": StatsInfo(),
        "on_epoch_end": StatsInfo(),
        "on_train_epoch_start": StatsInfo(),
        "on_train_epoch_end": StatsInfo(),
        "on_train_batch_start": StatsInfo(),
        "on_train_batch_end": StatsInfo(),
        "cpu_learn_predict": StatsInfo(),
        "gpu_learn_predict": StatsInfo(),
        "learn_predict": StatsInfo(),
        "preproc": StatsInfo(),
        "prepostproc": StatsInfo(),
        "postproc": StatsInfo(),
        "keras_proc": StatsInfo(),
        "before_init_time": StatsInfo(),
        "after_finalize": StatsInfo(),
        "update_state_dict": StatsInfo(),
        "save_checkpoint": StatsInfo(),
        "reboot": StatsInfo(),
        "ask_restart": StatsInfo(),
        "cleanup_device_resource": StatsInfo(),
        "overhead": OverheadInfo(),
        "acceleration_rate": 0.0,
        "proc_time": 0.0,
        "job_uuid": "",
    }
    for _, data in work_df.iterrows():
        local_min_start = min(local_min_start, data["calltime"])
        local_max_end = max(local_max_end, data["finish"])
        prefix_name = data["qual_name"].split(".")[0]
        if prefix_name == "main":
            continue
        func_name = data["qual_name"].split(".")[1]
        if func_name not in job_info:
            print("unknown event: ", func_name)
            continue
        if prefix_name == "LightningAdaptiveGPUAllocator":
            job_info[func_name].time.append(data["elapsed_time"])
            job_info[func_name].call_num += 1
            if func_name == "__init__":
                init_begin_start = data["finish"]
                if last_event_end_time is not None:
                    start_time = last_event_end_time
                else:
                    start_time = local_min_start
                elapsed_time = (data["calltime"] - start_time).total_seconds()
                if prev_event == "ask_restart":
                    job_info["reboot"].time.append(elapsed_time)
                    job_info["reboot"].call_num += 1
                    df = add_df_item(
                        df,
                        calltime=start_time,
                        qual_name="Reboot",
                        job_uuid=job_id,
                        elapsed_time=elapsed_time,
                        finish=data["calltime"],
                    )
                else:
                    job_info["before_init"].time.append(elapsed_time)
                    job_info["before_init"].call_num += 1
                    df = add_df_item(
                        df,
                        calltime=start_time,
                        qual_name="CPU allocated(before Init)",
                        job_uuid=job_id,
                        elapsed_time=elapsed_time,
                        finish=data["calltime"],
                    )
                last_finalize_end_time = data["finish"]  # in case that finalize is not executed
            elif func_name == "on_device_begin":
                calltime = data["finish"]
                if init_begin_start is not None:
                    elapsed_time = (data["calltime"] - init_begin_start).total_seconds()
                    job_info["preproc"].time.append(elapsed_time)
                    job_info["preproc"].call_num += 1
                    df = add_df_item(
                        df,
                        calltime=init_begin_start,
                        qual_name="CPU process(preprocess)",
                        job_uuid=job_id,
                        elapsed_time=elapsed_time,
                        finish=data["calltime"],
                    )
                    init_begin_start = None
                if end_begin_start is not None:
                    elapsed_time = (data["calltime"] - end_begin_start).total_seconds()
                    job_info["prepostproc"].time.append(elapsed_time)
                    job_info["prepostproc"].call_num += 1
                    df = add_df_item(
                        df,
                        calltime=end_begin_start,
                        qual_name="CPU process(pre/postprocess)",
                        job_uuid=job_id,
                        elapsed_time=elapsed_time,
                        finish=data["calltime"],
                    )
                    end_begin_start = None
            elif func_name == "on_device_end":
                finish = data["calltime"]
                end_begin_start = data["finish"]
                if calltime is not None:
                    learn_predict_time = (finish - calltime).total_seconds()
                    if "last_gpu_id" in data:
                        if str(data["last_gpu_id"]) == "CPU":
                            qual_name = "CPU process(learn/predict)"
                            job_info["cpu_learn_predict"].time.append(learn_predict_time)
                            job_info["cpu_learn_predict"].call_num += 1
                        else:
                            qual_name = "GPU process(learn/predict)"
                            job_info["gpu_learn_predict"].time.append(learn_predict_time)
                            job_info["gpu_learn_predict"].call_num += 1
                            gpu_total_use_time += learn_predict_time
                    elif "gpu_memory_mb" in data:
                        if str(data["gpu_memory_mb"]) == "nan":
                            qual_name = "CPU process(learn/predict)"
                            job_info["cpu_learn_predict"].time.append(learn_predict_time)
                            job_info["cpu_learn_predict"].call_num += 1
                        else:
                            qual_name = "GPU process(learn/predict)"
                            job_info["gpu_learn_predict"].time.append(learn_predict_time)
                            job_info["gpu_learn_predict"].call_num += 1
                            gpu_total_use_time += learn_predict_time
                    else:
                        qual_name = "learn/predict process (cannot get GPU info)"
                        job_info["learn_predict"].time.append(learn_predict_time)
                        job_info["learn_predict"].call_num += 1
                    df = add_df_item(
                        df,
                        calltime=calltime,
                        qual_name=qual_name,
                        job_uuid=job_id,
                        elapsed_time=learn_predict_time,
                        finish=finish,
                    )
            elif func_name == "ask_restart":
                if prev_event == "on_device_end":
                    end_begin_start = None
                elif prev_event == "on_device_begin":
                    init_begin_start = None
            prev_event = func_name
            last_event_end_time = data["finish"]
        elif prefix_name == "AGAComunicate" or prefix_name == "AGACheckpoint":
            job_info[func_name].time.append(data["elapsed_time"])
            job_info[func_name].call_num += 1
            if func_name == "on_train_end":
                prev_event = func_name
                last_finalize_end_time = data["finish"]
                last_event_end_time = data["finish"]
        else:  # prefix_name == "AdaptiveGPUAllocator":
            pass

    job_info["proc_time"] = (local_max_end - local_min_start).total_seconds()
    job_info["job_uuid"] = job_id[0][0:7]

    if last_finalize_end_time is not None and local_max_end != last_finalize_end_time:
        elapsed_time = (local_max_end - last_finalize_end_time).total_seconds()
        job_info["after_finalize"].time.append(elapsed_time)
        job_info["after_finalize"].call_num += 1
        df = add_df_item(
            df,
            calltime=last_finalize_end_time,
            qual_name="CPU allocated(after Finalize)",
            job_uuid=job_id,
            elapsed_time=elapsed_time,
            finish=local_max_end,
        )
    job_info["overhead"].time.append(
        sum(job_info["__init__"].time)
        + sum(job_info["finalize"].time)
        + sum(job_info["on_device_begin"].time)
        + sum(job_info["on_device_end"].time)
        + sum(job_info["move_tensor_to_device"].time)
    )
    calc_average(job_info)
    job_info["overhead"].ratio = calc_ratio(sum(job_info["overhead"].time), job_info["proc_time"])
    job_info["acceleration_rate"] = calc_ratio(
        job_info["cpu_learn_predict"].average, job_info["gpu_learn_predict"].average
    )

    df = df[df["qual_name"] != "main"]

    return df, local_max_end, local_min_start, gpu_total_use_time, job_info


def visualize(df):
    """visualize the analyzed dataframe.

    Args:
        df: analyzed pandas dataframe

    """
    desired_format = "%m %d %H:%M:%S.%L"
    df["job_uuid_head"] = df["job_uuid"].str[:7]
    df.to_csv("./visualized_data.csv")
    fig = px.timeline(df, x_start="calltime", x_end="finish", y="job_uuid_head", color="qual_name")
    fig.update_xaxes(tickformat=desired_format)
    fig.update_yaxes(autorange="reversed")
    fig.show()


def gen_df_list(df, job_ids):
    df_list = []
    for id in job_ids:
        df_item = df.copy()
        df_item = df_item[df_item["job_uuid"] == id]
        df_list.append(df_item)
    return df_list


def merge_results(results):
    analyzed_df = pd.DataFrame()
    max_end = pd.Timestamp(0)
    min_start = pd.Timestamp(sys.maxsize)
    gpu_use_time = 0
    job_infos = []
    for result in results:
        analyzed_df = pd.concat([analyzed_df, result[0]])
        max_end = max(max_end, result[1])
        min_start = min(min_start, result[2])
        gpu_use_time += result[3]
        job_infos.append(result[4])
    return analyzed_df, max_end, min_start, gpu_use_time, job_infos


def analyze(df, job_ids, func):
    proc_num = os.cpu_count()
    job_num = len(job_ids)
    pool_size = min(proc_num, job_num)
    df_list = gen_df_list(df, job_ids)
    with Pool(pool_size) as pool:
        results = pool.map(func, df_list)
    analyzed_df, max_end, min_start, gpu_use_time, job_infos = merge_results(results)
    return analyzed_df, max_end, min_start, gpu_use_time, job_infos


def main() -> None:
    parser = argparse.ArgumentParser(description="process visualizer.")
    parser.add_argument("log_file", help="The job history file")
    parser.add_argument("-a", "--no-graph", action="store_true", help="without output graph")

    args = parser.parse_args()
    logfile = args.log_file

    df = read_file(logfile)
    root_ext_pair = os.path.splitext(logfile)
    output_file = root_ext_pair[0] + ".csv"
    job_ids = df["job_uuid"].unique()
    pt_job = []
    tf_job = []
    keras_job = []
    pl_job = []
    noop_job = []
    max_end_pt = pd.Timestamp(0)
    max_end_tf = pd.Timestamp(0)
    max_end_keras = pd.Timestamp(0)
    max_end_pl = pd.Timestamp(0)
    max_end_noop = pd.Timestamp(0)
    min_start_pt = pd.Timestamp(sys.maxsize)
    min_start_tf = pd.Timestamp(sys.maxsize)
    min_start_keras = pd.Timestamp(sys.maxsize)
    min_start_pl = pd.Timestamp(sys.maxsize)
    min_start_noop = pd.Timestamp(sys.maxsize)
    gpu_use_time_pt = 0
    gpu_use_time_tf = 0
    gpu_use_time_keras = 0
    gpu_use_time_pl = 0
    gpu_use_time_noop = 0
    for id in job_ids:
        df_pt = df[(df["qual_name"].str.contains("PyTorchAdaptiveGPUAllocator")) & (df["job_uuid"] == id)]
        df_tf = df[(df["qual_name"].str.contains("TensorflowAdaptiveGPUAllocator")) & (df["job_uuid"] == id)]
        df_keras = df[(df["qual_name"].str.contains("AGATFCallback")) & (df["job_uuid"] == id)]
        df_pl = df[(df["qual_name"].str.contains("LightningAdaptiveGPUAllocator")) & (df["job_uuid"] == id)]
        df_noop = df[(df["qual_name"].str.contains("NoopAdaptiveGPUAllocator")) & (df["job_uuid"] == id)]
        if len(df_pt) != 0:
            pt_job.append(id)
        if len(df_tf) != 0 and len(df_keras) == 0:
            tf_job.append(id)
        if len(df_tf) != 0 and len(df_keras) != 0:
            keras_job.append(id)
        if len(df_pl) != 0:
            pl_job.append(id)
        if len(df_noop) != 0:
            noop_job.append(id)
    assert pt_job or tf_job or keras_job or pl_job or noop_job, "The log file must contain logs from some framework."
    analyzed_df = pd.DataFrame()
    job_infos = []
    if pt_job:
        analyzed_df_pt, max_end_pt, min_start_pt, gpu_use_time_pt, job_infos_pt = analyze(
            df, pt_job, analyze_pytorch_mp
        )
        analyzed_df = pd.concat([analyzed_df, analyzed_df_pt])
        job_infos.extend(job_infos_pt)
    if tf_job:
        analyzed_df_tf, max_end_tf, min_start_tf, gpu_use_time_tf, job_infos_tf = analyze(
            df, tf_job, analyze_tensorflow_mp
        )
        analyzed_df = pd.concat([analyzed_df, analyzed_df_tf])
        job_infos.extend(job_infos_tf)
    if keras_job:
        analyzed_df_keras, max_end_keras, min_start_keras, gpu_use_time_keras, job_infos_keras = analyze(
            df, keras_job, analyze_keras_mp
        )
        analyzed_df = pd.concat([analyzed_df, analyzed_df_keras])
        job_infos.extend(job_infos_keras)
    if pl_job:
        analyzed_df_pl, max_end_pl, min_start_pl, gpu_use_time_pl, job_infos_pl = analyze(
            df, pl_job, analyze_lightning_mp
        )
        analyzed_df = pd.concat([analyzed_df, analyzed_df_pl])
        job_infos.extend(job_infos_pl)
    if noop_job:
        analyzed_df_noop, max_end_noop, min_start_noop, gpu_use_time_noop, job_infos_noop = analyze(
            df, noop_job, analyze_pytorch_mp
        )
        analyzed_df = pd.concat([analyzed_df, analyzed_df_noop])
        job_infos.extend(job_infos_noop)
    max_end = max(max_end_pt, max_end_tf, max_end_keras, max_end_pl, max_end_noop)
    min_start = min(min_start_pt, min_start_tf, min_start_keras, min_start_pl, min_start_noop)
    calc_time = (max_end - min_start).total_seconds()
    gpu_total_use_time = gpu_use_time_pt + gpu_use_time_tf + gpu_use_time_keras + gpu_use_time_pl + gpu_use_time_noop
    gpu_utilize_rate = (gpu_total_use_time / calc_time) * 100
    print("calc_time[sec]       :", calc_time)
    print("gpu_use_time[sec]    :", gpu_total_use_time)
    print("gpu utilize rate[%]  :", gpu_utilize_rate)

    create_job_info_file(output_file)
    for info in job_infos:
        record_job_info(info, output_file)

    if not args.no_graph:
        visualize(analyzed_df)
        analyzed_df.to_csv("./visualizer_analyzed_df.csv")


if __name__ == "__main__":
    main()
