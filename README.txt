STEPS TO RUN: 

Clean first by running...

$ ./clean.sh
OR
$ bash ./clean.sh

Then to download the inputs and models and install dependencies run...

$ ./setup.sh
OR
$ bash ./setup.sh

Then...

$ source ./venv/bin/activate

to start the python environment

The main entry point is driver.py, call it with arguments: set and number of outputs.
E.g. python3 driver.py A 10
will generate 10 mixed objects in the output/ folder, and print generated probabilities sorted by scores.

Note:
If you're running on MacOS and you get an "import opengl" error then
you can fix it by modifying the following file:

./venv/lib/python3.8/site-packages/OpenGL/platform/ctypesloader.py

replace...

fullName = util.find_library( name ) 

at line 35 to...

fullName = "/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/System/Library/Frameworks/OpenGL.framework/OpenGL"