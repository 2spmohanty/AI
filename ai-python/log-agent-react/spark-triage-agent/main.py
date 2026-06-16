import json
from v1_react import run_v1_react_agent
from v2_react import run_v2_react_agent
from v3_react_on_mcp import run_v3_react_agent
from agent_result_judge import evaluate_agent_output
from datetime import datetime

def execute_diagnostic_pipeline(sample_name: str, log_payload: str, agent_type="v1"):
    """Orchestrates log diagnostics and judge valuations for a given scenario."""
    print("=" * 80)
    print(f"STARTING DIAGNOSTIC TRACE FOR: {sample_name}")
    print("=" * 80)

    try:
        if agent_type == "v1":
            # 1. Trigger manual ReAct Agent loop using gpt-5-mini
            print("=" * 80)
            print("Running diagnostic pipeline with Manual V1 ReAct Agentic Pipeline")
            diagnosis = run_v1_react_agent(log_payload, max_iterations=5)
        elif agent_type == "v2":
            print("Running diagnostic pipeline with V2 Anthropic Too Usage ReAct Agentic Pipeline")
            diagnosis = run_v2_react_agent(log_payload)
        else:
            print("Running diagnostic pipeline with V3 Anthropic Too Usage ReAct Agentic Pipeline & MCP Server")
            diagnosis = run_v3_react_agent(log_payload)

        print(f"\n [AGENT OUTCOME] [PIPELINE {agent_type}] -  Generated Structured Diagnosis:")
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

    oom_log_file = "../sample-test-data/application_1717820001123_0001_executor_4.log"
    access_log_file = "../sample-test-data/application_1717820001123_0001.log"
    executor_log_file="../sample-test-data/application_1717820001124_0001.log"
    schema_log_file = "../sample-test-data/application_1717920001124_0001.log"
    ############ The Agent has not ben trained on DIsk Space issue, The below log file will find how our agent will reason.
    disk_issue_log_file = "../sample-test-data/application_disk_1817920001125_0001.log"  # The agent has not been trained on this.
    dynamo_access_log_file="../sample-test-data/application_dynamo_1817920001126_0001.log"


    current_time = datetime.now().strftime("%Y%m%d-%H%M%S")

    log_data : str = None
    with open(oom_log_file, 'r', encoding='utf-8') as f:
        log_data = f.read()


    #execute_diagnostic_pipeline(f"REACT-ANALYSIS-{current_time}", log_data) # V1 Manual Agent
    execute_diagnostic_pipeline(f"REACT-ANALYSIS-{current_time}", log_data, agent_type="v3")


