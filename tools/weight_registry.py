# tools/weight_registry.py
"""
Registry mapping DeepfakeBench weight filenames to model configurations.
This enables automatic model selection and input preprocessing based on weight file.
"""

WEIGHT_REGISTRY = {
    "xception_best.pth":   {"model_key": "xception",        "input_size": 299},
    "meso4_best.pth":      {"model_key": "meso4",           "input_size": 256},
    "meso4Incep_best.pth": {"model_key": "meso4Inception",  "input_size": 256},
    "f3net_best.pth":      {"model_key": "f3net",           "input_size": 256},
    "effnb4_best.pth":     {"model_key": "efficientnetb4",  "input_size": 380},
    "capsule_best.pth":    {"model_key": "capsule_net",     "input_size": 128},
    "srm_best.pth":        {"model_key": "srm",             "input_size": 256},
    "recce_best.pth":      {"model_key": "recce",           "input_size": 224},
    "spsl_best.pth":       {"model_key": "spsl",            "input_size": 224},
    "ucf_best.pth":        {"model_key": "ucf",             "input_size": 256},
    "cnnaug_best.pth":     {"model_key": "multi_attention", "input_size": 224},
    "core_best.pth":       {"model_key": "core",            "input_size": 256},
}

