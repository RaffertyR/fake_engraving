#!/usr/bin/env python

# fake_engraving.py

# ##########################################################
# IMPORTANT: Load the patterns 'waves0.png' till 'waves5.png' in your Gimp pattern
# directory!
# ##########################################################
#
# This plugin fakes an engraving effect by creating several layers with layer masks
# based on different threshold values of the original image. The layers are filled 
# with wave patterns with various thicknesses and some of them will be rotated
# for a more realistic effect. At the end the engraving layers are merged together
# and a white layer is added to increase visibility.
#
# Tip: Add a layer filled with a colour above the engraved_layer and set layer mode
#  to screen in order to colour the engraved layer.
#
# Inspired by this Photoshop tutorial: 
# https://blog.spoongraphics.co.uk/tutorials/create-realistic-money-effect-photoshop
# ##########################################################
#
# License: GPLv3
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY# without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# To view a copy of the GNU General Public License
# visit: http://www.gnu.org/licenses/gpl.html
#
# ------------
#| Change Log |
# ------------
# Version 1.0 - 19/02/2021 - initial release for Gimp 2.10
# Version 2.0 - 01/03/2025 - adapted for Gimp 3.0
# ##########################################################

import sys

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
from gi.repository import GLib

class FakeEngraving (Gimp.PlugIn):
    def do_query_procedures(self):
        return [ "rr-FakeEngraving" ]

    def do_set_i18n (self, name):
        return False

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            self.run, None)

        procedure.set_image_types("*")

        procedure.set_menu_label("FakeEngraving...")
        procedure.add_menu_path('<Image>/Filters/Artistic/')

        procedure.set_documentation("Fake engraving",
                                    "Fake engraving Python 3 plug-in for GIMP 3.0",
                                    name)
        procedure.set_attribution("Rafferty", "Rafferty", "2025")

        return procedure

    def run(self, procedure, run_mode, image, drawables, config, run_data):

        merge_visible_layers=True # TO DO: create dialog to choose this
        ########## prepare the image ##########
        Gimp.message("Starting fake engraving plugin...")
        image.undo_group_start()
        Gimp.context_push()
        Gimp.Selection.none(image)
        layers = image.get_layers()
        image.flatten()
        layer=layers[0]
        Gimp.Item.set_name(layer,"original_image")
        channels = image.get_channels()
        for channel in channels:
            image.remove_channel(channel) # remove all custom channels

        ########## create the mask channels based on thresholds ##########
        thresPoints = [0.31,0.39,0.47,0.55,0.63,0.71] # 0.31=80/255, etc.
        Num=0
        for thres in thresPoints: # cycle through thresPoints list at each iteration
            layer_copy = Gimp.Layer.new_from_drawable(layer,image)
            image.insert_layer(layer_copy,None,0)
            layer_copy.threshold(1, 0, thres) # RED=1
            # copy Red channel as:
            channelName = Gimp.Channel.new_from_component(image,Gimp.ChannelType.RED,str(Num))
            image.insert_channel(channelName,None,0)
            Num+=1
            image.remove_layer(layer_copy) # remove layer that was used to create the mask

        ########## create layers filled with the patterns and apply the masks ##########
        maxDim=max(image.get_width(),image.get_height()) #in order to entirely fill the 90 degrees rotated layers
        rotatedDim=((maxDim**2+maxDim**2)**(0.5)) #in order to entirely fill the 45 degrees rotated layer (Pythagoras)
        rotations = [-45,0,0,90,90,0] # rotate the layers with the patterns at these angles
        Num=0
        channels = image.get_channels()
        for channel in channels:
            Gimp.Selection.none(image)
            if rotations[Num]==-45:
                layer_add = Gimp.Layer.new(image,str(Num),rotatedDim,rotatedDim,Gimp.ImageType.RGBA_IMAGE,100,Gimp.LayerMode.NORMAL)
            else:
                layer_add = Gimp.Layer.new(image,str(Num),maxDim,maxDim,Gimp.ImageType.RGBA_IMAGE,100,Gimp.LayerMode.NORMAL)
            Gimp.Image.insert_layer(image, layer_add, None,0)

            # fill with waves pattern
            pat=Gimp.Pattern.get_by_name("waves"+str(Num)+".png")
            Gimp.context_set_pattern(pat)
            layer_add.edit_fill(Gimp.FillType.PATTERN)

            # rotate pattern with rotations[x] and transform degrees to radians
            item=layer_add.transform_rotate(3.14159/180*rotations[Num],1,0,0)
            if item.is_floating_sel():
                Gimp.floating_sel_anchor(item)
            # move the 45 degrees rotated layer to fully cover the original image
            if rotations[Num]==-45:
                layer_add.set_offsets(int(-maxDim/2),int(-maxDim/2))

            # add mask to layer
            image.select_item(Gimp.ChannelOps.REPLACE,channel)
            mask = layer_add.create_mask(Gimp.AddMaskType.SELECTION)
            layer_add.add_mask(mask)
            Gimp.Image.remove_channel(image,channel)
            Num+=1

        ############# finalize #######################
        # hide original layer
        layers = image.get_layers()
        select_layer=layers[Num] #select 6th layer (the original_image-layer)
        select_layer.set_visible(0)

        # merge engrave layers and crop them to original image size
        if merge_visible_layers:
            image.merge_visible_layers(Gimp.MergeType.CLIP_TO_IMAGE)
            layers = image.get_layers()
            select_layer=layers[0]
            select_layer.set_name("engraved_layer")

        # add white layer for visibility
        white_layer = Gimp.Layer.new(image,"white_layer",image.get_width(),image.get_height(),Gimp.ImageType.RGBA_IMAGE,100,Gimp.LayerMode.NORMAL)
        image.insert_layer(white_layer,None,-1)
        image.lower_item_to_bottom(white_layer)
        Gimp.Selection.all(image)
        white_layer.edit_fill(Gimp.FillType.WHITE)

        ########## end of code ##########
        Gimp.Selection.none(image)
        Gimp.context_pop()
        Gimp.displays_flush()
        image.undo_group_end()
        Gimp.message("Finishing fake engraving plugin!")

        # in case of success, return:
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

Gimp.main(FakeEngraving.__gtype__, sys.argv)
