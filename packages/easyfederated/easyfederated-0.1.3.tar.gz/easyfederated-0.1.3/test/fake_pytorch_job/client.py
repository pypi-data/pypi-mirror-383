import nvflare.client as flare
import torch
from nvflare.client.tracking import SummaryWriter

from model import SimpleTorchModel


def main():
    # Initialize the model
    model = SimpleTorchModel()

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
            params = model.get_weights()
        else:
            params = torch.tensor(input_model.params['weights'])
        model.set_weights(params)

        # Perform local training
        print(f"Client {client_name} starting training...")
        new_params = model.train_step(learning_rate=1.0)

        print(f"Client {client_name} finished training for round {input_model.current_round}")
        print(f"Sending weights: {new_params}")

        output_model = flare.FLModel(
            params=model.cpu().state_dict(),
            params_type="FULL",
            current_round=input_model.current_round,
        )
        flare.send(output_model)


if __name__ == "__main__":
    main()
