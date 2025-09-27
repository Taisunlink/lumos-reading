#!/usr/bin/env python3
"""
成本控制功能测试脚本
测试预算检查、成本估算、自动降级等功能
"""

import asyncio
import json
import redis
from datetime import datetime
from core.cost_control import EnhancedCostController, BudgetExceededException

async def test_cost_control():
    """测试成本控制功能"""
    
    # 初始化Redis客户端和成本控制器
    redis_client = redis.Redis.from_url("redis://localhost:6379")
    cost_controller = EnhancedCostController(redis_client)
    
    print("🚀 开始测试成本控制功能...")
    print("=" * 60)
    
    # 测试用户ID
    test_user_id = "test_user_123"
    
    # 1. 测试成本估算
    print("\n📊 1. 测试成本估算")
    print("-" * 30)
    
    test_requests = [
        {
            "model": "claude-3-opus",
            "content_length": 2000,
            "type": "story_generation"
        },
        {
            "model": "qwen-max",
            "content_length": 1500,
            "type": "story_generation"
        },
        {
            "model": "gpt-3.5-turbo",
            "content_length": 1000,
            "type": "story_generation"
        }
    ]
    
    for i, request in enumerate(test_requests, 1):
        cost_estimate = cost_controller._estimate_request_cost(request)
        print(f"请求 {i}: {request['model']}")
        print(f"  估算成本: ${cost_estimate.estimated_cost:.4f}")
        print(f"  总tokens: {cost_estimate.total_tokens}")
        print(f"  处理时间: {cost_estimate.processing_time:.1f}秒")
        print(f"  置信度: {cost_estimate.confidence:.2f}")
        print()
    
    # 2. 测试预算检查
    print("\n💰 2. 测试预算检查")
    print("-" * 30)
    
    # 设置测试用户预算
    cost_controller.redis.set(f"user:tier:{test_user_id}", "standard")
    
    # 模拟一些使用量
    today = datetime.now().strftime('%Y-%m-%d')
    daily_key = f"cost:daily:{test_user_id}:{today}"
    cost_controller.redis.set(daily_key, "5.0")  # 已使用$5
    
    # 测试不同成本的请求
    test_scenarios = [
        {
            "name": "低成本请求",
            "request": {
                "model": "qwen-plus",
                "content_length": 500,
                "type": "story_generation"
            }
        },
        {
            "name": "中等成本请求",
            "request": {
                "model": "claude-3-sonnet",
                "content_length": 1500,
                "type": "story_generation"
            }
        },
        {
            "name": "高成本请求",
            "request": {
                "model": "claude-3-opus",
                "content_length": 3000,
                "type": "story_generation"
            }
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n{scenario['name']}:")
        can_proceed, decision_info = await cost_controller.pre_request_budget_check(
            test_user_id, scenario['request']
        )
        
        print(f"  允许执行: {'✅' if can_proceed else '❌'}")
        print(f"  预算状态: {decision_info['budget_status']}")
        print(f"  估算成本: ${decision_info['estimated_cost']:.4f}")
        print(f"  剩余预算: ${decision_info['remaining_budget']:.2f}")
        
        if decision_info.get('suggested_action'):
            print(f"  建议: {decision_info['suggested_action']}")
        
        if decision_info.get('alternative_options'):
            print(f"  替代方案数量: {len(decision_info['alternative_options'])}")
            for alt in decision_info['alternative_options'][:2]:  # 显示前2个
                print(f"    - {alt['description']} (节省: ${alt['cost_saving']:.4f})")
    
    # 3. 测试替代方案生成
    print("\n🔄 3. 测试替代方案生成")
    print("-" * 30)
    
    expensive_request = {
        "model": "claude-3-opus",
        "content_length": 2000,
        "type": "story_generation"
    }
    
    budget_info = await cost_controller._get_budget_info(test_user_id)
    alternatives = await cost_controller._generate_alternatives(expensive_request, budget_info)
    
    print(f"原始请求成本: ${cost_controller._estimate_request_cost(expensive_request).estimated_cost:.4f}")
    print(f"找到 {len(alternatives)} 个替代方案:")
    
    for i, alt in enumerate(alternatives, 1):
        print(f"  {i}. {alt['description']}")
        print(f"     新成本: ${alt['new_cost']:.4f}")
        print(f"     节省: ${alt['cost_saving']:.4f}")
        print()
    
    # 4. 测试成本记录
    print("\n📝 4. 测试成本记录")
    print("-" * 30)
    
    # 记录一些测试成本
    test_costs = [
        {"request": test_requests[0], "actual_cost": 0.15},
        {"request": test_requests[1], "actual_cost": 0.08},
        {"request": test_requests[2], "actual_cost": 0.03}
    ]
    
    for cost_data in test_costs:
        await cost_controller.record_actual_cost(
            test_user_id, 
            cost_data["request"], 
            cost_data["actual_cost"]
        )
        print(f"记录成本: ${cost_data['actual_cost']:.4f} ({cost_data['request']['model']})")
    
    # 5. 测试成本分析
    print("\n📈 5. 测试成本分析")
    print("-" * 30)
    
    analytics = await cost_controller.get_cost_analytics(test_user_id)
    print("成本分析报告:")
    print(f"  日成本分解: {analytics['daily_breakdown']}")
    print(f"  模型使用情况: {analytics['model_usage']}")
    
    # 6. 测试优化建议
    print("\n💡 6. 测试优化建议")
    print("-" * 30)
    
    optimization_suggestions = await cost_controller._suggest_cost_optimization(expensive_request)
    
    print("即时节省建议:")
    for suggestion in optimization_suggestions['immediate_savings']:
        print(f"  - {suggestion['action']}: {suggestion['description']}")
        print(f"    {suggestion['potential_saving']}")
    
    print("\n工作流优化建议:")
    for suggestion in optimization_suggestions['workflow_optimizations']:
        print(f"  - {suggestion['action']}: {suggestion['description']}")
        print(f"    {suggestion['potential_saving']}")
    
    print("\n✅ 成本控制功能测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_cost_control())
