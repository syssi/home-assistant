"""Provide common Z-Wave JS fixtures."""
import json
from unittest.mock import DEFAULT, patch

import pytest
from zwave_js_server.model.driver import Driver
from zwave_js_server.model.node import Node
from zwave_js_server.version import VersionInfo

from homeassistant.helpers.device_registry import (
    async_get_registry as async_get_device_registry,
)

from tests.common import MockConfigEntry, load_fixture


@pytest.fixture(name="device_registry")
async def device_registry_fixture(hass):
    """Return the device registry."""
    return await async_get_device_registry(hass)


@pytest.fixture(name="controller_state", scope="session")
def controller_state_fixture():
    """Load the controller state fixture data."""
    return json.loads(load_fixture("zwave_js/controller_state.json"))


@pytest.fixture(name="version_state", scope="session")
def version_state_fixture():
    """Load the version state fixture data."""
    return {
        "type": "version",
        "driverVersion": "6.0.0-beta.0",
        "serverVersion": "1.0.0",
        "homeId": 1234567890,
    }


@pytest.fixture(name="multisensor_6_state", scope="session")
def multisensor_6_state_fixture():
    """Load the multisensor 6 node state fixture data."""
    return json.loads(load_fixture("zwave_js/multisensor_6_state.json"))


@pytest.fixture(name="ecolink_door_sensor_state", scope="session")
def ecolink_door_sensor_state_fixture():
    """Load the Ecolink Door/Window Sensor node state fixture data."""
    return json.loads(load_fixture("zwave_js/ecolink_door_sensor_state.json"))


@pytest.fixture(name="hank_binary_switch_state", scope="session")
def binary_switch_state_fixture():
    """Load the hank binary switch node state fixture data."""
    return json.loads(load_fixture("zwave_js/hank_binary_switch_state.json"))


@pytest.fixture(name="bulb_6_multi_color_state", scope="session")
def bulb_6_multi_color_state_fixture():
    """Load the bulb 6 multi-color node state fixture data."""
    return json.loads(load_fixture("zwave_js/bulb_6_multi_color_state.json"))


@pytest.fixture(name="lock_schlage_be469_state", scope="session")
def lock_schlage_be469_state_fixture():
    """Load the schlage lock node state fixture data."""
    return json.loads(load_fixture("zwave_js/lock_schlage_be469_state.json"))


@pytest.fixture(name="client")
def mock_client_fixture(controller_state, version_state):
    """Mock a client."""
    with patch(
        "homeassistant.components.zwave_js.ZwaveClient", autospec=True
    ) as client_class:
        driver = Driver(client_class.return_value, controller_state)
        version = VersionInfo.from_message(version_state)
        client_class.return_value.driver = driver
        client_class.return_value.version = version
        client_class.return_value.ws_server_url = "ws://test:3000/zjs"
        client_class.return_value.state = "connected"
        yield client_class.return_value


@pytest.fixture(name="multisensor_6")
def multisensor_6_fixture(client, multisensor_6_state):
    """Mock a multisensor 6 node."""
    node = Node(client, multisensor_6_state)
    client.driver.controller.nodes[node.node_id] = node
    return node


@pytest.fixture(name="ecolink_door_sensor")
def legacy_binary_sensor_fixture(client, ecolink_door_sensor_state):
    """Mock a legacy_binary_sensor node."""
    node = Node(client, ecolink_door_sensor_state)
    client.driver.controller.nodes[node.node_id] = node
    return node


@pytest.fixture(name="hank_binary_switch")
def hank_binary_switch_fixture(client, hank_binary_switch_state):
    """Mock a binary switch node."""
    node = Node(client, hank_binary_switch_state)
    client.driver.controller.nodes[node.node_id] = node
    return node


@pytest.fixture(name="bulb_6_multi_color")
def bulb_6_multi_color_fixture(client, bulb_6_multi_color_state):
    """Mock a bulb 6 multi-color node."""
    node = Node(client, bulb_6_multi_color_state)
    client.driver.controller.nodes[node.node_id] = node
    return node


@pytest.fixture(name="lock_schlage_be469")
def lock_schlage_be469_fixture(client, lock_schlage_be469_state):
    """Mock a schlage lock node."""
    node = Node(client, lock_schlage_be469_state)
    client.driver.controller.nodes[node.node_id] = node
    return node


@pytest.fixture(name="integration")
async def integration_fixture(hass, client):
    """Set up the zwave_js integration."""
    entry = MockConfigEntry(domain="zwave_js", data={"url": "ws://test.org"})
    entry.add_to_hass(hass)

    def initialize_client(async_on_initialized):
        """Init the client."""
        hass.async_create_task(async_on_initialized())
        return DEFAULT

    client.register_on_initialized.side_effect = initialize_client

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    return entry
