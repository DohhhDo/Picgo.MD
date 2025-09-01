import { 
  Box, 
  Flex, 
  Button, 
  VStack, 
  HStack,
  Text,
  useToast, 
  useColorMode,
  useColorModeValue,
  Badge,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Image,
} from '@chakra-ui/react'
import { MoonIcon, SunIcon, SettingsIcon, CheckCircleIcon, WarningIcon } from '@chakra-ui/icons'
import { useState, useEffect, useRef } from 'react'
import { useApiState } from './hooks/useApiState'
import { MarkdownEditor, ControlPanel, FileOperations, StatsDisplay, ImageBedSettingsModal } from './components'
import { MeowdownAPI } from './services/api'
import { FiUpload, FiDownload } from 'react-icons/fi'

function App() {
  const toast = useToast()
  const { colorMode, toggleColorMode } = useColorMode()
  
  // 应用状态
  const [markdown, setMarkdown] = useState('')
  const [quality, setQuality] = useState(73)
  const [hasChanges, setHasChanges] = useState(false)
  const [originalMarkdown, setOriginalMarkdown] = useState('')
  const [isImageBedOpen, setIsImageBedOpen] = useState(false)
  
  // API 状态
  const { state: apiState, checkConnection, startConversion } = useApiState()

  // 颜色主题
  const bgColor = useColorModeValue('white', 'gray.900')
  const borderColor = useColorModeValue('gray.200', 'gray.700')
  const headerBg = useColorModeValue('gray.50', 'gray.800')
  const panelBg = useColorModeValue('white', 'gray.800')

  // 文件操作（顶栏）
  const fileInputRef = useRef<HTMLInputElement>(null)
  const handleFileOpen = () => fileInputRef.current?.click()
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file && file.name.endsWith('.md')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const content = e.target?.result as string
        setMarkdown(content)
        setOriginalMarkdown(content)
        setHasChanges(false)
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
    if (event.target) event.target.value = ''
  }
  const handleFileSave = () => {
    const blob = new Blob([markdown], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `meowdown-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    toast({ title: '文件已保存', description: 'Markdown 文件已下载到本地', status: 'success', duration: 2000 })
  }

  // 监听 markdown 变化
  useEffect(() => {
    setHasChanges(markdown !== originalMarkdown)
  }, [markdown, originalMarkdown])

  // 处理 markdown 变化
  const handleMarkdownChange = (content: string) => {
    setMarkdown(content)
    if (!originalMarkdown) {
      setOriginalMarkdown(content)
    }
  }

  // 转换功能
  const handleConvert = async () => {
    if (!markdown.trim()) {
      toast({
        title: '请输入 Markdown 内容',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      })
      return
    }

    if (!apiState.isConnected) {
      toast({
        title: '后端服务未连接',
        description: '请确保后端服务正在运行',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
      return
    }

    try {
      // 若启用图床，则附带图床信息（此处读取最近一次保存的配置）
      let imageBed: any = null
      try {
        imageBed = await MeowdownAPI.getImageBedConfig()
      } catch {}

      const response = await startConversion({
        markdown,
        quality,
        output_dir: 'images',
        use_image_bed: Boolean(imageBed?.enabled),
        image_bed_provider: imageBed?.provider || undefined,
        image_bed_config: imageBed?.config || undefined,
      })

      if (response.success) {
        toast({
          title: '转换开始',
          description: '正在处理图片转换...',
          status: 'info',
          duration: 3000,
          isClosable: true,
        })
      }
    } catch (error) {
      toast({
        title: '转换失败',
        description: error instanceof Error ? error.message : '未知错误',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    }
  }

  // 当转换完成时显示成功消息
  useEffect(() => {
    if (apiState.lastResult && apiState.progress === 100) {
      toast({
        title: '转换完成',
        description: apiState.lastResult.message,
        status: 'success',
        duration: 5000,
        isClosable: true,
      })
      
      // 更新 markdown 内容
      if (apiState.lastResult.new_markdown) {
        setMarkdown(apiState.lastResult.new_markdown)
        setOriginalMarkdown(apiState.lastResult.new_markdown)
        setHasChanges(false)
      }
    }
  }, [apiState.lastResult, apiState.progress, toast])

  // 显示错误信息
  useEffect(() => {
    if (apiState.error) {
      toast({
        title: '错误',
        description: apiState.error,
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    }
  }, [apiState.error, toast])

  return (
    <Flex direction="column" h="100vh" bg={bgColor}>
      {/* 顶部标题栏 */}
      <Box px={6} py={3} borderBottom="1px" borderColor={borderColor} bg={headerBg}>
        <HStack spacing={4}>
          {/* Logo 和标题 */}
          <HStack spacing={3}>
            <Image
              src="/maoer.png"
              alt="Meowdown Logo"
              w="32px"
              h="32px"
              borderRadius="8px"
              objectFit="cover"
              fallbackSrc="/icons/image/app-icon-192.png"
            />
            <VStack spacing={0} align="start">
              <Text fontSize="lg" fontWeight="bold" lineHeight="1.2">
                Meowdown
              </Text>
              <Text fontSize="xs" color="gray.500" lineHeight="1.2">
                Markdown 图片转换器
              </Text>
            </VStack>
          </HStack>
          {/* 打开/保存（顶栏左侧） */}
          <HStack spacing={2}>
            <Button size="sm" variant="outline" leftIcon={<FiUpload />} onClick={handleFileOpen}>
              打开文件
            </Button>
            <Button
              size="sm"
              variant="outline"
              leftIcon={<FiDownload />}
              onClick={handleFileSave}
              isDisabled={!markdown.trim()}
              colorScheme={hasChanges ? 'meowdown' : 'gray'}
            >
              保存文件
            </Button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".md"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
            />
          </HStack>

          <Box flex={1} />

          {/* 状态信息 */}
          <HStack spacing={3}>
            {/* 连接状态 */}
            <Badge
              colorScheme={apiState.isConnected ? 'green' : 'red'}
              variant="subtle"
              px={2}
              py={1}
              borderRadius="full"
              fontSize="xs"
            >
              {apiState.isConnected ? (
                <HStack spacing={1}>
                  <CheckCircleIcon w={3} h={3} />
                  <Text>已连接</Text>
                </HStack>
              ) : (
                <HStack spacing={1}>
                  <WarningIcon w={3} h={3} />
                  <Text>未连接</Text>
                </HStack>
              )}
            </Badge>
            
            {/* 转换状态 */}
            <Badge
              colorScheme={apiState.isConverting ? 'orange' : apiState.progress > 0 ? 'green' : 'gray'}
              variant="subtle"
              px={3}
              py={1}
              borderRadius="full"
            >
              {apiState.isConverting ? '转换中' : apiState.progress > 0 ? '已完成' : '就绪'}
            </Badge>
            
            <Text fontSize="sm" color="gray.600">
              质量: {quality}%
            </Text>
          </HStack>

          {/* 工具按钮 */}
          <HStack spacing={2}>
            <Button size="sm" variant="ghost" leftIcon={<SettingsIcon />} onClick={() => setIsImageBedOpen(true)}>
              设置
            </Button>
            <Button
              size="sm"
              variant="ghost"
              leftIcon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
              onClick={toggleColorMode}
            >
              主题
            </Button>
          </HStack>
        </HStack>
      </Box>

      {/* 连接状态提示 */}
      {!apiState.isConnected && (
        <Alert status="warning" variant="solid">
          <AlertIcon />
          <AlertTitle>后端服务未连接！</AlertTitle>
          <AlertDescription>
            请启动后端服务 (python meowdown-backend/main.py) 以使用转换功能
          </AlertDescription>
          <Box flex={1} />
          <Button
            size="sm"
            variant="outline"
            colorScheme="orange"
            onClick={checkConnection}
          >
            重新连接
          </Button>
        </Alert>
      )}

      {/* 主内容区域 */}
      <Flex flex={1} overflow="hidden">
        {/* 左侧编辑器区域 */}
        <Flex direction="column" flex={1} minW={0} bg={panelBg}>
          {/* 文件操作栏（仅保留拖拽能力，隐藏按钮） */}
          <FileOperations
            markdown={markdown}
            onMarkdownChange={handleMarkdownChange}
            hasChanges={hasChanges}
            showButtons={false}
          />
          
          {/* Markdown 编辑器 */}
          <Box flex={1}>
            <MarkdownEditor
              value={markdown}
              onChange={setMarkdown}
              placeholder="在此编辑Markdown内容...

示例:
# 标题
![图片描述](图片链接)"
            />
          </Box>

          {/* 统计显示 */}
          <StatsDisplay
            stats={apiState.lastResult?.stats || null}
            isVisible={apiState.progress === 100 && !!apiState.lastResult?.stats}
          />
        </Flex>

        {/* 右侧控制面板 */}
        <ControlPanel
          quality={quality}
          onQualityChange={setQuality}
          progress={apiState.progress}
          progressMessage={apiState.progressMessage}
          isConverting={apiState.isConverting}
          onConvert={handleConvert}
        />
      </Flex>

      {/* 底部状态栏 */}
      <Box px={6} py={2} borderTop="1px" borderColor={borderColor} bg="meowdown.500" color="white">
        <HStack justify="space-between" fontSize="sm">
          <Text>现代化 Web 版本 - 基于 React + Chakra UI</Text>
          <Text>{apiState.progressMessage}</Text>
        </HStack>
      </Box>

      {/* 图床设置弹窗 */}
      <ImageBedSettingsModal isOpen={isImageBedOpen} onClose={() => setIsImageBedOpen(false)} />
    </Flex>
  )
}

export default App