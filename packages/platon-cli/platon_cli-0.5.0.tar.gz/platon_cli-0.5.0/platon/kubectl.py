"""Kubernetes operations wrapper"""

import subprocess
import json
from typing import List, Dict, Optional


class KubectlManager:
    """Manages kubectl operations"""

    def __init__(self, repo):
        self.repo = repo
        self.namespace = repo.namespace

    def _run(self, *args, capture=True) -> Optional[str]:
        """Run kubectl command"""
        cmd = ["kubectl", "-n", self.namespace] + list(args)
        if capture:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        else:
            subprocess.run(cmd, check=True)
            return None

    def get_pods(self, selector: Optional[str] = None) -> List[Dict]:
        """List pods"""
        args = ["get", "pods", "-o=json"]
        if selector:
            args.extend(["-l", selector])

        output = self._run(*args)
        data = json.loads(output)

        pods = []
        for item in data.get("items", []):
            pods.append(
                {
                    "name": item["metadata"]["name"],
                    "status": item["status"]["phase"],
                    "restarts": sum(
                        c.get("restartCount", 0)
                        for c in item["status"].get("containerStatuses", [])
                    ),
                    "age": item["metadata"]["creationTimestamp"],
                }
            )
        return pods

    def logs(
        self,
        pod: str,
        follow: bool = False,
        previous: bool = False,
        tail: int = 100,
        container: Optional[str] = None,
    ):
        """View pod logs"""
        args = ["logs", pod, f"--tail={tail}"]
        if follow:
            args.append("-f")
        if previous:
            args.append("--previous")
        if container:
            args.extend(["-c", container])

        self._run(*args, capture=False)

    def exec(self, pod: str, command: str, container: Optional[str] = None):
        """Execute command in pod"""
        args = ["exec", "-it", pod]
        if container:
            args.extend(["-c", container])
        args.extend(["--", command])

        self._run(*args, capture=False)

    def scale(self, deployment: str, replicas: int):
        """Scale deployment"""
        self._run("scale", f"deployment/{deployment}", f"--replicas={replicas}")

    def restart(self, deployment: str):
        """Restart deployment"""
        self._run("rollout", "restart", f"deployment/{deployment}")

    def health_check(self) -> Dict:
        """Check cluster health"""
        try:
            pods = self.get_pods()
            return {
                "healthy": True,
                "cluster": "Connected",
                "pod_count": len(pods),
                "deployment_count": 0,  # Could fetch deployments
            }
        except Exception:
            return {
                "healthy": False,
                "cluster": "Disconnected",
                "pod_count": 0,
                "deployment_count": 0,
            }

