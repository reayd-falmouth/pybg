from typing import Callable, Dict

# Registry of encoders
INPUT_ENCODERS: Dict[str, Dict] = {}

def get_nn_inputs(board, input_type="crashed"):
    encoder = INPUT_ENCODERS.get(input_type)
    if encoder is None:
        raise ValueError(f"Unknown input type: {input_type}")
    return encoder["func"](board)

def register_encoder(name: str, func: Callable, num_inputs: int):
    INPUT_ENCODERS[name] = {
        "func": func,
        "num_inputs": num_inputs
    }