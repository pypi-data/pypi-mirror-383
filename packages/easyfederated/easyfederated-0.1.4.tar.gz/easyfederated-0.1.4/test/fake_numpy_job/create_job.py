# submit_job_using_script_runner.py
from nvflare.app_common.np.np_model_persistor import NPModelPersistor
from nvflare.job_config.api import FedJob
from nvflare.app_common.workflows.fedavg import FedAvg
from nvflare.job_config.script_runner import ScriptRunner, FrameworkType
from nvflare.client.config import ExchangeFormat

# Way better:
# Before creating job:
# export NVFLARE_STARTUP_KIT_DIR="/home/pablo/projects/easyfed/.easyfed/workspace/example_project/prod_00"
# After creating job:
# nvflare job submit -j train_with_custom_script

job_name = "train_with_custom_script"
SERVER = "server.localhost"
num_rounds = 3
CLIENTS = [ "site1", "site2"]
n_clients = len(CLIENTS)

def main():

    # Create a FedJob
    job = FedJob(name=job_name, min_clients=n_clients)

    # TODO: Change to Pytorch or Tensorflow
    persistor = NPModelPersistor(model_dir="/models", model_name="server.npy")
    persistor_id = job.to_server(persistor, SERVER)

    # Controller workflow
    controller = FedAvg(num_clients=n_clients, num_rounds=num_rounds, persistor_id=persistor_id)
    job.to_server(controller, SERVER)  # replace with your server name


    # Define script runner for clients
    train_script = "client.py"  # path relative to the custom folder of client
    script_runner = ScriptRunner(
        script=train_script,
        script_args="",
        launch_external_process=False,  # or True, depending on whether you want to use an external process
        framework=FrameworkType.NUMPY,                 # or specify (like for numpy / pytorch) if required
        server_expected_format=ExchangeFormat.NUMPY,
        params_transfer_type="FULL"
    )

    # Assign to clients
    for client in CLIENTS:
        job.to(script_runner, client, tasks=["train"])

    # Export job folder
    job_folder = job.export_job(job_root="./test")
    print(f"Exported job configuration inside folder: {job_folder}")


if __name__ == "__main__":
    main()