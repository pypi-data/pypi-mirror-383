"""
用Obsidian做KanBan管理, 本质是特殊格式的Markdown文件, 可视作KanBan的SDK
"""
from enum import Enum
from canvaz.core import Canvas,Color
from ..utils import sync_obsidian_github,controlKanban, read,write
from ..log import Log
logger = Log.logger
class Pool(Enum):
    """
    任务池类型枚举类。

    用于标识任务在看板中的不同状态池，包括：
        - 预备池：任务尚未准备好进入流程,是一个任务的集中地.
        - 就绪池：任务已准备好，添加了一些任务必要的信息,可以开始执行。
        - 阻塞池：任务因某些原因被阻塞，暂时无法继续。
        - 执行池：正在进行中的任务。
        - 完成池：已完成的任务。
        - 酱油池：无关紧要或暂时搁置的任务。

    Args:
        Enum (enum.Enum): 枚举基类，用于定义一组常量。
    """
    预备池 ='预备池'
    就绪池 ='就绪池'
    阻塞池 ='阻塞池'
    执行池 ='执行池'
    完成池 ='完成池'
    酱油池 ='酱油池'


class Kanban():
    """看板管理SDK 
    """
    def __init__(self,kanban_path:str):
        """
        初始化 Kanban 实例。

        Args:
            kanban_path (str): 看板文件的路径。
        """
        logger.info('初始化')
        self.kanban_path = kanban_path
        self.kanban_dict = {}

    def pull(self) -> None:
        """
        从文档拉取信息到 kanban_dict 属性。

        该方法会打开指定的看板文件（self.kanban_path），读取其内容，并使用 read 方法解析文本内容，
        最终将解析后的数据存储到 kanban_dict 属性中，便于后续操作。
        """
        logger.info('pull')
        with open(self.kanban_path, 'r', encoding="utf-8") as f:
            text = f.read()
        self.kanban_dict = read(text)

    def push(self) -> None:
        """
        将当前 kanban_dict 的内容序列化并保存到看板文件。

        本方法会调用 write(self.kanban_dict) 将字典内容转为文本，
        并以 UTF-8 编码写入 self.kanban_path 指定的文件，实现数据持久化。
        """
        logger.info('push')
        text = write(self.kanban_dict)
        with open(self.kanban_path, 'w', encoding="utf-8") as f:
            f.write(text)

    def insert(self, text: str, pool: Pool) -> None:
        """
        在指定的池中插入一条新的任务信息。

        Args:
            text (str): 任务的描述信息。
            pool (Pool): 要插入任务的池。

        Returns:
            None
        """
        logger.info('insert')
        self.kanban_dict[pool.value].append({'status': ' ',
                                             'description': text, 
                                             'id': 12, 'level': 2})

    def pop(self, text: str, pool: Pool) -> list["task"]:
        """
        从指定的池中删除一条任务信息。

        Args:
            text (str): 用于匹配的任务信息，可以是描述或ID。
            pool (Pool): 要从中删除任务的池。

        Returns:
            None
        """
        logger.info('pop')
        def delete_by_description(data: list, description: str) -> list:
            for i, item in enumerate(data):
                if item.get('description') == description:
                    del data[i]
                    return data
            logger.warning(f"未找到描述为 '{description}' 的数据列")
            return data

        data = self.kanban_dict[pool.value]
        return delete_by_description(data, text)

    def get_tasks_in(self, pool:Pool)->list[str]:
        """获取事件池中的任务

        Args:
            pool (Pool): 枚举的池类型

        Returns:
            list[str]: 返回对应的事件名称列表
        """
        logger.info('get_tasks_in')
        pools = self.kanban_dict.get(pool.value)
        return [des.get("description") for des in pools]

    def get_task_by_word(self,word:str, pool:Pool | None = None)->list[str]:
        """通过关键字查询任务

        Args:
            word (str): 关键字
            pool (Pool | None, optional): 任务池,枚举类型.. Defaults to None.

        Returns:
            list[str]: 返回查询到的任务列表

        """
        logger.info('get_task_by_word')
        output = []
        if pool is None:
            for _ , content in self.kanban_dict.items():
                for core in content:
                    if word in core.get('description'):
                        output.append(core.get("description"))
        else:
            content = self.kanban_dict.get(pool.value)
            for core in content:
                if word in core.get('description'):
                    output.append(core.get("description"))

        return output



class KanBanManager():
    def __init__(self,kanban_path:str,pathlibs:list[str]):
        """看板管理类

        Args:
            kanban_path (str): 看板文件路径 for example kb/x.md
            pathlibs (list[str]): 列表, 元素为所有监听的canvas文件路径

        for example:
            pathlibs = ["/工程系统级设计/项目级别/DigitalLife/DigitalLife.canvas",
                "/工程系统级设计/项目级别/近期工作/近期工作.canvas",
                "/工程系统级设计/项目级别/coder/coder.canvas",]
        """
        self.pathlibs = pathlibs
        self.kanban = Kanban(kanban_path)
        self.main_path = "/Users/zhaoxuefeng/GitHub/obsidian/工作"

    def sync_ready(self):
        """将任务从各canvas文件中提取出, 汇总到预备池
        """
        def encode(i,project_name):
            return project_name+'$'+i
        
        def save_in_pauses(i,pauses):
            for pause in pauses:
                if i.get('text') in pause:
                    return True
            return False

        for path in self.pathlibs:
            canvas_path=self.main_path+path
            try:
                canvas = Canvas(file_path=canvas_path)
            except FileNotFoundError as e:
                print(e)
                continue
            with controlKanban(self.kanban) as kb:
                project_name = canvas_path.rsplit('/',2)[-2] 
                pauses = kb.get_tasks_in(pool=Pool.阻塞池)
                readys = kb.get_tasks_in(pool=Pool.就绪池) + kb.get_tasks_in(pool=Pool.执行池)

                nodes = [i.get('text') or '' for i in canvas.select_by_color(Color.yellow,type='node') if not save_in_pauses(i,pauses=pauses)]
                for i in nodes:
                    if i not in readys:
                        kb.insert(text=encode(i,project_name),pool=Pool.预备池)
        return 'success'
        
    def _give_a_task_time(self,task:str,by='code'):
        """_summary_

        Args:
            task (str): _description_
            by (str, optional): _description_. Defaults to 'code'.

        Returns:
            str: _description_
        """
        if by == 'llm':
            from llmada.core import GoogleAdapter,BianXieAdapter
            from promptlibz import Templates,TemplateType

            llm = BianXieAdapter()
            template = Templates(TemplateType.ESTIMATE_DURATION)
            prompt = template.format(task=task)
            try:
                completion = llm.product(prompt)
            except Exception as e:
                print(f'大模型服务未连接: {e}')
                completion = "大模型服务未连接"
            if completion and len(completion)<5:
                return completion + " "+ task
            else:
                return "2P" + " "+ task
        else:
            return "1P" + " "+ task

    def sync_order(self,by='code'):
        """将预备池中的任务进行加工,并添加到就绪池

        Args:
            by (str, optional): 使用何种方式预估任务时间 支持code 与 llm 模式. Defaults to 'code'.

        Returns:
            None: _description_
        """
        with sync_obsidian_github("调整优先级"):
            with controlKanban(self.kanban) as kb:
                tasks = kb.get_tasks_in(Pool.预备池)
                order_tasks = kb.get_tasks_in(Pool.就绪池)
                orders = ' '.join(order_tasks)
                for task in tasks:
                    kb.pop(text = task,pool = Pool.预备池)
                    if task not in orders:
                        task_ = self._give_a_task_time(task,by=by)
                        
                        kb.insert(text=task_,pool=Pool.就绪池)

    def sync_run(self,max_p = 14):
        """将就绪池的排好顺序的任务移动到执行池中, 以填充一天的工作量

        Args:
            max_p (int, optional): 1P代表半小时, 该参数表示填充的最大工作时长, 也和之前的任务耗时估计有联系, 不超过max_p. Defaults to 14.

        Returns:
            None: _description_
        """
        with sync_obsidian_github("同步到执行池"):
            with controlKanban(self.kanban) as kb:
                tasks = kb.get_tasks_in(Pool.就绪池)
                all_task_time = 0
                for task in tasks:
                    if task.split(' ')[0][-1].lower() != 'p':
                        continue
                    task_time = int(task.split(' ')[0][:-1])

                    if all_task_time + task_time <=max_p:
                        all_task_time += task_time
                        kb.pop(text=task,pool=Pool.就绪池)
                        kb.insert(text=task,pool=Pool.执行池)

                    elif all_task_time < 8:
                        pass
