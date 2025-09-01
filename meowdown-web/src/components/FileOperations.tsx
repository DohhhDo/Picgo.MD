import React, { useCallback, useRef, useState } from 'react'
import {
  HStack,
  Button,
  Text,
  useColorModeValue,
  Box,
  useToast,
} from '@chakra-ui/react'
import { FiUpload, FiDownload } from 'react-icons/fi'

interface FileOperationsProps {
  markdown: string
  onMarkdownChange: (content: string) => void
  hasChanges: boolean
  showButtons?: boolean
}

export const FileOperations: React.FC<FileOperationsProps> = ({
  markdown,
  onMarkdownChange,
  hasChanges,
  showButtons = true,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [dragActive, setDragActive] = useState(false)
  const toast = useToast()
  const borderColor = useColorModeValue('gray.200', 'gray.600')
  const headerBg = useColorModeValue('gray.50', 'gray.800')
  const hoverBorderColor = useColorModeValue('meowdown.500', 'meowdown.300')

  // 处理文件打开
  const handleFileOpen = useCallback(() => {
    fileInputRef.current?.click()
  }, [])

  // 处理文件选择
  const handleFileSelect = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0]
      if (file && file.name.endsWith('.md')) {
        const reader = new FileReader()
        reader.onload = (e) => {
          const content = e.target?.result as string
          onMarkdownChange(content)
          toast({
            title: '文件已加载',
            description: `成功加载 ${file.name}`,
            status: 'success',
            duration: 2000,
          })
        }
        reader.readAsText(file)
      } else {
        toast({
          title: '文件格式错误',
          description: '请选择 .md 格式的 Markdown 文件',
          status: 'error',
          duration: 3000,
        })
      }
      // 清空输入，允许重复选择同一文件
      if (event.target) {
        event.target.value = ''
      }
    },
    [onMarkdownChange, toast]
  )

  // 处理文件保存
  const handleFileSave = useCallback(() => {
    const blob = new Blob([markdown], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `meowdown-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    toast({
      title: '文件已保存',
      description: 'Markdown 文件已下载到本地',
      status: 'success',
      duration: 2000,
    })
  }, [markdown, toast])

  // 处理拖拽事件
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleDragIn = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setDragActive(true)
    }
  }, [])

  const handleDragOut = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      e.stopPropagation()
      setDragActive(false)
      
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const file = e.dataTransfer.files[0]
        if (file.name.endsWith('.md')) {
          const reader = new FileReader()
          reader.onload = (event) => {
            const content = event.target?.result as string
            onMarkdownChange(content)
            toast({
              title: '文件已加载',
              description: `成功加载 ${file.name}`,
              status: 'success',
              duration: 2000,
            })
          }
          reader.readAsText(file)
        } else {
          toast({
            title: '文件格式错误',
            description: '请拖拽 .md 格式的 Markdown 文件',
            status: 'error',
            duration: 3000,
          })
        }
      }
    },
    [onMarkdownChange, toast]
  )

  return (
    <Box
      position="relative"
      onDragEnter={handleDragIn}
      onDragLeave={handleDragOut}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      {/* 拖拽覆盖层 */}
      {dragActive && (
        <Box
          position="absolute"
          top={0}
          left={0}
          right={0}
          bottom={0}
          bg="meowdown.50"
          border="2px dashed"
          borderColor="meowdown.400"
          borderRadius="md"
          display="flex"
          alignItems="center"
          justifyContent="center"
          zIndex={1000}
          _dark={{
            bg: 'meowdown.900',
            borderColor: 'meowdown.300',
          }}
        >
          <Text fontSize="lg" fontWeight="semibold" color="meowdown.600" _dark={{ color: 'meowdown.300' }}>
            拖放 Markdown 文件到这里
          </Text>
        </Box>
      )}

      {/* 文件操作按钮（可选显示） */}
      {showButtons && (
        <HStack spacing={3} p={4} borderBottom="1px" borderColor={borderColor} bg={headerBg}>
          <Button
            leftIcon={<FiUpload />}
            size="sm"
            variant="outline"
            onClick={handleFileOpen}
            _hover={{
              borderColor: hoverBorderColor,
            }}
          >
            打开文件
          </Button>
          
          <Button
            leftIcon={<FiDownload />}
            size="sm"
            variant="outline"
            onClick={handleFileSave}
            isDisabled={!markdown.trim()}
            colorScheme={hasChanges ? 'meowdown' : 'gray'}
            _hover={{
              borderColor: hoverBorderColor,
            }}
          >
            保存文件
          </Button>

          {hasChanges && (
            <Text fontSize="sm" color="meowdown.500" fontStyle="italic">
              有未保存的更改
            </Text>
          )}

          {/* 隐藏的文件输入 */}
          <input
            ref={fileInputRef}
            type="file"
            accept=".md"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
        </HStack>
      )}
    </Box>
  )
}
