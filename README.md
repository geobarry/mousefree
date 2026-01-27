# MouseFree for Windows
Talon commands for navigating windows by voice. The general capabilities are as follows (documentation on specific commands located within talon files as comments):

## Windows Accessibility Core
Core set of modules facilitating use of windows automation (UIAutomation). These modules have been developed over several years and include many tricks and defensive programming patterns to avoid stalls and crashes that are common with UIAutomation. 

### Auto Highlight
Automatically highlight and/or label currently focused element, so you don't have to guess.

### Win Accessibility
- Locate and navigate accessibility elements in applications using property lists and sequences.
- Wait for a particular element to come into focus.
- Automatically navigate through user interfaces using navigation keys (e.g. tab, right/left/up/down, f6) until a desired element is reached.
- Perform actions such as Select, Invoke, Expand, Collapse, etc. on accessibility elements.

### Text Selection
Navigate, select, replace, & format text dynamically using Windows Accessibility text patterns when available. Tested and used in Microsoft program such as MS Word. 

### App-Specific Modules
Modules for windows file explorer and talon (more to come). 

### Win Accessibility Dev
Utilities for investigating properties of accessibility elements and navigating/investigating elementary, for example to automatically capture and create commands for every item within a menu or ribbon. Some commands here can take a long time to complete so use with caution.

## Other Utilities
These are not inherently specific to windows, though there may be some windows accessibility dependencies that should be removed eventually.

### Compass
Control mouse with intuitive direction-distance framework.

### Mouse
Move mouse to anchor points on current screen, window or focused element.

### Slow Repeater
Continuously repeat commands and control repetition speed.

## Notes
### How Stable Is This?
Using UIAutomation is fraught with potential mishaps which can stall or crash the system. This seems to be a perennial problem for UIAutomation developers as has been noted by others in the talon slack channel. I have tried my best to write code that prevents such mishaps, and because I rely on this everyday and the element tracker is refreshing every 0.3 seconds, the code has been stress-tested quite rigorously. Nevertheless, this code may occasionally cause talon or windows to hang. 

To monitor this I always keep talon's log open. Stalls will be evident with repeated warnings, and if these go on for more than about 30 seconds I shut down and then restart talon.

### Are there specific issues to avoid or know about?
Yes, two.

Microsoft Excel seems to be a particular source of instability. At times, trying to access the currently focused element in Excel will stall. Once this happens, shutting down Excel will sometimes fix it, but at other times it seems to spiral into a doom loop that requires restarting talon. It is suggested that you completely avoid using accessibility with Excel.

The system tray is also problematic. Using this code to access talon options from the system tray works smoothly 50% of the time, but sometimes (often) gets into a situation where each action (expanding the tray, expanding an option within the tray) takes 20 seconds to complete - it always does complete eventually but typically there are three actions so it requires a full minute. 

### What steps are taken to avoid instability?
An attempt to understand what causes UIAutomation has led to the following techniques to avoid instabilities. 

First, it is observed that attempting to access a pattern that does not exist in an element, or call up a method or property on a variable that is assumed to be an accessibility element but actually is not, often causes unstable behavior. Thus built-in functions are designed to first check that an element or pattern exists before trying to access its methods.

Second, trying to use elements that are no longer active (i.e. "stale") is a known source of problems. All code attempts to use only accessibility elements that have just been retrieved.

Third, it appears that trying to query UIAutomation while another query is still in process will create unstable behavior. This problem seems to persist even in situations where I don't think that it should be possible for such conflicts to occur. Thus I have developed a system and protocol in which only one accessibility query is allowed at a time. Honestly it doesn't seem like this should be necessary, but every time I circumvent it the unstable behavior returns. I freely admit that I don't understand this one completely but the current system seems to avoid problems.

Fourth, applications known to cause issues have been blacklisted. Currently, this list only includes Microsoft Excel.

This is not a complete list, but an attempt to document the most important issues that I've experienced so that maybe others won't make the same mistakes.

Please note that I do not consider myself an expert programmer let alone an expert UIAutomation programmer. At the time of writing I think that I have explored UIAutomation with talon more than anybody else contributing regularly to the talon Slack, but that is out of necessity not because I have particular expertise. If you have suggestions or see things that I am doing wrong, or better yet want to contribute or collaborate, please let me know!

### Will this code be maintained & updated?
Maybe - let me know if you think this is useful! I've created this for my own personal use, but I've tried to structure it in a way that might be generally useful to others. I will admit however that I am not the most structured programmer. Issues and pull requests are welcome, though it may take me some time to address them. If you have general suggestions or ideas as to how to improve or maintain this repository, please contribute to the discussion by adding comments or sub issues under the "General" issue.