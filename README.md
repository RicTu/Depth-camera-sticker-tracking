# Experiments
This project uses the RGB frame and depth frame from the OAK-D camera to track the stickers.
The tracking result contains the 2D tracking result from the RGB frame and the depth information from the depth frame.

## Foundation of OAK-D camera
* The OAK-D camera is a depth camera that contains an AI processor inside.
* OAK-D spec: https://store.opencv.ai/products/oak-d
* Control OAK-D camera: https://docs.luxonis.com/en/latest/

## How this project work
1. We capture the RGB frame and depth frame from the OAK-D camera.
1. Align the RGB frame and the depth frame.
1. Filter out the stickers through the color mask.
1. Utilize the Hough Circles algorithm to determine the center of the stickers.
1. Get the depth information of the sticker from the depth frame which has been aligned with the RGB frame. 

<!---
![OAK-D_FFT_work_flow](Figures/OAK-D_FFT_work_flow.png)
![OAK-D_FFT_pipeline](Figures/OAK-D_FFT_pipeline.png)

<p align="center">
<img src="Figures/OAK-D_FFT_pipeline.png" width="400">
</p>
-->

## Work flow of this project
* The interaction pipeline between host side (e.g. computer) and the device side (e.g. camera): 
<img src="Figures/OAK-D_FFT_pipeline.png" width="400">

* The work flow when we capture the image data from the OAK-D camera
<img src="Figures/OAK-D_FFT_work_flow.png" width="750">


