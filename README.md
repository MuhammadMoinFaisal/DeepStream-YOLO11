# DeepStream-Yolo11

### Update packages
```
sudo apt update
sudo apt upgrade
```
### Install Python 3.8
```
sudo apt install python3.8 python3.8-dev python3.8-distutils
```
### Set it up with update-alternatives
```
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 2
```
Then choose the default version:
```
sudo update-alternatives --config python3
```
You'll be prompted to select a version. Choose Python 3.8

### Install pip for Python 3.8
Download the get-pip.py script:

```
wget https://bootstrap.pypa.io/get-pip.py
```
### Run it with Python 3.8 version
```
sudo python3.8 get-pip.py
```
### Verify pip is working
```
python3.8 -m pip --version
```



### Check the Python Version
```
python3 --version 
```

### Install DeepStream SDK according to the JetPack version
Download the DeepStream File From NVIDIA
* For JetPack 4.6.4, install [`DeepStream 6.0.1`](https://docs.nvidia.com/metropolis/deepstream/6.0.1/dev-guide/text/DS_Quickstart.html)
* For JetPack 5.1.3, install [`DeepStream 6.3`](https://docs.nvidia.com/metropolis/deepstream/6.3/dev-guide/text/DS_Quickstart.html)
* For JetPack 6.1, install [`DeepStream 7.1`](https://docs.nvidia.com/metropolis/deepstream/dev-guide/text/DS_Installation.html)

### Install DeepStream
```
sudo apt-get install ./deepstream-6.0_6.0.1-1_arm64.deb
```

### Check DeepStream Version
```
deepstream-app --version
```
### Check CUDA Version
```
nvcc --version
```
### Check the TensorRT Version
```
dpkg -l | grep TensorRT
```
### Convert model

#### Download the YOLO11 repo and install the requirements
```
git clone https://github.com/ultralytics/ultralytics.git
cd ultralytics
pip3 install -e .
pip3 install onnx onnxslim onnxruntime
```

#### Download the model

Download Ultralytics YOLO11 detection model (.pt) of your choice from [YOLO11](https://github.com/ultralytics/assets/releases/) releases. Here we use yolo11n.pt.

```
wget https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt
```

#### CLone this repository

```
cd ~
git clone https://github.com/marcoslucianops/DeepStream-Yolo.git
```

#### Convert model
Copy the export_yolo11.py file from DeepStream-Yolo/utils directory to the ultralytics folder.
Generate the ONNX model file 
```
cd ultralytics
python3 export_yolo11.py -w yolo11n.pt --dynamic
```

#### 6. Compile the lib

1. Open the `DeepStream-Yolo` folder and compile the lib

2. Set the `CUDA_VER` according to your DeepStream version

```
cd ~
cd DeepStream-Yolo
export CUDA_VER=10.2
```

* x86 platform

  ```
  DeepStream 7.1 = 12.6
  DeepStream 7.0 / 6.4 = 12.2
  DeepStream 6.3 = 12.1
  DeepStream 6.2 = 11.8
  DeepStream 6.1.1 = 11.7
  DeepStream 6.1 = 11.6
  DeepStream 6.0.1 / 6.0 = 11.4
  DeepStream 5.1 = 11.1
  ```

* Jetson platform

  ```
  DeepStream 7.1 = 12.6
  DeepStream 7.0 / 6.4 = 12.2
  DeepStream 6.3 / 6.2 / 6.1.1 / 6.1 = 11.4
  DeepStream 6.0.1 / 6.0 / 5.1 = 10.2
  ```

3. Make the lib

```
make -C nvdsinfer_custom_impl_Yolo clean && make -C nvdsinfer_custom_impl_Yolo
```

##

### Edit the config_infer_primary_yolo11 file

Edit the `config_infer_primary_yolo11.txt` file according to your model

```
[property]
...
onnx-file=yolo11n.pt.onnx
...
num-detected-classes=80
...
parse-bbox-func-name=NvDsInferParseYolo
...
```


##

### Edit the deepstream_app_config file

```
...
[primary-gie]
...
config-file=config_infer_primary_yolo11.txt
```

### Create a new Directory by the name "predictions" to save the detection results i.e. bounding box coordinates, class name and confidence score

```
mkdir predictions
```

### Testing the model

```
deepstream-app -c deepstream_app_config.txt
```

### Multiple Streams Setup
To set up multiple streams under a single deepstream application, you can do the following changes to the deepstream_app_config.txt file

* Change the rows and columns to build a grid display according to the number of streams you want to have. For example, for 4 streams, we can add 2 rows and 2 columns.
```
[tiled-display]
rows=2
columns=2
```
* Set num-sources=4 and add uri of all the 4 streams
```
[source0]
enable=1
type=3
uri=path/to/video1.mp4
uri=path/to/video2.mp4
uri=path/to/video3.mp4
uri=path/to/video4.mp4
num-sources=4

```

### Run Inference
```
deepstream-app -c deepstream_app_config.txt
```
### Save all the predictions in a database

```
sudo apt update
sudo apt install sqlite3
```

### Create a new file called, save_predictions_to_db.py.

```
nano save_predictions_to_db.py
```

### Paste the following code inside
```
import os
import sqlite3

# Set the path to your predictions folder
PREDICTIONS_FOLDER = 'predictions'  # Change this if your folder name is different

# 1. Connect to (or create) a SQLite database file
conn = sqlite3.connect('predictions.db')  # This file will be created in your current directory
cursor = conn.cursor()

# 2. Create a table if it does not exist already
cursor.execute('''
    CREATE TABLE IF NOT EXISTS detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        frame_name TEXT,
        class_name TEXT,
        x1 REAL,
        y1 REAL,
        x2 REAL,
        y2 REAL,
        confidence REAL
    )
''')
conn.commit()

# 3. Loop through all .txt files inside the predictions folder
for filename in sorted(os.listdir(PREDICTIONS_FOLDER)):
    if filename.endswith('.txt'):
        frame_name = filename.replace('.txt', '')  # Remove ".txt" from the filename
        file_path = os.path.join(PREDICTIONS_FOLDER, filename)
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.strip().split(' ')

                # Make sure there are enough parts in the line
                if len(parts) >= 16:
                    class_name = parts[0]
                    x1 = float(parts[4])
                    y1 = float(parts[5])
                    x2 = float(parts[6])
                    y2 = float(parts[7])
                    confidence = float(parts[-1])

                    # Insert into the database
                    cursor.execute('''
                        INSERT INTO detections (frame_name, class_name, x1, y1, x2, y2, confidence)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (frame_name, class_name, x1, y1, x2, y2, confidence))

# 4. Commit and close the database
conn.commit()
conn.close()

print('All predictions have been saved successfully into predictions.db')

```

### Save the script as save_predictions_to_db.py and in terminal
```
python3 save_predictions_to_db.py
```
It will process all .txt files inside predictions/ and save detections to predictions.db.

After running, you will see a new file created "predictions.db"

### View data inside database
```
nano view_database.py
```
### Paste the following code inside
```
import sqlite3

conn = sqlite3.connect('predictions.db')
cursor = conn.cursor()

for row in cursor.execute('SELECT * FROM detections LIMIT 10'):
    print(row)

conn.close()
```
```
python3 view_database.py
```
It will print first 10 detections!

### Open .db file online
Go to [SQLite Viewer](https://sqliteviewer.app/)

### DeepStream-YOLO11 Docker Guide
This guide helps you build and run the Docker container for DeepStream-YOLO11 on Jetson Nano using DeepStream 6.0.1.

```
sudo apt install docker.io
```
```
sudo apt install nvidia-container-runtime
```
### Create Dockerfile
```
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

```
### Save Output to File
Open the deepstream_app_config.txt file and update [source0] and [sink0]
```
[source0]
enable=1
type=3
uri=file:///opt/deepstream-yolo11/video.mp4
num-sources=1
gpu-id=0
cudadec-memtype=0

[sink0]
enable=1
type=3
container=1
codec=1
output-file=/opt/deepstream-yolo11/output.mp4
```

### Build Docker Image
```
sudo docker build -t deepstream-yolo11 .
```

### Run Container
```
sudo docker run -it --rm \
  --runtime nvidia \
  --gpus all \
  -v /home/muhammad/DeepStream-YOLO11:/opt/deepstream-yolo11 \
  deepstream-yolo11
```

### Pull from Docker Hub
```
docker pull muhammadmoin619/deepstream-yolo11:latest

```
#### Then run it like:
```
docker run -it --rm --runtime nvidia --gpus all muhammadmoin619/deepstream-yolo11:latest
```
```
docker run -it --rm \
  --runtime nvidia \
  --gpus all \
  -v /home/muhammad/DeepStream-YOLO11:/opt/deepstream-yolo11 \
  muhammadmoinfaisal/deepstream-yolo11:latest
```

