from typing import Dict

from bluer_objects.README.consts import assets2

from bluer_sandbox.README.consts import ai4k_assets2

dict_of_experiments: Dict[str, Dict] = {
    "caliper": {
        "marquee": f"{ai4k_assets2}/20251009_114411.jpg",
        "description": [
            "mechanical calipers",
            "digital calipers",
            "safety precautions",
            "measure the thickness of hair, paper, finger (what's wrong?)",
            "measure the different sides of a spoon, what else?",
            "what else?",
        ],
    },
    "multimeter": {
        "marquee": f"{ai4k_assets2}/20250616_112027.jpg",
        "description": [
            "measure the voltage of batteries, AC, battery-bus w/ different lights + on charger, what else?",
            "measure the resistance of water, metal, what else?",
            "what else?",
        ],
    },
    "ultrasonic": {
        "marquee": f"{assets2}/ultrasonic-sensor-tester/00.jpg?raw=true",
        "description": [
            "watching the film [Here's What Bat Echolocation Sounds Like, Slowed Down](https://youtu.be/qJOloliWvB8?si=_lzHkcyTP0B1S7Ba).",
            "work with the [ultrasonic sensor tester](https://github.com/kamangir/bluer-sbc/blob/main/bluer_sbc/docs/ultrasonic-sensor-tester.md), make sense of how it works, measure with one sensor.",
            "drive [arzhang](https://github.com/kamangir/bluer-ugv/tree/main/bluer_ugv/docs/arzhang) and measure how far from an obstacle it stops.",
        ],
        "items": {
            f"{assets2}/arzhang/20251005_112250.jpg?raw=true": "",
            f"{assets2}/arzhang/VID-20250830-WA0000~3_1.gif?raw=true": "",
            f"{assets2}/arzhang/VID-20250830-WA0000~3_1.gif?raw=true": "",
        },
        "cols": 2,
    },
    "robin": {
        "marquee": f"{assets2}/robin/20250807_103534.jpg?raw=true",
        "description": [
            "what is [robin](https://github.com/kamangir/bluer-ugv/tree/main/bluer_ugv/docs/robin)?",
            "what technologies make robin work?",
            "drive robin",
            "what are robin's shortcomings and how can we make it better?",
        ],
        "items": {
            f"{assets2}/robin/20250728_112123.jpg?raw=true": "",
            f"{assets2}/robin/20250723_095022.jpg?raw=true": "",
            f"{assets2}/robin/20250723_095155~2_1.gif?raw=true": "",
        },
        "cols": 2,
    },
    "template": {
        "marquee": "template",
        "description": [
            "",
        ],
    },
}
