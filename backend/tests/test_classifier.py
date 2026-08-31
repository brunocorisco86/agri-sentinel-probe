import pytest
from app.services.classifier import classify_device_state, STATE_ONLINE, STATE_LAN_FAILURE, STATE_WAN_TIMEOUT

def test_classify_online_wan_only():
    status, desc = classify_device_state(is_alive=True, local_target_enabled=False, local_target_online=False)
    assert status == STATE_ONLINE

def test_classify_online_with_lan():
    status, desc = classify_device_state(is_alive=True, local_target_enabled=True, local_target_online=True)
    assert status == STATE_ONLINE

def test_classify_lan_failure():
    status, desc = classify_device_state(is_alive=True, local_target_enabled=True, local_target_online=False)
    assert status == STATE_LAN_FAILURE
    assert "Gateway Dragino" in desc

def test_classify_wan_timeout():
    status, desc = classify_device_state(is_alive=False, local_target_enabled=True, local_target_online=True)
    assert status == STATE_WAN_TIMEOUT
