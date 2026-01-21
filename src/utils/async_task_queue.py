"""
异步任务队列系统
支持多次任务提交、后台异步处理、实时状态追踪
"""

import threading
import queue
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from enum import Enum


class TaskType(str, Enum):
    """任务类型"""
    TEXT = "text"
    IMAGE = "image"
    BATCH = "batch"


class TaskStatus(str, Enum):
    """任务状态"""
    QUEUED = "queued"  # 排队中
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败


@dataclass
class Task:
    """任务数据类"""
    id: str
    type: TaskType
    status: TaskStatus = TaskStatus.QUEUED
    input_data: Any = None  # 输入数据（文本内容、文件路径等）
    generate_answers: bool = False
    export_format: str = "both"

    # 时间戳
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    # 结果
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: float = 0.0

    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)


class AsyncTaskQueue:
    """异步任务队列管理器（单例模式）"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._tasks: Dict[str, Task] = {}
            self._task_queue = queue.Queue()
            self._worker_thread: Optional[threading.Thread] = None
            self._running = False
            self._process_func: Optional[Callable] = None

    def set_process_function(self, func: Callable):
        """
        设置任务处理函数

        Args:
            func: 处理函数，接收 Task 对象，返回处理结果字典
        """
        self._process_func = func

    def start_worker(self):
        """启动后台工作线程"""
        if self._running:
            return

        self._running = True
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
        print("✓ 异步任务队列已启动")

    def stop_worker(self):
        """停止后台工作线程"""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
        print("✓ 异步任务队列已停止")

    def submit_task(
        self,
        task_type: TaskType,
        input_data: Any,
        generate_answers: bool = False,
        export_format: str = "both",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        提交新任务到队列

        Args:
            task_type: 任务类型
            input_data: 输入数据
            generate_answers: 是否生成答案
            export_format: 导出格式
            metadata: 额外的元数据

        Returns:
            任务ID
        """
        task_id = str(uuid.uuid4())

        task = Task(
            id=task_id,
            type=task_type,
            input_data=input_data,
            generate_answers=generate_answers,
            export_format=export_format,
            metadata=metadata or {}
        )

        self._tasks[task_id] = task
        self._task_queue.put(task_id)

        print(f"✓ 任务已提交: {task_id} (类型: {task_type}, 队列位置: {self._task_queue.qsize()})")

        return task_id

    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务详情"""
        return self._tasks.get(task_id)

    def get_all_tasks(self, status: Optional[str] = None) -> List[Task]:
        """
        获取所有任务

        Args:
            status: 可选，按状态过滤（字符串值："queued", "processing", "completed", "failed"）

        Returns:
            任务列表
        """
        tasks = list(self._tasks.values())

        if status:
            # 支持字符串比较（枚举的值）
            tasks = [t for t in tasks if t.status.value == status]

        # 按创建时间降序排列
        tasks.sort(key=lambda t: t.created_at, reverse=True)

        return tasks

    def get_queue_info(self) -> Dict[str, Any]:
        """获取队列统计信息"""
        tasks = list(self._tasks.values())

        return {
            "total_tasks": len(tasks),
            "queued": len([t for t in tasks if t.status == TaskStatus.QUEUED]),
            "processing": len([t for t in tasks if t.status == TaskStatus.PROCESSING]),
            "completed": len([t for t in tasks if t.status == TaskStatus.COMPLETED]),
            "failed": len([t for t in tasks if t.status == TaskStatus.FAILED]),
            "queue_size": self._task_queue.qsize(),
            "is_running": self._running
        }

    def _worker_loop(self):
        """后台工作线程主循环"""
        print("⊙ 任务处理线程已启动")

        while self._running:
            try:
                # 从队列获取任务（超时1秒）
                task_id = self._task_queue.get(timeout=1)

                task = self._tasks.get(task_id)
                if not task:
                    continue

                # 处理任务
                self._process_task(task)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"✗ 工作线程错误: {e}")

        print("⊙ 任务处理线程已停止")

    def _process_task(self, task: Task):
        """处理单个任务"""
        try:
            # 更新状态为处理中
            task.status = TaskStatus.PROCESSING
            task.started_at = datetime.now().isoformat()

            print(f"⊙ 开始处理任务: {task.id} (类型: {task.type})")

            start_time = time.time()

            # 调用处理函数
            if self._process_func:
                result = self._process_func(task)
                task.result = result
                task.status = TaskStatus.COMPLETED
                print(f"✓ 任务完成: {task.id} (耗时: {time.time() - start_time:.2f}s)")
            else:
                raise Exception("未设置任务处理函数")

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            print(f"✗ 任务失败: {task.id} - {e}")

        finally:
            task.completed_at = datetime.now().isoformat()
            task.processing_time = time.time() - start_time

    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """
        清理旧任务

        Args:
            max_age_hours: 最大保留时间（小时）
        """
        now = datetime.now()
        cutoff = now.timestamp() - (max_age_hours * 3600)

        tasks_to_remove = []
        for task_id, task in self._tasks.items():
            created_timestamp = datetime.fromisoformat(task.created_at).timestamp()
            if created_timestamp < cutoff:
                tasks_to_remove.append(task_id)

        for task_id in tasks_to_remove:
            del self._tasks[task_id]

        if tasks_to_remove:
            print(f"✓ 清理了 {len(tasks_to_remove)} 个旧任务")


# 全局单例实例
task_queue = AsyncTaskQueue()
