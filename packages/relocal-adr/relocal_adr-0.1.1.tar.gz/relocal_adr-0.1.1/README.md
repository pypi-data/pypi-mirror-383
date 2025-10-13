# ADR: Real-Time and Robust 3D Place Recognition with Adaptive Data Reorganization and Geodesic-Constrained Plane Suppression

[![Project Page](https://img.shields.io/badge/Project%20Page-6cc644&cacheSeconds=60)](https://utn-air.github.io/flownav.github.io/)
[![arXiv](https://img.shields.io/badge/DOI-10.1109%2FLRA.2025.3609614-b31b1b.svg)](https://ieeexplore.ieee.org/document/11162696)
![GitHub License](https://img.shields.io/badge/LICENSE-MIT-pink)
[![Latest Release](https://img.shields.io/github/v/release/HopeCollector/adr_code
)](https://github.com/utn-air/flownav/releases)

> [**NOTE**]  
> This document may be out of date. See [adr_code](https://github.com/HopeCollector/adr_code) for the latest document.  
> This source code was based on [STD: A Stable Triangle Descriptor for 3D place recognition](https://github.com/hku-mars/STD).  

## 💡 News

- **September 2025**: Accepted at [RA-L](https://ieeexplore.ieee.org/document/11162696)

## 🍝 Install with pip

1. Install dependencies

    ```bash
    sudo apt update \
    && sudo apt install libgoogle-glog-dev \
        libgflags-dev \
        libatlas-base-dev \
        libeigen3-dev \
        libpcl-dev \
        libtbb-dev
    ```

2. Install python package

    ```bash
    pip install relocal_adr
    ```

## 🎼 Usage

1. Init place recognition object

    ```python
    from relocal_adr import ADR, Feature
    from yaml import safe_load

    cfg = safe_load(open("config_kitti.yaml", "r"))
    adr = ADR(cfg)
    ```

2. Extract Descriptor from points

    ```python
    # It is recommended to use dense point clouds
    frame_num = 10

    # Select the data loading method independently according to the data set
    # Load points in world frame, !!! NOT LOCAL FRAME !!!
    points: np.ndarray = dataloader.get(start_id, frame_num, frame.WORLD)

    # Extract feature from raw points
    feature: Feature = adr.extract(points)
    ```

3. Query matching results

    ```python
    ress = adr.query(feature)

    # Print results
    if ress[0] >= 0:
        print(f"current frame match frame[{id}] in database, score is: {score}")
    ```

4. Update the feature to the database

    ```python
    adr.update(feature)
    ```

5. For detailed usage, see [demo.py](./demo.py)

## 🐋 Develop in Docker

1. Build docker image
    
    ```
    docker compose build --pull
    ```

2. Attach the service with VSCode

    - Install `ms-vscode-remote.remote-containers` in vscode extension marketplace
    - Press `F1`, search "reopen in container"
    - Click it, and all settings are complete

3. Install local package

    ```bash
    uv sync
    uv pip install ./relocal_adr
    ```

## 🔗 Datasets

The demo sample uses the `kitti_odom_2012_dataloader` to load data. Similar data loaders include

- kaist-dataloader
- nclt-dataloader
- wild-dataloader

can be installed directly using pip

## 📝 Citation

```
@ARTICLE{wang2025adr,
  author={Wang, Chengmin and Zhuang, Yan and Yan, Fei and Zhang, Xuetao},
  journal={IEEE Robotics and Automation Letters}, 
  title={Real-Time and Robust 3D Place Recognition With Adaptive Data Reorganization and Geodesic-Constrained Plane Suppression}, 
  year={2025},
  volume={10},
  number={11},
  pages={11251-11258},
  doi={10.1109/LRA.2025.3609614}
}

```