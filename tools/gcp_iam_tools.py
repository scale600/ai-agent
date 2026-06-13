"""
GCP IAM audit tools — callable by ADK LlmAgent via tool calling.
Each function maps to one GCP API call and returns a plain dict
so Gemini can reason over the result.
"""

from google.cloud import resourcemanager_v3, iam_admin_v1
from google.iam.v1 import iam_policy_pb2
from config.settings import GCP_PROJECT_ID


def get_iam_policy(project_id: str = GCP_PROJECT_ID) -> dict:
    """
    Fetch the IAM policy for a GCP project.

    Args:
        project_id: GCP project ID to audit. Defaults to the configured project.

    Returns:
        dict with 'project_id' and 'bindings' (list of role → members mappings).
    """
    client = resourcemanager_v3.ProjectsClient()
    request = iam_policy_pb2.GetIamPolicyRequest(
        resource=f"projects/{project_id}"
    )
    policy = client.get_iam_policy(request=request)

    bindings = [
        {"role": b.role, "members": list(b.members)}
        for b in policy.bindings
    ]
    return {"project_id": project_id, "bindings": bindings}


def list_service_accounts(project_id: str = GCP_PROJECT_ID) -> dict:
    """
    List all service accounts in a GCP project.

    Args:
        project_id: GCP project ID to inspect.

    Returns:
        dict with 'project_id' and 'service_accounts' (list of name/email/display_name).
    """
    client = iam_admin_v1.IAMClient()
    request = iam_admin_v1.ListServiceAccountsRequest(
        name=f"projects/{project_id}"
    )
    accounts = client.list_service_accounts(request=request)

    result = [
        {
            "name": sa.name,
            "email": sa.email,
            "display_name": sa.display_name,
            "disabled": sa.disabled,
        }
        for sa in accounts
    ]
    return {"project_id": project_id, "service_accounts": result}


# Roles that grant broad, potentially dangerous access
_HIGH_RISK_ROLES = {
    "roles/owner",
    "roles/editor",
    "roles/iam.securityAdmin",
    "roles/resourcemanager.projectIamAdmin",
    "roles/iam.serviceAccountAdmin",
}

_PRIMITIVE_ROLES = {"roles/owner", "roles/editor", "roles/viewer"}


def analyze_permissions(project_id: str = GCP_PROJECT_ID) -> dict:
    """
    Analyze IAM policy and flag excessive or risky permissions.

    Checks for:
    - High-risk roles (owner, editor, security admin, etc.)
    - Primitive roles assigned to service accounts
    - allUsers / allAuthenticatedUsers (public access)

    Args:
        project_id: GCP project ID to analyze.

    Returns:
        dict with 'violations' list and 'summary' string.
    """
    policy = get_iam_policy(project_id)
    violations = []

    for binding in policy["bindings"]:
        role = binding["role"]
        members = binding["members"]

        for member in members:
            # Public access — always a violation
            if member in ("allUsers", "allAuthenticatedUsers"):
                violations.append({
                    "severity": "CRITICAL",
                    "role": role,
                    "member": member,
                    "reason": "Public access granted — anyone on the internet can assume this role",
                })
                continue

            # High-risk role assigned to a real identity
            if role in _HIGH_RISK_ROLES:
                violations.append({
                    "severity": "HIGH",
                    "role": role,
                    "member": member,
                    "reason": f"{role} grants broad permissions; use a least-privilege role instead",
                })
                continue

            # Primitive role on service accounts is suspicious
            if role in _PRIMITIVE_ROLES and member.startswith("serviceAccount:"):
                violations.append({
                    "severity": "MEDIUM",
                    "role": role,
                    "member": member,
                    "reason": "Primitive role on a service account; prefer granular predefined roles",
                })

    summary = (
        f"Found {len(violations)} violation(s) in project '{project_id}': "
        f"{sum(1 for v in violations if v['severity'] == 'CRITICAL')} CRITICAL, "
        f"{sum(1 for v in violations if v['severity'] == 'HIGH')} HIGH, "
        f"{sum(1 for v in violations if v['severity'] == 'MEDIUM')} MEDIUM."
    )

    return {"project_id": project_id, "violations": violations, "summary": summary}
