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

![Alt text](./Figures/OAK-D_FFT_pipeline.pdf?raw=true "Title")



