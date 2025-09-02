import React, { useEffect, useState } from 'react'
import { Badge, HStack, Text, Tooltip } from '@chakra-ui/react'
import { CheckCircleIcon, WarningIcon } from '@chakra-ui/icons'
import { MeowdownAPI, type ImageBedConfig } from '../services/api'

export const ImageBedStatusBadge: React.FC = () => {
  const [config, setConfig] = useState<ImageBedConfig | null>(null)
  const [loading, setLoading] = useState<boolean>(false)

  useEffect(() => {
    let mounted = true
    const load = async () => {
      try {
        setLoading(true)
        const cfg = await MeowdownAPI.getImageBedConfig()
        if (mounted) setConfig(cfg as ImageBedConfig)
      } catch {
        if (mounted) setConfig(null)
      } finally {
        setLoading(false)
      }
    }
    load()

    // 周期性刷新，防止设置变更后不更新
    const timer = setInterval(load, 10000)
    return () => {
      mounted = false
      clearInterval(timer)
    }
  }, [])

  const enabled = Boolean(config?.enabled)
  const provider = config?.provider || '未配置'
  const colorScheme = enabled ? 'green' : 'gray'
  const label = enabled ? provider : '图床未启用'
  const title = enabled ? `图床：${provider}` : '图床未启用'

  return (
    <Tooltip label={title} hasArrow openDelay={300}>
      <Badge
        colorScheme={colorScheme}
        variant="subtle"
        px={2}
        py={1}
        borderRadius="full"
        fontSize="xs"
      >
        <HStack spacing={1}>
          {enabled ? <CheckCircleIcon w={3} h={3} /> : <WarningIcon w={3} h={3} />}
          <Text>{loading ? '读取中...' : label}</Text>
        </HStack>
      </Badge>
    </Tooltip>
  )
}

export default ImageBedStatusBadge


