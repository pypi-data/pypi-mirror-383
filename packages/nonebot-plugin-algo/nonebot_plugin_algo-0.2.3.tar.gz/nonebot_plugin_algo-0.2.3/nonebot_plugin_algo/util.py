import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Union

import httpx
from nonebot.log import logger

from .config import algo_config

class Util:
    
    @staticmethod
    def utc_to_local(time: str) -> datetime:
        """将UTC时间转换为本地时间datetime对象"""
        start_time = datetime.fromisoformat(time).replace(tzinfo=timezone.utc)
        local_time = start_time.astimezone()
        return local_time
    
    @staticmethod
    async def _make_request(url: str, params: dict) -> Union[List[Dict], int]:
        """统一的HTTP请求方法"""
        timeout = httpx.Timeout(10.0)
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    return response.json().get("objects", [])
            except httpx.ReadTimeout:
                wait_time = min(2 ** attempt, 5)
                logger.warning(f"[Attempt {attempt + 1}/3] Timeout, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            except httpx.HTTPStatusError as e:
                if attempt == 2:
                    logger.error(f"请求失败,状态码{e.response.status_code}: {e}")
                    return e.response.status_code
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                logger.exception(f"请求失败,发生异常: {e}")
                return 0
        return 0

    @staticmethod
    def _normalize_params(params: dict) -> dict:
        normalized: dict = {}
        for key, value in params.items():
            if isinstance(value, datetime):
                if value.tzinfo is None:
                    value = value.replace(tzinfo=timezone.utc)
                normalized[key] = value.isoformat(timespec="seconds")
            else:
                normalized[key] = value
        return normalized

    @classmethod
    def build_contest_params(
        cls,
        days=None, 
        resource_id=None, 
        id=None, 
        event__regex=None,
    ) -> dict:
        #当前时间
        if days is None:
            base_params = {
                "id": id,
                "event__regex": event__regex,
                **algo_config.default_params,
            }
        else:
            # 使用本地时区的“今日”日界来构建查询窗口
            # 起点：当前本地时间；终点：days 天后的本地 00:00（减 1 秒确保不包含次日 00:00）
            now_local = datetime.now().astimezone()
            end_local = (now_local + timedelta(days=days)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            # 统一转为 UTC，服务端以 UTC 解析更稳定
            now_utc = now_local.astimezone(timezone.utc)
            end_utc = end_local.astimezone(timezone.utc)

            base_params = {
                "start__gte": now_utc,
                # 使用 <= 边界，减 1 秒避免包含次日 00:00 整点
                "start__lte": end_utc - timedelta(seconds=1),
                **algo_config.default_params,
                **{"resource_id": resource_id},
            }
        base_params = {k: v for k, v in base_params.items() if v is not None}
        return cls._normalize_params(base_params)

    @classmethod
    def build_problem_params(
        cls,
        contest_ids=None, 
        url=None
    ) -> dict:
        base_params = {
            **algo_config.default_params,
            "contest_ids": str(contest_ids),
            "order_by": "rating",
            "limit": algo_config.algo_limit,
            "url": url,
        }
        base_params = {k: v for k, v in base_params.items() if v is not None}
        return cls._normalize_params(base_params)

    @classmethod
    async def get_contest_info(
        cls,
        id=None, #比赛id
        event__regex=None #比赛名称
    ) -> Union[List[Dict], int]:
        params = cls.build_contest_params(id=id, event__regex=event__regex)
        return await cls._make_request("https://clist.by/api/v4/contest/", params)

    @classmethod
    async def get_upcoming_contests(
        cls,
        resource_id=None, #平台id
        id=None, #比赛id
        days:int= algo_config.algo_days #查询天数
    ) -> Union[List[Dict], int]:
        params = cls.build_contest_params(resource_id=resource_id, id=id, days=days)
        return await cls._make_request("https://clist.by/api/v4/contest/", params)

    @classmethod
    async def get_problems_by_contest(
        cls,
        contest_ids: int  # 比赛id
    ) -> Union[List[Dict], int]:
        params = cls.build_problem_params(contest_ids)
        return await cls._make_request("https://clist.by/api/v4/problem/", params)

    @classmethod
    async def get_problems_info(
        cls,
        contest_ids=None,
        url=None
    ) -> Union[List[Dict], int]:
        """条件查询题目信息
        
        Args:
            contest_ids: 比赛id
            url: 题目链接
        Returns:
            List[Dict] | int: 题目信息列表或错误状态码
        """
        params = cls.build_problem_params(contest_ids, url)
        return await cls._make_request("https://clist.by/api/v4/problem/", params)