"use client"

import { useState, useEffect } from 'react'
import Papa from 'papaparse'

export interface Player {
  player_id: string
  full_name: string
  current_club: string
  competition: string
  youth_club: string
  youth_club_country: string
  nationality: string
  position: string
  date_of_birth: string
  latest_market_value: string
  latest_transfer_date: string
  latest_fee: string
  age: string
  dominant_foot: string
  youth_club_cleaned: string
}

function normalizeCountryName(country: string): string {
  if (!country || country.trim() === '' || country === 'Not found') {
    return country
  }
  
  const normalized = country.trim()
  
  // Common country name normalizations
  const countryMappings: Record<string, string> = {
    'brasil': 'Brazil',
    'BRASIL': 'Brazil',
    'Brasil': 'Brazil',
    'usa': 'United States',
    'USA': 'United States',
    'united states of america': 'United States',
    'us': 'United States',
    'uk': 'United Kingdom',
    'UK': 'United Kingdom',
    'great britain': 'United Kingdom',
    'england': 'England',
    'scotland': 'Scotland',
    'wales': 'Wales',
    'northern ireland': 'Northern Ireland',
    'korea south': 'South Korea',
    'korea, south': 'South Korea',
    'south korea': 'South Korea',
    'korea north': 'North Korea',
    'korea, north': 'North Korea',
    'north korea': 'North Korea',
    'bosnia-herzegovina': 'Bosnia and Herzegovina',
    'bosnia & herzegovina': 'Bosnia and Herzegovina',
    'czech republic': 'Czech Republic',
    'czechia': 'Czech Republic',
    'russian federation': 'Russia',
    'russian fed.': 'Russia',
    'congo dr': 'Democratic Republic of the Congo',
    'congo, dr': 'Democratic Republic of the Congo',
    'dr congo': 'Democratic Republic of the Congo',
    'ivory coast': 'Côte d\'Ivoire',
    'cape verde': 'Cape Verde',
    'cape verde islands': 'Cape Verde'
  }
  
  // Check exact matches first (case insensitive)
  const lowerNormalized = normalized.toLowerCase()
  for (const [key, value] of Object.entries(countryMappings)) {
    if (lowerNormalized === key.toLowerCase()) {
      return value
    }
  }
  
  // Return the original with proper casing (first letter uppercase)
  return normalized.charAt(0).toUpperCase() + normalized.slice(1).toLowerCase()
}

interface UsePlayerDataReturn {
  players: Player[]
  loading: boolean
  error: string | null
  totalPlayers: number
  playersWithYouthClub: number
  marketValueSum: number
}

export function usePlayerData(): UsePlayerDataReturn {
  const [players, setPlayers] = useState<Player[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true)
        const response = await fetch('/data.csv')
        
        if (!response.ok) {
          throw new Error('Failed to load data')
        }
        
        const csvText = await response.text()
        
        Papa.parse(csvText, {
          header: true,
          skipEmptyLines: true,
          complete: (results) => {
            if (results.errors.length > 0) {
              console.warn('CSV parsing warnings:', results.errors)
            }
            
            const processedData = results.data as Player[]
            
            // Filter out invalid or incomplete rows and normalize country names
            const validPlayers = processedData
              .filter(player => 
                player.player_id && 
                player.full_name && 
                player.full_name.trim() !== ''
              )
              .map(player => ({
                ...player,
                youth_club_country: normalizeCountryName(player.youth_club_country)
              }))
            
            setPlayers(validPlayers)
            setLoading(false)
          },
          error: (error: unknown) => {
            console.error('CSV parsing error:', error)
            setError('Failed to parse CSV data')
            setLoading(false)
          }
        })
      } catch (err) {
        console.error('Data loading error:', err)
        setError(err instanceof Error ? err.message : 'An error occurred')
        setLoading(false)
      }
    }

    loadData()
  }, [])

  // Calculate metrics
  const uniquePlayerIds = new Set(players.map(player => player.player_id))
  const totalPlayers = uniquePlayerIds.size
  
  const playersWithYouthClub = new Set(
    players
      .filter(player => 
        player.youth_club && 
        player.youth_club.trim() !== '' && 
        player.youth_club !== 'Not found' &&
        !player.youth_club.includes(')')
      )
      .map(player => player.player_id)
  ).size

  const marketValueSum = players.reduce((sum, player) => {
    if (!player.latest_market_value) return sum
    
    // Parse market value (format like "1,000,000" or "€1.20m")
    let value = player.latest_market_value.replace(/[€$,]/g, '')
    
    if (value.includes('m')) {
      value = value.replace('m', '')
      return sum + (parseFloat(value) * 1000000)
    } else if (value.includes('k')) {
      value = value.replace('k', '')
      return sum + (parseFloat(value) * 1000)
    } else {
      const numValue = parseFloat(value)
      return sum + (isNaN(numValue) ? 0 : numValue)
    }
  }, 0)

  return {
    players,
    loading,
    error,
    totalPlayers,
    playersWithYouthClub,
    marketValueSum
  }
}
