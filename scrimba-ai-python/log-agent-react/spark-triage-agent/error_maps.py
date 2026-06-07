from collections import defaultdict

# Core categorisation index
error_index = defaultdict(set)
error_index['access_exception_set'] = {'authentication token not found', 'access exception', 'access denied',
                                       'permission error'}
error_index['timeout_exception_set'] = {'timed out', 'timeoutexception', 'timeout'}
error_index['oom_exception_set'] = {'oom', 'oomexception', 'out of memory', 'overhead limit exceeded',
                                    'java heap space'}
error_index['schema_exception_set'] = {'schema validation failed', 'incompatible data', 'schema validation error',
                                       'failed to merge'}
error_index['executor_error_exception_set'] = {'executor error', 'rpc client disassociated', 'executorlostfailure'}

# Flat lookup cache for rapid substring evaluation
reverse_error_index = {}
for error_key, error_types in error_index.items():
    for error_type in error_types:
        reverse_error_index[error_type.lower()] = error_key


def lookup_known_error(error_signature: str) -> dict:
    """Matches a signature against known maps; falls back to semantic inference if missing."""
    sig_lower = error_signature.lower()

    # Check for direct keyword overlap
    for keyword, category in reverse_error_index.items():
        if keyword in sig_lower:
            return {"category": category, "known_match": True, "matched_keyword": keyword}

    return {"category": "unknown_exception_set", "known_match": False, "matched_keyword": None}

RECOMMENDATION_INDEX = {
    'access_exception_set': (
        "Verify IAM Roles, instance profiles, and S3 Bucket policies. "
        "Ensure the EMR execution role has permission to access the target metadata/KMS keys."
    ),
    'timeout_exception_set': (
        "Increase spark.network.timeout to 800s and spark.executor.heartbeatInterval to 60s. "
        "Check for network bottlenecks or heavy garbage collection pauses on your nodes."
    ),
    'oom_exception_set': (
        "Increase executor/driver memory parameters. Adjust spark.memory.fraction, "
        "or change your instance fleet profile to use memory-optimized instances (e.g., r5 or r6g series)."
    ),
    'schema_exception_set': (
        "Verify the source schema using a data validator. Clean up dirty source rows, or explicitly "
        "enable spark.sql.parquet.mergeSchema if merging evolution logs across historical directories."
    ),
    'executor_error_exception_set': (
        "Investigate underlying node terminations on YARN or spot instance reclaims. "
        "Consider configuring a percentage of on-demand core nodes to preserve framework coordination stability."
    ),
    'unknown_exception_set': (
        "Examine secondary container stderr/stdout tracking spaces. Re-run with spark.master log-level set to DEBUG."
    )
}

def get_infrastructure_fix(category: str) -> str:
    """Returns an actionable recommendation string based on the categorized error."""
    return RECOMMENDATION_INDEX.get(category, RECOMMENDATION_INDEX['unknown_exception_set'])
