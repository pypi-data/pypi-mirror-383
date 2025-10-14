import numpy as np
from model import SimpleNumpyModel

import nvflare.client as flare
from nvflare.client.tracking import SummaryWriter


def main():
    # Initialize the model
    model = SimpleNumpyModel()

    # Initialize FLARE
    flare.init()
    sys_info = flare.system_info()
    client_name = sys_info["site_name"]

    print(f"Client {client_name} initialized")

    # Initialize summary writer for tracking
    summary_writer = SummaryWriter()

    while flare.is_running():
        # Receive model from server
        input_model = flare.receive()
        print(f"Client {client_name}, current_round={input_model.current_round}")
        print(f"Received weights: {input_model.params}")

        # Load the received model weights
        if input_model.params == {}:
            # Initialize with default weights if this is the first round
            params = model.get_weights()
        else:
            params = np.array(input_model.params["numpy_key"], dtype=np.float32)

        model.set_weights(params)

        # Perform local training
        print(f"Client {client_name} starting training...")
        new_params = model.train_step(learning_rate=1.0)

        # Evaluate the model
        metrics = model.evaluate()
        print(f"Client {client_name} evaluation metrics: {metrics}")

        # Log metrics to summary writer
        global_step = input_model.current_round
        summary_writer.add_scalar(tag="weight_mean", scalar=metrics["weight_mean"], global_step=global_step)

        print(f"Client {client_name} finished training for round {input_model.current_round}")
        print(f"Sending weights: {new_params}")

        # Send updated model back to server
        output_model = flare.FLModel(
            params={"numpy_key": new_params},
            params_type="FULL",
            metrics=metrics,
            current_round=input_model.current_round,
        )

        flare.send(output_model)


if __name__ == "__main__":
    main()
