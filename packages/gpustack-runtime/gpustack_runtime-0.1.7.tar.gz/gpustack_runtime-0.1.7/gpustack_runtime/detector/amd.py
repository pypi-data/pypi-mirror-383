from __future__ import annotations

import contextlib
import logging
from functools import lru_cache

from .. import envs
from . import pyamdgpu, pyamdsmi, pyrocmsmi
from .__types__ import Detector, Device, Devices, ManufacturerEnum
from .__utils__ import PCIDevice, get_device_files, get_pci_devices

logger = logging.getLogger(__name__)


class AMDDetector(Detector):
    """
    Detect AMD GPUs.
    """

    @staticmethod
    @lru_cache
    def is_supported() -> bool:
        """
        Check if the AMD detector is supported.

        Returns:
            True if supported, False otherwise.

        """
        supported = False
        if envs.GPUSTACK_RUNTIME_DETECT.lower() not in ("auto", "amd"):
            logger.debug("AMD detection is disabled by environment variable")
            return supported

        pci_devs = AMDDetector.detect_pci_devices()
        if not pci_devs:
            logger.debug("No AMD PCI devices found")
            return supported

        try:
            pyamdsmi.amdsmi_init()
            pyamdsmi.amdsmi_shut_down()
            supported = True
        except pyamdsmi.AmdSmiException:
            if logger.isEnabledFor(logging.DEBUG):
                logger.exception("Failed to initialize AMD SMI")

        return supported

    @staticmethod
    @lru_cache
    def detect_pci_devices() -> dict[str, PCIDevice] | None:
        # See https://pcisig.com/membership/member-companies?combine=AMD.
        pci_devs = get_pci_devices(vendor="0x1002")
        if not pci_devs:
            return None
        return {dev.address: dev for dev in pci_devs}

    def __init__(self):
        super().__init__(ManufacturerEnum.AMD)

    def detect(self) -> Devices | None:
        """
        Detect AMD GPUs using pyamdsmi, pyamdgpu and pyrocmsmi.

        Returns:
            A list of detected AMD GPU devices,
            or None if not supported.

        Raises:
            If there is an error during detection.

        """
        if not self.is_supported():
            return None

        ret: Devices = []

        try:
            pyamdsmi.amdsmi_init()

            sys_runtime_ver = pyamdsmi.amdsmi_get_rocm_version_major_minor()
            sys_runtime_ver_t = (
                [int(v) if v.isdigit() else v for v in sys_runtime_ver.split(".")]
                if sys_runtime_ver
                else None
            )

            devs = pyamdsmi.amdsmi_get_processor_handles()
            dev_files = get_device_files(
                pattern=r"card(?P<number>\d+)",
                directory="/dev/dri",
            )
            for dev_idx, dev in enumerate(devs):
                dev_card = None
                dev_index = dev_idx
                if len(dev_files) > dev_idx:
                    dev_file = dev_files[dev_idx]
                    if dev_file.number is not None:
                        dev_card = dev_file.number
                        if envs.GPUSTACK_RUNTIME_DETECT_PHYSICAL_INDEX_PRIORITY:
                            dev_index = (
                                dev_file.number - 1 if dev_file.number > 0 else 0
                            )

                dev_gpudev_info = None
                if dev_card is not None:
                    with contextlib.suppress(pyamdgpu.AMDGPUError):
                        _, _, dev_gpudev = pyamdgpu.amdgpu_device_initialize(dev_card)
                        dev_gpudev_info = pyamdgpu.amdgpu_query_gpu_info(dev_gpudev)
                        pyamdgpu.amdgpu_device_deinitialize(dev_gpudev)

                dev_gpu_driver_info = pyamdsmi.amdsmi_get_gpu_driver_info(dev)
                dev_driver_ver = dev_gpu_driver_info.get("driver_version")
                dev_driver_ver_t = (
                    [int(v) if v.isdigit() else v for v in dev_driver_ver.split(".")]
                    if dev_driver_ver
                    else None
                )

                dev_gpu_asic_info = pyamdsmi.amdsmi_get_gpu_asic_info(dev)
                dev_uuid = dev_gpu_asic_info.get("asic_serial")
                dev_name = "AMD " + dev_gpu_asic_info.get("market_name")
                dev_cc = None
                dev_cc_t = None
                if hasattr(dev_gpu_asic_info, "target_graphics_version"):
                    dev_cc = dev_gpu_asic_info.target_graphics_version
                else:
                    with contextlib.suppress(pyrocmsmi.ROCMSMIError):
                        pyrocmsmi.rsmi_init()
                        dev_cc = pyrocmsmi.rsmi_dev_target_graphics_version_get(dev_idx)
                if dev_cc:
                    dev_cc = dev_cc[3:]  # Strip "gfx" prefix
                    dev_cc_t = [int(v) if v.isdigit() else v for v in dev_cc.split(".")]

                dev_gpu_metrics_info = pyamdsmi.amdsmi_get_gpu_metrics_info(dev)
                dev_cores = (
                    dev_gpudev_info.cu_active_number if dev_gpudev_info else None
                )
                dev_cores_util = dev_gpu_metrics_info.get("average_gfx_activity", 0)
                dev_gpu_vram_usage = pyamdsmi.amdsmi_get_gpu_vram_usage(dev)
                dev_mem = dev_gpu_vram_usage.get("vram_total")
                dev_mem_used = dev_gpu_vram_usage.get("vram_used")
                dev_temp = dev_gpu_metrics_info.get("temperature_hotspot", 0)

                dev_power_info = pyamdsmi.amdsmi_get_power_info(dev)
                dev_power = dev_power_info.get("power_limit", 0) // 1000000  # uW to W
                dev_power_used = (
                    dev_power_info.get("current_socket_power")
                    if dev_power_info.get("current_socket_power", "N/A") != "N/A"
                    else dev_power_info.get("average_socket_power", 0)
                )

                dev_compute_partition = None
                with contextlib.suppress(pyamdsmi.AmdSmiException):
                    dev_compute_partition = pyamdsmi.amdsmi_get_gpu_compute_partition(
                        dev,
                    )

                dev_appendix = {
                    "arch_family": _get_arch_family(dev_gpudev_info),
                    "vgpu": dev_compute_partition is not None,
                }

                ret.append(
                    Device(
                        manufacturer=self.manufacturer,
                        index=dev_index,
                        name=dev_name,
                        uuid=dev_uuid,
                        driver_version=dev_driver_ver,
                        driver_version_tuple=dev_driver_ver_t,
                        runtime_version=sys_runtime_ver,
                        runtime_version_tuple=sys_runtime_ver_t,
                        compute_capability=dev_cc,
                        compute_capability_tuple=dev_cc_t,
                        cores=dev_cores,
                        cores_utilization=dev_cores_util,
                        memory=dev_mem,
                        memory_used=dev_mem_used,
                        memory_utilization=(
                            (dev_mem_used * 100 // dev_mem) if dev_mem > 0 else 0
                        ),
                        temperature=dev_temp,
                        power=dev_power,
                        power_used=dev_power_used,
                        appendix=dev_appendix,
                    ),
                )
        except pyamdsmi.AmdSmiException:
            if logger.isEnabledFor(logging.DEBUG):
                logger.exception("Failed to fetch devices")
            raise
        except Exception:
            if logger.isEnabledFor(logging.DEBUG):
                logger.exception("Failed to process devices fetching")
            raise
        finally:
            pyamdsmi.amdsmi_shut_down()

        return ret


def _get_arch_family(
    dev_gpudev_info: pyamdgpu.c_amdgpu_gpu_info | None,
) -> str | None:
    if not dev_gpudev_info:
        return None

    family_id = dev_gpudev_info.family_id
    if family_id is None:
        return None

    arch_family = {
        pyamdgpu.AMDGPU_FAMILY_SI: "Southern Islands",
        pyamdgpu.AMDGPU_FAMILY_CI: "Sea Islands",
        pyamdgpu.AMDGPU_FAMILY_KV: "Kaveri",
        pyamdgpu.AMDGPU_FAMILY_VI: "Volcanic Islands",
        pyamdgpu.AMDGPU_FAMILY_CZ: "Carrizo",
        pyamdgpu.AMDGPU_FAMILY_AI: "Arctic Islands",
        pyamdgpu.AMDGPU_FAMILY_RV: "Raven",
        pyamdgpu.AMDGPU_FAMILY_NV: "Navi",
        pyamdgpu.AMDGPU_FAMILY_VGH: "Van Gogh",
        pyamdgpu.AMDGPU_FAMILY_GC_11_0_0: "GC 11.0.0",
        pyamdgpu.AMDGPU_FAMILY_YC: "Yellow Carp",
        pyamdgpu.AMDGPU_FAMILY_GC_11_0_1: "GC 11.0.1",
        pyamdgpu.AMDGPU_FAMILY_GC_10_3_6: "GC 10.3.6",
        pyamdgpu.AMDGPU_FAMILY_GC_10_3_7: "GC 10.3.7",
        pyamdgpu.AMDGPU_FAMILY_GC_11_5_0: "GC 11.5.0",
        pyamdgpu.AMDGPU_FAMILY_GC_12_0_0: "GC 12.0.0",
    }

    return arch_family.get(family_id, "Unknown")
