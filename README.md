# 用法

需要先pip安装pybind11

在此目录下的终端执行

```bash
> python setup.py install
```

其中，python是python3可执行文件的名字. 如果你的python3是用python就能执行的，就填python，否则填python3啥的

对于某些python2与python3共存的系统，python有可能指python2，这样是装不上的

此外，`./setup.py install`往往是不行的，因为类unix系统会把它当做一个shell脚本而不是python文件

由于需要编译，所以系统中肯定得有编译器，没装msvc的windows系统大概是没法装的

安装好后，你就可以

```Python
from libchessboard import Chessboard
chessboard = Chessboard(range(blablabla))
```
