"""Module providing __init__ functionality."""


from matrice_common.utils import dependencies_check

dependencies_check(["docker", "psutil", "cryptography", "notebook", "aiohttp", "kafka-python"])
from matrice_compute.instance_manager import InstanceManager  # noqa: E402

__all__ = ["InstanceManager"]
