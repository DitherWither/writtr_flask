#!/bin/sh
# Builds the containerfile and starts the podman kube
buildah build -t blog_mgr_flask:latest .
podman kube play blog_mgr_kube.yml