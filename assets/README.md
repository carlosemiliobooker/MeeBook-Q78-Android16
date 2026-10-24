# Calibration assets

These files are **included in the repository**:

- `q78-input-manager-state.xml`: human-readable copy of the exact working calibration.
- `q78-input-manager-state.abx`: 322-byte Android Binary XML rendition, generated from the XML using the included `scripts/build-abx.py`.
- `q78-calibration-seed.rc`: Android init instructions used successfully for the Android 16 boot.

The affine calibration descriptor and matrix are specific to the tested MeeBook Q78 hardware:

- Descriptor: `a1cc21cba608c55d28d6dd2b1939004df0e0c756`
- Display: 1404 × 1872
- Rotation: `0`
- Coefficients: `0, 1.3333333, 0, -0.75, 0, 1404`

ABX was reconstructed using the AOSP serialization format and matches the measured 322-byte length of the original exported binary. **It has not been byte-for-byte compared to the user's extracted original ABX**, which is not present in this repository. The *calibration contents and boot-time copy strategy* are proven in the Q78 Android 16 DSU and permanent installation.
