'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Loader2, AlertCircle, Image as ImageIcon } from 'lucide-react'

interface SmartImageProps {
  src?: string
  alt: string
  prompt?: string
  fallbackText?: string
  className?: string
  style?: React.CSSProperties
  onLoad?: () => void
  onError?: () => void
  showPrompt?: boolean
  loadingDelay?: number
}

export function SmartImage({
  src,
  alt,
  prompt,
  fallbackText = "插图加载中...",
  className = "",
  style = {},
  onLoad,
  onError,
  showPrompt = false,
  loadingDelay = 1000
}: SmartImageProps) {
  const [imageStatus, setImageStatus] = useState<'loading' | 'loaded' | 'error' | 'fallback'>('loading')
  const [showLoading, setShowLoading] = useState(false)

  useEffect(() => {
    if (loadingDelay > 0) {
      const timer = setTimeout(() => {
        setShowLoading(true)
      }, loadingDelay)
      return () => clearTimeout(timer)
    } else {
      setShowLoading(true)
    }
  }, [loadingDelay])

  const handleImageLoad = () => {
    setImageStatus('loaded')
    onLoad?.()
  }

  const handleImageError = () => {
    setImageStatus('error')
    onError?.()
  }

  const renderFallback = () => (
    <div 
      className={`flex flex-col items-center justify-center bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg ${className}`}
      style={style}
    >
      <div className="text-center p-8">
        <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
          <ImageIcon className="w-8 h-8 text-white" />
        </div>
        <p className="text-gray-600 text-sm mb-2">{fallbackText}</p>
        {showPrompt && prompt && (
          <p className="text-gray-500 text-xs italic max-w-xs">
            {prompt}
          </p>
        )}
      </div>
    </div>
  )

  const renderLoading = () => (
    <div 
      className={`flex flex-col items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg ${className}`}
      style={style}
    >
      <div className="text-center p-8">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-8 h-8 mx-auto mb-4"
        >
          <Loader2 className="w-8 h-8 text-blue-500" />
        </motion.div>
        <p className="text-gray-600 text-sm">生成插图中...</p>
        {showPrompt && prompt && (
          <p className="text-gray-500 text-xs italic max-w-xs mt-2">
            {prompt}
          </p>
        )}
      </div>
    </div>
  )

  const renderError = () => (
    <div 
      className={`flex flex-col items-center justify-center bg-gradient-to-br from-red-100 to-orange-100 rounded-lg ${className}`}
      style={style}
    >
      <div className="text-center p-8">
        <AlertCircle className="w-8 h-8 text-red-500 mx-auto mb-4" />
        <p className="text-gray-600 text-sm mb-2">插图生成失败</p>
        <p className="text-gray-500 text-xs">将显示占位符</p>
        {showPrompt && prompt && (
          <p className="text-gray-500 text-xs italic max-w-xs mt-2">
            {prompt}
          </p>
        )}
      </div>
    </div>
  )

  // 如果没有src，直接显示占位符
  if (!src) {
    return renderFallback()
  }

  return (
    <div className="relative">
      <AnimatePresence mode="wait">
        {imageStatus === 'loading' && showLoading && (
          <motion.div
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            {renderLoading()}
          </motion.div>
        )}

        {imageStatus === 'loaded' && (
          <motion.div
            key="loaded"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.5 }}
            className="relative"
          >
            <img
              src={src}
              alt={alt}
              className={`w-full h-auto rounded-lg ${className}`}
              style={style}
              onLoad={handleImageLoad}
              onError={handleImageError}
            />
            {showPrompt && prompt && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3, duration: 0.3 }}
                className="absolute bottom-2 left-2 right-2 bg-black bg-opacity-50 text-white text-xs p-2 rounded opacity-0 hover:opacity-100 transition-opacity"
              >
                {prompt}
              </motion.div>
            )}
          </motion.div>
        )}

        {imageStatus === 'error' && (
          <motion.div
            key="error"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            {renderError()}
          </motion.div>
        )}
      </AnimatePresence>

      {/* 隐藏的图片用于预加载 */}
      {src && imageStatus === 'loading' && (
        <img
          src={src}
          alt=""
          className="hidden"
          onLoad={handleImageLoad}
          onError={handleImageError}
        />
      )}
    </div>
  )
}

// 预设的插图组件
export function StoryIllustration({
  storyId,
  pageNumber,
  prompt,
  className = "",
  style = {},
  showPrompt = true,
  onLoad,
  onError
}: {
  storyId: string
  pageNumber: number
  prompt: string
  className?: string
  style?: React.CSSProperties
  showPrompt?: boolean
  onLoad?: () => void
  onError?: () => void
}) {
  const [imageUrl, setImageUrl] = useState<string>()
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchIllustration = async () => {
      try {
        setIsLoading(true)

        // 首先检查是否已经有现成的插图
        const existingResponse = await fetch(`http://localhost:8000/api/v1/illustrations/story/${storyId}`)
        if (existingResponse.ok) {
          const existingData = await existingResponse.json()
          const existingIllustration = existingData.find((img: any) => img.page_number === pageNumber)

          if (existingIllustration && existingIllustration.image_url) {
            setImageUrl(existingIllustration.image_url)
            setIsLoading(false)
            return
          }
        }

        // 如果没有现成的插图，创建新的插图
        console.log(`Generating illustration for story ${storyId}, page ${pageNumber}, prompt: ${prompt}`)

        const createResponse = await fetch('http://localhost:8000/api/v1/illustrations/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            story_id: storyId,
            page_number: pageNumber,
            prompt: prompt,
            style: 'watercolor'
          })
        })

        if (createResponse.ok) {
          const newIllustration = await createResponse.json()
          if (newIllustration.image_url) {
            setImageUrl(newIllustration.image_url)
          }
        } else {
          console.error('Failed to create illustration:', await createResponse.text())
        }

        setIsLoading(false)
      } catch (error) {
        console.error('Failed to fetch illustration:', error)
        setIsLoading(false)
      }
    }

    fetchIllustration()
  }, [storyId, pageNumber, prompt])

  return (
    <SmartImage
      src={imageUrl}
      alt={`故事插图 - 第${pageNumber}页`}
      prompt={prompt}
      fallbackText="插图生成中..."
      className={className}
      style={style}
      showPrompt={showPrompt}
      onLoad={onLoad}
      onError={onError}
      loadingDelay={isLoading ? 1000 : 0}
    />
  )
}
