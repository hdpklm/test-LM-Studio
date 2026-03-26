# Implementation Plan - UART Debug Protocol Update

The goal is to update the communication protocol between the MCU and Python to match the specification in [project_status.md](file:///c:/Users/Hassan/e2_studio/workspace.4.5/CEN01H_Beta_Modules/project_status.md). This includes switching to a 2-byte CRC16-CCITT checksum, implementing a Key-Value data structure, and using Little-Endian (native MCU order) for performance.

## Proposed Changes

### [MCU] Protocol Definition and Handler

#### [MODIFY] [lut_protocol.h](file:///c:/Users/Hassan/e2_studio/workspace.4.5/CEN01H_Beta_Modules/src/unit-test/lut_protocol.h)
- Update `e_lut_id` to match the new ID list (0-16, 30).
- Define `e_lut_key` constants for the pre-defined keys (1-6).
- Remove old `e_lut_key_read` and `e_lut_key_write` if they are redundant with the new Key-Value system.
- Add CRC16-CCITT calculation macro or function prototype.

#### [MODIFY] [lut_protocol_handler.cpp](file:///c:/Users/Hassan/e2_studio/workspace.4.5/CEN01H_Beta_Modules/src/unit-test/lut_protocol_handler.cpp)
- Implement `uint16_t crc16_ccitt(const uint8_t* data, uint16_t length)`.
- Update [send_packet](file:///c:/Users/Hassan/e2_studio/workspace.4.5/CEN01H_Beta_Modules/tools/unit-test/main.py#58-68) to use the new 2-byte CRC16 and Little-Endian `index`.
- Update [lut_protocol_loop](file:///c:/Users/Hassan/e2_studio/workspace.4.5/CEN01H_Beta_Modules/src/unit-test/lut_protocol_handler.cpp#134-206) to:
    - Search for the new header format.
    - Validate using CRC16-CCITT.
    - Parse the Key-Value data structure.
- Update [handle_packet](file:///c:/Users/Hassan/e2_studio/workspace.4.5/CEN01H_Beta_Modules/src/unit-test/lut_protocol_handler.cpp#95-133) to process multiple Key-Value pairs.

### [Python] Unit Test Bridge

#### [MODIFY] [main.py](file:///c:/Users/Hassan/e2_studio/workspace.4.5/CEN01H_Beta_Modules/tools/unit-test/main.py)
- Expand `self.machine_state` to include detailed status, sensor values, and flags.
- Implement [log_error(msg, critical=False)](file:///c:/Users/Hassan/e2_studio/workspace.4.5/CEN01H_Beta_Modules/tools/unit-test/main.py#40-47) to track validation failures.
- Add [wait_for_condition(cond_func, timeout=5.0)](file:///c:/Users/Hassan/e2_studio/workspace.4.5/CEN01H_Beta_Modules/tools/unit-test/main.py#48-57) helper for callbacks.
- Pass the bridge instance to `TICKS` callbacks as the second argument.
- Add an abort mechanism that stops playback and prints an error summary.

#### [MODIFY] [mock_1.py](file:///c:/Users/Hassan/e2_studio/workspace.4.5/CEN01H_Beta_Modules/tools/unit-test/mock_1.py)
- Update/add example callbacks (`fn`) that use the bridge state to verify MCU response.
- Example: [wait_for_condition(lambda b: b.machine_state['state'] == 0x34, timeout=2.0)](file:///c:/Users/Hassan/e2_studio/workspace.4.5/CEN01H_Beta_Modules/tools/unit-test/main.py#48-57).

### [Documentation] Timing and Units

#### [MODIFY] [project_status.md](file:///c:/Users/Hassan/e2_studio/workspace.4.5/CEN01H_Beta_Modules/project_status.md)
- Update documentation to reflect that `delta_ms` is now in **milliseconds** (changed from seconds).

### [Python] Sensor Reader

#### [MODIFY] [sensor_reader.py](file:///c:/Users/Hassan/e2_studio/workspace.4.5/CEN01H_Beta_Modules/tools/unit-test/sensor-reader/sensor_reader.py)
- Consolidate all captured data into a single `mock_{timestamp}.py` file using the `All` category.
- Save files directly in `reads/` without an additional timestamp subdirectory.
- Maintain the standardized `TICKS` Python format.

#### [MODIFY] [project_status.md](file:///c:/Users/Hassan/e2_studio/workspace.4.5/CEN01H_Beta_Modules/project_status.md)
- Ensure the documentation reflects the new path: `tools/unit-test/sensor-reader/reads/mock_{index}.py`.

## Verification Plan
...
...
...

### Manual Verification
1.  **State Mirroring**: Run [main.py](file:///c:/Users/Hassan/e2_studio/workspace.4.5/CEN01H_Beta_Modules/tools/unit-test/main.py) and verify [machine_state](file:///c:/Users/Hassan/e2_studio/workspace.4.5/CEN01H_Beta_Modules/src/unit-test/lut_protocol_handler.cpp#79-82) accurately reflects MCU updates.
2.  **Validation Callbacks**: Trigger a state change in the MCU and verify a callback in [mock_1.py](file:///c:/Users/Hassan/e2_studio/workspace.4.5/CEN01H_Beta_Modules/tools/unit-test/mock_1.py) can detect it and log success/error.
3.  **Abort Flow**: Force a critical error and verify the test aborts and shows the summary.
