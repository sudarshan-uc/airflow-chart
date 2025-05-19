#!/usr/bin/env python3
import argparse

import yaml
from tabulate import tabulate

REQUIRED_KINDS = {"Deployment", "DaemonSet", "StatefulSet", "CronJob", "Job"}

# Helper to get containers from a workload spec
def get_containers(doc):
    kind = doc.get("kind")
    spec = doc.get("spec", {})
    # For CronJob, containers are under spec.jobTemplate.spec.template.spec
    if kind == "CronJob":
        t = spec.get("jobTemplate", {}).get("spec", {}).get("template", {}).get("spec", {})
    elif kind == "Job":
        t = spec.get("template", {}).get("spec", {})
    else:
        t = spec.get("template", {}).get("spec", {})
    containers = t.get("containers", [])
    return containers, t.get("initContainers", [])

def check_container_fields(container):
    # Returns a dictionary indicating presence of fields
    checks = {
        "livenessProbe": "livenessProbe" in container,
        "readinessProbe": "readinessProbe" in container,
        "resources": "resources" in container,
    }
    return checks

def main():
    parser = argparse.ArgumentParser(description="Validate and list Kubernetes manifest components.")
    parser.add_argument("filename", help="The YAML file to validate")
    args = parser.parse_args()

    filename = args.filename
    all_components_valid = True
    table_data = []
    headers = ["Kind", "Name", "Container", "Liveness", "Readiness", "Resources"]

    with open(filename) as f:
        docs = list(yaml.safe_load_all(f))

    for doc in docs:
        if not isinstance(doc, dict):
            continue
        kind = doc.get("kind")
        if kind not in REQUIRED_KINDS:
            continue

        meta = doc.get("metadata", {})
        name = meta.get("name", "<no-name>")

        containers, _ = get_containers(doc) # We are not checking initContainers

        if not containers:
            table_data.append([kind, name, "No containers found", "-", "-", "-"])
            continue

        for c in containers:
            cname = c.get("name", "<unnamed>")
            field_checks = check_container_fields(c)
    
            # Add row to table data
            row = [
                kind,
                name,
                cname,
                field_checks["livenessProbe"],
                field_checks["readinessProbe"],
                field_checks["resources"]
            ]
            table_data.append(row)
    
            # Check if all required fields are present
            if not all(field_checks.values()):
                all_components_valid = False

    # Print table
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    # Print summary
    if all_components_valid:
        print("\nAll checked containers have livenessProbe, readinessProbe, and resources defined.")
    else:
        print("\nValidation issues found. Some containers are missing required fields.")

if __name__ == "__main__":
    main()