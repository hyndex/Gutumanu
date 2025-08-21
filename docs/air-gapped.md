# Air-Gapped Deployment Guide

This guide describes how to maintain offline package repositories and apply patches in air-gapped environments.

## Offline Package Repositories

1. **Mirror upstream packages**
   - For Python dependencies:
     ```bash
     pip download -r requirements.txt --dest /opt/repo/pip
     ```
   - For system packages, create an `apt` mirror:
     ```bash
     apt-mirror /etc/apt/mirror.list
     ```
2. **Transfer the mirror** to the secure network using signed media.
3. **Configure clients** to use the local mirrors by updating `pip.conf` and `sources.list`.

## Patch Workflow

1. **Export patches** from the online development environment:
   ```bash
   git format-patch origin/main
   ```
2. **Verify signatures** on received patches.
3. **Apply patches** inside the air-gapped environment and run tests:
   ```bash
   git am *.patch
   ```
4. **Rebuild containers** using the provided Dockerfile and sign images with offline keys.

## Timestamping

Store build and patch metadata in the audit log and periodically timestamp the log using the provided management command:
```bash
python manage.py timestamp_audit_log --tsa https://freetsa.org/tsr
```
