#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速单页网站生成器 - 优化生成速度"""

from typing import Dict, Any, Optional, List
import json


class QuickSiteGenerator:
    """快速生成单页面网站的辅助类"""
    
    @staticmethod
    def create_single_page_plan(
        project_name: str,
        site_type: str,
        description: str
    ) -> Dict[str, Any]:
        """创建单页面网站的简化计划
        
        Args:
            project_name: 项目名称
            site_type: 网站类型（咖啡店、企业、作品集等）
            description: 用户需求描述
            
        Returns:
            简化的执行计划
        """
        
        # 基础步骤（所有类型通用）
        base_steps = [
            {
                "step": 1,
                "tool": "create_project_structure",
                "params": {
                    "project_name": project_name,
                    "project_path": "."
                },
                "description": "创建项目目录结构",
                "rationale": "建立规范的项目结构"
            },
            {
                "step": 2,
                "tool": "create_css_file",
                "params": {
                    "file_path": "assets/css/style.css"
                },
                "description": "创建样式文件",
                "rationale": "定义网站视觉风格"
            },
            {
                "step": 3,
                "tool": "create_js_file",
                "params": {
                    "file_path": "assets/js/main.js"
                },
                "description": "创建交互脚本",
                "rationale": "添加动态效果和交互"
            },
            {
                "step": 4,
                "tool": "create_html_file",
                "params": {
                    "file_path": "index.html",
                    "title": f"{project_name} - 首页"
                },
                "description": "创建单页面网站主文件",
                "rationale": "生成包含所有内容的单页面"
            },
            {
                "step": 5,
                "tool": "add_bootstrap",
                "params": {
                    "project_path": "."
                },
                "description": "添加Bootstrap框架",
                "rationale": "加速响应式开发"
            },
            {
                "step": 6,
                "tool": "create_responsive_navbar",
                "params": {
                    "file_path": "index.html",
                    "brand_name": project_name,
                    "nav_items": QuickSiteGenerator._get_nav_items(site_type)
                },
                "description": "创建导航栏",
                "rationale": "页面内导航锚点"
            },
            {
                "step": 7,
                "tool": "inject_images",
                "params": {
                    "file_path": "index.html",
                    "provider": "pollinations",
                    "topics": QuickSiteGenerator._get_image_topics(site_type),
                    "size": "1920x1080",
                    "save": True
                },
                "description": "注入AI生成图片",
                "rationale": "添加视觉内容"
            },
            {
                "step": 8,
                "tool": "open_in_browser",
                "params": {
                    "file_path": "index.html"
                },
                "description": "浏览器预览",
                "rationale": "查看最终效果"
            }
        ]
        
        # 根据网站类型定制配色
        color_scheme = QuickSiteGenerator._get_color_scheme(site_type)
        
        return {
            "task_analysis": f"快速生成{site_type}单页面网站",
            "project_name": project_name,
            "site_type": site_type,
            "design_style": "现代简洁",
            "color_scheme": color_scheme,
            "estimated_time": "2-3分钟",
            "tools_sequence": base_steps
        }
    
    @staticmethod
    def _get_nav_items(site_type: str) -> List[Dict[str, str]]:
        """根据网站类型返回导航项（锚点链接）"""
        
        nav_templates = {
            "咖啡店": [
                {"name": "首页", "link": "#hero"},
                {"name": "菜单", "link": "#menu"},
                {"name": "关于", "link": "#about"},
                {"name": "联系", "link": "#contact"}
            ],
            "企业": [
                {"name": "首页", "link": "#hero"},
                {"name": "服务", "link": "#services"},
                {"name": "关于", "link": "#about"},
                {"name": "联系", "link": "#contact"}
            ],
            "作品集": [
                {"name": "首页", "link": "#hero"},
                {"name": "作品", "link": "#portfolio"},
                {"name": "技能", "link": "#skills"},
                {"name": "联系", "link": "#contact"}
            ],
            "餐厅": [
                {"name": "首页", "link": "#hero"},
                {"name": "菜单", "link": "#menu"},
                {"name": "预约", "link": "#booking"},
                {"name": "位置", "link": "#location"}
            ]
        }
        
        # 默认导航
        default = [
            {"name": "首页", "link": "#hero"},
            {"name": "介绍", "link": "#about"},
            {"name": "服务", "link": "#services"},
            {"name": "联系", "link": "#contact"}
        ]
        
        # 查找最匹配的类型
        for key in nav_templates:
            if key in site_type:
                return nav_templates[key]
        
        return default
    
    @staticmethod
    def _get_image_topics(site_type: str) -> List[str]:
        """根据网站类型返回图片主题"""
        
        topics_map = {
            "咖啡": ["coffee shop interior modern", "latte art", "coffee beans", "cozy cafe"],
            "餐厅": ["restaurant interior elegant", "gourmet food", "dining table", "chef cooking"],
            "企业": ["modern office", "business team", "corporate building", "technology workspace"],
            "作品集": ["creative workspace", "design portfolio", "artistic studio", "digital art"],
            "电商": ["product showcase", "online shopping", "ecommerce", "shopping cart"],
            "博客": ["writing desk", "laptop workspace", "books and coffee", "minimal desk setup"]
        }
        
        # 查找匹配的主题
        for key, topics in topics_map.items():
            if key in site_type:
                return topics
        
        # 默认主题
        return ["modern website hero", "business concept", "technology background", "professional workspace"]
    
    @staticmethod
    def _get_color_scheme(site_type: str) -> Dict[str, str]:
        """根据网站类型返回配色方案"""
        
        schemes = {
            "咖啡": {
                "primary": "#6F4E37",  # 咖啡棕
                "secondary": "#C8A882",  # 奶泡色
                "accent": "#D2691E"  # 焦糖色
            },
            "餐厅": {
                "primary": "#8B0000",  # 深红
                "secondary": "#FFD700",  # 金色
                "accent": "#228B22"  # 森林绿
            },
            "企业": {
                "primary": "#003366",  # 企业蓝
                "secondary": "#F0F0F0",  # 浅灰
                "accent": "#FF6B35"  # 橙色
            },
            "作品集": {
                "primary": "#2C3E50",  # 深蓝灰
                "secondary": "#ECF0F1",  # 云白
                "accent": "#E74C3C"  # 红色
            },
            "电商": {
                "primary": "#FF6B6B",  # 珊瑚红
                "secondary": "#4ECDC4",  # 青绿
                "accent": "#FFE66D"  # 黄色
            }
        }
        
        # 查找匹配的配色
        for key, scheme in schemes.items():
            if key in site_type:
                return scheme
        
        # 默认配色（现代通用）
        return {
            "primary": "#3B82F6",  # 蓝色
            "secondary": "#F3F4F6",  # 浅灰
            "accent": "#10B981"  # 绿色
        }
    
    @staticmethod
    def optimize_for_speed(plan: Dict[str, Any]) -> Dict[str, Any]:
        """优化计划以提升生成速度
        
        - 移除不必要的验证步骤
        - 简化图片生成
        - 减少工具调用次数
        """
        optimized_steps = []
        
        for step in plan.get("tools_sequence", []):
            tool = step.get("tool", "")
            
            # 跳过验证类工具（可选）
            if tool in ["validate_html", "check_mobile_friendly"]:
                continue
                
            # 简化图片参数
            if tool == "inject_images":
                params = step.get("params", {})
                # 限制图片数量
                if "topics" in params and len(params["topics"]) > 3:
                    params["topics"] = params["topics"][:3]
                # 使用较小的尺寸
                if "size" in params:
                    params["size"] = "1280x720"
                step["params"] = params
            
            optimized_steps.append(step)
        
        plan["tools_sequence"] = optimized_steps
        plan["estimated_time"] = "1-2分钟"
        
        return plan