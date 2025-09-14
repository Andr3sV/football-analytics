import countries from 'i18n-iso-countries'
import en from 'i18n-iso-countries/langs/en.json'

countries.registerLocale(en as any)

function countryCodeToFlagEmoji(countryCode: string): string {
  if (!countryCode || countryCode.length !== 2) return ''
  const codePoints = countryCode
    .toUpperCase()
    .split('')
    .map((char) => 127397 + char.charCodeAt(0))
  return String.fromCodePoint(...codePoints)
}

function normalizeCountryName(name: string): string {
  if (!name) return ''
  // Common normalizations in dataset
  const trimmed = name.trim()
  const replacements: Record<string, string> = {
    'Korea, South': 'South Korea',
    'Korea, North': 'North Korea',
    'Bosnia-Herzegovina': 'Bosnia and Herzegovina',
    'Congo, DR': 'Congo, The Democratic Republic of the',
    'Congo DR': 'Congo, The Democratic Republic of the',
    'Czech Republic': 'Czechia',
    'USA': 'United States',
    'UK': 'United Kingdom',
  }
  return replacements[trimmed] ?? trimmed
}

export function getFlagEmojiByCountryName(countryName?: string): string {
  if (!countryName) return ''
  const normalized = normalizeCountryName(countryName)
  let code = countries.getAlpha2Code(normalized, 'en')
  if (!code && normalized.includes('-')) {
    code = countries.getAlpha2Code(normalized.replace('-', ' '), 'en')
  }
  if (!code && normalized.includes(',')) {
    const parts = normalized.split(',')
    const swapped = parts.slice(1).concat(parts[0]).join(' ').trim()
    code = countries.getAlpha2Code(swapped, 'en')
  }
  return code ? countryCodeToFlagEmoji(code) : ''
}


