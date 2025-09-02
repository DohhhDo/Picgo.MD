import { 
  Button, 
  Menu, 
  MenuButton, 
  MenuList, 
  MenuItem, 
  HStack, 
  Text 
} from '@chakra-ui/react'
import { ChevronDownIcon } from '@chakra-ui/icons'
import { useTranslation } from 'react-i18next'

const languages = [
  { code: 'zh', name: '中文', flag: '🇨🇳' },
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'es', name: 'Español', flag: '🇪🇸' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' }
]

export function LanguageSelector() {
  const { i18n } = useTranslation()

  const currentLanguage = languages.find(lang => lang.code === i18n.language) || languages[0]

  const changeLanguage = (languageCode: string) => {
    i18n.changeLanguage(languageCode)
  }

  return (
    <Menu>
      <MenuButton
        as={Button}
        size="sm"
        variant="ghost"
        rightIcon={<ChevronDownIcon />}
        minW="auto"
      >
        <HStack spacing={1}>
          <Text fontSize="sm">{currentLanguage.flag}</Text>
          <Text fontSize="xs" display={{ base: 'none', md: 'block' }}>
            {currentLanguage.name}
          </Text>
        </HStack>
      </MenuButton>
      <MenuList minW="120px">
        {languages.map((language) => (
          <MenuItem
            key={language.code}
            onClick={() => changeLanguage(language.code)}
            bg={i18n.language === language.code ? 'meowdown.50' : 'transparent'}
            _hover={{ bg: 'meowdown.100' }}
          >
            <HStack spacing={2}>
              <Text>{language.flag}</Text>
              <Text fontSize="sm">{language.name}</Text>
            </HStack>
          </MenuItem>
        ))}
      </MenuList>
    </Menu>
  )
}
