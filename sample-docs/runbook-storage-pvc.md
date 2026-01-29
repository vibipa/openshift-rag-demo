# Runbook: PVC Issues

## PVC Stuck in Pending

### Diagnostic Steps
1. Check PVC status:
```bash
   oc get pvc <pvc-name>
   oc describe pvc <pvc-name>
```

2. Verify StorageClass:
```bash
   oc get storageclass
   oc describe storageclass <storage-class-name>
```

3. Check available PVs:
```bash
   oc get pv | grep Available
```

### Common Issues

**No Available PV**
- Provisioner may be down
- Storage quota exceeded
- No PV matches PVC requirements

**StorageClass Not Found**
- Verify storageClassName in PVC spec
- Check if storageclass exists: `oc get sc`

## Quick Fixes

### Increase PVC Size
```bash
oc patch pvc <pvc-name> -p '{"spec":{"resources":{"requests":{"storage":"10Gi"}}}}'
```