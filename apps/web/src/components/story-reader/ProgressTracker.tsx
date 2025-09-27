'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { BookOpen, Clock } from 'lucide-react'

interface ProgressTrackerProps {
  currentPage: number
  totalPages: number
  storyTitle: string
}

export function ProgressTracker({ 
  currentPage, 
  totalPages, 
  storyTitle 
}: ProgressTrackerProps) {
  const progress = (currentPage / totalPages) * 100

  return (
    <motion.div
      className="fixed top-4 right-4 z-40"
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="bg-white/90 backdrop-blur-sm rounded-lg p-4 shadow-lg border max-w-xs">
        {/* 故事标题 */}
        <div className="flex items-center gap-2 mb-3">
          <BookOpen className="w-4 h-4 text-blue-500" />
          <h3 className="font-medium text-gray-800 truncate">
            {storyTitle}
          </h3>
        </div>

        {/* 进度信息 */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm text-gray-600">
            <span>阅读进度</span>
            <span>{currentPage}/{totalPages}</span>
          </div>
          
          {/* 进度条 */}
          <div className="w-full bg-gray-200 rounded-full h-2">
            <motion.div
              className="bg-blue-500 h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            />
          </div>

          {/* 百分比 */}
          <div className="text-right text-sm text-gray-500">
            {Math.round(progress)}% 完成
          </div>
        </div>

        {/* 预估剩余时间 */}
        <div className="mt-3 pt-3 border-t border-gray-200">
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <Clock className="w-3 h-3" />
            <span>
              预计还需 {Math.max(0, totalPages - currentPage)} 页
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
