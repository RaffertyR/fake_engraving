#!/usr/bin/env python

# fake_engraving.py

# ##########################################################
# IMPORTANT: Load the patterns 'waves0.png' till 'waves5.png' in your pattern
# directory first!
# ##########################################################
#
# This plugin fakes an engraving effect by creating several layers with layer masks
# based on different threshold values of the original image. The layers are filled 
# with wave patterns with various thicknesses and some of them will be rotated
# for a more realistic effect. At the end the engraving layers are merged together
# and a white layer is added to increase visibility.
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
# # ------------
#| Change Log |
# ------------
# Version 1.0 - 19/02/2021 - initial release
# ##########################################################

from gimpfu import *

def python_fake_engraving(image,layer,merge_visible_layers=True) :

	########## prepare the image ##########
	pdb.gimp_image_undo_group_start(image)
	pdb.gimp_context_push()
	pdb.gimp_selection_none(image)
	pdb.gimp_image_flatten(image)
	layers = image.layers
	layer=layers[0]
	pdb.gimp_item_set_name(layer,"original_image")
	for channel in image.channels:
		image.remove_channel(channel)		# remove all custom channels
		
	########## create the mask channels based on thresholds ##########
	thresPoints = [0.31,0.39,0.47,0.55,0.63,0.71]	# 0.31=80/255, etc.
	Num=0
	for thres in thresPoints:	# cycle through thresPoints list at each iteration
		layer_copy = pdb.gimp_layer_new_from_drawable(layer,image)
		pdb.gimp_image_insert_layer(image,layer_copy,None,0)
		pdb.gimp_drawable_threshold(layer_copy,0,0,thres)
		# copy Red channel as:
		channelName = pdb.gimp_channel_new_from_component(image,CHANNEL_RED,str(Num))
		pdb.gimp_image_insert_channel(image,channelName,None,0)
		Num+=1
		pdb.gimp_image_remove_layer(image,layer_copy)	# remove layer that was used to create the mask
	
	########## create layers filled with the patterns and apply the masks ##########
	maxDim=max(image.width,image.height) #in order to entirely fill the 90 degrees rotated layers
	rotatedDim=((maxDim**2+maxDim**2)**(0.5)) #in order to entirely fill the 45 degrees rotated layer (Pythagoras)
	rotations = [-45,0,0,90,90,0] # rotate the layers with the patterns at these angles
	Num=0	
	for channel in image.channels:
		pdb.gimp_selection_none(image)
		if rotations[Num]==-45:
			layer_add = pdb.gimp_layer_new(image,rotatedDim,rotatedDim,RGBA_IMAGE,str(Num),100,NORMAL_MODE)
		else:
			layer_add = pdb.gimp_layer_new(image,maxDim,maxDim,RGBA_IMAGE,str(Num),100,NORMAL_MODE)
		pdb.gimp_image_insert_layer(image, layer_add, None,0)
		
		# fill with waves pattern
		pdb.gimp_context_set_pattern("waves"+str(Num)+".png")
		pdb.gimp_edit_fill(layer_add,PATTERN_FILL)

		# rotate pattern with rotations[x] and transform degrees to radians
		item=pdb.gimp_item_transform_rotate(layer_add,3.14159/180*rotations[Num],1,0,0)
		if pdb.gimp_layer_is_floating_sel(item):
			pdb.gimp_floating_sel_anchor(item)
		# move the 45 degrees rotated layer to fully cover the original image
		if rotations[Num]==-45:
			pdb.gimp_layer_set_offsets(layer_add,int(-maxDim/2),int(-maxDim/2))
		
		# add mask to layer
		pdb.gimp_image_select_item(image, CHANNEL_OP_REPLACE,channel)
		mask = pdb.gimp_layer_create_mask(layer_add, ADD_MASK_SELECTION)
		pdb.gimp_layer_add_mask(layer_add, mask)
		pdb.gimp_image_remove_channel(image,channel)
		Num+=1

	############# finalize #######################
	# hide original layer
	layers = image.layers
	select_layer=layers[Num] #select 6th layer (the original_image-layer)
	pdb.gimp_item_set_visible(select_layer,0)
	
	# merge engrave layers and crop them to original image size
	if merge_visible_layers:
		pdb.gimp_image_merge_visible_layers(image,CLIP_TO_IMAGE)
		layers = image.layers
		select_layer=layers[0]
		pdb.gimp_item_set_name(select_layer,"engraved")	
	
	# add white layer for visibility
	white_layer = pdb.gimp_layer_new(image,image.width,image.height,RGBA_IMAGE,"white_layer",100,NORMAL_MODE)
	pdb.gimp_image_insert_layer(image,white_layer,None,-1)
	pdb.gimp_image_lower_item_to_bottom(image,white_layer)
	pdb.gimp_selection_all(image)
	pdb.gimp_edit_fill(white_layer,WHITE_FILL)
	
	pdb.gimp_selection_none(image)
	pdb.gimp_context_pop()
	pdb.gimp_image_undo_group_end(image)
	pdb.gimp_displays_flush()

# The plugin registration
register(
	"python_fu_fake_engraving",
	"Create Fake Engraving",
	"Create Fake Engraving",
	"Rafferty",
	"Rafferty",
	"Feb.2021",
	"<Image>/Python-Fu/Fake Engraving...",             					#Menu path
	"RGB*, GRAY*", 
	[
		(PF_TOGGLE, "merge_visible_layers", "Merge visible layers:", True)
	],
	[],
	python_fake_engraving)

main()
