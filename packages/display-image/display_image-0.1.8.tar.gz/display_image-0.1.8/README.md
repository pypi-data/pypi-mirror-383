# Display Image

Display image is a Python project which provides a command `display-image` to visualize the image and metadata by QtPy6.

## Installation

~~~~~~~~~~~~~~~{.shell}
pip install display-image
~~~~~~~~~~~~~~~

## Usage

~~~~~~~~~~~~~~~{.shell}
display-image -i <path_to_image>
~~~~~~~~~~~~~~~


The following format extensions can be displayed by command `display-image`

| Image format  | Read | EXIF | Pixel precision        | Pixel type           | File extension                   |  Sidecar needed  |
|---------------|------|------|------------------------|----------------------|----------------------------------|------------------|
| BMP           | x    |      | 8 bits                 | Grayscale, RGB, RGBA | .bmp                             |                  |
| CFA           | x    |      | 16 bits                | Bayer                | .cfa                             |                  |
| DNG           | x    | x    | 16 bits                | Bayer                | .dng                             |                  |
| JPEG          | x    | x    | 8 bits                 | Grayscale, RGB       | .jpg, .jpeg                      |                  |
| MIPI RAW      | x    |      | 10 bits, 12 bits       | Bayer                | .RAWMIPI, .RAWMIPI10, .RAWMIPI12 | x                |
| PLAIN RAW     | x    |      | *                      | *                    | .raw .plain16, *                 | x                |
| PNG           | x    |      | 8 bits                 | Grayscale, RGB, RGBA | .png                             |                  |
| TIFF          | x    | x    | 8 bits, 16 bits        | Bayer, RGB           | .tif, .tiff                      |                  |


### Read Camera manufacturer RAW image display

The RAW image formats of the following camera manufacturers are supported, user can display these camera raw files by dependency `cxx-image-io` version`v1.1.2`.

| Camera manufacturer | Image format |
|---------------------|--------------|
| Canon               | CR2          |
| Nikon               | NEF          |
| Sony                | ARW          |
| Panasonic           | RW2          |
| Kodak               | DCR          |
| Samsung             | SRW          |
| Olympus             | ORF          |
| Leica               | RAW          |
| Pentax              | PEF          |

![displaye-image RAW image](https://media.githubusercontent.com/media/sygslhy/display-image/refs/heads/master/.github/images/display-image-gui.png)

- User can scroll mouse to zoom in/out, and at bottom it can display the zoom factor and pixel value where use clicked with mouse. 
- Since 0.1.6, `CalibrationData`, `CameraControls`, `LibRawParams` are added in metadata info display, they includes some image processing params such as:
    - black level and white level
    - color matrix
    - white balances scales
    - visible zone crop coordinates on camera Raw image


![Calibration](https://media.githubusercontent.com/media/sygslhy/display-image/refs/heads/master/.github/images/Calibration.png)

![CameraControls](https://media.githubusercontent.com/media/sygslhy/display-image/refs/heads/master/.github/images/cameracontrol.png)

![LibRawParams](https://media.githubusercontent.com/media/sygslhy/display-image/refs/heads/master/.github/images/libraw.png)

### Image display with sidecar JSON

Some file formats need to know in advance some informations about the image. For example, the PLAIN RAW format is just a simple dump of a buffer into a file, thus it needs to know how to interpret the data.
In this case, user need to have an image sidecar JSON located next to the image file as the same name and path `path_to_image.json`

~~~~~~~~~~~~~~~{.json}
{
    "fileInfo": {
        "format": "plain",
        "height": 3072,
        "width": 4080
        "pixelPrecision": 16,
        "pixelType": "bayer_gbrg",
    }
}
~~~~~~~~~~~~~~~

After image reading, the information in JSON sidecar will be shown in tab Widegt of `ImageMetadata`

### Other image reading with sidecar examples

<details>
  <summary>
  Click to unfold other image format sidecar examples
  </summary>

#### Packed RAW MIPI 12 bits:

sidecar json
~~~~~~~~~~~~~~~{.json}
{
    "fileInfo": {
        "fileFormat": "raw12",
        "height": 3000,
        "width": 4000,
        "pixelPrecision": 12,
        "pixelType": "bayer_gbrg"
    }
}
~~~~~~~~~~~~~~~

#### Packed RAW MIPI 10 bits:

sidecar json
~~~~~~~~~~~~~~~{.json}
{
    "fileInfo": {
        "height": 3000,
        "width": 4000,
        "format": "raw10",
        "pixelPrecision": 10,
        "pixelType": "bayer_grbg"
    }
}
~~~~~~~~~~~~~~~

</details>

## License

This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/sygslhy/display-image/blob/master/LICENSE.md) file for details.
