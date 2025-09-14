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
            
            // Filter out invalid or incomplete rows
            const validPlayers = processedData.filter(player => 
              player.player_id && 
              player.full_name && 
              player.full_name.trim() !== ''
            )
            
            setPlayers(validPlayers)
            setLoading(false)
          },
          error: (error) => {
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
  const totalPlayers = players.length
  const playersWithYouthClub = players.filter(player => 
    player.youth_club && 
    player.youth_club.trim() !== '' && 
    player.youth_club !== 'Not found' &&
    !player.youth_club.includes(')')
  ).length

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
