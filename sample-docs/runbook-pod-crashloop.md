# Runbook: Pod CrashLoopBackOff Troubleshooting

## Common Causes

### Exit Code 137 (OOMKilled)
**Symptom:** Pod killed due to out of memory

**Solution:**
1. Check current memory limits: `oc describe pod <pod-name>`
2. Review memory usage: `oc top pod <pod-name>`
3. Increase memory limit:
```bash
   oc set resources deployment/<name> --limits=memory=1Gi
```

### Exit Code 1 (Application Error)
**Symptom:** Application fails to start

**Solution:**
1. Check logs: `oc logs <pod-name> --previous`
2. Verify environment variables
3. Check ConfigMap and Secret references

## Quick Commands
```bash
oc get pod <pod-name> -o yaml
oc get events --sort-by='.lastTimestamp'
oc logs <pod-name> --tail=50
oc describe pod <pod-name>
```