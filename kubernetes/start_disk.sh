#!/bin/bash

# old storage files
#kubectrl create -f ./storage/storage_class-gce-fast.yaml
#kubectrl create -f ./storage/nfs-server-pvc.yaml
#kubectrl create -f ./storage/nfs-server-rc.yaml
#kubectrl create -f ./storage/nfs-server-service.yaml

# new storage files
kubectrl create -f ./storage/fastStorageClass.yaml
kubectrl create -f ./storage/claim.yaml
kubectrl create -f ./storage/repControl.yaml
kubectrl create -f ./storage/service.yaml
