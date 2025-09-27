'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { ChevronLeft, ChevronRight, CheckCircle } from 'lucide-react'

interface StoryNavigationProps {
  currentPage: number
  totalPages: number
  canGoNext: boolean
  canGoPrev: boolean
  onNext: () => void
  onPrev: () => void
  onComplete?: () => void
}

export function StoryNavigation({
  currentPage,
  totalPages,
  canGoNext,
  canGoPrev,
  onNext,
  onPrev,
  onComplete
}: StoryNavigationProps) {
  const isLastPage = currentPage === totalPages
  const progress = (currentPage / totalPages) * 100

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      {/* 进度条 */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>第 {currentPage} 页，共 {totalPages} 页</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <motion.div
            className="bg-blue-500 h-2 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
      </div>

      {/* 导航按钮 */}
      <div className="flex justify-between items-center">
        <button
          onClick={onPrev}
          disabled={!canGoPrev}
          className={`
            flex items-center gap-2 px-4 py-2 rounded-lg transition-colors
            ${canGoPrev 
              ? 'bg-gray-100 hover:bg-gray-200 text-gray-700' 
              : 'bg-gray-50 text-gray-400 cursor-not-allowed'
            }
          `}
        >
          <ChevronLeft className="w-4 h-4" />
          上一页
        </button>

        <div className="flex gap-2">
          {isLastPage ? (
            <button
              onClick={onComplete}
              className="flex items-center gap-2 px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors font-medium"
            >
              <CheckCircle className="w-4 h-4" />
              完成阅读
            </button>
          ) : (
            <button
              onClick={onNext}
              disabled={!canGoNext}
              className={`
                flex items-center gap-2 px-4 py-2 rounded-lg transition-colors font-medium
                ${canGoNext 
                  ? 'bg-blue-500 hover:bg-blue-600 text-white' 
                  : 'bg-gray-50 text-gray-400 cursor-not-allowed'
                }
              `}
            >
              下一页
              <ChevronRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
