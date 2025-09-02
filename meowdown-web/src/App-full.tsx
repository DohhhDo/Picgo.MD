import { 
  Box, 
  Flex, 
  Button, 
  VStack, 
  HStack,
  Textarea,
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
  Text,
  Progress,
  useToast, 
  useColorMode,
  useColorModeValue,
  Badge,
  Divider,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
} from '@chakra-ui/react'
import { MoonIcon, SunIcon, SettingsIcon, CheckCircleIcon, WarningIcon } from '@chakra-ui/icons'
import { useState, useEffect } from 'react'
import { useApiState } from './hooks/useApiState'

function App() {
  const toast = useToast()
  const { colorMode, toggleColorMode } = useColorMode()
  
  // 应用状态
  const [markdown, setMarkdown] = useState('')
  const [quality, setQuality] = useState(73)
  
  // API 状态
  const { state: apiState, checkConnection, startConversion } = useApiState()

  // 颜色主题
  const bgColor = useColorModeValue('white', 'gray.900')
  const borderColor = useColorModeValue('gray.200', 'gray.700')
  const headerBg = useColorModeValue('gray.50', 'gray.800')

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
      const response = await startConversion({
        markdown,
        quality,

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
            <Box
              w="32px"
              h="32px"
              bg="green.500"
              borderRadius="8px"
              display="flex"
              alignItems="center"
              justifyContent="center"
              color="white"
              fontWeight="bold"
              fontSize="lg"
            >
              🐾
            </Box>
            <VStack spacing={0} align="start">
              <Text fontSize="lg" fontWeight="bold" lineHeight="1.2">
                Meowdown
              </Text>
              <Text fontSize="xs" color="gray.500" lineHeight="1.2">
                Markdown 图片转换器
              </Text>
            </VStack>
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
            <Button
              size="sm"
              variant="ghost"
              leftIcon={<SettingsIcon />}
              onClick={() => toast({ title: '设置功能开发中', status: 'info', duration: 2000 })}
            >
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
        {/* 左侧编辑器 */}
        <Box flex={1} minW={0} borderRight="1px" borderColor={borderColor}>
          <VStack spacing={0} h="full" align="stretch">
            <Box px={4} py={2} borderBottom="1px" borderColor={borderColor} bg={headerBg}>
              <Text fontSize="sm" fontWeight="medium" color="gray.600">
                Markdown 编辑器
              </Text>
            </Box>
            <Box flex={1}>
              <Textarea
                value={markdown}
                onChange={(e) => setMarkdown(e.target.value)}
                placeholder="在此编辑Markdown内容...

示例:
# 标题
![图片描述](图片链接)"
                resize="none"
                border="none"
                fontSize="14px"
                fontFamily="mono"
                lineHeight="1.6"
                p={4}
                h="full"
                _focus={{ boxShadow: 'none' }}
              />
            </Box>
          </VStack>
        </Box>

        {/* 右侧控制面板 */}
        <Box w="280px" h="full" p={6}>
          <VStack spacing={6} align="stretch" h="full">
            {/* 转换按钮 */}
            <Button
              size="lg"
              h="48px"
              colorScheme="green"
              isLoading={apiState.isConverting}
              loadingText="转换中..."
              onClick={handleConvert}
              isDisabled={!apiState.isConnected}
            >
              转换
            </Button>

            <Divider />

            {/* 图片质量控制 */}
            <VStack spacing={4} align="stretch">
              <HStack justify="space-between">
                <Text fontSize="md" fontWeight="semibold">图片质量</Text>
                <Badge colorScheme="green" variant="solid" px={3} py={1} borderRadius="full">
                  {quality}%
                </Badge>
              </HStack>

              <Box px={2}>
                <Slider
                  value={quality}
                  min={1}
                  max={100}
                  step={1}
                  onChange={setQuality}
                  colorScheme="green"
                >
                  <SliderTrack h="6px" borderRadius="full">
                    <SliderFilledTrack />
                  </SliderTrack>
                  <SliderThumb boxSize="20px" />
                </Slider>
              </Box>

              <Text fontSize="sm" color="gray.500" textAlign="center">
                {quality <= 30 ? '极致压缩' : quality <= 60 ? '平衡模式' : quality <= 80 ? '推荐设置' : '高质量'}
              </Text>
            </VStack>

            <Divider />

            {/* 进度显示 */}
            <VStack spacing={3} align="stretch">
              <HStack justify="space-between">
                <Text fontSize="md" fontWeight="semibold">转换进度</Text>
                <Text fontSize="sm" color="gray.500">{apiState.progress}%</Text>
              </HStack>

              <Progress
                value={apiState.progress}
                colorScheme="green"
                size="md"
                borderRadius="full"
              />

              <Text fontSize="sm" color="gray.600" textAlign="center" minH="20px">
                {apiState.progressMessage}
              </Text>
            </VStack>

            <Box flex={1} />
          </VStack>
        </Box>
      </Flex>

      {/* 底部状态栏 */}
      <Box px={6} py={2} borderTop="1px" borderColor={borderColor} bg="green.500" color="white">
        <HStack justify="space-between" fontSize="sm">
          <Text>现代化 Web 版本 - 基于 React + Chakra UI</Text>
          <Text>{apiState.progressMessage}</Text>
        </HStack>
      </Box>
    </Flex>
  )
}

export default App