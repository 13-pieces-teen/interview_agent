"""
批量处理任务管理器
支持按顺序处理多个面经上传任务
"""

import uuid
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading
from pathlib import Path


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class SubTask:
    """单个子任务（对应一个文件）"""
    id: str
    file_path: str
    file_name: str
    status: TaskStatus = TaskStatus.PENDING
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    experience_id: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    processing_time: float = 0.0


@dataclass
class BatchTask:
    """批量任务"""
    id: str
    total_files: int
    created_at: str
    status: TaskStatus = TaskStatus.PENDING
    current_index: int = 0
    completed_count: int = 0
    failed_count: int = 0
    sub_tasks: List[SubTask] = field(default_factory=list)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    generate_answers: bool = False
    export_format: str = "both"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "total_files": self.total_files,
            "created_at": self.created_at,
            "status": self.status.value,
            "current_index": self.current_index,
            "completed_count": self.completed_count,
            "failed_count": self.failed_count,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "generate_answers": self.generate_answers,
            "export_format": self.export_format,
            "sub_tasks": [
                {
                    "id": st.id,
                    "file_name": st.file_name,
                    "status": st.status.value,
                    "error": st.error,
                    "experience_id": st.experience_id,
                    "started_at": st.started_at,
                    "completed_at": st.completed_at,
                    "processing_time": st.processing_time,
                }
                for st in self.sub_tasks
            ]
        }


class BatchProcessor:
    """批量任务处理器 - 单例模式"""

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
            self.tasks: Dict[str, BatchTask] = {}
            self.processing_threads: Dict[str, threading.Thread] = {}
            self._initialized = True

    def create_batch_task(
        self,
        file_paths: List[str],
        file_names: List[str],
        generate_answers: bool = False,
        export_format: str = "both"
    ) -> str:
        """
        创建批量任务

        Args:
            file_paths: 文件路径列表
            file_names: 文件名列表
            generate_answers: 是否生成答案
            export_format: 导出格式

        Returns:
            任务ID
        """
        task_id = str(uuid.uuid4())

        # 创建子任务
        sub_tasks = [
            SubTask(
                id=str(uuid.uuid4()),
                file_path=file_path,
                file_name=file_name
            )
            for file_path, file_name in zip(file_paths, file_names)
        ]

        # 创建批量任务
        batch_task = BatchTask(
            id=task_id,
            total_files=len(file_paths),
            created_at=datetime.now().isoformat(),
            sub_tasks=sub_tasks,
            generate_answers=generate_answers,
            export_format=export_format
        )

        self.tasks[task_id] = batch_task
        return task_id

    def start_batch_processing(
        self,
        task_id: str,
        process_func: Callable[[str, str, bool, str], Dict[str, Any]]
    ):
        """
        启动批量处理（后台线程）

        Args:
            task_id: 任务ID
            process_func: 处理函数，接收(file_path, file_name, generate_answers, export_format)
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")

        if task_id in self.processing_threads:
            raise ValueError(f"Task {task_id} is already processing")

        # 创建处理线程
        thread = threading.Thread(
            target=self._process_batch,
            args=(task_id, process_func),
            daemon=True
        )
        self.processing_threads[task_id] = thread
        thread.start()

    def _process_batch(
        self,
        task_id: str,
        process_func: Callable[[str, str, bool, str], Dict[str, Any]]
    ):
        """
        内部方法：按顺序处理批量任务

        Args:
            task_id: 任务ID
            process_func: 处理函数
        """
        task = self.tasks[task_id]
        task.status = TaskStatus.PROCESSING
        task.started_at = datetime.now().isoformat()

        try:
            # 按顺序处理每个子任务
            for index, sub_task in enumerate(task.sub_tasks):
                task.current_index = index
                sub_task.status = TaskStatus.PROCESSING
                sub_task.started_at = datetime.now().isoformat()

                try:
                    start_time = time.time()

                    # 调用处理函数
                    result = process_func(
                        sub_task.file_path,
                        sub_task.file_name,
                        task.generate_answers,
                        task.export_format
                    )

                    # 记录结果
                    sub_task.status = TaskStatus.COMPLETED
                    sub_task.result = result
                    sub_task.experience_id = result.get("experience_id")
                    sub_task.completed_at = datetime.now().isoformat()
                    sub_task.processing_time = time.time() - start_time

                    task.completed_count += 1

                except Exception as e:
                    # 记录错误
                    sub_task.status = TaskStatus.FAILED
                    sub_task.error = str(e)
                    sub_task.completed_at = datetime.now().isoformat()
                    task.failed_count += 1

                finally:
                    # 清理临时文件
                    try:
                        Path(sub_task.file_path).unlink(missing_ok=True)
                    except Exception:
                        pass

            # 批量任务完成
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()

        except Exception as e:
            # 批量任务失败
            task.status = TaskStatus.FAILED
            print(f"Batch task {task_id} failed: {e}")

        finally:
            # 清理线程引用
            if task_id in self.processing_threads:
                del self.processing_threads[task_id]

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态字典，如果任务不存在返回None
        """
        task = self.tasks.get(task_id)
        if task is None:
            return None
        return task.to_dict()

    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务（仅能取消未开始的任务）

        Args:
            task_id: 任务ID

        Returns:
            是否成功取消
        """
        task = self.tasks.get(task_id)
        if task is None:
            return False

        if task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
            return True

        return False

    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """
        清理旧任务（释放内存）

        Args:
            max_age_hours: 最大保留时间（小时）
        """
        current_time = datetime.now()
        tasks_to_remove = []

        for task_id, task in self.tasks.items():
            created_at = datetime.fromisoformat(task.created_at)
            age_hours = (current_time - created_at).total_seconds() / 3600

            # 只清理已完成、失败或取消的任务
            if age_hours > max_age_hours and task.status in [
                TaskStatus.COMPLETED,
                TaskStatus.FAILED,
                TaskStatus.CANCELLED
            ]:
                tasks_to_remove.append(task_id)

        for task_id in tasks_to_remove:
            del self.tasks[task_id]

    def get_all_tasks(self, status_filter: Optional[TaskStatus] = None) -> List[Dict[str, Any]]:
        """
        获取所有任务

        Args:
            status_filter: 状态过滤器

        Returns:
            任务列表
        """
        tasks = list(self.tasks.values())

        if status_filter:
            tasks = [t for t in tasks if t.status == status_filter]

        return [t.to_dict() for t in tasks]


# 全局单例实例
batch_processor = BatchProcessor()
