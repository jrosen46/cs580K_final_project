#!/bin/bash

# old storage files
#kubectl create -f ./storage/storage_class-gce-fast.yaml
#kubectl create -f ./storage/nfs-server-pvc.yaml
#kubectl create -f ./storage/nfs-server-rc.yaml
#kubectl create -f ./storage/nfs-server-service.yaml

# new storage files
kubectl create -f ./storage/fastStorageClass.yaml
kubectl create -f ./storage/claim.yaml
kubectl create -f ./storage/repControl.yaml
kubectl create -f ./storage/service.yaml
