# fake_engraving
Fake engraving plugin for Gimp 3.0

description:
------------
This plugin fakes an engraving effect by creating several layers with layer masks
based on different threshold values of the original image. The layers are filled 
with wave patterns with various thicknesses and some of them will be rotated
for a more realistic effect. At the end the engraving layers are merged together, 
the original image is hidden and a white layer is added to increase visibility.

instructions:
-------------
1) In your Gimp plug-in directory create a subdirectory called "fake_engraving". Copy the fake_engraving.py plug-in into it.
2) Copy the wave pattern files (waves0.png, etc.) into your Gimp patterns directory.
3) Start Gimp and open an image which has sufficient contrast. Upscale or downscale the image for more or less detailed engraving.
4) Apply the FakeEngraving script in the Filters / Artistic menu.
Tip: Add a layer filled with a colour above the engraved_layer and set layer mode to screen in order to colour the engraved layer.

![sample](sample.png)
