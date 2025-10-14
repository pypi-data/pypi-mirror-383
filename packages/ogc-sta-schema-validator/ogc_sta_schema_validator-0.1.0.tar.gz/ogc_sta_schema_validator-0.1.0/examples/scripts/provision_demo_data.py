#!/usr/bin/env python3
"""
Demo Data Provisioning Script

This script provisions the FROST-Server with sample entities for demonstration purposes.
It creates a complete entity hierarchy following the SensorThings API data model.
"""

import sys
import time
import traceback

import requests


def wait_for_frost_server(base_url: str, max_attempts: int = 30, delay: int = 2):
    """Wait for FROST-Server to be ready."""
    print(f"Waiting for FROST-Server at {base_url}...")

    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(base_url, timeout=5)
            if response.status_code == 200:
                print(f"✓ FROST-Server is ready! (attempt {attempt}/{max_attempts})")
                return True
        except requests.exceptions.RequestException:
            pass

        print(f"  Attempt {attempt}/{max_attempts} - waiting {delay}s...")
        time.sleep(delay)

    print(f"✗ FROST-Server did not become ready after {max_attempts} attempts")
    return False


def create_entity(base_url: str, entity_type: str, entity_data: dict) -> dict:
    """Create an entity in FROST-Server and return the created entity with ID."""
    url = f"{base_url}/{entity_type}"

    try:
        response = requests.post(
            url, json=entity_data, headers={"Content-Type": "application/json"}, timeout=10
        )

        if response.status_code == 201:
            # Get the created entity ID from the response
            # FROST-Server may return the entity in the body or just a Location header
            try:
                if response.text.strip():
                    created_entity = response.json()
                    entity_id = created_entity.get("@iot.id", "unknown")
                else:
                    # Parse ID from Location header
                    location = response.headers.get("Location", "")
                    entity_id = location.split("(")[-1].rstrip(")")
                    created_entity = {"@iot.id": entity_id}
            except Exception as e:
                print(f"  ⚠ Warning: Could not parse response: {e}")
                # Still consider it successful since we got 201
                location = response.headers.get("Location", "")
                entity_id = location.split("(")[-1].rstrip(")") if location else "unknown"
                created_entity = {"@iot.id": entity_id}

            entity_name = entity_data.get("name", entity_data.get("description", entity_id))
            print(f"  ✓ Created {entity_type} '{entity_name}' (ID: {entity_id})")
            return created_entity
        else:
            entity_name = entity_data.get("name", entity_data.get("description", "unknown"))
            print(f"  ✗ Failed to create {entity_type} '{entity_name}': {response.status_code}")
            print(f"     Error: {response.text[:200]}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error creating {entity_type}: {e}")
        return None


def provision_demo_data(base_url: str):  # noqa: PLR0915
    """Provision FROST-Server with demo data following the SensorThings API data model."""
    print("\n" + "=" * 60)
    print("PROVISIONING DEMO DATA")
    print("=" * 60)
    print("\nCreating complete SensorThings API entity hierarchy...")
    print("This includes: Things, Locations, Sensors, ObservedProperties,")
    print("Datastreams, and Observations\n")

    created_count = 0
    failed_count = 0

    # Step 1: Create Things (valid and invalid for custom property validation)
    print("\n1. Creating Things:")
    print("-" * 40)

    thing_valid_data = {
        "name": "Temperature Sensor Station A",
        "description": "Outdoor temperature monitoring station in Building A",
        "properties": {
            "building": "Building A",
            "floor": 1,
            "room": "A123",
            "status": "active",
            "installationDate": "2024-01-15T10:00:00Z",
        },
    }

    thing_valid = create_entity(base_url, "Things", thing_valid_data)
    if thing_valid:
        created_count += 1
    else:
        failed_count += 1

    # Thing with invalid custom properties (for schema validation to catch)
    thing_invalid_data = {
        "name": "Weather Station B",  # Has name so FROST accepts it
        "description": "Indoor monitoring station with invalid properties",
        "properties": {
            "building": 123,  # Should be string
            "floor": "first",  # Should be number
            "status": "unknown_status",  # Invalid enum value
            "installationDate": "not-a-date",  # Invalid date format
        },
    }

    thing_invalid = create_entity(base_url, "Things", thing_invalid_data)
    if thing_invalid:
        created_count += 1
    else:
        failed_count += 1

    # Step 2: Create Locations for Things
    print("\n2. Creating Locations:")
    print("-" * 40)

    if thing_valid:
        location_data = {
            "name": "Building A Rooftop",
            "description": "Rooftop location for weather monitoring",
            "encodingType": "application/vnd.geo+json",
            "location": {"type": "Point", "coordinates": [8.4037, 49.0069]},
            "Things": [{"@iot.id": thing_valid["@iot.id"]}],
        }
        if create_entity(base_url, "Locations", location_data):
            created_count += 1
        else:
            failed_count += 1

    # Step 3: Create Sensors (valid and invalid for custom property validation)
    print("\n3. Creating Sensors:")
    print("-" * 40)

    sensor_valid_data = {
        "name": "DHT22 Temperature Humidity Sensor",
        "description": "Digital temperature and humidity sensor",
        "encodingType": "application/pdf",
        "metadata": "https://www.sparkfun.com/datasheets/Sensors/Temperature/DHT22.pdf",
        "properties": {
            "manufacturer": "Aosong Electronics",
            "model": "DHT22",
            "serialNumber": "DHT22001234",
            "calibrationDate": "2024-01-10T09:00:00Z",
            "status": "operational",
        },
    }

    sensor_valid = create_entity(base_url, "Sensors", sensor_valid_data)
    if sensor_valid:
        created_count += 1
    else:
        failed_count += 1

    # Sensor with invalid custom properties
    sensor_invalid_data = {
        "name": "Faulty Temperature Sensor",  # Has name so FROST accepts it
        "description": "Sensor with invalid property values",
        "encodingType": "application/pdf",
        "metadata": "https://example.com/datasheet.pdf",
        "properties": {
            "manufacturer": 12345,  # Should be string
            "serialNumber": "inv",  # Too short
            "calibrationDate": "invalid-date",  # Invalid date
            "status": "unknown_status",  # Invalid enum
        },
    }

    sensor_invalid = create_entity(base_url, "Sensors", sensor_invalid_data)
    if sensor_invalid:
        created_count += 1
    else:
        failed_count += 1

    # Step 4: Create ObservedProperties
    print("\n4. Creating ObservedProperties:")
    print("-" * 40)

    obs_prop_data = {
        "name": "Temperature",
        "description": "Air temperature measurement",
        "definition": "http://www.qudt.org/qudt/owl/1.0.0/quantity/Instances.html#Temperature",
    }

    obs_prop = create_entity(base_url, "ObservedProperties", obs_prop_data)
    if obs_prop:
        created_count += 1
    else:
        failed_count += 1

    # Step 5: Create Datastreams (valid and invalid for custom property validation)
    print("\n5. Creating Datastreams:")
    print("-" * 40)

    if thing_valid and sensor_valid and obs_prop:
        datastream_valid_data = {
            "name": "Temperature Measurements",
            "description": "Hourly temperature measurements from DHT22 sensor",
            "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement",
            "unitOfMeasurement": {
                "name": "degree Celsius",
                "symbol": "°C",
                "definition": "http://www.qudt.org/qudt/owl/1.0.0/unit/Instances.html#DegreeCelsius",
            },
            "Thing": {"@iot.id": thing_valid["@iot.id"]},
            "Sensor": {"@iot.id": sensor_valid["@iot.id"]},
            "ObservedProperty": {"@iot.id": obs_prop["@iot.id"]},
            "properties": {
                "measurementType": "continuous",
                "dataQuality": "operational",
                "samplingFrequency": "1 hour",
                "processingLevel": "L1",
            },
        }

        datastream_valid = create_entity(base_url, "Datastreams", datastream_valid_data)
        if datastream_valid:
            created_count += 1
        else:
            failed_count += 1
    else:
        datastream_valid = None

    if thing_invalid and sensor_invalid and obs_prop:
        datastream_invalid_data = {
            "name": "Faulty Datastream",  # Has name so FROST accepts it
            "description": "Datastream with invalid property values",
            "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement",
            "unitOfMeasurement": {
                "name": "degree Celsius",
                "symbol": "°C",
                "definition": "http://www.qudt.org/qudt/owl/1.0.0/unit/Instances.html#DegreeCelsius",
            },
            "Thing": {"@iot.id": thing_invalid["@iot.id"]},
            "Sensor": {"@iot.id": sensor_invalid["@iot.id"]},
            "ObservedProperty": {"@iot.id": obs_prop["@iot.id"]},
            "properties": {
                "measurementType": "unknown_type",  # Invalid enum
                "dataQuality": "unknown_quality",  # Invalid enum
                "processingLevel": "L99",  # Invalid value
                "precision": "not-a-number",  # Invalid type
            },
        }

        datastream_invalid = create_entity(base_url, "Datastreams", datastream_invalid_data)
        if datastream_invalid:
            created_count += 1
        else:
            failed_count += 1
    else:
        datastream_invalid = None

    # Step 6: Create Observations (valid and invalid for custom property validation)
    print("\n6. Creating Observations:")
    print("-" * 40)

    if datastream_valid:
        observation_valid_data = {
            "phenomenonTime": "2024-09-22T10:00:00Z",
            "result": 23.5,
            "resultTime": "2024-09-22T10:00:05Z",
            "Datastream": {"@iot.id": datastream_valid["@iot.id"]},
            "parameters": {
                "qualityFlag": "good",
                "uncertainty": 2.5,
                "validationLevel": "validated",
            },
        }

        if create_entity(base_url, "Observations", observation_valid_data):
            created_count += 1
        else:
            failed_count += 1

    if datastream_invalid:
        observation_invalid_data = {
            "phenomenonTime": "2024-09-22T11:00:00Z",  # Required by FROST
            "result": 25.8,
            "resultTime": "2024-09-22T11:00:05Z",
            "Datastream": {"@iot.id": datastream_invalid["@iot.id"]},
            "parameters": {
                "qualityFlag": "invalid_flag",  # Invalid enum
                "uncertainty": 150,  # Out of range
                "validationLevel": "unknown_level",  # Invalid enum
            },
        }

        if create_entity(base_url, "Observations", observation_invalid_data):
            created_count += 1
        else:
            failed_count += 1

    # Summary
    print("\n" + "=" * 60)
    print("PROVISIONING SUMMARY")
    print("=" * 60)
    print(f"  Created: {created_count}")
    print(f"  Failed:  {failed_count}")
    print(f"  Total:   {created_count + failed_count}")

    if failed_count > 0:
        print("\n⚠ Some entities failed to provision.")
    else:
        print("\n✓ All entities provisioned successfully!")

    print("\n" + "=" * 60)
    print("ABOUT THE DEMO DATA")
    print("=" * 60)
    print("The provisioned data includes VALID entities that FROST-Server accepts,")
    print("but some contain INVALID custom properties that will be caught by the")
    print("schema validator. This demonstrates the difference between:")
    print("  • FROST-Server validation (core OGC spec compliance)")
    print("  • Schema validator (organization-specific rules)")
    print("\nLook for validation errors in custom properties like:")
    print("  • Invalid data types (string vs number)")
    print("  • Invalid enum values (status, measurementType, etc.)")
    print("  • Invalid date formats")
    print("  • Out-of-range values\n")


def main():
    """Main entry point."""
    # Configuration
    base_url = "http://frost-server:8080/FROST-Server/v1.1"

    # Wait for FROST-Server to be ready
    if not wait_for_frost_server(base_url):
        sys.exit(1)

    # Give FROST-Server a bit more time to fully initialize
    print("\nWaiting 5 seconds for FROST-Server to fully initialize...")
    time.sleep(5)

    # Provision the demo data
    try:
        provision_demo_data(base_url)
    except Exception as e:
        print(f"\n✗ Provisioning failed: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
