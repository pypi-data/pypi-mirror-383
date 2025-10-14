"""Kubernetes client initialization and helpers."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from kubernetes import client, config
from kubernetes.client import ApiClient
from kubernetes.config.config_exception import ConfigException

logger = logging.getLogger(__name__)


class K8sClientManager:
    """Manages Kubernetes API client initialization and configuration."""

    def __init__(self, in_cluster: bool = False, kubeconfig_path: Optional[str] = None):
        """Initialize K8s client manager.

        Args:
            in_cluster: Whether to use in-cluster configuration
            kubeconfig_path: Path to kubeconfig file (if not in-cluster)
        """
        self.in_cluster = in_cluster
        self.kubeconfig_path = kubeconfig_path
        self._api_client: Optional[ApiClient] = None
        self._core_v1_api: Optional[client.CoreV1Api] = None
        self._apps_v1_api: Optional[client.AppsV1Api] = None
        self._batch_v1_api: Optional[client.BatchV1Api] = None

    def initialize(self) -> None:
        """Initialize Kubernetes configuration."""
        try:
            if self.in_cluster:
                config.load_incluster_config()
                logger.info("Loaded in-cluster Kubernetes configuration")
            else:
                config.load_kube_config(config_file=self.kubeconfig_path)
                logger.info(f"Loaded kubeconfig from {self.kubeconfig_path or 'default location'}")
        except ConfigException as e:
            logger.error(f"Failed to load Kubernetes configuration: {e}")
            raise

    @property
    def api_client(self) -> ApiClient:
        """Get or create API client."""
        if self._api_client is None:
            self._api_client = ApiClient()
        return self._api_client

    @property
    def core_v1_api(self) -> client.CoreV1Api:
        """Get or create CoreV1Api client."""
        if self._core_v1_api is None:
            self._core_v1_api = client.CoreV1Api()
        return self._core_v1_api

    @property
    def apps_v1_api(self) -> client.AppsV1Api:
        """Get or create AppsV1Api client."""
        if self._apps_v1_api is None:
            self._apps_v1_api = client.AppsV1Api()
        return self._apps_v1_api

    @property
    def batch_v1_api(self) -> client.BatchV1Api:
        """Get or create BatchV1Api client."""
        if self._batch_v1_api is None:
            self._batch_v1_api = client.BatchV1Api()
        return self._batch_v1_api

    def close(self) -> None:
        """Close API client connection."""
        if self._api_client:
            self._api_client.close()
            self._api_client = None
            self._core_v1_api = None
            self._apps_v1_api = None
            self._batch_v1_api = None


def create_k8s_client(in_cluster: bool = False, kubeconfig_path: Optional[str] = None) -> K8sClientManager:
    """Create and initialize a Kubernetes client manager.

    Args:
        in_cluster: Whether to use in-cluster configuration
        kubeconfig_path: Path to kubeconfig file

    Returns:
        Initialized K8sClientManager
    """
    manager = K8sClientManager(in_cluster=in_cluster, kubeconfig_path=kubeconfig_path)
    manager.initialize()
    return manager


def extract_k8s_resource_metadata(resource: Any) -> Dict[str, Any]:
    """Extract common metadata from a Kubernetes resource.

    Args:
        resource: Kubernetes resource object

    Returns:
        Dictionary containing common metadata fields
    """
    metadata = {}

    if hasattr(resource, 'metadata'):
        meta = resource.metadata
        metadata['name'] = meta.name
        metadata['namespace'] = getattr(meta, 'namespace', None)
        metadata['uid'] = meta.uid
        metadata['resource_version'] = meta.resource_version
        metadata['creation_timestamp'] = str(meta.creation_timestamp) if meta.creation_timestamp else None
        metadata['labels'] = dict(meta.labels) if meta.labels else {}
        metadata['annotations'] = dict(meta.annotations) if meta.annotations else {}

    if hasattr(resource, 'kind'):
        metadata['kind'] = resource.kind

    if hasattr(resource, 'api_version'):
        metadata['api_version'] = resource.api_version

    return metadata
