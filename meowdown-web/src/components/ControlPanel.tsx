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
import { useTranslation } from 'react-i18next'

interface ControlPanelProps {
  quality: number
  onQualityChange: (value: number) => void
  progress: number
  progressMessage: string
  isConverting: boolean
  onConvert: () => void
  onUpload?: () => void
}

const qualityPresets: Array<{ key: string; value: number }> = [
  { key: 'extreme', value: 30 },
  { key: 'normal', value: 50 },
  { key: 'recommended', value: 73 },
  { key: 'high', value: 90 },
  { key: 'lossless', value: 100 },
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
  const { t } = useTranslation()
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
          loadingText={t('control.converting')}
          onClick={onConvert}
          disabled={isConverting}
        >
          {isConverting ? t('control.converting') : t('control.convert')}
        </Button>

        <Divider borderColor={dividerColor} opacity={dividerOpacity} />

        {/* 图片质量控制 */}
        <VStack spacing={4} align="stretch">
          <HStack justify="space-between" align="center">
            <Text fontSize="md" fontWeight="semibold">
              {t('control.quality')}
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
              ? t('presets.desc.extreme')
              : quality <= 60
              ? t('presets.desc.normal')
              : quality <= 80
              ? t('presets.desc.recommended')
              : t('presets.desc.high')}
          </Text>
        </VStack>

        <Divider borderColor={dividerColor} opacity={dividerOpacity} />

        {/* 预设网格 */}
        <VStack spacing={3} align="stretch">
          <Text fontSize="md" fontWeight="semibold">
            {t('presets.title')}
          </Text>
          <SimpleGrid columns={3} spacing={2}>
            {qualityPresets.map((preset) => (
              <Button
                key={preset.key}
                size="sm"
                variant={quality === preset.value ? 'solid' : 'outline'}
                colorScheme={quality === preset.value ? 'meowdown' : 'gray'}
                onClick={() => onQualityChange(preset.value)}
                fontSize="xs"
                h="32px"
              >
                {t(`presets.${preset.key}`)}
              </Button>
            ))}
          </SimpleGrid>
        </VStack>

        <Divider borderColor={dividerColor} opacity={dividerOpacity} />

        {/* 进度显示 */}
        <VStack spacing={3} align="stretch">
          <HStack justify="space-between" align="center">
            <Text fontSize="md" fontWeight="semibold">
              {t('progress.title')}
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
              {t('imageBed.upload')}
            </Button>
          </>
        )}

        {/* 底部空间 */}
        <Box flex={1} />
      </VStack>
    </Box>
  )
}
