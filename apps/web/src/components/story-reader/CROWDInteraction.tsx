'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { MessageCircle, X } from 'lucide-react'

interface CROWDInteractionProps {
  prompt: {
    type: 'completion' | 'recall' | 'open_ended' | 'wh_question' | 'distancing'
    text: string
  }
  onComplete: (response: string) => void
  onSkip: () => void
}

export function CROWDInteraction({ prompt, onComplete, onSkip }: CROWDInteractionProps) {
  const [response, setResponse] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const getPromptTitle = (type: string) => {
    const titles = {
      completion: '完成句子',
      recall: '回忆问题',
      open_ended: '开放讨论',
      wh_question: '思考问题',
      distancing: '联系生活'
    }
    return titles[type as keyof typeof titles] || '互动问题'
  }

  const getPromptIcon = (type: string) => {
    const icons = {
      completion: '✏️',
      recall: '🧠',
      open_ended: '💭',
      wh_question: '❓',
      distancing: '🔗'
    }
    return icons[type as keyof typeof icons] || '💬'
  }

  const handleSubmit = async () => {
    if (!response.trim()) return

    setIsSubmitting(true)
    
    // 模拟提交延迟
    await new Promise(resolve => setTimeout(resolve, 500))
    
    onComplete(response)
    setIsSubmitting(false)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      handleSubmit()
    }
  }

  return (
    <motion.div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <motion.div
        className="bg-white rounded-xl p-6 max-w-md w-full"
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
      >
        {/* 头部 */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <MessageCircle className="w-5 h-5 text-blue-500" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-800">
                {getPromptTitle(prompt.type)}
              </h3>
              <p className="text-sm text-gray-500">
                {getPromptIcon(prompt.type)} 让我们来互动一下吧！
              </p>
            </div>
          </div>
          <button
            onClick={onSkip}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-4 h-4 text-gray-500" />
          </button>
        </div>

        {/* 问题内容 */}
        <div className="mb-6">
          <p className="text-gray-700 leading-relaxed">
            {prompt.text}
          </p>
        </div>

        {/* 输入区域 */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            你的回答：
          </label>
          <textarea
            value={response}
            onChange={(e) => setResponse(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="在这里写下你的想法..."
            className="w-full h-24 p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isSubmitting}
          />
          <p className="text-xs text-gray-500 mt-1">
            按 Ctrl+Enter 快速提交
          </p>
        </div>

        {/* 按钮组 */}
        <div className="flex gap-3">
          <button
            onClick={onSkip}
            disabled={isSubmitting}
            className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            跳过
          </button>
          <button
            onClick={handleSubmit}
            disabled={!response.trim() || isSubmitting}
            className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? '提交中...' : '提交回答'}
          </button>
        </div>
      </motion.div>
    </motion.div>
  )
}
