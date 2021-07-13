# fake_engraving
Fake engraving plugin for Gimp 2.10

description:
------------
This plugin fakes an engraving effect by creating several layers with layer masks
based on different threshold values of the original image. The layers are filled 
with wave patterns with various thicknesses and some of them will be rotated
for a more realistic effect. At the end the engraving layers are merged together
and a white layer is added to increase visibility.

instructions:
-------------
1) Copy the plugin fake_engraving.py into your Gimp plugin directory and the wave pattern files (waves0.png, etc.) into your Gimp patterns directory.
2) Start Gimp and open an image of about 1000 pixels or more at 300dpi which has sufficient contrast.
3) Apply the script in the Python-Fu menu.
