from pathlib import Path

from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class ToucanConfig:
    """
    Class to define the mandatory fields in the config.yml files.

    :param alice: The emulator for Alice
    :param bob: The emulator for Bob
    :param use_snapshots: If True, saves snapshots after starting the emulators
    :param debug_snapshot_name: The name of the snapshots of the emulators
    :param wait_time: The maximum number of seconds to wait for booting of the emulators
    :param result_path: The path to the result folder, to which results and logs are written
    """

    alice: str
    bob: str
    use_snapshots: bool
    debug_snapshot_name: str
    wait_time: int
    result_path: Path
