import React from 'react'
import {
  Box,
  Text,
  VStack,
  HStack,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  SimpleGrid,
  useColorModeValue,
  Icon,
} from '@chakra-ui/react'
import { FiImage, FiCheckCircle, FiClock } from 'react-icons/fi'
import { useTranslation } from 'react-i18next'

interface ConversionStats {
  total_images: number
  converted_images: number
  failed_images: number
  skipped_images: number
  conversion_time: number
}

interface StatsDisplayProps {
  stats: ConversionStats | null
  isVisible: boolean
}

// 格式化时间（容错 undefined/null）
const formatTime = (seconds: number | undefined | null): string => {
  const s = Number(seconds ?? 0)
  if (s < 1) return `${(s * 1000).toFixed(0)}ms`
  return `${s.toFixed(1)}s`
}

export const StatsDisplay: React.FC<StatsDisplayProps> = ({ stats, isVisible }) => {
  const { t } = useTranslation()
  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')

  if (!isVisible || !stats) {
    return null
  }

  // 兼容不同命名风格并做空值保护
  const s: any = stats
  const totalImages = Number(s.total_images ?? s.totalImages ?? 0)
  const convertedImages = Number(s.converted_images ?? s.convertedImages ?? 0)
  const failedImages = Number(s.failed_images ?? s.failedImages ?? 0)
  const skippedImages = Number(s.skipped_images ?? s.skippedImages ?? 0)
  const timeSec = Number(s.conversion_time ?? s.conversionTime ?? 0)

  const successRate = totalImages > 0
    ? ((convertedImages / totalImages) * 100).toFixed(1)
    : '0'

  return (
    <Box
      p={4}
      bg={bgColor}
      borderTop="1px"
      borderColor={borderColor}
      borderRadius="md"
    >
      <VStack spacing={4} align="stretch">
        <Text fontSize="sm" fontWeight="semibold" color="gray.600">
          {t('stats.title')}
        </Text>
        
        <SimpleGrid columns={3} spacing={4}>
          <Stat>
            <StatLabel>
              <HStack spacing={2}>
                <Icon as={FiImage} />
                <Text>{t('stats.total')}</Text>
              </HStack>
            </StatLabel>
            <StatNumber fontSize="xl">{totalImages}</StatNumber>
          </Stat>

          <Stat>
            <StatLabel>
              <HStack spacing={2}>
                <Icon as={FiCheckCircle} />
                <Text>{t('stats.success')}</Text>
              </HStack>
            </StatLabel>
            <StatNumber fontSize="xl" color="green.500">
              {convertedImages}
            </StatNumber>
            <StatHelpText>成功率 {successRate}%</StatHelpText>
          </Stat>

          <Stat>
            <StatLabel>
              <HStack spacing={2}>
                <Icon as={FiClock} />
                <Text>{t('stats.time')}</Text>
              </HStack>
            </StatLabel>
            <StatNumber fontSize="xl">
              {formatTime(timeSec)}
            </StatNumber>
          </Stat>
        </SimpleGrid>

        {(failedImages > 0 || skippedImages > 0) && (
          <SimpleGrid columns={2} spacing={4}>
            {failedImages > 0 && (
              <Stat>
                <StatLabel>{t('stats.failed')}</StatLabel>
                <StatNumber fontSize="md" color="red.500">
                  {failedImages}
                </StatNumber>
              </Stat>
            )}
            
            {skippedImages > 0 && (
              <Stat>
                <StatLabel>{t('stats.skipped')}</StatLabel>
                <StatNumber fontSize="md" color="yellow.500">
                  {skippedImages}
                </StatNumber>
              </Stat>
            )}
          </SimpleGrid>
        )}
      </VStack>
    </Box>
  )
}