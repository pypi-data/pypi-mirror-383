#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集群状态管理模块 - 支持分布式部署
"""

import json
import time
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StateManager:
    """
    抽象状态管理器基类
    可以有多种实现：RedisStateManager, PostgreSQLStateManager, MongoDBStateManager
    """
    
    def create_task(self, task_id: str, user_input: str, project_directory: str, metadata: dict = None) -> bool:
        """创建新任务"""
        raise NotImplementedError
    
    def update_task_status(self, task_id: str, status: TaskStatus, message: str = None) -> bool:
        """更新任务状态"""
        raise NotImplementedError
    
    def get_task_status(self, task_id: str) -> Optional[dict]:
        """获取任务状态"""
        raise NotImplementedError
    
    def add_created_file(self, task_id: str, file_path: str, size: int = 0) -> bool:
        """记录创建的文件"""
        raise NotImplementedError
    
    def get_created_files(self, task_id: str) -> List[str]:
        """获取任务创建的所有文件"""
        raise NotImplementedError
    
    def add_execution_step(self, task_id: str, step: dict) -> bool:
        """添加执行步骤记录"""
        raise NotImplementedError
    
    def get_execution_history(self, task_id: str) -> List[dict]:
        """获取执行历史"""
        raise NotImplementedError
    
    def acquire_lock(self, resource_id: str, timeout: int = 10) -> bool:
        """获取分布式锁"""
        raise NotImplementedError
    
    def release_lock(self, resource_id: str) -> bool:
        """释放分布式锁"""
        raise NotImplementedError


class RedisStateManager(StateManager):
    """基于 Redis 的状态管理器"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        try:
            import redis
            from redis.lock import Lock
        except ImportError:
            raise ImportError("请安装 redis: pip install redis")
        
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.Lock = Lock
        
    def create_task(self, task_id: str, user_input: str, project_directory: str, metadata: dict = None) -> bool:
        """创建新任务"""
        task_data = {
            "task_id": task_id,
            "user_input": user_input,
            "project_directory": project_directory,
            "status": TaskStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # 使用 Hash 存储任务基本信息
        self.redis.hset(f"task:{task_id}", mapping={
            k: json.dumps(v) if isinstance(v, (dict, list)) else str(v)
            for k, v in task_data.items()
        })
        
        # 设置过期时间（7天）
        self.redis.expire(f"task:{task_id}", 7 * 24 * 3600)
        
        return True
    
    def update_task_status(self, task_id: str, status: TaskStatus, message: str = None) -> bool:
        """更新任务状态"""
        updates = {
            "status": status.value,
            "updated_at": datetime.now().isoformat()
        }
        if message:
            updates["message"] = message
        
        self.redis.hset(f"task:{task_id}", mapping=updates)
        return True
    
    def get_task_status(self, task_id: str) -> Optional[dict]:
        """获取任务状态"""
        data = self.redis.hgetall(f"task:{task_id}")
        if not data:
            return None
        
        # 反序列化 JSON 字段
        for key in ["metadata"]:
            if key in data:
                try:
                    data[key] = json.loads(data[key])
                except (json.JSONDecodeError, TypeError):
                    pass
        
        return data
    
    def add_created_file(self, task_id: str, file_path: str, size: int = 0) -> bool:
        """记录创建的文件"""
        file_info = {
            "path": file_path,
            "size": size,
            "created_at": datetime.now().isoformat()
        }
        
        # 使用 List 存储文件列表
        self.redis.rpush(f"task:{task_id}:files", json.dumps(file_info))
        self.redis.expire(f"task:{task_id}:files", 7 * 24 * 3600)
        
        return True
    
    def get_created_files(self, task_id: str) -> List[str]:
        """获取任务创建的所有文件"""
        files_json = self.redis.lrange(f"task:{task_id}:files", 0, -1)
        files = []
        for file_json in files_json:
            try:
                file_info = json.loads(file_json)
                files.append(file_info["path"])
            except (json.JSONDecodeError, KeyError):
                continue
        return files
    
    def add_execution_step(self, task_id: str, step: dict) -> bool:
        """添加执行步骤记录"""
        step_data = {
            **step,
            "timestamp": datetime.now().isoformat()
        }
        
        # 使用 List 存储执行历史
        self.redis.rpush(f"task:{task_id}:history", json.dumps(step_data))
        self.redis.expire(f"task:{task_id}:history", 7 * 24 * 3600)
        
        return True
    
    def get_execution_history(self, task_id: str) -> List[dict]:
        """获取执行历史"""
        history_json = self.redis.lrange(f"task:{task_id}:history", 0, -1)
        history = []
        for step_json in history_json:
            try:
                history.append(json.loads(step_json))
            except json.JSONDecodeError:
                continue
        return history
    
    def acquire_lock(self, resource_id: str, timeout: int = 10) -> bool:
        """获取分布式锁"""
        lock = self.redis.lock(f"lock:{resource_id}", timeout=timeout)
        return lock.acquire(blocking=True, blocking_timeout=timeout)
    
    def release_lock(self, resource_id: str) -> bool:
        """释放分布式锁"""
        try:
            lock = self.redis.lock(f"lock:{resource_id}")
            lock.release()
            return True
        except Exception:
            return False


class DatabaseStateManager(StateManager):
    """基于 PostgreSQL/MySQL 的状态管理器"""
    
    def __init__(self, db_url: str):
        try:
            from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, JSON
            from sqlalchemy.ext.declarative import declarative_base
            from sqlalchemy.orm import sessionmaker
        except ImportError:
            raise ImportError("请安装 sqlalchemy: pip install sqlalchemy psycopg2-binary")
        
        self.engine = create_engine(db_url)
        Base = declarative_base()
        
        # 定义数据模型
        class Task(Base):
            __tablename__ = 'agent_tasks'
            
            task_id = Column(String(64), primary_key=True)
            user_input = Column(Text)
            project_directory = Column(String(512))
            status = Column(String(20))
            message = Column(Text, nullable=True)
            metadata = Column(JSON, nullable=True)
            created_at = Column(DateTime, default=datetime.now)
            updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
        
        class CreatedFile(Base):
            __tablename__ = 'agent_files'
            
            id = Column(Integer, primary_key=True, autoincrement=True)
            task_id = Column(String(64), index=True)
            file_path = Column(String(1024))
            size = Column(Integer, default=0)
            created_at = Column(DateTime, default=datetime.now)
        
        class ExecutionStep(Base):
            __tablename__ = 'agent_execution_history'
            
            id = Column(Integer, primary_key=True, autoincrement=True)
            task_id = Column(String(64), index=True)
            step = Column(Integer)
            tool = Column(String(100))
            status = Column(String(20))
            result = Column(Text)
            duration = Column(Integer, default=0)
            created_at = Column(DateTime, default=datetime.now)
        
        Base.metadata.create_all(self.engine)
        
        self.Session = sessionmaker(bind=self.engine)
        self.Task = Task
        self.CreatedFile = CreatedFile
        self.ExecutionStep = ExecutionStep
    
    def create_task(self, task_id: str, user_input: str, project_directory: str, metadata: dict = None) -> bool:
        """创建新任务"""
        session = self.Session()
        try:
            task = self.Task(
                task_id=task_id,
                user_input=user_input,
                project_directory=project_directory,
                status=TaskStatus.PENDING.value,
                metadata=metadata
            )
            session.add(task)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"创建任务失败: {e}")
            return False
        finally:
            session.close()
    
    def update_task_status(self, task_id: str, status: TaskStatus, message: str = None) -> bool:
        """更新任务状态"""
        session = self.Session()
        try:
            task = session.query(self.Task).filter_by(task_id=task_id).first()
            if task:
                task.status = status.value
                task.updated_at = datetime.now()
                if message:
                    task.message = message
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"更新任务状态失败: {e}")
            return False
        finally:
            session.close()
    
    def get_task_status(self, task_id: str) -> Optional[dict]:
        """获取任务状态"""
        session = self.Session()
        try:
            task = session.query(self.Task).filter_by(task_id=task_id).first()
            if not task:
                return None
            
            return {
                "task_id": task.task_id,
                "user_input": task.user_input,
                "project_directory": task.project_directory,
                "status": task.status,
                "message": task.message,
                "metadata": task.metadata,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None
            }
        finally:
            session.close()
    
    def add_created_file(self, task_id: str, file_path: str, size: int = 0) -> bool:
        """记录创建的文件"""
        session = self.Session()
        try:
            file_record = self.CreatedFile(
                task_id=task_id,
                file_path=file_path,
                size=size
            )
            session.add(file_record)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"记录文件失败: {e}")
            return False
        finally:
            session.close()
    
    def get_created_files(self, task_id: str) -> List[str]:
        """获取任务创建的所有文件"""
        session = self.Session()
        try:
            files = session.query(self.CreatedFile).filter_by(task_id=task_id).all()
            return [f.file_path for f in files]
        finally:
            session.close()
    
    def add_execution_step(self, task_id: str, step: dict) -> bool:
        """添加执行步骤记录"""
        session = self.Session()
        try:
            step_record = self.ExecutionStep(
                task_id=task_id,
                step=step.get("step", 0),
                tool=step.get("tool", ""),
                status=step.get("status", ""),
                result=json.dumps(step.get("result", "")),
                duration=step.get("duration", 0)
            )
            session.add(step_record)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"记录执行步骤失败: {e}")
            return False
        finally:
            session.close()
    
    def get_execution_history(self, task_id: str) -> List[dict]:
        """获取执行历史"""
        session = self.Session()
        try:
            steps = session.query(self.ExecutionStep).filter_by(task_id=task_id).order_by(self.ExecutionStep.step).all()
            return [
                {
                    "step": s.step,
                    "tool": s.tool,
                    "status": s.status,
                    "result": s.result,
                    "duration": s.duration,
                    "created_at": s.created_at.isoformat() if s.created_at else None
                }
                for s in steps
            ]
        finally:
            session.close()
    
    def acquire_lock(self, resource_id: str, timeout: int = 10) -> bool:
        """获取分布式锁（需要配合数据库锁实现）"""
        # PostgreSQL 可以使用 advisory lock
        # MySQL 可以使用 GET_LOCK
        # 这里简化实现，实际应使用数据库特定的锁机制
        return True
    
    def release_lock(self, resource_id: str) -> bool:
        """释放分布式锁"""
        return True


def create_state_manager(backend: str = "redis", connection_string: str = None) -> StateManager:
    """
    工厂函数：根据配置创建状态管理器
    
    Args:
        backend: 后端类型，支持 'redis', 'postgresql', 'mysql'
        connection_string: 连接字符串
            - Redis: redis://localhost:6379/0
            - PostgreSQL: postgresql://user:pass@localhost/dbname
            - MySQL: mysql://user:pass@localhost/dbname
    
    Returns:
        StateManager 实例
    """
    if backend == "redis":
        return RedisStateManager(connection_string or "redis://localhost:6379/0")
    elif backend in ["postgresql", "mysql"]:
        if not connection_string:
            raise ValueError(f"{backend} 需要提供 connection_string")
        return DatabaseStateManager(connection_string)
    else:
        raise ValueError(f"不支持的后端类型: {backend}")
