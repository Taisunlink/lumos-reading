'use client'

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { StoryPage } from '@/types/story'
import { useNeuroAdaptiveStore } from '@/stores/neuro-adaptive'
import { StoryIllustration } from '@/components/illustration/SmartImage'

interface StoryPageRendererProps {
  page: StoryPage
  pageNumber: number
  storyId?: string
  onReadComplete: () => void
  autoAdvance?: boolean
}

export function StoryPageRenderer({ 
  page, 
  pageNumber, 
  storyId,
  onReadComplete, 
  autoAdvance = false 
}: StoryPageRendererProps) {
  const { adaptations } = useNeuroAdaptiveStore()
  const [hasRead, setHasRead] = useState(false)
  const [showReadButton, setShowReadButton] = useState(false)

  // 模拟阅读时间
  const readingTime = page.reading_time_seconds || 30

  useEffect(() => {
    if (autoAdvance && !hasRead) {
      const timer = setTimeout(() => {
        setHasRead(true)
        onReadComplete()
      }, readingTime * 1000)

      return () => clearTimeout(timer)
    } else if (!autoAdvance) {
      // 显示"我已读完"按钮
      setShowReadButton(true)
    }
  }, [autoAdvance, hasRead, readingTime, onReadComplete])

  const handleManualComplete = () => {
    setHasRead(true)
    onReadComplete()
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-8 max-w-2xl mx-auto">
      {/* 页面标题 */}
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          第 {pageNumber} 页
        </h2>
        {readingTime > 0 && (
          <p className="text-sm text-gray-500">
            建议阅读时间: {readingTime} 秒
          </p>
        )}
      </div>

      {/* 故事文本 */}
      <div 
        className="text-center mb-8"
        style={{
          fontSize: adaptations?.dyslexia?.largerFontSize ? 
            `${(adaptations?.textSize || 16) + 4}px` : 
            `${adaptations?.textSize || 16}px`,
          lineHeight: adaptations?.dyslexia?.largerFontSize ? 2.2 : adaptations?.lineHeight,
          color: adaptations?.dyslexia?.highContrastText ? '#000000' : adaptations?.textColor,
          backgroundColor: adaptations?.dyslexia?.highContrastText ? '#ffffff' : 'transparent',
          padding: adaptations?.dyslexia?.highContrastText ? '1rem' : '0'
        }}
      >
        <p className="leading-relaxed whitespace-pre-line">
          {page.text}
        </p>
      </div>

      {/* 智能插图组件 */}
      <div className="text-center mb-8">
        <StoryIllustration
          storyId={storyId || "mock-story-id"}
          pageNumber={pageNumber}
          prompt={page.illustration_prompt}
          className="w-full h-64"
          style={{
            border: adaptations?.autism?.clearVisualStructure ? '2px solid #e5e7eb' : 'none'
          }}
          showPrompt={true}
          onLoad={() => console.log('Illustration loaded')}
          onError={() => console.log('Illustration failed to load')}
        />
      </div>

      {/* 阅读完成按钮 */}
      {showReadButton && !hasRead && (
        <motion.div
          className="text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1 }}
        >
          <button
            onClick={handleManualComplete}
            className="px-8 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium"
          >
            我已读完这一页 ✨
          </button>
        </motion.div>
      )}

      {/* 阅读完成指示 */}
      {hasRead && (
        <motion.div
          className="text-center"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <div className="inline-flex items-center gap-2 text-green-600 font-medium">
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
            已读完
          </div>
        </motion.div>
      )}
    </div>
  )
}
