export TF_CPP_MIN_LOG_LEVEL=1

WORKSPACE=/home/${USER}/workspace
PYLOT_PATH="${WORKSPACE}/pylot"
export PYTHONPATH=$PYLOT_PATH:$PYTHONPATH
project_root=${WORKSPACE}/ADSFuzzer
save_root="${WORKSPACE}/results/ADSFuzzer/data_collection"

GPU=0
server_config='fuzzing_process_2'

scenario_name='intersection_straight_bak'
agent_name='pylot'
# config_used='main_fuzzer'

entry_point_target_agent='ads.systems.Pylot.ERDOSRootCauseAgent:ERDOSRootCauseAgent'
# entry_point_target_agent='ads.systems.Pylot.ERDOSAgent:ERDOSAgent'
# config_target_agent=${project_root}/ads/systems/Pylot/pylot_configs/perfect_detection_pylot.conf
ori_config_target_agent=${project_root}/ads/systems/Pylot/pylot_configs/root_cause.conf

ori_fuzzer_config_file="${WORKSPACE}/ADSFuzzer/configs/main_fuzzer.yaml"
ori_fuzzer_config_file="${WORKSPACE}/ADSFuzzer/configs/main_fuzzer.yaml"
fuzzing_name='RandomFuzzer'
entry_point_fuzzer='fuzzer.suites:RandomFuzzer'

config_used=${scenario_name}_${fuzzing_name}
config_target_agent=${project_root}/configs/pylot_configs/${scenario_name}_${fuzzing_name}.conf
fuzzer_config_file=${WORKSPACE}/ADSFuzzer/configs/${config_used}.yaml
cp ${ori_config_target_agent} ${config_target_agent}
cp ${ori_fuzzer_config_file} ${fuzzer_config_file}



# fuzzer_config_file="${WORKSPACE}/ADSFuzzer/configs/${config_used}.yaml"
# fuzzing_name='RandomFuzzer'
# entry_point_fuzzer='fuzzer.suites:BehAVExplor'
erdos_start_port=19200
sed -i "s#--erdos_start_port=.*#--erdos_start_port=${erdos_start_port}#" ${config_target_agent}



total_repeats=1
run_hour=4

mutator_vehicle_num=10
mutator_walker_num=10
mutator_static_num=0

save_folder=${save_root}/${agent_name}/${scenario_name}/${fuzzing_name}
seed_path=${project_root}/data/seeds/${scenario_name}.json

sed -i "s#entry_point_target_agent:.*#entry_point_target_agent: ${entry_point_target_agent}#" ${fuzzer_config_file}
sed -i "s#config_target_agent:.*#config_target_agent: ${config_target_agent}#" ${fuzzer_config_file}
sed -i "s#seed_path:.*#seed_path: ${seed_path}#" ${fuzzer_config_file}
sed -i "s#gpu:.*#gpu: ${GPU}#" ${fuzzer_config_file}
sed -i "s#entry_point_fuzzer:.*#entry_point_fuzzer: ${entry_point_fuzzer}#" ${fuzzer_config_file}

for run_index in $(seq "1" "$total_repeats"); do
  echo "Current run time: $run_index"
  #CUDA_VISIBLE_DEVICES=$GPU python ${project_root}/main_fuzzer.py \
  python ${project_root}/main_fuzzer.py \
  -cn ${config_used} \
  server_configs=$server_config \
  save_root=$save_folder \
  seed_path=$seed_path \
  gpu=$GPU \
  time_limit=$run_hour \
  mutator_vehicle_num=$mutator_vehicle_num \
  mutator_walker_num=$mutator_walker_num \
  mutator_static_num=$mutator_static_num
  sleep 1
done

rm ${config_target_agent}
rm ${fuzzer_config_file}