# DeepStream-Yolo

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

### Create a New Directory by the name "predictions" to save the detection results i.e. bounding box coordinates, class name and confidence score

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
