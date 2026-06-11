# Admin Panel Hardware Slot Setup Guide

## Overview
This guide explains how to set up and manage hardware prototype parking slots in the Django admin panel for Arduino Uno integration.

## Accessing the Admin Panel

1. Start the Django development server:
   ```bash
   python manage.py runserver
   ```

2. Navigate to: `http://127.0.0.1:8000/admin/`

3. Login with your superuser credentials

## Setting Up Hardware Slots

### Method 1: Adding Slots Within a Parking Lot (Recommended)

1. **Navigate to Parking Lots**
   - Click on "Parking lots" in the admin panel
   - Select an existing parking lot or create a new one

2. **Add Hardware Slots**
   - Scroll down to the "Parking slots" section (inline form)
   - You'll see 5 empty slot forms by default
   
3. **Configure Each Hardware Slot**
   For each slot (H1, H2, H3, etc.):
   
   | Field | Value | Description |
   |-------|-------|-------------|
   | **Slot number** | `H1`, `H2`, `H3` | The slot number displayed to users |
   | **Vehicle type** | `car`, `bike`, or `ev` | Type of vehicle this slot supports |
   | **Is available** | ✓ (checked) | Whether the slot is currently available |
   | **Is hardware slot** | ✓ (checked) | Mark this to identify it as Arduino-connected |
   | **Hardware slot id** | `H1`, `H2`, `H3` | Arduino identifier (must match Arduino code) |

4. **Example Configuration**
   ```
   Slot 1:
   - Slot number: H1
   - Vehicle type: car
   - Is available: ✓
   - Is hardware slot: ✓
   - Hardware slot id: H1
   
   Slot 2:
   - Slot number: H2
   - Vehicle type: car
   - Is available: ✓
   - Is hardware slot: ✓
   - Hardware slot id: H2
   
   Slot 3:
   - Slot number: H3
   - Vehicle type: bike
   - Is available: ✓
   - Is hardware slot: ✓
   - Hardware slot id: H3
   ```

5. **Save the Parking Lot**
   - Click "Save" or "Save and continue editing"
   - Hardware slots are now ready for Arduino integration

### Method 2: Managing Individual Slots

1. **Navigate to Parking Slots**
   - Click on "Parking slots" in the admin panel
   - You'll see a list of all parking slots

2. **Filter Hardware Slots**
   - Use the right sidebar filters:
     - **Is hardware slot**: Select "Yes" to see only hardware slots
     - **Is available**: Filter by availability status
     - **Lot**: Filter by specific parking lot

3. **Edit or Add Slots**
   - Click on a slot to edit it
   - Or click "Add Parking Slot" to create a new one
   - Set the hardware fields as described in Method 1

## Understanding the List View

When viewing the Parking Slots list, you'll see these columns:

| Column | Description |
|--------|-------------|
| **Slot number** | User-facing slot identifier |
| **Vehicle type** | Type of vehicle supported |
| **Lot** | Which parking lot this slot belongs to |
| **Is available** | Current availability status |
| **Is hardware slot** | ✓ if connected to Arduino |
| **Hardware slot id** | Arduino identifier (H1, H2, H3, etc.) |

## Quick Identification

### Visual Indicators
- Hardware slots will show a **checkmark (✓)** in the "Is hardware slot" column
- The "Hardware slot id" will display the Arduino identifier (H1, H2, H3)
- Regular slots will show an **X** in the "Is hardware slot" column

### Filtering Hardware Slots Only
1. In the Parking Slots list view
2. Look at the right sidebar
3. Under "By Is hardware slot", click **"Yes"**
4. You'll see only Arduino-connected slots

## Arduino Integration Notes

### Hardware Slot ID Requirements
- **Format**: Use simple identifiers like H1, H2, H3
- **Maximum Length**: 10 characters
- **Uniqueness**: Each hardware slot should have a unique ID
- **Case Sensitive**: H1 is different from h1

### Matching with Arduino Code
Your Arduino code should reference these IDs:
```cpp
// Arduino example
if (hardware_slot_id == "H1") {
    // Control servo for slot H1
}
else if (hardware_slot_id == "H2") {
    // Control servo for slot H2
}
```

## Demo Setup Checklist

For a hardware demo with 3 Arduino slots:

- [ ] Access Django admin panel
- [ ] Select or create a parking lot
- [ ] Add 3 parking slots with these details:
  - [ ] Slot H1: is_hardware_slot=✓, hardware_slot_id="H1"
  - [ ] Slot H2: is_hardware_slot=✓, hardware_slot_id="H2"
  - [ ] Slot H3: is_hardware_slot=✓, hardware_slot_id="H3"
- [ ] Save the parking lot
- [ ] Verify slots appear in the Parking Slots list
- [ ] Test filter: Show only hardware slots
- [ ] Configure Arduino with matching IDs (H1, H2, H3)

## Common Tasks

### Temporarily Disable a Hardware Slot
1. Navigate to the slot in admin
2. Uncheck "Is available"
3. Save
4. The slot won't be bookable but remains hardware-enabled

### Convert Regular Slot to Hardware Slot
1. Find the slot in admin
2. Check "Is hardware slot"
3. Enter the "Hardware slot id" (e.g., H4)
4. Save

### Remove Hardware Integration
1. Find the hardware slot in admin
2. Uncheck "Is hardware slot"
3. Clear the "Hardware slot id" field
4. Save

## Troubleshooting

### Hardware slot doesn't show in list
- **Check**: Is "Is hardware slot" checked?
- **Check**: Is the parking lot active?
- **Filter**: Try clearing all filters

### Arduino can't find slot
- **Check**: Hardware slot id matches exactly (case-sensitive)
- **Check**: Slot exists in database
- **Check**: API endpoint is receiving the correct ID

### Can't add more than 5 slots inline
- Save the parking lot first
- Refresh the page
- You'll see 5 more empty slots

## API Integration

For Arduino to communicate with these slots:

```python
# Example API endpoint (to be implemented)
POST /api/hardware/slot-status/
{
    "hardware_slot_id": "H1",
    "is_available": false,
    "occupancy_status": "occupied"
}
```

## Support

For issues or questions:
- Check Django admin logs
- Verify database migrations are applied
- Ensure Arduino is sending correct hardware_slot_id
- Review server logs for API errors

---

**Last Updated**: June 9, 2026  
**Compatible With**: SmartPark v1.0.0+
