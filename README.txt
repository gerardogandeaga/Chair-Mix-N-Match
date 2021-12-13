STEPS TO RUN: 

You will have to delete the ./venv folder with...

$ rm -rf venv

then create a new virtual environment with...

$ python3 -m venv venv

Activate the new environment with (on unix or mac)...

$ source ./venv/bin/activate

Then install dependencies with...

$ pip install -r requirements.txt

Note:
If you're running on MacOS and you get an "import opengl" error then
you can fix it by modifying the following file:

./venv/lib/python3.8/site-packages/OpenGL/platform/ctypesloader.py

replace...

fullName = util.find_library( name ) 

at line 35 to...

fullName = "/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/System/Library/Frameworks/OpenGL.framework/OpenGL"