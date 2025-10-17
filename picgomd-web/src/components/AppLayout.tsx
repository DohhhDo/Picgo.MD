import React from 'react'
import {
  Box,
  Flex,
  HStack,
  VStack,
  Text,
  IconButton,
  useColorMode,
  useColorModeValue,
  Spacer,
  Badge,
} from '@chakra-ui/react'
import { MoonIcon, SunIcon, SettingsIcon } from '@chakra-ui/icons'
import { MarkdownEditor } from './MarkdownEditor'
import { ControlPanel } from './ControlPanel'

interface AppLayoutProps {
  markdown: string
  onMarkdownChange: (value: string) => void
  quality: number
  onQualityChange: (value: number) => void
  progress: number
  progressMessage: string
  isConverting: boolean
  onConvert: () => void
  onUpload?: () => void
  onOpenSettings?: () => void
}

export const AppLayout: React.FC<AppLayoutProps> = ({
  markdown,
  onMarkdownChange,
  quality,
  onQualityChange,
  progress,
  progressMessage,
  isConverting,
  onConvert,
  onUpload,
  onOpenSettings,
}) => {
  const { colorMode, toggleColorMode } = useColorMode()
  const bgColor = useColorModeValue('white', 'gray.900')
  const borderColor = useColorModeValue('gray.200', 'gray.700')
  const headerBg = useColorModeValue('gray.50', 'gray.800')

  return (
    <Flex direction="column" h="100vh" bg={bgColor}>
      {/* 顶部标题栏 */}
      <Box
        px={6}
        py={3}
        borderBottom="1px"
        borderColor={borderColor}
        bg={headerBg}
      >
        <HStack spacing={4}>
          {/* Logo 和标题 */}
          <HStack spacing={3}>
            <Box
              w="32px"
              h="32px"
              bg="meowdown.500"
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

          <Spacer />

          {/* 状态信息 */}
          <HStack spacing={3}>
            <Badge
              colorScheme={isConverting ? 'orange' : progress > 0 ? 'green' : 'gray'}
              variant="subtle"
              px={3}
              py={1}
              borderRadius="full"
            >
              {isConverting ? '转换中' : progress > 0 ? '已完成' : '就绪'}
            </Badge>
            
            <Text fontSize="sm" color="gray.600">
              质量: {quality}%
            </Text>
          </HStack>

          {/* 工具按钮 */}
          <HStack spacing={2}>
            {onOpenSettings && (
              <IconButton
                aria-label="设置"
                icon={<SettingsIcon />}
                variant="ghost"
                size="sm"
                onClick={onOpenSettings}
              />
            )}
            <IconButton
              aria-label="切换主题"
              icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
              variant="ghost"
              size="sm"
              onClick={toggleColorMode}
            />
          </HStack>
        </HStack>
      </Box>

      {/* 主内容区域 */}
      <Flex flex={1} overflow="hidden">
        {/* 左侧编辑器 */}
        <Box flex={1} minW={0}>
          <MarkdownEditor
            value={markdown}
            onChange={onMarkdownChange}
          />
        </Box>

        {/* 右侧控制面板 */}
        <ControlPanel
          quality={quality}
          onQualityChange={onQualityChange}
          progress={progress}
          progressMessage={progressMessage}
          isConverting={isConverting}
          onConvert={onConvert}
          onUpload={onUpload}
        />
      </Flex>

      {/* 底部状态栏 */}
      <Box
        px={6}
        py={2}
        borderTop="1px"
        borderColor={borderColor}
        bg="meowdown.500"
        color="white"
      >
        <HStack justify="space-between" fontSize="sm">
          <Text>
            现代化 Web 版本 - 基于 React + Chakra UI
          </Text>
          <Text>
            {progressMessage}
          </Text>
        </HStack>
      </Box>
    </Flex>
  )
}


