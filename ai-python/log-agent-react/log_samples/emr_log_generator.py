#!/usr/bin/env python3
import argparse
import os
import random
import time
from datetime import datetime, timedelta

HOSTS = ["ip-10-12-8-44", "ip-10-12-9-21", "ip-10-12-7-18", "ip-10-12-6-33"]
EXCLUDE_USERS = ["synthetic_user", "unknown_user", "test_user"]
BUCKETS = ["synthetic-bucket", "data-bucket", "prod-bucket", "logs-bucket"]
PATHS = [
    "landing/orders/",
    "warehouse/analytics/",
    "input/transactions/",
    "processed/events/",
]
COLUMNS = [
    ("total_amount", "decimal(18,2)", "string"),
    ("customer_id", "bigint", "string"),
    ("event_ts", "timestamp", "string"),
    ("region", "string", "int"),
]
CONTAINERS = [
    "container_20260607_0001_01_000001",
    "container_20260607_0001_01_000002",
    "container_20260607_0001_01_000003",
    "container_20260607_0007_01_000014",
    "container_20260607_0012_01_000021",
]

# EMR-style log file names (no compression)
EMR_LOG_NAMES = ["controller", "stderr", "stdout", "syslog"]

def _random_id(prefix, min_len=4, max_len=8):
    length = random.randint(min_len, max_len)
    return prefix + "".join(random.choices("0123456789", k=length))

def _ts(base=None, delta_seconds=None):
    base = base or datetime(2026, 6, 7, 16, 0, 0)
    if delta_seconds is None:
        delta_seconds = random.randint(0, 3599)
    return (base + timedelta(seconds=delta_seconds)).strftime("%Y-%m-%d %H:%M:%S")

def _line(level, component, message):
    return f"{_ts()} {level} {component}: {message}"

def _choice(seq):
    return random.choice(seq)

def _success_log():
    job = _random_id("Job")
    stage = random.randint(0, 20)
    tid = _random_id("TID", min_len=3, max_len=5)
    return [
        _line("INFO", "org.apache.spark.internal.Logging", "Running Spark version 3.5.0"),
        _line("INFO", "org.apache.hadoop.yarn.client.RMProxy",
              f"Connecting to ResourceManager at rm.cluster.local/10.12.8.34:8032"),
        _line("INFO", "org.apache.spark.storage.BlockManagerMaster",
              f"Registered BlockManager BlockManagerId(driver, 10.12.8.34, {random.randint(30000,40000)}, None)"),
        _line("INFO", "org.apache.spark.scheduler.DAGScheduler",
              f"{job} {random.randint(0, 10)} finished: count at JobRunner.scala:{random.randint(10, 100)}"),
        _line("INFO", "org.apache.spark.storage.BlockManager",
              f"BlockManager shut down cleanly for {job}"),
    ]

def _oom_log():
    app_id = _random_id("application_")
    stage = random.randint(0, 15)
    task = random.randint(0, 199)
    tid = _random_id("TID", min_len=3, max_len=5)
    container = _random_id("container_")
    exec_id = random.randint(1, 10)
    host = _choice(HOSTS)
    page = random.randint(100, 200)
    line = random.randint(100, 250)
    page2 = random.randint(100, 200)
    line2 = random.randint(100, 250)

    msg_variation = [
        "Job failed due to driver-side out of memory condition.",
        "Driver exceeded memory limits while building broadcast table.",
        "Application failed due to broadcast join driver OOM.",
    ]
    oom_type = [
        "Not enough memory to build and broadcast the table to all worker nodes.",
        "Java heap space exhausted during broadcast serialization.",
        "Broadcast exchange exceeded memory threshold.",
    ]

    return [
        _line("INFO", "org.apache.spark.internal.Logging", "Running Spark version 3.5.0"),
        _line("INFO", "org.apache.hadoop.yarn.client.RMProxy",
              f"Connecting to ResourceManager at rm.cluster.local/10.12.8.34:8032"),
        _line("INFO", "org.apache.spark.storage.BlockManagerMaster",
              f"Registered BlockManager BlockManagerId(driver, {host}, {random.randint(30000,40000)}, None)"),
        _line("INFO", "org.apache.spark.scheduler.DAGScheduler", f"Submitting ResultStage {stage}"),
        _line("INFO", "org.apache.spark.scheduler.TaskSetManager",
              f"Starting task {task}.0 in stage {stage}.0 ({tid}, {container}, executor {exec_id}, partition {task}, PROCESS_LOCAL)"),
        _line("INFO", "org.apache.spark.scheduler.TaskSetManager",
              f"Finished task {task}.0 in stage {stage}.0 ({tid}) in {random.randint(50000,90000)} ms"),
        _line("INFO", "org.apache.spark.sql.execution.exchange.BroadcastExchangeExec",
              f"HashedRelation up to {random.randint(40, 70) * 1000000} bytes total, starting serialization..."),
        _line("ERROR", "org.apache.spark.scheduler.DAGScheduler", _choice(msg_variation)),
        "",
        "java.lang.OutOfMemoryError: " + _choice(oom_type),
        "As a workaround, you can set spark.sql.autoBroadcastJoinThreshold to -1 or increase spark.driver.memory.",
        f"    at org.apache.spark.sql.execution.exchange.BroadcastExchangeExec.relationFuture(BroadcastExchangeExec.scala:{page})",
        f"    at org.apache.spark.util.ThreadUtils.newForkJoinPool(ThreadUtils.scala:{line})",
        "",
        _line("ERROR", "org.apache.spark.executor.Executor",
              f"Task {random.randint(10, 60)}.0 in stage {random.randint(1, 5)}.0 failed: GC overhead limit exceeded"),
        "java.lang.OutOfMemoryError: GC overhead limit exceeded",
        f"    at java.util.Arrays.copyOf(Arrays.java:{3000 + random.randint(0, 300)})",
        f"    at java.lang.AbstractStringBuilder.ensureCapacityInternal(AbstractStringBuilder.java:{100 + random.randint(0, 200)})",
        "",
        _line("ERROR", "org.apache.spark.executor.Executor",
              f"Task {random.randint(10, 60)}.0 in stage {random.randint(1, 5)}.0 failed: Java heap space"),
        "java.lang.OutOfMemoryError: Java heap space",
        f"    at org.apache.spark.util.collection.ExternalAppendOnlyMap.insert(ExternalAppendOnlyMap.scala:{page2})",
        f"    at org.apache.spark.shuffle.sort.BypassMergeSortShuffleWriter.write(BypassMergeSortShuffleWriter.java:{line2})",
        "",
        _line("ERROR", "org.apache.spark.scheduler.DAGScheduler",
              f"Application {app_id} failed due to unrecoverable executor loss."),
    ]

def _lost_executor_log():
    app_id = _random_id("application_")
    stage = random.randint(5, 30)
    task = random.randint(0, 150)
    tid = _random_id("TID", min_len=3, max_len=5)
    container = _choice(CONTAINERS)
    exec_id = random.randint(1, 10)
    host = _choice(HOSTS)
    dline = random.randint(2000, 2500)
    dline2 = random.randint(2300, 2450)
    job = _random_id("Job")

    return [
        _line("INFO", "org.apache.spark.scheduler.DAGScheduler", f"Submitting ShuffleMapStage {stage}"),
        _line("INFO", "org.apache.spark.scheduler.TaskSetManager",
              f"Starting task {task}.0 in stage {stage}.0 ({tid}, {container}, executor {exec_id}, partition {task}, NODE_LOCAL)"),
        _line("WARN", "org.apache.spark.scheduler.TaskSetManager",
              f"Lost task {task}.0 in stage {stage}.0 ({tid}) on executor {exec_id}: ExecutorLostFailure"),
        _line("ERROR", "org.apache.spark.scheduler.cluster.YarnSchedulerBackend$YarnSchedulerEndpoint",
              f"Lost executor {exec_id} on {host}: remote Rpc client disassociated"),
        "",
        "Traceback (most recent call last):",
        f"  File \"/opt/jobs/job_runner{random.randint(1, 20)}.py\", line {random.randint(100, 200)}, in <module>",
        f'    result = df.groupby("{_choice(["region", "customer_id", "product_id"])}").count().collect()',
        f"  File \"/opt/spark/python/pyspark/sql/dataframe.py\", line {random.randint(1200, 1300)}, in collect",
        "    sock_info = self._jdf.collectToPython()",
        "py4j.protocol.Py4JJavaError: An error occurred while calling o87.collectToPython.",
        "",
        "Caused by: org.apache.spark.SparkException: Job aborted due to stage failure:",
        f"Task {task} in stage {stage}.0 failed {random.randint(3, 5)} times, most recent failure: Lost task {task}.0 in stage {stage}.0 ({tid}) on executor {exec_id}",
        f"    at org.apache.spark.scheduler.DAGScheduler.failJobAndIndependentStages(DAGScheduler.scala:{dline})",
        f"    at org.apache.spark.scheduler.DAGScheduler.abortStage(DAGScheduler.scala:{dline2})",
        "",
        _line("WARN", "org.apache.spark.scheduler.TaskSetManager",
              f"Re-queueing tasks for stage {stage} after executor loss"),
        _line("ERROR", "org.apache.spark.scheduler.DAGScheduler",
              f"{job} {random.randint(1, 30)} failed: count at JobRunner.scala:{random.randint(10, 100)}, took {random.randint(10, 30)}.118 s"),
    ]

def _schema_log():
    bucket = _choice(BUCKETS)
    path = _choice(PATHS)
    col, src_type, tgt_type = _choice(COLUMNS)
    table_db = _choice(["analytics", "warehouse", "prod"])
    table_name = _choice(["orders", "transactions", "events"])
    line = random.randint(80, 100)
    rw_line = random.randint(1500, 1600)
    cmd_line = random.randint(120, 130)
    side_line = random.randint(70, 90)
    writer_line = random.randint(600, 650)

    return [
        _line("INFO", "org.apache.spark.internal.Logging",
              f"Starting Spark session for job schema_validation_{random.randint(1, 30)}"),
        _line("INFO", "org.apache.spark.internal.Logging",
              f"Reading input files from s3a://{bucket}/{path}"),
        _line("INFO", "org.apache.spark.sql.execution.datasources.InMemoryFileIndex",
              f"Selected {random.randint(4, 12)} partitions from path: s3a://{bucket}/{path}"),
        "",
        _line("ERROR", "org.apache.spark.sql.execution.QueryExecution",
              f"AnalysisException: [SCHEMA_MISMATCH] The schema of the DataFrame does not match the target table schema."),
        "",
        "Traceback (most recent call last):",
        f"  File \"/opt/jobs/schema_loader{random.randint(1, 20)}.py\", line {line}, in <module>",
        f'    df.write.mode("append").saveAsTable("{table_db}.{table_name}")',
        f'  File "/opt/spark/python/pyspark/sql/readwriter.py", line {rw_line}, in saveAsTable',
        "    self._jwrite.saveAsTable(tableName)",
        f'pyspark.sql.utils.AnalysisException: [SCHEMA_MISMATCH] Failed to merge fields:',
        f"    source column: {col} ({src_type})",
        f"    target column: {col} ({tgt_type})",
        "",
        "Caused by: org.apache.spark.sql.AnalysisException: Cannot write incompatible data to table "
        f"`{table_db}`.`{table_name}`.",
        f"    at org.apache.spark.sql.execution.datasources.InsertIntoHadoopFsRelationCommand.run(InsertIntoHadoopFsRelationCommand.scala:{cmd_line})",
        f"    at org.apache.spark.sql.execution.command.DataWritingCommandExec.sideEffectResult(DataWritingCommandExec.scala:{side_line})",
        f"    at org.apache.spark.sql.DataFrameWriter.saveAsTable(DataFrameWriter.scala:{writer_line})",
        "",
        _line("WARN", "org.apache.spark.scheduler.DAGScheduler",
              "Job aborted due to stage failure: write operation rejected by schema validation."),
    ]

def _timeout_log():
    stage = random.randint(10, 40)
    task = random.randint(0, 120)
    tid = _random_id("TID", min_len=3, max_len=5)
    container = _choice(CONTAINERS)
    exec_id = random.randint(1, 10)
    bucket = _choice(BUCKETS)
    t_line = random.randint(250, 300)
    e_line = random.randint(1200, 1250)
    job = _random_id("Job")
    scala_line = random.randint(50, 70)

    return [
        _line("INFO", "org.apache.spark.scheduler.DAGScheduler", f"Submitting ShuffleMapStage {stage}"),
        _line("INFO", "org.apache.spark.scheduler.TaskSetManager",
              f"Starting task {task}.0 in stage {stage}.0 ({tid}, {container}, executor {exec_id}, partition {task}, NODE_LOCAL)"),
        _line("WARN", "org.apache.spark.executor.Executor",
              f"Task {task}.0 in stage {stage}.0 is taking longer than expected; heartbeat still pending."),
        _line("ERROR", "org.apache.spark.scheduler.TaskSetManager",
              f"Lost task {task}.0 in stage {stage}.0 ({tid}) on executor {exec_id}: Task timed out after 120000 ms"),
        "",
        "Traceback (most recent call last):",
        f"  File \"/opt/jobs/timeout_job{random.randint(1, 20)}.py\", line {random.randint(90, 120)}, in <module>",
        f'    output = joined_df.write.mode("overwrite").parquet("s3a://{bucket}/output/")',
        f"  File \"/opt/spark/python/pyspark/sql/readwriter.py\", line 1650, in parquet",
        "    self._jwrite.parquet(path)",
        "py4j.protocol.Py4JJavaError: An error occurred while calling o91.parquet.",
        "",
        "Caused by: java.util.concurrent.TimeoutException: Futures timed out after [120000 milliseconds]",
        f"    at org.apache.spark.network.client.TransportClientFactory.createClient(TransportClientFactory.scala:{t_line})",
        f"    at org.apache.spark.executor.Executor.reportHeartBeat(Executor.scala:{e_line})",
        "",
        _line("ERROR", "org.apache.spark.scheduler.DAGScheduler",
              f"{job} {random.randint(1, 30)} failed: write at TimeoutJob.scala:{scala_line}, took {random.randint(100, 150)}.884 s"),
        _line("WARN", "org.apache.spark.scheduler.cluster.YarnSchedulerBackend",
              f"Executor {exec_id} removed after task timeout and missed heartbeat."),
    ]

def _access_log():
    bucket = _choice(BUCKETS)
    user = _choice(EXCLUDE_USERS)
    scala_line = random.randint(800, 850)
    reader_line = random.randint(60, 70)
    java_line = random.randint(100, 120)

    return [
        _line("INFO", "org.apache.spark.sql.execution.datasources.FileScanRDD",
              f"Scanning s3a://{bucket}/protected/"),
        _line("WARN", "org.apache.hadoop.security.UserGroupInformation",
              f"Authentication token not found for user: {user}"),
        _line("ERROR", "org.apache.spark.sql.AnalysisException",
              "Access denied while reading input path."),
        "",
        "Caused by: com.amazonaws.services.s3.model.AmazonS3Exception: Access Denied",
        f"    at org.apache.hadoop.fs.s3a.S3AFileSystem.open(S3AFileSystem.java:{scala_line})",
        f"    at org.apache.spark.sql.execution.datasources.HadoopFileLinesReader.read(HadoopFileLinesReader.scala:{reader_line})",
        "",
        _line("ERROR", "org.apache.spark.sql.execution.QueryExecution",
              "Job aborted due to permission error."),
    ]

def _generic_log(success_prob):
    if random.random() < success_prob:
        return _success_log()
    job = _random_id("Job")
    scala_line = random.randint(40, 60)
    return [
        _line("ERROR", "org.apache.spark.scheduler.DAGScheduler",
              f"{job} {random.randint(1, 30)} failed with an unknown error category."),
        "",
        "Traceback (most recent call last):",
        f"  File \"/opt/jobs/generic_runner{random.randint(1, 20)}.py\", line {random.randint(20, 50)}, in <module>",
        "    run_job()",
        "RuntimeError: Synthetic failure generated for training data",
    ]

GENERATORS = {
    "oom": _oom_log,
    "lost_executor": _lost_executor_log,
    "schema": _schema_log,
    "timeout": _timeout_log,
    "access": _access_log,
}

def generate_log(log_type=None, success_prob=0.0):
    log_type = (log_type or "").strip().lower()
    if log_type == "":
        return "\n".join(_generic_log(success_prob)())
    if log_type in GENERATORS:
        return "\n".join(GENERATORS[log_type]())
    return "\n".join(_generic_log(success_prob)())

def _timestamped_base_name():
    # e.g. 2026-06-07_16-30-45_cluster1_step_s12345
    now = datetime.now()
    ts = now.strftime("%Y-%m-%d_%H-%M-%S")
    cluster_id = _random_id("cluster", min_len=1, max_len=2)
    step_id = _random_id("s", min_len=5, max_len=7)
    return f"{ts}_cluster{cluster_id}_step_{step_id}"

def _emr_log_name_with_timestamp(base_name):
    log_name = _choice(EMR_LOG_NAMES)
    return f"{base_name}_{log_name}"

def write_emr_file(path, log_type=None, success_prob=0.0):
    text = generate_log(log_type, success_prob)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def write_mixed_file(path, n_segments=20, types=None, success_prob=0.3):
    types = types or list(GENERATORS.keys())
    lines = []
    for i in range(n_segments):
        if random.random() < success_prob:
            seg_lines = _success_log()
        else:
            t = random.choice(types)
            seg_lines = GENERATORS[t]()
        lines.extend(seg_lines)
        lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")

def write_emr_bundle_mixed(outdir, n_files=50, n_segments_per_file=20, types=None, success_prob=0.3):
    os.makedirs(outdir, exist_ok=True)
    for i in range(n_files):
        base = _timestamped_base_name()
        filename = _emr_log_name_with_timestamp(base)
        path = os.path.join(outdir, filename)
        write_mixed_file(path, n_segments=n_segments_per_file, types=types, success_prob=success_prob)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--bundle", default="")
    ap.add_argument("--bundle-mixed", default="")
    ap.add_argument("--n", type=int, default=1)
    ap.add_argument("--n-files", type=int, default=50)
    ap.add_argument("--n-segments", type=int, default=20)
    ap.add_argument("--success-prob", type=float, default=0.3,
                    help="Probability of success log when type is unknown or in mixed mode")
    args = ap.parse_args()

    if args.bundle_mixed:
        write_emr_bundle_mixed(
            args.bundle_mixed,
            n_files=args.n_files,
            n_segments_per_file=args.n_segments,
            success_prob=args.success_prob
        )
    elif args.bundle:
        for i in range(args.n):
            base = _timestamped_base_name()
            t = random.choice(list(GENERATORS.keys()) + [""])
            suffix = (t or "generic")
            filename = f"{base}_{suffix}"
            os.makedirs(args.bundle, exist_ok=True)
            path = os.path.join(args.bundle, filename)
            write_emr_file(path, t, args.success_prob)
    elif args.out:
        # If out is a directory, use timestamped EMR-style names
        if os.path.isdir(args.out):
            base = _timestamped_base_name()
            log_type = args.type.strip().lower() if args.type else ""
            suffix = log_type or "generic"
            filename = f"{base}_{suffix}"
            path = os.path.join(args.out, filename)
        else:
            path = args.out
        write_emr_file(path, args.type or None, args.success_prob)
    else:
        for _ in range(args.n):
            print(generate_log(args.type or None, args.success_prob))
            if args.n > 1:
                print()

if __name__ == "__main__":
    main()