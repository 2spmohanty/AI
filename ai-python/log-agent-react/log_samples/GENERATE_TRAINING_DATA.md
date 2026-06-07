
## Test Data GEneration for Agent Training

```shell
#Generate a single specific error log (e.g., OOM)
python3 emr_log_generator.py --type oom --out oom_error.log
python3 emr_log_generator.py --type lost_executor --out lost_executor.log
python3 emr_log_generator.py --type schema --out schema_mismatch.log
python3 emr_log_generator.py --type timeout --out timeout_error.log
python3 emr_log_generator.py --type access --out access_denied.log

# Generate many files of a single error type
for i in $(seq 1 5); do
  python3 emr_log_generator.py \
    --type access \
    --out training_data \
    --success-prob 0.1
done
# 100 files, 20 segments each, 30% success, 70% error
python3 emr_log_generator.py --bundle-mixed emr_mixed_logs \
    --n-files 100 --n-segments 20 --success-prob 0.3
    
# 4. Generate mixed error logs (multiple error types in one file)
python3 emr_log_generator.py \
  --bundle-mixed emr_mixed_error_logs \
  --n-files 50 \
  --n-segments 20 \
  --success-prob 0.0

#Generate mixed success + error logs (recommended for training)
#This is the most realistic setup: each file has both successful runs and errors.

# 5.1. 100 mixed files, 20 segments each, 30% success / 70% error

python3 emr_log_generator.py \
  --bundle-mixed emr_mixed_logs_30pct_success \
  --n-files 100 \
  --n-segments 20 \
  --success-prob 0.3    

#Generate a single mixed file for testing
# Example: one file with 20 segments, 30% success:

python3 emr_log_generator.py \
  --out mixed_sample.log \
  --n-segments 20 \
  --success-prob 0.3
  
python3 emr_log_generator.py \
  --bundle-mixed emr_all_errors \
  --n-files 3 \
  --n-segments 20 \
  --success-prob 0.3
```

| Goal                                | Command pattern                                                  |
| ----------------------------------- | ---------------------------------------------------------------- |
| One specific error file             | --type <type> --out <file>.log                                   |
| Many specific error files           | loop with --type <type> --out dir/file_$i.log                    |
| Mixed error types (no success)      | --bundle-mixed dir --n-files N --n-segments M --success-prob 0.0 |
| Mixed success + error (30% success) | --bundle-mixed dir --n-files N --n-segments M --success-prob 0.3 |
| Mixed success + error (50% success) | --bundle-mixed dir --n-files N --n-segments M --success-prob 0.5 |
| One test mixed file                 | --out mixed_sample.log --n-segments 20 --success-prob 0.3        |
