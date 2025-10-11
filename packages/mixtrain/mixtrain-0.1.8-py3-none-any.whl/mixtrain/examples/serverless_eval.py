import time
from dataclasses import dataclass

from mixtrain.client import get_eval_status, start_eval
from pydantic import BaseModel


@dataclass
class InputDataSchema(BaseModel):
    prompt: str
    image_path: str


@dataclass
class OutputDataSchema(BaseModel):
    answer: str

def dummy_eval_func(data: InputDataSchema) -> OutputDataSchema:
    return OutputDataSchema(answer="The answer is 42")

def main():
    id = start_eval(dummy_eval_func, "test_dataset", "1.0.0", 10)
    print(id)
    while True:
        status = get_eval_status(id)
        if status == "completed":
            break
        time.sleep(1)

if __name__ == "__main__":
    main()
