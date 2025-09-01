import React from 'react'
import {
  VStack,
  Button,
  Text,
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
  Box,
  Progress,
  SimpleGrid,
  useColorModeValue,
  Badge,
  HStack,
  Divider,
} from '@chakra-ui/react'
import type { QualityPreset } from '../types'

interface ControlPanelProps {
  quality: number
  onQualityChange: (value: number) => void
  progress: number
  progressMessage: string
  isConverting: boolean
  onConvert: () => void
  onUpload?: () => void
}

const qualityPresets: QualityPreset[] = [
  { name: '极缩', value: 30, description: '最小体积' },
  { name: '常规', value: 50, description: '平衡模式' },
  { name: '推荐', value: 73, description: '推荐设置' },
  { name: '高品', value: 90, description: '高质量' },
  { name: '无损', value: 100, description: '原图质量' },
]

export const ControlPanel: React.FC<ControlPanelProps> = ({
  quality,
  onQualityChange,
  progress,
  progressMessage,
  isConverting,
  onConvert,
  onUpload,
}) => {
  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.600')
  const dividerColor = useColorModeValue('gray.200', 'gray.700')
  const dividerOpacity = useColorModeValue(0.6, 0.3)

  return (
    <Box
      w="280px"
      bg={bgColor}
      border="1px"
      borderColor={borderColor}
      borderRadius="lg"
      boxShadow={useColorModeValue('xl', 'dark-lg')}
      position="fixed"
      right={6}
      top={20}
      maxH="82vh"
      overflowY="auto"
      zIndex={10}
      p={6}
    >
      <VStack spacing={6} align="stretch" h="full">
        {/* 转换按钮 */}
        <Button
          size="lg"
          h="48px"
          colorScheme="meowdown"
          isLoading={isConverting}
          loadingText="转换中..."
          onClick={onConvert}
          disabled={isConverting}
        >
          {isConverting ? '转换中...' : '转换'}
        </Button>

        <Divider borderColor={dividerColor} opacity={dividerOpacity} />

        {/* 图片质量控制 */}
        <VStack spacing={4} align="stretch">
          <HStack justify="space-between" align="center">
            <Text fontSize="md" fontWeight="semibold">
              图片质量
            </Text>
            <Badge
              colorScheme="meowdown"
              variant="solid"
              fontSize="sm"
              px={3}
              py={1}
              borderRadius="full"
            >
              {quality}%
            </Badge>
          </HStack>

          {/* 质量滑块 */}
          <Box px={2}>
            <Slider
              value={quality}
              min={1}
              max={100}
              step={1}
              onChange={onQualityChange}
              colorScheme="meowdown"
            >
              <SliderTrack h="6px" borderRadius="full">
                <SliderFilledTrack />
              </SliderTrack>
              <SliderThumb boxSize="20px" />
            </Slider>
          </Box>

          {/* 质量描述 */}
          <Text fontSize="sm" color="gray.500" textAlign="center">
            {quality <= 30
              ? '极致压缩，最小体积'
              : quality <= 60
              ? '平衡模式，适合网络传输'
              : quality <= 80
              ? '推荐设置，质量与体积兼顾'
              : '高质量，接近原图'}
          </Text>
        </VStack>

        <Divider borderColor={dividerColor} opacity={dividerOpacity} />

        {/* 预设网格 */}
        <VStack spacing={3} align="stretch">
          <Text fontSize="md" fontWeight="semibold">
            快速预设
          </Text>
          <SimpleGrid columns={3} spacing={2}>
            {qualityPresets.map((preset) => (
              <Button
                key={preset.name}
                size="sm"
                variant={quality === preset.value ? 'solid' : 'outline'}
                colorScheme={quality === preset.value ? 'meowdown' : 'gray'}
                onClick={() => onQualityChange(preset.value)}
                fontSize="xs"
                h="32px"
              >
                {preset.name}
              </Button>
            ))}
          </SimpleGrid>
        </VStack>

        <Divider borderColor={dividerColor} opacity={dividerOpacity} />

        {/* 进度显示 */}
        <VStack spacing={3} align="stretch">
          <HStack justify="space-between" align="center">
            <Text fontSize="md" fontWeight="semibold">
              转换进度
            </Text>
            <Text fontSize="sm" color="gray.500">
              {progress}%
            </Text>
          </HStack>

          <Progress
            value={progress}
            colorScheme="meowdown"
            size="md"
            borderRadius="full"
            bg={useColorModeValue('gray.100', 'gray.700')}
          />

          <Text fontSize="sm" color="gray.600" textAlign="center" minH="20px">
            {progressMessage}
          </Text>
        </VStack>

        {/* 图床上传按钮 */}
        {onUpload && (
          <>
            <Divider borderColor={dividerColor} opacity={dividerOpacity} />
            <Button
              variant="outline"
              colorScheme="meowdown"
              onClick={onUpload}
              disabled={isConverting || progress === 0}
              size="md"
            >
              上传到图床
            </Button>
          </>
        )}

        {/* 底部空间 */}
        <Box flex={1} />
      </VStack>
    </Box>
  )
}
