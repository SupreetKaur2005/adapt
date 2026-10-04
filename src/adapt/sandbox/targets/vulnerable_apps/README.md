# vulnerable_apps/

Seeded-vulnerability target applications (deliberately flawed web apps/services)
for Red Team to attack outside the AD-specific scenarios. Each subdirectory here
should be a self-contained, seeded-CVE target (e.g. a vulnerable web app with a
known injection point) that `container_manager.py` can build and run.
