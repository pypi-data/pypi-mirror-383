#!/bin/bash
set -e
conda_env_path=$1

py_version=$(${conda_env_path}/bin/python -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
                      
${conda_env_path}/bin/pip install --index-url https://pypi.org/simple dash==3.0.3 dash-renderer==1.9.1 plotly==6.0.1 typing==3.7.4.3 streamlit==1.45.1 ipython==9.2.0 ipykernel==6.29.5 ipython-sql==0.4.1 jupysql==0.10.14 psycopg2-binary==2.9.10 cryptography==44.0.3 dataflow-core==2.1.14rc2 dataflow-dbt==0.0.3

# 3. Install Dataflow Airflow to a separate path in environment 
${conda_env_path}/bin/pip install --index-url https://pypi.org/simple \
    --force-reinstall --root-user-action ignore \
    --no-warn-conflicts dataflow-airflow==2.10.7 \
    --constraint https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-${py_version}.txt \
    --target ${conda_env_path}/bin/airflow-libraries/

files=(
    ${conda_env_path}/lib/python${py_version}/site-packages/dbt/config/profile.py 
    ${conda_env_path}/lib/python${py_version}/site-packages/dbt/task/debug.py
)
for file in ${files[@]}
do      
    awk '{gsub("from dbt.clients.yaml_helper import load_yaml_text", "from dbt.dataflow_config.secrets_manager import load_yaml_text"); print}' $file > temp 
    mv temp $file
done

echo "Environment Creation Successful"