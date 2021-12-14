STEPS TO RUN: 

Clean first by running...

$ ./clean.sh

Then to download the inputs and models and install dependencies run...

$ ./setup.sh

Then...

$ source ./venv/bin/activate

to start the python environment

Note:
If you're running on MacOS and you get an "import opengl" error then
you can fix it by modifying the following file:

./venv/lib/python3.8/site-packages/OpenGL/platform/ctypesloader.py

replace...

fullName = util.find_library( name ) 

at line 35 to...

fullName = "/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/System/Library/Frameworks/OpenGL.framework/OpenGL"