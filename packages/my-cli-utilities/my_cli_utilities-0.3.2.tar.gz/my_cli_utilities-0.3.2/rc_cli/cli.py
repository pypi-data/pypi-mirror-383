# -*- coding: utf-8 -*-

import os
import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import typer
import httpx
from tqdm.auto import tqdm
from my_cli_utilities_common.config import BaseConfig, LoggingUtils
from .sp_commands import sp_app

# Initialize logger
logger = LoggingUtils.setup_logger('rc_cli')

# 禁用httpx的INFO级别日志，只保留警告和错误
logging.getLogger("httpx").setLevel(logging.WARNING)

# Create main app and subcommands
app = typer.Typer(
    name="rc",
    help="🚀 RC CLI - RingCentral Development Tools",
    add_completion=False,
    rich_markup_mode="rich"
)

download_app = typer.Typer(
    name="download",
    help="📥 Application download commands",
    add_completion=False
)

app.add_typer(download_app, name="download")
app.add_typer(download_app, name="d")
app.add_typer(download_app, name="down")

# Add SP sub-app
app.add_typer(sp_app, name="sp")


@dataclass
class DownloadResult:
    """下载结果数据类"""
    success: bool
    app_name: str
    size: int = 0
    duration: float = 0.0
    error_message: str = ""


class Config(BaseConfig):
    """Configuration for RC CLI"""
    HOME_DIR = os.path.expanduser("~")
    FILE_DIR = os.path.join(HOME_DIR, "Downloads", "BrandApp")
    BASE_URL = "http://cloud-xmn.int.rclabenv.com/remote.php/dav/files/mthor_cloud/mThor/apps/mthor"
    
    # Download settings
    TIMEOUT_TOTAL = 600.0
    TIMEOUT_CONNECT = 60.0
    CHUNK_SIZE = 8192
    MAX_CONCURRENT_DOWNLOADS = 5
    PROGRESS_UPDATE_INTERVAL = 0.1
    
    # Authentication
    AUTH_USERNAME = "mThor_cloud"
    AUTH_PASSWORD = "NextCloud123"
    
    # App definitions
    SUFFIX = "coverage"
    
    APP_TYPES = {
        'aqa': [
            "web-aqa-xmn-ringcentral-inhouse-debug.apk",
            "WEB-AQA-XMN-Glip-Inhouse.ipa",
            "WEB-AQA-XMN-Glip.zip"
        ],
        'up': [
            "xmn-up-ringcentral-inhouse-debug.apk",
            "XMN-UP-Glip-Inhouse.ipa",
            "XMN-UP-Glip.zip"
        ],
        'df': [
            "web-aqa-xmn-ringcentral-inhouse-debug-23.4.10.1.apk",
            "WEB-AQA-XMN-Glip-23.4.10.1-Inhouse.ipa",
            "WEB-AQA-XMN-Glip-23.4.10.1.zip",
            "xmn-up-ringcentral-inhouse-debug-23.4.10.1.apk",
            "XMN-UP-Glip-23.4.10.1-Inhouse.ipa",
            "XMN-UP-Glip-23.4.10.1.zip"
        ]
    }


class DownloadManager:
    """下载管理器 - 处理单个文件下载"""
    
    def __init__(self):
        self.print_lock = threading.Lock()
        
    def _safe_print(self, message: str) -> None:
        """线程安全的打印函数"""
        with self.print_lock:
            tqdm.write(message)

    def _format_size(self, size_bytes: int) -> str:
        """将字节数格式化为可读的大小"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"

    def _log_download_result(self, result: DownloadResult) -> None:
        """记录下载结果"""
        if result.success:
            self._safe_print(
                f"✅ 下载完成: {result.app_name} ({self._format_size(result.size)}) "
                f"平均速度: {self._format_size(result.size / result.duration if result.duration > 0 else 0)}/s "
                f"耗时: {int(result.duration)}秒"
            )
        else:
            self._safe_print(f"❌ 下载失败: {result.app_name} - {result.error_message}")

    def download_single_app(self, app_name: str) -> DownloadResult:
        """下载单个应用"""
        app_name = app_name.strip()
        start_time = time.time()
        
        # 确保下载目录存在
        os.makedirs(Config.FILE_DIR, exist_ok=True)
        file_path = os.path.join(Config.FILE_DIR, app_name)
        download_url = f"{Config.BASE_URL}/{app_name}"

        # 删除已存在的文件
        if os.path.exists(file_path):
            self._safe_print(f"🗑️  删除已存在文件: {app_name}")
            try:
                os.remove(file_path)
            except OSError as e:
                return DownloadResult(False, app_name, error_message=f"删除文件失败: {e}")

        self._safe_print(f"⬇️  开始下载: {app_name}")
        
        timeout_config = httpx.Timeout(Config.TIMEOUT_TOTAL, connect=Config.TIMEOUT_CONNECT)
        progress_bar = None
        downloaded_size = 0

        try:
            auth = (Config.AUTH_USERNAME, Config.AUTH_PASSWORD)
            with httpx.Client(timeout=timeout_config, auth=auth, follow_redirects=True) as client:
                with client.stream("GET", download_url) as response:
                    response.raise_for_status()
                    
                    total_size = response.headers.get("Content-Length")
                    if total_size:
                        total_size = int(total_size)
                        self._safe_print(f"📊 {app_name} 文件大小: {self._format_size(total_size)}")
                        progress_bar = self._create_progress_bar(app_name, total_size)

                    with open(file_path, "wb") as f:
                        for chunk in response.iter_bytes(chunk_size=Config.CHUNK_SIZE):
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            if progress_bar:
                                progress_bar.update(len(chunk))
                    
                    duration = time.time() - start_time
                    result = DownloadResult(True, app_name, downloaded_size, duration)
                    
                    # 验证下载完整性
                    if total_size and downloaded_size < total_size:
                        result.success = False
                        result.error_message = f"下载不完整 (期望: {self._format_size(total_size)}, 实际: {self._format_size(downloaded_size)})"
                    
                    return result

        except httpx.TimeoutException as e:
            return DownloadResult(False, app_name, error_message=f"下载超时: {e}")
        except httpx.HTTPStatusError as e:
            return DownloadResult(False, app_name, error_message=f"HTTP错误 状态码 {e.response.status_code}")
        except httpx.RequestError as e:
            return DownloadResult(False, app_name, error_message=f"请求错误: {e}")
        except Exception as e:
            return DownloadResult(False, app_name, error_message=f"未知错误: {e}")
        finally:
            if progress_bar:
                progress_bar.close()
                time.sleep(0.1)

    def _create_progress_bar(self, app_name: str, total_size: int) -> tqdm:
        """创建进度条"""
        return tqdm(
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
            desc=f"📥 {app_name[:15]}...",
            leave=False,
            ncols=100,
            miniters=1,
            mininterval=Config.PROGRESS_UPDATE_INTERVAL,
            dynamic_ncols=True,
        )


# Global download manager instance
download_manager = DownloadManager()


def _get_regression_apps(version_arg: Optional[str] = None) -> List[str]:
    """获取回归测试应用列表"""
    version = f"-{version_arg}" if version_arg else ""
    base_patterns = [
        "web-aqa-xmn-ringcentral-inhouse-debug{version}-{suffix}",
        "WEB-AQA-XMN-Glip{version}-{suffix}-Inhouse", 
        "WEB-AQA-XMN-Glip{version}-{suffix}",
        "xmn-up-ringcentral-inhouse-debug{version}-{suffix}",
        "XMN-UP-Glip{version}-{suffix}-Inhouse",
        "XMN-UP-Glip{version}-{suffix}"
    ]
    
    extensions = [".apk", ".ipa", ".zip", ".apk", ".ipa", ".zip"]
    
    return [
        pattern.format(version=version, suffix=Config.SUFFIX) + ext
        for pattern, ext in zip(base_patterns, extensions)
    ]


def _download_apps_batch(apps_list: List[str], app_type: str) -> None:
    """批量下载应用"""
    typer.echo(f"🚀 开始下载 {app_type} 应用 ({len(apps_list)} 个)...")
    typer.echo(f"📁 下载目录: {Config.FILE_DIR}")
    typer.echo(f"🔧 最大并发数: {Config.MAX_CONCURRENT_DOWNLOADS}")
    typer.echo("-" * 50)
    
    results = []
    with ThreadPoolExecutor(max_workers=Config.MAX_CONCURRENT_DOWNLOADS) as executor:
        future_to_app = {
            executor.submit(download_manager.download_single_app, app): app 
            for app in apps_list
        }
        
        for future in as_completed(future_to_app):
            result = future.result()
            results.append(result)
            download_manager._log_download_result(result)
    
    _print_summary(results, app_type)


def _print_summary(results: List[DownloadResult], app_type: str) -> None:
    """打印下载总结"""
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    
    total_size = sum(r.size for r in successful)
    total_time = sum(r.duration for r in successful)
    
    typer.echo("-" * 50)
    typer.echo(f"🎉 {app_type} 应用下载完成!")
    typer.echo(f"📊 成功: {len(successful)} | 失败: {len(failed)} | 总计: {len(results)}")
    if successful:
        typer.echo(f"📁 总大小: {download_manager._format_size(total_size)}")
        typer.echo(f"⏱️  总耗时: {int(total_time)}秒")
    if failed:
        typer.echo(f"❌ 失败文件: {', '.join(r.app_name for r in failed)}")


def _download_app_type(app_type: str) -> None:
    """下载指定类型的应用"""
    if app_type not in Config.APP_TYPES:
        available_types = ', '.join(Config.APP_TYPES.keys())
        typer.echo(f"❌ 未知应用类型: {app_type}", err=True)
        typer.echo(f"可用类型: {available_types}")
        raise typer.Exit(1)
        
    apps_list = Config.APP_TYPES[app_type]
    _download_apps_batch(apps_list, app_type.upper())


# Download commands
@download_app.command("aqa")
def download_aqa():
    """📱 下载 AQA 版本应用"""
    _download_app_type('aqa')


@download_app.command("up")
def download_up():
    """📱 下载 UP 版本应用"""
    _download_app_type('up')


@download_app.command("df")
def download_df():
    """📱 下载 DF (默认固定) 版本应用"""
    _download_app_type('df')


@download_app.command("regress")
def download_regress(
    version: Optional[str] = typer.Argument(
        None, 
        help="版本号，如 '23.4' 或 '24.1'。不指定则下载最新版本"
    )
):
    """🧪 下载回归测试应用
    
    Examples:
    
        rc download regress        # 下载最新版本
        
        rc d regress 24.1         # 下载 24.1 版本
    """
    apps = _get_regression_apps(version)
    version_text = f"版本 {version}" if version else "最新版本"
    _download_apps_batch(apps, f"回归测试 ({version_text})")


# Main app commands
@app.command("info")
def show_info():
    """ℹ️  显示配置信息"""
    typer.echo("\n🚀 RC CLI - RingCentral Development Tools")
    typer.echo(f"📁 下载目录: {Config.FILE_DIR}")
    typer.echo(f"🔧 最大并发数: {Config.MAX_CONCURRENT_DOWNLOADS}")
    typer.echo(f"🌐 服务器地址: {Config.BASE_URL}")
    
    available_types = ', '.join(Config.APP_TYPES.keys())
    typer.echo(f"📱 可用应用类型: {available_types}")
    
    typer.echo("\n💡 使用示例:")
    typer.echo("  rc download aqa          # 下载 AQA 应用")
    typer.echo("  rc d up                  # 下载 UP 应用")
    typer.echo("  rc d regress 24.1        # 下载 24.1 版本回归测试应用")
    typer.echo("  rc sp list               # 查询所有 SP 信息")
    typer.echo("  rc sp search 'SMS'       # 搜索 SMS 相关 SP")
    typer.echo("  rc sp get 'SP-123' '8023391076'  # 查询账号 SP 值")


def main_rc_function():
    """Main entry point for RC CLI"""
    app()


if __name__ == "__main__":
    main_rc_function() 