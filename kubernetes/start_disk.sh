#!/bin/bash

kubectrl create -f storage_class-gce-fast.yaml
kubectrl create -f nfs-server-pvc.yaml
kubectrl create -f nfs-server-rc.yaml
kubectrl create -f nfs-server-service.yaml
