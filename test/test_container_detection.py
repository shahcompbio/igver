#!/usr/bin/env python
"""Test container detection logic"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from igver.igver import is_running_in_container

print("=== Testing Container Detection ===")
print()

# Test current environment
print("Current environment:")
print(f"  is_running_in_container(): {is_running_in_container()}")
print()

# Test environment variables
print("Environment variables:")
print(f"  IGVER_IN_CONTAINER: {os.environ.get('IGVER_IN_CONTAINER', 'not set')}")
print(f"  IGVER_NO_SINGULARITY: {os.environ.get('IGVER_NO_SINGULARITY', 'not set')}")
print(f"  SINGULARITY_CONTAINER: {os.environ.get('SINGULARITY_CONTAINER', 'not set')}")
print()

# Test Docker detection
print("Docker detection:")
print(f"  /.dockerenv exists: {os.path.exists('/.dockerenv')}")
try:
    with open('/proc/1/cgroup', 'r') as f:
        cgroup_content = f.read()
        print(f"  'docker' in /proc/1/cgroup: {'docker' in cgroup_content}")
        print(f"  'lxc' in /proc/1/cgroup: {'lxc' in cgroup_content}")
except:
    print("  Could not read /proc/1/cgroup")
print()

# Test with different environment settings
print("Testing with different settings:")

# Test 1: IGVER_IN_CONTAINER=1
os.environ['IGVER_IN_CONTAINER'] = '1'
print(f"  With IGVER_IN_CONTAINER=1: {is_running_in_container()}")
del os.environ['IGVER_IN_CONTAINER']

# Test 2: IGVER_NO_SINGULARITY=1
os.environ['IGVER_NO_SINGULARITY'] = '1'
print(f"  With IGVER_NO_SINGULARITY=1: {is_running_in_container()}")
del os.environ['IGVER_NO_SINGULARITY']

# Test 3: SINGULARITY_CONTAINER set
os.environ['SINGULARITY_CONTAINER'] = '/some/path'
print(f"  With SINGULARITY_CONTAINER set: {is_running_in_container()}")
del os.environ['SINGULARITY_CONTAINER']

print()
print("Container detection test complete!")