"""
AI服务成本控制精确实施机制
包含预算检查、成本预测、自动降级等功能
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import redis
import json

class CostLevel(Enum):
    """成本等级"""
    MINIMAL = "最低成本"     # 预生产内容 + 通义千问
    STANDARD = "标准成本"    # 模板 + 通义千问/GPT-3.5
    PREMIUM = "高级成本"     # 定制 + Claude/GPT-4
    EMERGENCY = "紧急模式"   # 仅预生产库

class BudgetStatus(Enum):
    """预算状态"""
    SAFE = "安全"           # <70%预算
    WARNING = "警告"        # 70-90%预算
    CRITICAL = "临界"       # 90-100%预算
    EXCEEDED = "超支"       # >100%预算

@dataclass
class CostEstimate:
    """成本估算"""
    total_tokens: int
    estimated_cost: float
    processing_time: float
    confidence: float
    breakdown: Dict[str, float]

@dataclass
class BudgetInfo:
    """预算信息"""
    daily_limit: float
    monthly_limit: float
    current_daily_usage: float
    current_monthly_usage: float
    remaining_daily: float
    remaining_monthly: float
    status: BudgetStatus

class EnhancedCostController:
    """
    增强版成本控制器
    支持预算预检查、智能降级、成本优化
    """

    def __init__(self, redis_client):
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)

        # 模型成本配置 (每1000 tokens)
        self.model_costs = {
            'claude-3-opus': {'input': 0.15, 'output': 0.75},
            'claude-3-sonnet': {'input': 0.03, 'output': 0.15},
            'gpt-4-turbo': {'input': 0.10, 'output': 0.30},
            'gpt-3.5-turbo': {'input': 0.01, 'output': 0.02},
            'qwen-max': {'input': 0.008, 'output': 0.008},
            'qwen-plus': {'input': 0.004, 'output': 0.004}
        }

        # 预算限制配置
        self.budget_limits = {
            'free': {'daily': 5.0, 'monthly': 100.0},
            'standard': {'daily': 20.0, 'monthly': 500.0},
            'premium': {'daily': 100.0, 'monthly': 2000.0},
            'family': {'daily': 150.0, 'monthly': 3000.0}
        }

        # 降级策略配置
        self.fallback_strategies = {
            CostLevel.PREMIUM: [
                ('claude-3-opus', 'claude-3-sonnet'),
                ('gpt-4-turbo', 'gpt-3.5-turbo'),
                ('qwen-max', 'qwen-plus')
            ],
            CostLevel.STANDARD: [
                ('claude-3-sonnet', 'qwen-max'),
                ('gpt-3.5-turbo', 'qwen-plus')
            ],
            CostLevel.MINIMAL: [
                ('qwen-plus', 'preproduced')
            ]
        }

    async def pre_request_budget_check(self, user_id: str, request_details: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        请求前预算检查

        Args:
            user_id: 用户ID
            request_details: 请求详情 (包含模型、内容长度等)

        Returns:
            (是否允许请求, 决策信息)
        """
        # 1. 获取用户预算信息
        budget_info = await self._get_budget_info(user_id)

        # 2. 估算请求成本
        cost_estimate = self._estimate_request_cost(request_details)

        # 3. 预算充足性检查
        can_proceed = self._check_budget_sufficiency(budget_info, cost_estimate)

        # 4. 生成决策信息
        decision_info = {
            'can_proceed': can_proceed,
            'budget_status': budget_info.status.value,
            'estimated_cost': cost_estimate.estimated_cost,
            'remaining_budget': budget_info.remaining_daily,
            'suggested_action': None,
            'alternative_options': []
        }

        # 5. 如果预算不足，提供替代方案
        if not can_proceed:
            alternatives = await self._generate_alternatives(request_details, budget_info)
            decision_info['alternative_options'] = alternatives
            decision_info['suggested_action'] = '预算不足，建议选择替代方案'

        # 6. 如果预算警告，提供优化建议
        elif budget_info.status in [BudgetStatus.WARNING, BudgetStatus.CRITICAL]:
            optimization = await self._suggest_cost_optimization(request_details)
            decision_info['suggested_action'] = '预算紧张，建议成本优化'
            decision_info['optimization_suggestions'] = optimization

        return can_proceed, decision_info

    async def _get_budget_info(self, user_id: str) -> BudgetInfo:
        """获取用户预算信息"""
        # 获取用户订阅等级
        user_tier = await self._get_user_tier(user_id)
        limits = self.budget_limits[user_tier]

        # 获取当前使用情况
        today = datetime.now().strftime('%Y-%m-%d')
        month = datetime.now().strftime('%Y-%m')

        daily_key = f"cost:daily:{user_id}:{today}"
        monthly_key = f"cost:monthly:{user_id}:{month}"

        current_daily = float(self.redis.get(daily_key) or 0)
        current_monthly = float(self.redis.get(monthly_key) or 0)

        # 计算剩余预算
        remaining_daily = max(0, limits['daily'] - current_daily)
        remaining_monthly = max(0, limits['monthly'] - current_monthly)

        # 确定预算状态
        daily_usage_ratio = current_daily / limits['daily']
        if daily_usage_ratio >= 1.0:
            status = BudgetStatus.EXCEEDED
        elif daily_usage_ratio >= 0.9:
            status = BudgetStatus.CRITICAL
        elif daily_usage_ratio >= 0.7:
            status = BudgetStatus.WARNING
        else:
            status = BudgetStatus.SAFE

        return BudgetInfo(
            daily_limit=limits['daily'],
            monthly_limit=limits['monthly'],
            current_daily_usage=current_daily,
            current_monthly_usage=current_monthly,
            remaining_daily=remaining_daily,
            remaining_monthly=remaining_monthly,
            status=status
        )

    def _estimate_request_cost(self, request_details: Dict[str, Any]) -> CostEstimate:
        """估算请求成本"""
        model = request_details.get('model', 'qwen-plus')
        content_length = request_details.get('content_length', 1000)
        request_type = request_details.get('type', 'story_generation')

        # 基于内容长度估算 token 数量
        if request_type == 'story_generation':
            # 故事生成：输入较少，输出较多
            input_tokens = min(content_length * 0.5, 2000)  # 输入提示词
            output_tokens = content_length * 2              # 生成的故事内容
        elif request_type == 'illustration':
            # 插画生成：固定成本
            input_tokens = 500
            output_tokens = 100
        else:
            # 其他类型：均衡估算
            input_tokens = content_length * 0.8
            output_tokens = content_length * 0.3

        # 计算成本
        if model in self.model_costs:
            cost_config = self.model_costs[model]
            input_cost = (input_tokens / 1000) * cost_config['input']
            output_cost = (output_tokens / 1000) * cost_config['output']
            total_cost = input_cost + output_cost
        else:
            # 未知模型，使用平均成本
            total_cost = ((input_tokens + output_tokens) / 1000) * 0.05

        # 添加处理时间估算
        processing_time = self._estimate_processing_time(model, input_tokens + output_tokens)

        # 置信度：基于历史数据的准确性（简化版）
        confidence = 0.85

        return CostEstimate(
            total_tokens=int(input_tokens + output_tokens),
            estimated_cost=round(total_cost, 4),
            processing_time=processing_time,
            confidence=confidence,
            breakdown={
                'input_cost': round(input_cost, 4),
                'output_cost': round(output_cost, 4),
                'model': model
            }
        )

    def _estimate_processing_time(self, model: str, total_tokens: int) -> float:
        """估算处理时间（秒）"""
        # 不同模型的处理速度（tokens/秒）
        model_speeds = {
            'claude-3-opus': 20,
            'claude-3-sonnet': 40,
            'gpt-4-turbo': 30,
            'gpt-3.5-turbo': 60,
            'qwen-max': 50,
            'qwen-plus': 80
        }

        speed = model_speeds.get(model, 40)
        base_time = total_tokens / speed

        # 添加网络延迟和处理开销
        overhead = 2.0  # 2秒基础开销
        return base_time + overhead

    def _check_budget_sufficiency(self, budget_info: BudgetInfo, cost_estimate: CostEstimate) -> bool:
        """检查预算充足性"""
        # 保守检查：确保有余量应对估算误差
        safety_margin = 1.2  # 20%安全边际
        required_budget = cost_estimate.estimated_cost * safety_margin

        # 检查日预算和月预算
        daily_sufficient = budget_info.remaining_daily >= required_budget
        monthly_sufficient = budget_info.remaining_monthly >= required_budget

        return daily_sufficient and monthly_sufficient

    async def _generate_alternatives(self, request_details: Dict[str, Any], budget_info: BudgetInfo) -> List[Dict[str, Any]]:
        """生成替代方案"""
        alternatives = []
        original_model = request_details.get('model', 'qwen-plus')

        # 1. 模型降级方案
        for fallback_model in self._get_fallback_models(original_model):
            alt_request = request_details.copy()
            alt_request['model'] = fallback_model
            alt_cost = self._estimate_request_cost(alt_request)

            if self._check_budget_sufficiency(budget_info, alt_cost):
                alternatives.append({
                    'type': 'model_downgrade',
                    'description': f'使用 {fallback_model} 替代 {original_model}',
                    'cost_saving': request_details.get('estimated_cost', 0) - alt_cost.estimated_cost,
                    'new_cost': alt_cost.estimated_cost,
                    'parameters': alt_request
                })

        # 2. 内容长度减少方案
        original_length = request_details.get('content_length', 1000)
        for reduction_ratio in [0.8, 0.6, 0.4]:
            alt_request = request_details.copy()
            alt_request['content_length'] = int(original_length * reduction_ratio)
            alt_cost = self._estimate_request_cost(alt_request)

            if self._check_budget_sufficiency(budget_info, alt_cost):
                alternatives.append({
                    'type': 'content_reduction',
                    'description': f'内容长度减少 {int((1-reduction_ratio)*100)}%',
                    'cost_saving': request_details.get('estimated_cost', 0) - alt_cost.estimated_cost,
                    'new_cost': alt_cost.estimated_cost,
                    'parameters': alt_request
                })

        # 3. 预生产内容方案
        if budget_info.remaining_daily >= 0.5:  # 预生产内容的小额成本
            alternatives.append({
                'type': 'preproduced',
                'description': '使用预生产内容库',
                'cost_saving': request_details.get('estimated_cost', 0) - 0.1,
                'new_cost': 0.1,
                'parameters': {'type': 'preproduced', 'fallback': True}
            })

        return sorted(alternatives, key=lambda x: x['cost_saving'], reverse=True)

    def _get_fallback_models(self, original_model: str) -> List[str]:
        """获取降级模型列表"""
        fallback_chain = {
            'claude-3-opus': ['claude-3-sonnet', 'qwen-max', 'qwen-plus'],
            'claude-3-sonnet': ['qwen-max', 'qwen-plus'],
            'gpt-4-turbo': ['gpt-3.5-turbo', 'qwen-max', 'qwen-plus'],
            'gpt-3.5-turbo': ['qwen-plus'],
            'qwen-max': ['qwen-plus'],
            'qwen-plus': []
        }

        return fallback_chain.get(original_model, ['qwen-plus'])

    async def _suggest_cost_optimization(self, request_details: Dict[str, Any]) -> Dict[str, Any]:
        """建议成本优化方案"""
        optimizations = {
            'immediate_savings': [],
            'workflow_optimizations': [],
            'subscription_suggestions': []
        }

        # 即时节省建议
        current_model = request_details.get('model', 'qwen-plus')
        if current_model in ['claude-3-opus', 'gpt-4-turbo']:
            optimizations['immediate_savings'].append({
                'action': '使用高效模型',
                'description': f'将 {current_model} 替换为 claude-3-sonnet 或 qwen-max',
                'potential_saving': '节省 60-80% 成本，质量损失 <10%'
            })

        # 工作流优化建议
        optimizations['workflow_optimizations'].extend([
            {
                'action': '批量处理',
                'description': '将多个请求合并处理，减少API调用次数',
                'potential_saving': '节省 20-30% 成本'
            },
            {
                'action': '智能缓存',
                'description': '启用相似内容缓存，避免重复生成',
                'potential_saving': '节省 40-60% 重复成本'
            }
        ])

        # 订阅建议（基于当前使用模式）
        current_usage = request_details.get('daily_requests', 1)
        if current_usage > 10:
            optimizations['subscription_suggestions'].append({
                'suggestion': '升级到高级版',
                'reason': '高频使用用户享受更高预算和优先处理',
                'benefit': '每日预算从 ¥20 提升到 ¥100'
            })

        return optimizations

    async def record_actual_cost(self, user_id: str, request_details: Dict[str, Any], actual_cost: float):
        """记录实际成本"""
        today = datetime.now().strftime('%Y-%m-%d')
        month = datetime.now().strftime('%Y-%m')

        # 更新使用统计
        daily_key = f"cost:daily:{user_id}:{today}"
        monthly_key = f"cost:monthly:{user_id}:{month}"

        # 原子性更新
        pipe = self.redis.pipeline()
        pipe.incrbyfloat(daily_key, actual_cost)
        pipe.expire(daily_key, 86400 * 2)  # 2天过期
        pipe.incrbyfloat(monthly_key, actual_cost)
        pipe.expire(monthly_key, 86400 * 35)  # 35天过期
        pipe.execute()

        # 记录详细使用日志
        usage_log = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'model': request_details.get('model'),
            'type': request_details.get('type'),
            'actual_cost': actual_cost,
            'estimated_cost': request_details.get('estimated_cost'),
            'accuracy': actual_cost / request_details.get('estimated_cost', actual_cost)
        }

        log_key = f"cost:log:{user_id}:{today}"
        self.redis.lpush(log_key, json.dumps(usage_log))
        self.redis.expire(log_key, 86400 * 7)  # 7天日志保留

        self.logger.info(f"Cost recorded for user {user_id}: ${actual_cost}")

    async def get_cost_analytics(self, user_id: str) -> Dict[str, Any]:
        """获取成本分析报告"""
        today = datetime.now().strftime('%Y-%m-%d')

        # 获取最近7天的详细日志
        analytics = {
            'daily_breakdown': {},
            'model_usage': {},
            'cost_trends': {},
            'efficiency_metrics': {}
        }

        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            log_key = f"cost:log:{user_id}:{date}"
            logs = self.redis.lrange(log_key, 0, -1)

            daily_cost = 0
            model_usage = {}

            for log_data in logs:
                log = json.loads(log_data)
                daily_cost += log['actual_cost']
                model = log['model']
                model_usage[model] = model_usage.get(model, 0) + log['actual_cost']

            analytics['daily_breakdown'][date] = daily_cost
            if date == today:
                analytics['model_usage'] = model_usage

        return analytics

    async def _get_user_tier(self, user_id: str) -> str:
        """获取用户订阅等级（简化版）"""
        # 这里应该从数据库获取，暂时返回默认值
        tier_key = f"user:tier:{user_id}"
        tier = self.redis.get(tier_key)
        return tier.decode() if tier else 'standard'

# 自动降级装饰器
def with_cost_control(cost_controller: EnhancedCostController):
    """成本控制装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 提取用户信息和请求详情
            user_id = kwargs.get('user_id') or args[0] if args else None
            request_details = kwargs.get('request_details', {})

            # 预算检查
            can_proceed, decision_info = await cost_controller.pre_request_budget_check(
                user_id, request_details
            )

            if not can_proceed:
                # 尝试自动降级
                alternatives = decision_info.get('alternative_options', [])
                if alternatives:
                    best_alternative = alternatives[0]
                    kwargs['request_details'] = best_alternative['parameters']
                    cost_controller.logger.warning(
                        f"Auto-fallback for user {user_id}: {best_alternative['description']}"
                    )
                else:
                    raise BudgetExceededException("预算不足且无可用替代方案")

            # 执行原始函数
            start_time = datetime.now()
            try:
                result = await func(*args, **kwargs)
                # 记录成功的成本
                actual_cost = result.get('actual_cost', request_details.get('estimated_cost', 0))
                await cost_controller.record_actual_cost(user_id, request_details, actual_cost)
                return result
            except Exception as e:
                # 记录失败（部分成本可能已产生）
                processing_time = (datetime.now() - start_time).total_seconds()
                partial_cost = min(processing_time * 0.01, request_details.get('estimated_cost', 0) * 0.3)
                await cost_controller.record_actual_cost(user_id, request_details, partial_cost)
                raise e

        return wrapper
    return decorator

class BudgetExceededException(Exception):
    """预算超支异常"""
    pass
