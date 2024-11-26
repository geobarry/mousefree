![compass_screenshot](https://github.com/user-attachments/assets/186c40be-2914-420a-a33d-baa23f0cb43b)

# Talon compass
Talon voice commands to control mouse using a first-person navigation perspective.
## Overview
Perform mouse movement with command sequences like:

``` "Compass North - 20 East - Go 500 - Exit Compass" ```
#### Important Note
Compass has been designed to allow for short voice commands while avoiding misrecognitions that can disrupt your workflow. To achieve this, Command Mode is turned off when initiating the first compass command. You can always restore Command Mode with "Exit Compass".
## Motivation
The computer mouse is a major source of RSI and a big reason that I switched to Talon, but mouse control with voice was one of the more frustrating tasks for me as a new Talon user. Although a rectangular grid can be very efficient, for many people it is more natural and intuitive to move your mouse a specified direction and distance. 

With this in mind, Compass uses a cardinal direction - offset - distance protocol inspired by surveying and navigation to make voice-controlled mouse movement feel more natural. With a concise grammar and automatic mode management to avoid misrecognitions, my hope is that mouse control with Compass can help other Talon users stop reaching for their actual mouse.
## Installation
#### Existing talon users
Just copy or clone all files to somewhere in your talon user folder. 
#### New talon users
1. Read up on how to install and get started with talon here:
   - https://talonvoice.com/
   - https://talon.wiki/
2. Once you are up and running, just copy or clone all files to somewhere in your talon user folder. 
## Usage
The basic sequence involves three conceptual steps:
  1. Set an initial bearing direction
  2. Adjust the bearing direction (optional)
  3. Move the mouse a given number of pixels

This procedure can be combined with standard Talon mouse control commands to click, right-click or drag the mouse. 

#### Examples
A basic sequence:  

``` compass north ```  
``` go 300 ```  
``` Touch ```  

A more complicated sequence showing additional capabilities:

``` compass Center```  
``` north-northeast ```  
``` 5 right ```  
``` Drag ```  
``` Walk 300 ```  
``` Backup 15 ```  
``` Drag End ```  
``` compass Reverse ```  

<br/>

## Detailed Command List
(but maybe not comprehensive - always check actual talon files for most up to date list)

### Initialization
``` compass <compass direction> ```  
  * Starts compass from the current mouse position 
  * Compass directions include ```North``` ```East``` ```South``` ```West``` ```northeast``` ```southeast``` ```southwest``` ```northwest``` ```north-northeast``` ```east-northeast``` ```east-southeast``` ```south-southeast``` ```south-southwest``` ```west-southwest``` ```west-northwest``` ```north-northwest``` ```up``` ```right``` ```down``` ```left```  

### Commands available after initialization
``` <number> [degrees] <compass direction> ```
  * Rotates compass towards the new compass direction.
  * For fine control you can use decimal places, e.g. "zero point five west"

``` go <number> ```  
  * Move the mouse the specified distance in pixels in the compass direction.
  * Replace "go" with "move", "walk" or "crawl" for slower mouse movement.

``` backup <number> ```
  * Same as "go" but moves in the opposite direction.

``` compass Reverse ```
  * reverses the compass direction without moving.

``` compass Display (heavy|medium|light|tiny) ```
  * Adjusts the size and density of the tick marks and labels showing distances and directions on screen

## Distance and Direction Guides
A radial grid is displayed to guide direction and distance specification. Here are some visual landmarks:
  * Red lines are 500 pixels
  * Longer black/white lines are 100 pixels or 10 degrees
  * Shorter black/white lines are 50/10 pixels or 5/1 degrees
  * The end of the red arrow is 50 pixels
  * The outer edge of the red circle is 30 pixels
  
## Command Mode Management
Compass has been designed to allow for short voice commands while avoiding misrecognitions that can disrupt your workflow. Upon initialization:
  * Command Mode is turned off 
  * Compass Mode is turned on

To return to Command Mode:
  * Say "Exit Compass"
  * Perform a mouse action ("click" (or "touch"), "right-click", "drag end", "wheel downer")
  * Wait 15 seconds

All of the above options will enable Command Mode immediately. The last two options will also keep Compass Mode enabled for 5 seconds, so you can perform additional Compass actions without re-initializing.
  
# Feedback
I hope that you find this tool useful. Any feedback on how to improve Compass is welcome!
