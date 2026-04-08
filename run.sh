#!/bin/bash
echo "Building Meta-Hackathon Legal Contract Evaluation Environment..."
docker build -t openenv .

echo "Running environment container on port 7860..."
docker run -p 7860:7860 openenv
