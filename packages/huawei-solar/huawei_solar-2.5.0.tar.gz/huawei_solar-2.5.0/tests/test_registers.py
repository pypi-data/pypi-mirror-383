import huawei_solar.register_names as rn
from huawei_solar.registers import REGISTERS, PeakSettingPeriod


def test_capacity_control_register():
    value = [
        PeakSettingPeriod(0, 1439, 2551, (True, True, True, True, True, True, False)),
        PeakSettingPeriod(
            0,
            200,
            2550,
            (False, False, False, False, False, False, True),
        ),
        PeakSettingPeriod(
            200,
            1439,
            2449,
            (False, False, False, False, False, False, True),
        ),
    ]

    pspr = REGISTERS[rn.STORAGE_CAPACITY_CONTROL_PERIODS]

    payload = pspr.encode(value)

    decoded_result = pspr.decode(payload)

    assert decoded_result == value
