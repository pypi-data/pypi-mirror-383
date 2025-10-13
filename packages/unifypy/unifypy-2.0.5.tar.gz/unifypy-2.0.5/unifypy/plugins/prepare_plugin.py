#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

from unifypy.core.plugin import BasePlugin
from unifypy.core.event_bus import EventBus
from unifypy.core.events import PREPARE
from unifypy.utils.file_ops import FileOperations


class PreparePlugin(BasePlugin):
    name = "prepare"
    priority = 40

    def register(self, bus: EventBus):
        bus.subscribe(PREPARE, self.prepare, priority=self.priority)

    def prepare(self, ctx):
        stage = "环境准备"
        if ctx.progress:
            ctx.progress.start_stage(stage, "创建构建目录和临时文件")

        ctx.file_ops = ctx.file_ops or FileOperations()

        # 创建临时目录
        temp_dir = ctx.file_ops.create_temp_dir("unifypy_build_")
        ctx.temp_dir = Path(temp_dir)
        if ctx.progress:
            ctx.progress.update_stage(stage, 20, f"创建临时目录: {ctx.temp_dir}", absolute=True)

        # 创建输出目录
        ctx.file_ops.ensure_dir(str(ctx.dist_dir))
        ctx.file_ops.ensure_dir(str(ctx.installer_dir))
        if ctx.progress:
            ctx.progress.update_stage(stage, 40, "创建输出目录", absolute=True)

        # 清理旧文件（按需）
        if getattr(ctx.args, "clean", False):
            if ctx.progress:
                ctx.progress.update_stage(stage, 60, "清理旧的构建文件", absolute=True)
            ctx.file_ops.remove_dir(str(ctx.dist_dir))
            ctx.file_ops.remove_dir(str(ctx.installer_dir))
            ctx.file_ops.ensure_dir(str(ctx.dist_dir))
            ctx.file_ops.ensure_dir(str(ctx.installer_dir))

        # 初始化配置 hash（用于后续缓存检测）
        try:
            if ctx.cache_manager and ctx.cache_manager.should_pre_generate_all_configs(ctx.config.merged_config):
                if ctx.progress:
                    ctx.progress.update_stage(stage, 45, "初始化配置缓存", absolute=True)

                # 保存全局配置 hash
                global_hash = ctx.cache_manager.calculate_config_hash(ctx.config.merged_config)
                ctx.cache_manager.save_config_hash(global_hash)

                # 保存各平台 hash
                for platform in ["windows", "macos", "linux"]:
                    if platform in ctx.config.merged_config.get("platforms", {}):
                        platform_hash = ctx.cache_manager.calculate_config_hash(ctx.config.merged_config, platform)
                        ctx.cache_manager.save_config_hash(platform_hash, platform)

                if getattr(ctx.args, "verbose", False) and ctx.progress:
                    ctx.progress.info("✅ 配置 hash 已初始化")
            else:
                if ctx.progress:
                    ctx.progress.update_stage(stage, 45, "使用缓存配置", absolute=True)
                    if getattr(ctx.args, "verbose", False):
                        ctx.progress.info("📋 配置未变化，使用现有 hash")
        except Exception as e:
            if ctx.progress:
                ctx.progress.warning(f"配置 hash 初始化失败: {e}")

        # 预处理图标（如无效则移除，避免PyInstaller报错）
        icon_path = ctx.config.get("icon")
        if icon_path:
            icon_full = ctx.config.resolve_path(icon_path)
            if not icon_full.exists():
                ctx.config.merged_config.pop("icon", None)
                if "pyinstaller" in ctx.config.merged_config:
                    ctx.config.merged_config["pyinstaller"].pop("icon", None)

        if ctx.progress:
            ctx.progress.update_stage(stage, 80, "准备资源文件", absolute=True)
            ctx.progress.complete_stage(stage)
