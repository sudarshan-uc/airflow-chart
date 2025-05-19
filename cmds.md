# Validation commands

```bash
helm template -f values-git-sync.yaml release-name . --set authSidecar.enabled=true --set dagDeploy.enabled=true --set gitSyncRelay.enabled=true --set ingress.enabled=true --set loggingSidecar.enabled=true --set sccEnabled=true > all.yaml
python validate.py all.yaml
```