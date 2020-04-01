from multiprocessing import Process, Queue


def fn(q_recv, q_send, module_name, class_name, init_arg):
    '''
    此函数运行于与主进程不同的地址空间, 因此即使import白名单被绕过, 也难以对比赛平台进程造成影响
    '''
    import importlib
    # 导入类
    imported_module = importlib.import_module(module_name)
    del importlib
    imported_class = vars(imported_module)[class_name]
    imported_class_vars = vars(imported_class)
    # 遍历所有成员并返回成员函数名字列表. 仅支持访问成员函数.
    imported_class_methods = []
    for item in imported_class_vars:
        if hasattr(imported_class_vars[item], "__call__") and item != '__init__' and item != '__del__':
            imported_class_methods.append(item)
    q_send.put(imported_class_methods)

    # 导入类的实例. 类变量由于处于不同的进程中不能共享
    instance = imported_class(init_arg)

    # 循环接受命令
    while True:
        try:
            command = q_recv.get(block=True)
            fn = command[0]
            arg = command[1]
            # 销毁对象
            if fn == '__del__':
                del instance
                return
            res = imported_class_vars[fn](instance, *(arg))
            q_send.put([res, None])
        except Exception as e:
            q_send.put([None, e])


def secureimportandinstanceclass(module_name, class_name, init_arg, decoration=lambda x: x):
    '''
    返回一个傀儡对象, 具有要导入的类的所有方法, 会将可序列化参数转发给真正的对象.
    可以将
        from player import Player
        player0 = Player(init_arg)
    替换为
        player0 = secureimportandinstanceclass('player', 'Player', init_arg, decoration=timeManager(0))
    decoration将会被作用于所有方法上, 可用于计时/日志等目的.
    '''
    q_send = Queue()
    q_recv = Queue()
    p = Process(target=fn, args=(q_send, q_recv, module_name,
                                 class_name, init_arg), daemon=True)
    p.start()
    pdir = q_recv.get()

    class Puppet:
        pass

    def gen_stub(attr_name):
        '''
        根据attribute name生成对应的函数
        '''
        @decoration
        def stub(self, *args):
            q_send.put([attr_name, args])
            return q_recv.get()[0]  # 应当检查返回值类型并设置超时时间.
        return stub

    # 对构造函数和析构函数特殊处理
    def p__init__(self, *args):
        pass

    def p__del__(self):
        q_send.put(['__del__', []])
        p.kill()

    for item in pdir:
        setattr(Puppet, item, gen_stub(item))
    Puppet.__init__ = p__init__
    Puppet.__del__ = p__del__
    return Puppet()


if __name__ == "__main__":
    p = secureimportandinstanceclass("player", "Player", True)
    q = secureimportandinstanceclass("player", "Player", True)
    del p # 测试析构函数
    del q
