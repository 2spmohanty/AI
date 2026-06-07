import json
from v1_react import run_v1_react_agent, evaluate_agent_output
from datetime import datetime

def execute_diagnostic_pipeline(sample_name: str, log_payload: str):
    """Orchestrates log diagnostics and judge valuations for a given scenario."""
    print("=" * 80)
    print(f"STARTING DIAGNOSTIC TRACE FOR: {sample_name}")
    print("=" * 80)

    try:
        # 1. Trigger manual ReAct Agent loop using gpt-5-mini
        diagnosis = run_v1_react_agent(log_payload, max_iterations=5)

        print("\n [AGENT OUTCOME] -  Generated Structured Diagnosis:")
        print(json.dumps(diagnosis, indent=2))

        # 2. Forward output to the flagship GPT-5 evaluation judge
        print("\n[JUDGING] Dispatching diagnosis to the expert infrastructure judge...")
        evaluation_results = evaluate_agent_output(log_payload, diagnosis)

        print("\n[JUDGE RESULTS] Evaluation Matrix:")
        print(json.dumps(evaluation_results, indent=2))

    except Exception as e:
        print(f"Critical Pipeline Failure: {str(e)}")

    print("=" * 80 + "\n")


if __name__ == "__main__":

    oom_log_file = "../test-data/application_1717820001123_0001_executor_4.log"
    access_log_file = "../test-data/application_1717820001123_0001.log"
    executor_log_file="../test-data/application_1717820001124_0001.log"
    schema_log_file = "../test-data/application_1717920001124_0001.log"


    current_time = datetime.now().strftime("%Y%m%d-%H%M%S")

    log_data : str = None
    with open(schema_log_file, 'r', encoding='utf-8') as f:
        log_data = f.read()

    execute_diagnostic_pipeline(f"REACT-ANALYSIS-{current_time}", log_data)

