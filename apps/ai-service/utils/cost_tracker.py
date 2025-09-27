import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any
import redis
import logging

logger = logging.getLogger(__name__)

class CostTracker:
    """AI服务成本跟踪器"""
    
    # 模型成本配置 (每1000 tokens的美元成本)
    MODEL_COSTS = {
        "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
        "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
        "qwen-max": {"input": 0.002, "output": 0.006},
        "qwen-plus": {"input": 0.001, "output": 0.003},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.001, "output": 0.002}
    }
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.daily_cost_key = "ai_daily_cost"
        self.cost_history_key = "ai_cost_history"
    
    async def record_usage(
        self, 
        model: str, 
        input_tokens: int, 
        output_tokens: int
    ) -> float:
        """记录API使用成本"""
        
        if model not in self.MODEL_COSTS:
            logger.warning(f"Unknown model cost: {model}")
            return 0.0
        
        costs = self.MODEL_COSTS[model]
        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        total_cost = input_cost + output_cost
        
        # 记录到Redis
        today = datetime.now().strftime("%Y-%m-%d")
        await self._increment_daily_cost(today, total_cost)
        
        # 记录详细使用历史
        usage_record = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": total_cost
        }
        
        await self._record_usage_history(usage_record)
        
        logger.info(f"Recorded usage: {model}, Cost: ${total_cost:.4f}")
        return total_cost
    
    async def get_daily_cost(self, date: str = None) -> float:
        """获取指定日期的总成本"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        cost_data = await self.redis.hget(self.daily_cost_key, date)
        return float(cost_data) if cost_data else 0.0
    
    async def get_cost_summary(self, days: int = 7) -> Dict[str, Any]:
        """获取成本摘要"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        total_cost = 0.0
        daily_costs = {}
        
        for i in range(days):
            date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            cost = await self.get_daily_cost(date)
            daily_costs[date] = cost
            total_cost += cost
        
        return {
            "period_days": days,
            "total_cost": total_cost,
            "average_daily_cost": total_cost / days,
            "daily_breakdown": daily_costs,
            "cost_alerts": await self._check_cost_alerts(total_cost)
        }
    
    async def _increment_daily_cost(self, date: str, cost: float):
        """增加日成本"""
        await self.redis.hincrbyfloat(self.daily_cost_key, date, cost)
        await self.redis.expire(self.daily_cost_key, 86400 * 30)  # 30天过期
    
    async def _record_usage_history(self, usage_record: Dict[str, Any]):
        """记录使用历史"""
        await self.redis.lpush(
            self.cost_history_key, 
            json.dumps(usage_record)
        )
        await self.redis.ltrim(self.cost_history_key, 0, 9999)  # 保留最近10000条
        await self.redis.expire(self.cost_history_key, 86400 * 7)  # 7天过期
    
    async def _check_cost_alerts(self, total_cost: float) -> list:
        """检查成本警报"""
        alerts = []
        
        if total_cost > 80.0:  # 超过80美元
            alerts.append({
                "type": "high_cost",
                "message": f"Daily cost exceeded $80: ${total_cost:.2f}",
                "severity": "warning"
            })
        
        if total_cost > 100.0:  # 超过100美元
            alerts.append({
                "type": "cost_limit",
                "message": f"Daily cost limit exceeded: ${total_cost:.2f}",
                "severity": "critical"
            })
        
        return alerts
