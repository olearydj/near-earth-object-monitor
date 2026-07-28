#!/usr/bin/env bash

echo "Starting hello.sh"

for name in Ada Linus Grace; do
  echo "Hello, $name"
done

if [[ -f pyproject.toml ]]; then
  echo "This directory contains a Python project"
else
  echo "No pyproject.toml was found"
fi
