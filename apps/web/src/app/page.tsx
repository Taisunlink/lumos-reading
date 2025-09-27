'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { AdaptiveProvider } from '@/components/neuro-adaptive/AdaptiveProvider'
import { StoryReader } from '@/components/story-reader/StoryReader'
import { useNeuroAdaptiveStore } from '@/stores/neuro-adaptive'
import { BookOpen, Settings, User, Sparkles } from 'lucide-react'

export default function HomePage() {
  const [currentStoryId, setCurrentStoryId] = useState<string | null>(null)
  const [showSettings, setShowSettings] = useState(false)
  const { adaptations, applyPreset } = useNeuroAdaptiveStore()

  // 模拟儿童档案数据
  const mockChildProfile = {
    id: 'child-1',
    name: '小明',
    age: 6,
    age_group: '6-8',
    cognitive_stage: 'concrete_operational',
    neuro_profile: {
      adhd: {
        shortAttentionBlocks: true,
        enableBreakReminders: true,
        autoResumeAfterBreak: false,
        reduceVisualClutter: true,
        increaseFocusIndicators: true,
        showProgressIndicator: true
      },
      autism: {
        enhancePredictability: false,
        reduceAnimations: false,
        clearVisualStructure: false,
        explicitInstructions: false,
        sensoryComfort: false
      },
      dyslexia: {
        highContrastText: false,
        largerFontSize: false,
        readingGuide: false,
        audioSupport: false
      }
    }
  }

  // 模拟故事数据
  const mockStory = {
    id: 'story-1',
    title: '小兔子的冒险',
    theme: '友谊',
    reading_time: 600, // 10分钟
    content: {
      pages: [
        {
          page_number: 1,
          text: '从前有一只小兔子，它非常喜欢跳跳跳。小兔子每天都会在花园里蹦蹦跳跳，快乐极了。',
          illustration_prompt: '一只快乐的小兔子在花园里跳跃',
          crowd_prompt: {
            type: 'completion',
            text: '小兔子喜欢...'
          },
          reading_time_seconds: 30,
          word_count: 45
        },
        {
          page_number: 2,
          text: '有一天，小兔子遇到了一个关于友谊的挑战。它发现自己的朋友小熊看起来很伤心。',
          illustration_prompt: '小兔子关心地看着伤心的小熊',
          crowd_prompt: {
            type: 'wh_question',
            text: '你觉得小熊为什么伤心呢？'
          },
          reading_time_seconds: 35,
          word_count: 50
        },
        {
          page_number: 3,
          text: '通过努力和智慧，小兔子学会了友谊的真谛。它帮助小熊解决了问题，两个好朋友更加亲密了。',
          illustration_prompt: '小兔子和小熊快乐地拥抱在一起',
          reading_time_seconds: 40,
          word_count: 55
        }
      ]
    }
  }

  const handleStartReading = () => {
    setCurrentStoryId(mockStory.id)
  }

  const handleStoryComplete = () => {
    setCurrentStoryId(null)
    alert('恭喜你完成了故事阅读！🎉')
  }

  if (currentStoryId) {
    return (
      <AdaptiveProvider childProfile={mockChildProfile}>
        <StoryReader
          storyId={currentStoryId}
          childId={mockChildProfile.id}
          onComplete={handleStoryComplete}
        />
      </AdaptiveProvider>
    )
  }

  return (
    <AdaptiveProvider childProfile={mockChildProfile}>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
        {/* 头部导航 */}
        <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
                  <BookOpen className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-800">LumosReading</h1>
                  <p className="text-sm text-gray-600">AI驱动的儿童阅读平台</p>
                </div>
              </div>
              
              <div className="flex items-center gap-4">
                <button
                  onClick={() => setShowSettings(!showSettings)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <Settings className="w-5 h-5 text-gray-600" />
                </button>
                <div className="flex items-center gap-2">
                  <User className="w-5 h-5 text-gray-600" />
                  <span className="text-sm text-gray-700">{mockChildProfile.name}</span>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* 主要内容 */}
        <main className="container mx-auto px-4 py-8">
          <div className="max-w-4xl mx-auto">
            {/* 欢迎区域 */}
            <motion.div
              className="text-center mb-12"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-6">
                <Sparkles className="w-12 h-12 text-white" />
              </div>
              <h2 className="text-4xl font-bold text-gray-800 mb-4">
                欢迎来到 LumosReading！
              </h2>
              <p className="text-xl text-gray-600 mb-8">
                为 {mockChildProfile.name} 量身定制的AI故事阅读体验
              </p>
            </motion.div>

            {/* 故事卡片 */}
            <motion.div
              className="bg-white rounded-xl shadow-lg p-8 mb-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <div className="text-center">
                <h3 className="text-2xl font-bold text-gray-800 mb-4">
                  {mockStory.title}
                </h3>
                <p className="text-gray-600 mb-6">
                  主题：{mockStory.theme} | 适合年龄：{mockChildProfile.age_group}岁
                </p>
                <p className="text-gray-700 mb-8 leading-relaxed">
                  这是一个关于友谊的温馨故事，讲述了小兔子如何帮助朋友小熊，
                  并在这个过程中学会友谊真谛的冒险旅程。
                </p>
                
                <button
                  onClick={handleStartReading}
                  className="px-8 py-4 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium text-lg"
                >
                  开始阅读 📖
                </button>
              </div>
            </motion.div>

            {/* 自适应设置面板 */}
            {showSettings && (
              <motion.div
                className="bg-white rounded-xl shadow-lg p-6"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <h3 className="text-lg font-semibold text-gray-800 mb-4">
                  阅读偏好设置
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <button
                    onClick={() => applyPreset('adhd')}
                    className={`p-4 rounded-lg border-2 transition-colors ${
                      adaptations.adhd?.shortAttentionBlocks
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="text-center">
                      <div className="text-2xl mb-2">🎯</div>
                      <h4 className="font-medium">ADHD友好</h4>
                      <p className="text-sm text-gray-600">短时间专注块</p>
                    </div>
                  </button>

                  <button
                    onClick={() => applyPreset('autism')}
                    className={`p-4 rounded-lg border-2 transition-colors ${
                      adaptations.autism?.enhancePredictability
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="text-center">
                      <div className="text-2xl mb-2">🌟</div>
                      <h4 className="font-medium">自闭谱系友好</h4>
                      <p className="text-sm text-gray-600">增强可预测性</p>
                    </div>
                  </button>

                  <button
                    onClick={() => applyPreset('dyslexia')}
                    className={`p-4 rounded-lg border-2 transition-colors ${
                      adaptations.dyslexia?.highContrastText
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="text-center">
                      <div className="text-2xl mb-2">📖</div>
                      <h4 className="font-medium">阅读障碍友好</h4>
                      <p className="text-sm text-gray-600">高对比度文本</p>
                    </div>
                  </button>
                </div>
              </motion.div>
            )}
          </div>
        </main>
      </div>
    </AdaptiveProvider>
  )
}