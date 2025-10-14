#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
资源下载模块
提供网络资源下载功能，支持阿里云OSS认证和普通HTTP下载
"""
import os
import logging
import requests
import time
from urllib.parse import urlparse, unquote, parse_qsl
from typing import Optional, Tuple
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)

class ResourceDownloader:
    """资源下载器类"""
    
    def __init__(self, download_dir: str = "./downloads"):
        """初始化资源下载器
        
        Args:
            download_dir: 下载目录路径
        """
        self.download_dir = download_dir
        self.timeout = 30  # 下载超时时间（秒）
        self.max_retries = 3  # 最大重试次数
        
        # 确保下载目录存在
        os.makedirs(self.download_dir, exist_ok=True)
        
        # 阿里云OSS配置，从环境变量获取（可选）
        self.oss_access_key_id = os.environ.get('OSS_ACCESS_KEY_ID')
        self.oss_access_key_secret = os.environ.get('OSS_ACCESS_KEY_SECRET')
        self.oss_endpoint = os.environ.get('OSS_ENDPOINT', 'oss-cn-shanghai.aliyuncs.com')
        
        # OSS功能可用性检查
        self.oss_available = bool(self.oss_access_key_id and self.oss_access_key_secret)
    
    def download(self, url: str, filename: Optional[str] = None) -> Optional[str]:
        """下载资源

        Args:
            url: 资源URL
            filename: 保存的文件名，如果为None则从URL解析

        Returns:
            下载后的文件路径，失败返回None
        """
        try:
            logger.info(f"开始下载资源: {url[:100]}{'...' if len(url) > 100 else ''}")

            # 🔍 调试信息：检查OSS配置和URL类型
            is_oss = self._is_oss_url(url)
            has_config = self._has_oss_config()
            if is_oss:
                logger.info(f"[下载器] 检测到OSS URL | OSS凭证{'可用' if has_config else '不可用'} | Endpoint: {self.oss_endpoint}")

            # 解析URL获取文件名
            if filename is None:
                parsed_url = urlparse(url)
                filename = os.path.basename(unquote(parsed_url.path))

                if not filename:
                    logger.warning(f"无法从URL解析文件名: {url}")
                    filename = f"download_{hash(url) % 10000}.dat"

            save_path = os.path.join(self.download_dir, filename)

            # 如果文件已存在，检查是否需要重新下载
            if os.path.exists(save_path):
                logger.info(f"文件已存在: {save_path}")
                return save_path

            # 尝试使用阿里云OSS下载（如果是OSS URL且配置了认证）
            if is_oss and has_config:
                try:
                    logger.info("[下载器] 尝试使用OSS SDK下载")
                    return self._download_from_oss(url, save_path)
                except Exception as e:
                    logger.warning(f"OSS SDK下载失败，切换到HTTP下载: {str(e)}")

            # 普通HTTP下载
            logger.info("[下载器] 使用HTTP方式下载")
            return self._download_via_http(url, save_path)

        except Exception as e:
            logger.error(f"下载失败: {str(e)}")
            return None
    
    def _is_oss_url(self, url: str) -> bool:
        """检查是否为OSS URL"""
        return 'aliyuncs.com' in url or 'oss-' in url
    
    def _has_oss_config(self) -> bool:
        """检查是否配置了OSS认证信息"""
        return all([self.oss_access_key_id, self.oss_access_key_secret, self.oss_endpoint])
    
    def _download_from_oss(self, url: str, save_path: str) -> str:
        """从阿里云OSS下载文件"""
        try:
            import oss2
        except ImportError:
            raise ImportError("需要安装oss2库: pip install oss2")
        
        # 解析OSS URL
        parsed_url = urlparse(url)
        
        # 提取bucket名称和object key
        bucket_name = parsed_url.hostname.split('.')[0]
        object_key = parsed_url.path.lstrip('/')
        
        # 创建OSS认证和客户端
        auth = oss2.Auth(self.oss_access_key_id, self.oss_access_key_secret)
        bucket = oss2.Bucket(auth, self.oss_endpoint, bucket_name)
        
        # 下载文件
        bucket.get_object_to_file(object_key, save_path)
        logger.info(f"OSS下载成功: {save_path}")
        
        return save_path
    
    def _download_via_http(self, url: str, save_path: str) -> str:
        """通过HTTP下载文件，支持智能OSS签名处理"""
        force_regenerate = False  # 🔧 添加标志，用于控制是否强制重新生成签名

        for retry in range(self.max_retries):
            try:
                # 设置请求头来模拟浏览器
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive'
                }

                # 🔧 智能OSS签名处理（从AutoReportV3移植）
                # 关键修复：在重试时传递 force_regenerate 标志
                download_url = self._process_oss_signature(url, force_regenerate=force_regenerate)

                response = requests.get(download_url, headers=headers, timeout=self.timeout, stream=True, allow_redirects=True)
                response.raise_for_status()

                # 获取文件大小
                total_size = int(response.headers.get('content-length', 0))

                # 写入文件
                downloaded_size = 0
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)

                            # 显示下载进度
                            if total_size > 0:
                                progress = (downloaded_size / total_size) * 100
                                if downloaded_size % (1024 * 1024) == 0:  # 每MB显示一次
                                    logger.info(f"下载进度: {progress:.1f}%")

                logger.info(f"HTTP下载成功: {save_path}")
                return save_path

            except Exception as e:
                logger.warning(f"下载失败 (重试 {retry + 1}/{self.max_retries}): {str(e)}")
                if retry < self.max_retries - 1:
                    time.sleep(2 ** retry)  # 指数退避

                    # 🔧 关键修复：如果是OSS签名相关错误且有OSS凭证，设置强制重新生成签名标志
                    if ('403' in str(e) or 'Forbidden' in str(e) or 'SignatureDoesNotMatch' in str(e)) and self._is_oss_url(url) and self.oss_available:
                        logger.info("[下载重试] 检测到OSS签名过期/无效，将在下次重试时强制重新生成签名")
                        force_regenerate = True  # 🔧 设置标志，下次循环会强制重新生成签名
                    else:
                        force_regenerate = False  # 非签名问题，不强制重新生成
                else:
                    raise e
    
    def _process_oss_signature(self, url: str, force_regenerate: bool = False) -> str:
        """智能OSS签名处理（从AutoReportV3移植）

        Args:
            url: 原始OSS URL
            force_regenerate: 是否强制重新生成签名（用于处理签名过期情况）

        Returns:
            处理后的下载URL
        """
        try:
            # 检查是否为OSS URL
            if not self._is_oss_url(url):
                return url

            # 解析URL获取查询参数
            parsed_url = urlparse(url)
            query_params = dict(parse_qsl(parsed_url.query))

            # 🔧 关键修复：如果强制重新生成，移除现有签名参数
            if force_regenerate:
                logger.info("[OSS签名] 🔄 强制重新生成签名（检测到签名过期）")
                # 移除签名相关的查询参数，强制走重新签名逻辑
                url_without_signature = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                parsed_url = urlparse(url_without_signature)
                query_params = {}  # 清空查询参数

            # 如果URL中有OSSAccessKeyId和Signature参数，说明是预签名URL
            if 'OSSAccessKeyId' in query_params and 'Signature' in query_params:
                # 直接使用预签名URL
                logger.debug("[OSS签名] 检测到预签名URL，直接使用")
                return url
            else:
                # 如果没有签名参数，且我们有OSS凭证，生成新的签名URL
                if self.oss_available:
                    bucket_name, object_key = self._parse_oss_url(url)
                    if bucket_name and object_key:
                        try:
                            import oss2
                            auth = oss2.Auth(self.oss_access_key_id, self.oss_access_key_secret)
                            bucket = oss2.Bucket(auth, self.oss_endpoint, bucket_name)
                            signed_url = bucket.sign_url('GET', object_key, 60)  # 1分钟有效期
                            logger.info(f"[OSS签名] ✅ {'强制' if force_regenerate else ''}重新生成OSS签名URL成功")
                            return signed_url
                        except Exception as e:
                            logger.error(f"[OSS签名] ❌ 生成签名URL失败: {str(e)}")
                            return url
                    else:
                        logger.warning("[OSS签名] ⚠️ 无法解析bucket和object信息")
                else:
                    logger.debug("[OSS签名] OSS凭证不可用，使用原始URL")

                # 返回原始URL
                return url

        except Exception as e:
            logger.error(f"[OSS签名] ❌ OSS签名处理失败: {str(e)}")
            return url
    
    def _parse_oss_url(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """解析OSS URL，提取bucket和object信息
        
        Args:
            url: OSS资源URL
            
        Returns:
            (bucket_name, object_key)元组
        """
        try:
            parsed_url = urlparse(url)
            
            # 尝试从主机名中提取bucket信息
            host_parts = parsed_url.netloc.split('.')
            if len(host_parts) >= 1 and ('aliyuncs.com' in parsed_url.netloc or 'oss-' in parsed_url.netloc):
                bucket_name = host_parts[0]
                
                # 处理路径中的对象名
                object_key = parsed_url.path
                if object_key.startswith('/'):
                    object_key = object_key[1:]  # 移除开头的斜杠
                
                # URL解码
                object_key = unquote(object_key)
                
                # 从查询参数中尝试获取key
                query_params = dict(parse_qsl(parsed_url.query))
                if 'key' in query_params:
                    object_key = unquote(query_params['key'])
                
                logger.debug(f"解析的对象键: {object_key}")
                return bucket_name, object_key
            
            return None, None
        except Exception as e:
            logger.error(f"解析OSS URL时出错: {str(e)}")
            return None, None
    
    def cleanup(self):
        """清理下载目录"""
        try:
            import shutil
            if os.path.exists(self.download_dir):
                shutil.rmtree(self.download_dir)
                logger.info(f"已清理下载目录: {self.download_dir}")
        except Exception as e:
            logger.warning(f"清理下载目录失败: {str(e)}")