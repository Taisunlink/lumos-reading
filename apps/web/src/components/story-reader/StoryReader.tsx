'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { Story, StoryPage } from '@/types/story'
import { AttentionManager } from '@/components/neuro-adaptive/AttentionManager'
import { StoryPageRenderer } from './StoryPageRenderer'
import { StoryNavigation } from './StoryNavigation'
import { CROWDInteraction } from './CROWDInteraction'
import { ProgressTracker } from './ProgressTracker'
import { useNeuroAdaptiveStore } from '@/stores/neuro-adaptive'
import { storyApi } from '@/lib/api/stories'

interface StoryReaderProps {
  storyId: string
  childId: string
  onComplete: () => void
}

export function StoryReader({ storyId, childId, onComplete }: StoryReaderProps) {
  const [currentPageIndex, setCurrentPageIndex] = useState(0)
  const [hasCompletedPage, setHasCompletedPage] = useState(false)
  const [showCROWDPrompt, setShowCROWDPrompt] = useState(false)
  const [readingStartTime, setReadingStartTime] = useState<Date>()

  const { adaptations } = useNeuroAdaptiveStore()

  // 获取故事数据
  const { data: story, isLoading, error } = useQuery({
    queryKey: ['story', storyId],
    queryFn: () => storyApi.getStory(storyId)
  })

  const pages = story?.content?.pages || []
  const currentPage = pages[currentPageIndex]
  const isLastPage = currentPageIndex === pages.length - 1
  const totalReadingTime = story?.reading_time ? Math.ceil(story.reading_time / 60) : 10 // 分钟

  useEffect(() => {
    if (story && !readingStartTime) {
      setReadingStartTime(new Date())
    }
  }, [story, readingStartTime])

  // 页面阅读完成处理
  const handlePageComplete = useCallback(async () => {
    if (!hasCompletedPage) {
      setHasCompletedPage(true)

      // 显示CROWD互动（如果有）
      if (currentPage?.crowd_prompt && adaptations.enableCROWDInteractions) {
        setShowCROWDPrompt(true)
      } else {
        // 自动进入下一页或完成
        setTimeout(() => {
          handleNextPage()
        }, adaptations.autism?.enhancePredictability ? 2000 : 1000)
      }
    }
  }, [currentPageIndex, pages.length, currentPage, hasCompletedPage, adaptations])

  // 下一页处理
  const handleNextPage = useCallback(() => {
    if (isLastPage) {
      // 完成整个故事
      handleStoryComplete()
    } else {
      setCurrentPageIndex(prev => prev + 1)
      setHasCompletedPage(false)
      setShowCROWDPrompt(false)
    }
  }, [isLastPage])

  // 上一页处理
  const handlePrevPage = useCallback(() => {
    if (currentPageIndex > 0) {
      setCurrentPageIndex(prev => prev - 1)
      setHasCompletedPage(false)
      setShowCROWDPrompt(false)
    }
  }, [currentPageIndex])

  // 故事完成处理
  const handleStoryComplete = useCallback(async () => {
    if (readingStartTime) {
      const endTime = new Date()
      const durationMinutes = (endTime.getTime() - readingStartTime.getTime()) / 60000
      console.log(`Story completed in ${durationMinutes.toFixed(1)} minutes`)
    }

    onComplete()
  }, [readingStartTime, onComplete])

  // CROWD互动完成处理
  const handleCROWDComplete = useCallback((response: string) => {
    setShowCROWDPrompt(false)

    // 记录互动响应
    console.log('CROWD response:', response)

    // 继续到下一页
    setTimeout(() => {
      handleNextPage()
    }, 500)
  }, [handleNextPage])

  // 注意力休息处理
  const handleAttentionBreak = useCallback(() => {
    console.log('Attention break suggested')
  }, [])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">正在加载故事...</p>
        </div>
      </div>
    )
  }

  if (error || !story) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-500 mb-4">故事加载失败</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            重新加载
          </button>
        </div>
      </div>
    )
  }

  return (
    <AttentionManager
      targetDurationMinutes={totalReadingTime}
      onAttentionBreak={handleAttentionBreak}
      onSessionComplete={handleStoryComplete}
    >
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
        {/* 进度追踪器 */}
        <ProgressTracker
          currentPage={currentPageIndex + 1}
          totalPages={pages.length}
          storyTitle={story.title}
        />

        {/* 主要阅读区域 */}
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-4xl mx-auto">
            {/* 故事页面渲染 */}
            <AnimatePresence mode="wait">
              <motion.div
                key={currentPageIndex}
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -50 }}
                transition={{
                  duration: adaptations.autism?.reduceAnimations ? 0.2 : 0.5
                }}
                className="mb-8"
              >
                <StoryPageRenderer
                  page={currentPage}
                  pageNumber={currentPageIndex + 1}
                  onReadComplete={handlePageComplete}
                  autoAdvance={!adaptations.autism?.enhancePredictability}
                />
              </motion.div>
            </AnimatePresence>

            {/* CROWD互动弹窗 */}
            <AnimatePresence>
              {showCROWDPrompt && currentPage?.crowd_prompt && (
                <CROWDInteraction
                  prompt={currentPage.crowd_prompt}
                  onComplete={handleCROWDComplete}
                  onSkip={() => setShowCROWDPrompt(false)}
                />
              )}
            </AnimatePresence>

            {/* 导航控制 */}
            <StoryNavigation
              currentPage={currentPageIndex + 1}
              totalPages={pages.length}
              canGoNext={hasCompletedPage}
              canGoPrev={currentPageIndex > 0}
              onNext={handleNextPage}
              onPrev={handlePrevPage}
              onComplete={isLastPage ? handleStoryComplete : undefined}
            />
          </div>
        </div>
      </div>
    </AttentionManager>
  )
}
