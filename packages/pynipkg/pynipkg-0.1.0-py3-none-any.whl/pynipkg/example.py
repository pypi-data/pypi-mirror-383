from pynipkg.run_commands_utility import run_command_live
from pynipkg.main import build_from_pspec

# build_from_pspec(
#     r"C:\pynipkg\example_package\example_package.pspec",
#     r"C:\pynipkg\example_package"
# )


run_command_live(
    command=[
        "pynipkg",
        "C:\pynipkg\example_package\example_package.pspec",
        'C:\pynipkg\example_package'
    ]
)