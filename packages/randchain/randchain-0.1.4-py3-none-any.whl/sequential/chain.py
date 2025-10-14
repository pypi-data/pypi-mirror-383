import inspect
from typing import List, Callable

from randchain_core.utils import output_conversion
from randchain_core.config import EmailConfig, Whatsappconfig


class Layer:
    def __init__(
            self,
            func: Callable,
            input_size: int = None,
            output_type: str = None,
            prompt_template: str = None,
            model_id: str = None,
            output_file_path: str = None,
            whatsapp_config: Whatsappconfig = None,
            email_config :  EmailConfig = None,
            **kwargs
    ):
        self.func = func
        self.input_size = input_size
        self.output_type = output_type
        self.prompt_template = prompt_template
        self.model_id = model_id
        self.output_file_path = output_file_path
        self.whatsapp_config = whatsapp_config
        self.email_config = email_config
        self.extra_args = kwargs

    def get_func_args(self):
        sig = inspect.signature(self.func)
        return [p.name for p in sig.parameters.values()]


class Sequential:
    def __init__(self, layers: List[Layer]):
        self.layers = layers

    def run(self, inputs: List):
        function_result = None
        for i, layer in enumerate(self.layers):

            # First layer uses user-provided inputs
            if i == 0:
                args = []
                if layer.prompt_template:
                    args.append(layer.prompt_template)
                if layer.output_file_path:
                    args.append(layer.output_file_path)
                if layer.whatsapp_config:
                    args.append(layer.whatsapp_config)
                if layer.email_config:
                    args.append(layer.email_config)
                if layer.model_id:
                    args.append(layer.model_id)
                args.extend(inputs)

            else:  # Next layers use previous result
                args = []
                if layer.prompt_template:
                    args.append(layer.prompt_template)
                if layer.output_file_path:
                    args.append(layer.output_file_path)
                if layer.whatsapp_config:
                    args.append(layer.whatsapp_config)
                if layer.email_config:
                    args.append(layer.email_config)
                if layer.model_id:
                    args.append(layer.model_id)
                args.append(function_result)
            # Merge with extra keyword arguments provided at init
            output = layer.func(*args, **layer.extra_args)

            # Handle output type conversion
            if layer.output_type:
                function_result = output_conversion(layer.output_type, output, layer.func.__name__)
            else:
                function_result = output

            print(f"[{layer.func.__name__}] -> {function_result}")

        return function_result


