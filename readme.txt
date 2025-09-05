Troubleshooting:
When I start the project I use the newest Python in my time Python 3.13.7 and it's kind of unstable when I first set up the project this Python 3.13.7 break pip installer while I run Unicorn. And when I try to redownload and reinstall the Python 3.13.7 it shows that it have an error and cannot do that which is not a very nice experience. So use just stable Python like Python 3.12.5

I meet an error when using FastAPI and SQLAlchemy together. This error is like this. For example, we have three files. File1, File2, and File3. I write Base and engine (signed the value create_engine( )) in File3.  In File2 I import Base and engine from File3. In File1, I import Base and engine from File2. When I run uvicorn, system say there is an error: there isn't File3 module. Python itself can support this kind of usage. I can run Python directly in those three files no error. But if I run uvicorn, then it will have error. My solution is to merge file 2 and file 3, and then uvicorn can run smoothly.


Formatting and naming convention
all python file is using Camel case such as: testDateTime.py