# Nostradamus IoTO SDK Examples

This directory contains example scripts demonstrating various features of the Nostradamus IoTO Python SDK.

## Prerequisites

1. **Install the SDK**:
   ```bash
   pip install nostradamus-ioto-sdk
   # Or from source:
   pip install -e .
   ```

2. **Set up authentication**:
   ```bash
   export NOSTRADAMUS_API_KEY="your-api-key-here"
   ```

## Examples

### Getting Started

| Example | Domain | Description |
|---------|--------|-------------|
| `basic_usage.py` | General | Fundamental SDK operations (CRUD, data send/query) |
| `async_usage.py` | General | Async client with concurrent operations |
| `data_ingestion.py` | General | Sensor data ingestion patterns (individual, batch, continuous) |
| `soil_monitoring_example.py` | Agriculture | Complete workflow matching official API demo ⭐ |

### Real-World Domain Examples

All domain examples follow the same 6-step workflow: create collection → send data → query with filters → statistics → delete → cleanup. They require the same environment variables:

```bash
export NOSTRADAMUS_PROJECT_ID="your-project-id"
export NOSTRADAMUS_MASTER_KEY="your-master-key"
export NOSTRADAMUS_WRITE_KEY="your-write-key"
export NOSTRADAMUS_READ_KEY="your-read-key"
```

#### 🌾 Agriculture

| Example | Scenario | Sensors | Data Points |
|---------|----------|---------|-------------|
| `agriculture/precision_farming.py` | Multi-zone crop monitoring | Soil moisture, NDVI, leaf wetness, wind, rainfall | 4 zones × 24h |
| `agriculture/greenhouse_automation.py` | Greenhouse climate control | Air temp, CO2, PAR light, VPD, vent/heating/irrigation actuators | 3 zones × 48 readings |
| `agriculture/livestock_tracking.py` | Cattle health & GPS tracking | Body temp, heart rate, rumination, activity, GPS coordinates | 5 animals × 24h |

**Agriculture query highlights:**
- Drought stress detection (low moisture + high temp)
- Disease risk filtering (high leaf wetness + humidity)
- Fever detection (body temp > 39.5°C)
- Heat stress alerts (ambient > 30°C + high heart rate)

#### 🏙️ Smart City

| Example | Scenario | Sensors | Data Points |
|---------|----------|---------|-------------|
| `smart_city/air_quality_monitoring.py` | Urban air quality network | PM2.5, PM10, NO2, O3, CO, SO2, AQI | 4 stations × 48 readings |

Station-specific pollution profiles (industrial, downtown, highway, park) with rush-hour traffic effects.

#### ⚡ Smart Energy

| Example | Scenario | Sensors | Data Points |
|---------|----------|---------|-------------|
| `smart_energy/microgrid_monitoring.py` | Solar/wind/battery microgrid | Power output, voltage, efficiency, SOC, irradiance | 4 assets × 48 readings |

Realistic day/night solar curves, wind gusts, and battery charge/discharge cycles.

#### 🚛 Smart Transportation

| Example | Scenario | Sensors | Data Points |
|---------|----------|---------|-------------|
| `smart_transportation/fleet_management.py` | Vehicle fleet telemetry | GPS, speed, fuel, engine diagnostics, driver behavior | 5 vehicles × 24h |

Vehicle-type-specific profiles (trucks, vans, buses) with speeding and overheating detection.

#### 🤖 Cyber-Physical Systems

| Example | Scenario | Sensors | Data Points |
|---------|----------|---------|-------------|
| `cyber_physical/robot_fleet_monitoring.py` | Warehouse robot fleet | Position, velocity, battery, LiDAR, task status, CPU | 5 robots × 24h |

Mixed robot types (AGVs, robotic arms, inspection drones) with error detection and performance bottleneck filtering.

---

### Running Examples

```bash
# General examples (API key only)
python examples/basic_usage.py
python examples/async_usage.py
python examples/data_ingestion.py

# Domain examples (require project + multi-key auth)
python examples/soil_monitoring_example.py
python examples/agriculture/precision_farming.py
python examples/agriculture/greenhouse_automation.py
python examples/agriculture/livestock_tracking.py
python examples/smart_city/air_quality_monitoring.py
python examples/smart_energy/microgrid_monitoring.py
python examples/smart_transportation/fleet_management.py
python examples/cyber_physical/robot_fleet_monitoring.py
```

## Tips

### Batch Operations

When sending multiple data points, use batch operations for better performance:

```python
# Instead of this:
for data_point in data_points:
    client.data.send(project_id, collection_id, data_point)

# Do this:
client.data.send(project_id, collection_id, data_points)
```

### Error Handling

Always handle potential errors:

```python
from nostradamus_ioto_sdk.exceptions import (
    AuthenticationError,
    ResourceNotFoundError,
    ValidationError,
)

try:
    project = client.projects.get(project_id)
except ResourceNotFoundError:
    print("Project not found")
except AuthenticationError:
    print("Invalid credentials")
```

### Context Managers

Use context managers to ensure proper cleanup:

```python
with NostradamusClient(api_key=api_key) as client:
    # Your code here
    pass
# Client automatically closed
```

### Async Operations

For high-throughput scenarios, use the async client:

```python
import asyncio
from nostradamus_ioto_sdk import AsyncNostradamusClient

async def main():
    async with AsyncNostradamusClient(api_key=api_key) as client:
        # Concurrent operations
        results = await asyncio.gather(
            client.projects.alist(),
            client.organizations.aget(),
        )

asyncio.run(main())
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NOSTRADAMUS_API_KEY` | Your API key | Yes (if not using OAuth2) |
| `NOSTRADAMUS_USERNAME` | OAuth2 username | Yes (if not using API key) |
| `NOSTRADAMUS_PASSWORD` | OAuth2 password | Yes (if not using API key) |

## Need Help?

- Check the main [README.md](../README.md)
- Read the [documentation](https://nostradamus-ioto-sdk.readthedocs.io/)
- Open an issue on [GitHub](https://github.com/yourusername/nostradamus-ioto-sdk/issues)
