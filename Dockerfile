# Use NVIDIA DeepStream 6.0.1 base image for Jetson Nano
FROM nvcr.io/nvidia/deepstream-l4t:6.0.1-triton

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3-pip \
    python3-opencv \
    python3-numpy \
    nano && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /opt/deepstream-yolo11

# Copy everything from local repo into container
COPY . /opt/deepstream-yolo11/

# Default command to run DeepStream
CMD ["deepstream-app", "-c", "deepstream_app_config.txt"]
