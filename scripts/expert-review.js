#!/usr/bin/env node

/**
 * LumosReading 专家评审脚本
 * 用于代码质量检查和专家建议
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 LumosReading 专家评审系统启动...\n');

// 检查项目结构
function checkProjectStructure() {
  console.log('📁 检查项目结构...');
  
  const requiredDirs = [
    'apps/web',
    'apps/api', 
    'apps/ai-service',
    'packages/ui',
    'packages/types',
    'infrastructure/docker',
    'docs',
    'tests'
  ];
  
  const missingDirs = requiredDirs.filter(dir => !fs.existsSync(dir));
  
  if (missingDirs.length === 0) {
    console.log('✅ 项目结构完整');
  } else {
    console.log('❌ 缺少目录:', missingDirs.join(', '));
  }
  
  return missingDirs.length === 0;
}

// 检查配置文件
function checkConfigFiles() {
  console.log('\n⚙️ 检查配置文件...');
  
  const requiredFiles = [
    'package.json',
    'turbo.json',
    'docker-compose.yml',
    'env.example',
    '.gitignore'
  ];
  
  const missingFiles = requiredFiles.filter(file => !fs.existsSync(file));
  
  if (missingFiles.length === 0) {
    console.log('✅ 配置文件完整');
  } else {
    console.log('❌ 缺少文件:', missingFiles.join(', '));
  }
  
  return missingFiles.length === 0;
}

// 检查AI服务结构
function checkAIServiceStructure() {
  console.log('\n🤖 检查AI服务结构...');
  
  const aiDirs = [
    'apps/ai-service/agents/psychology',
    'apps/ai-service/agents/story_creation', 
    'apps/ai-service/agents/quality_control',
    'apps/ai-service/prompts',
    'apps/ai-service/validators'
  ];
  
  const missingDirs = aiDirs.filter(dir => !fs.existsSync(dir));
  
  if (missingDirs.length === 0) {
    console.log('✅ AI服务结构完整');
  } else {
    console.log('❌ AI服务缺少目录:', missingDirs.join(', '));
  }
  
  return missingDirs.length === 0;
}

// 专家建议
function generateExpertAdvice() {
  console.log('\n💡 专家建议:');
  console.log('1. 确保所有AI Agent都实现了BaseAgent接口');
  console.log('2. 配置好降级策略，确保100%可用性');
  console.log('3. 设置好神经多样性适配参数');
  console.log('4. 配置好监控和日志系统');
  console.log('5. 准备好预生产内容库');
}

// 主函数
function main() {
  const structureOk = checkProjectStructure();
  const configOk = checkConfigFiles();
  const aiOk = checkAIServiceStructure();
  
  console.log('\n📊 评审结果:');
  console.log(`项目结构: ${structureOk ? '✅' : '❌'}`);
  console.log(`配置文件: ${configOk ? '✅' : '❌'}`);
  console.log(`AI服务: ${aiOk ? '✅' : '❌'}`);
  
  if (structureOk && configOk && aiOk) {
    console.log('\n🎉 项目已准备好进入下一阶段！');
  } else {
    console.log('\n⚠️ 请先完善上述问题再继续');
  }
  
  generateExpertAdvice();
}

main();
