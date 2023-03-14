# Calibration of direct laser writing systems

Note: If you want to use this procedure, first check
the [scribe-calibration-data](https://github.com/psl-uillinois/scribe-calibration-data) repository to see if someone
else has already measured calibration data for your system.
If so, you can download the ``calibration_data`` folder and ``index.txt``
file, placing them in the top directory of this repository.
This will allow you to skip steps 1-6, which are fairly
time consuming (~20 hours).

Calibration Procedure: 

1. Fabricate calibration devices.
2. Measure calibration devices.
3. Calculate calibration curves.
4. Fabricate prisms.
5. Measure prisms.
6. Calculate refractive index function.

    After this initial procedure, the necessary data for calibration has been computed,
and designs for optical elements may be calibrated and fabricated.

    Operating Procedure:

7. Design a refractive index profile, analogous to those in the ``example_devices``
folder. This profile can either be 2D (and specify the thickness) or be 3D.
8. Use the helper function in ``calibration_utility.py`` to convert the
refractive index profile to a fluorescence intensity target profile.
9. Store the resulting intensity profile in a ``Device``
(defined in ``device_data.py``) and save it as a pickled file
in the ``device_input`` directory.
10. Check/modify the settings in ``calibration_settings.py``.
11. Run ``run_calibrate_device.py``. By default, it will multithread and use
the maximum number of cores to generate the calibrated files as fast as possible.
12. Copy the GWL files from ``device_input`` to ``source_gwl/device``.
13. Check/modify the settings at the top of ``assemble_master_file.py``.
14. Run ``assemble_master_file.py``.
15. Copy the entire ``source_gwl`` directory to the cloud or a USB drive.
Copy it onto the Nanoscribe computer, and load ``MasterFile.gwl`` as the job.
16. (Optional) Wait until the laser has reached a stable state.
17. Run the job.