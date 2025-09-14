"use client"

import { useState, useMemo } from 'react'
import { usePlayerData } from '@/hooks/usePlayerData'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Slider } from '@/components/ui/slider'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { 
  ChevronLeft, 
  ChevronRight, 
  Search,
  Filter,
  Users,
  TrendingUp
} from 'lucide-react'
import { getFlagEmojiByCountryName } from '@/lib/flags'

const ITEMS_PER_PAGE = 20

function parseMarketValueToNumber(value?: string): number {
  if (!value) return 0
  // Remove currency symbols and thousand separators
  const cleaned = value.replace(/[€$,\s]/g, '').trim()
  // Match formats like 18m, 18.5m, 150000, 150k
  const match = cleaned.match(/^([0-9]+(?:\.[0-9]+)?)([mMkK])?$/)
  if (!match) {
    const n = Number(cleaned.replace(/,/g, ''))
    return isNaN(n) ? 0 : n
  }
  const num = parseFloat(match[1])
  const suffix = match[2]?.toLowerCase()
  if (suffix === 'm') return num * 1_000_000
  if (suffix === 'k') return num * 1_000
  return isNaN(num) ? 0 : num
}

export default function PlayersPage() {
  const { players, loading, error, totalPlayers, playersWithYouthClub } = usePlayerData()
  const [currentPage, setCurrentPage] = useState(1)
  const [searchTerm, setSearchTerm] = useState('')
  const [countryFilter, setCountryFilter] = useState<string[]>([])
  const [competitionFilter, setCompetitionFilter] = useState<string[]>([])
  const [minMarketValue, setMinMarketValue] = useState<number>(0)

  // Handle multiple selection
  const handleCountryToggle = (country: string) => {
    setCountryFilter(prev => 
      prev.includes(country) 
        ? prev.filter(c => c !== country)
        : [...prev, country]
    )
  }

  const handleCompetitionToggle = (competition: string) => {
    setCompetitionFilter(prev => 
      prev.includes(competition) 
        ? prev.filter(c => c !== competition)
        : [...prev, competition]
    )
  }

  const clearAllFilters = () => {
    setCountryFilter([])
    setCompetitionFilter([])
    setMinMarketValue(0)
  }

  // Filter and search players with indexed data
  const indexedPlayers = useMemo(() => {
    return players.map((player, index) => ({ ...player, originalIndex: index }))
  }, [players])

  const filteredPlayers = useMemo(() => {
    const term = searchTerm.toLowerCase()
    return indexedPlayers.filter(player => {
      const matchesSearch = player.full_name.toLowerCase().includes(term) ||
        player.current_club.toLowerCase().includes(term) ||
        (player.youth_club?.toLowerCase() || '').includes(term)

      const matchesCountry = countryFilter.length === 0 || countryFilter.includes(player.youth_club_country)

      const matchesCompetition = competitionFilter.length === 0 || competitionFilter.includes(player.competition)

      const meetsMinValue = parseMarketValueToNumber(player.latest_market_value) >= minMarketValue

      return matchesSearch && matchesCountry && matchesCompetition && meetsMinValue
    })
  }, [indexedPlayers, searchTerm, countryFilter, competitionFilter, minMarketValue])

  // Pagination
  const totalPages = Math.ceil(filteredPlayers.length / ITEMS_PER_PAGE)
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE
  const endIndex = startIndex + ITEMS_PER_PAGE
  const currentPlayers = filteredPlayers.slice(startIndex, endIndex)

  // Unique countries for filter (youth club country)
  const uniqueCountries = useMemo(() => {
    const countries = indexedPlayers
      .map(p => p.youth_club_country)
      .filter(c => c && c !== 'Not found' && c.trim() !== '') as string[]
    return Array.from(new Set(countries)).sort((a, b) => a.localeCompare(b))
  }, [indexedPlayers])

  // Unique competitions for filter
  const uniqueCompetitions = useMemo(() => {
    const competitions = indexedPlayers
      .map(p => p.competition)
      .filter(c => c && c.trim() !== '') as string[]
    return Array.from(new Set(competitions)).sort((a, b) => a.localeCompare(b))
  }, [indexedPlayers])

  const maxMarketValue = useMemo(() => {
    return indexedPlayers.reduce((max, p) => Math.max(max, parseMarketValueToNumber(p.latest_market_value)), 0)
  }, [indexedPlayers])

  const formatMarketValue = (value: string) => {
    if (!value || value === 'Not found') return 'N/A'
    return value
  }

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A'
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString()
    } catch {
      return 'N/A'
    }
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4">
          <p className="text-sm font-medium text-destructive">
            Error loading data: {error}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 space-y-6">

      {/* Filters */}
      <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-12 mb-6">
            {/* Search */}
            <div className="flex flex-col gap-2 lg:col-span-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="search"
                  placeholder="Search players, clubs, or youth clubs..."
                  value={searchTerm}
                  onChange={(e) => {
                    setSearchTerm(e.target.value)
                    setCurrentPage(1)
                  }}
                  className="pl-10 w-full"
                />
              </div>
            </div>

            {/* Country filter */}
            <div className="flex flex-col gap-2 lg:col-span-2">
              <div className="relative">
                <Select>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder={`Countries ${countryFilter.length > 0 ? `(${countryFilter.length})` : ''}`} />
                  </SelectTrigger>
                  <SelectContent className="max-h-72">
                    <div className="p-2">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">Select Countries</span>
                        {countryFilter.length > 0 && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setCountryFilter([])}
                            className="h-6 px-2 text-xs"
                          >
                            Clear all
                          </Button>
                        )}
                      </div>
                      <div className="space-y-1 max-h-48 overflow-y-auto">
                        {uniqueCountries.map((c) => (
                          <div key={c} className="flex items-center space-x-2 p-1 hover:bg-muted rounded">
                            <Checkbox
                              id={`country-${c}`}
                              checked={countryFilter.includes(c)}
                              onCheckedChange={() => {
                                handleCountryToggle(c)
                                setCurrentPage(1)
                              }}
                            />
                            <label
                              htmlFor={`country-${c}`}
                              className="text-sm cursor-pointer flex items-center gap-2 flex-1"
                            >
                              {getFlagEmojiByCountryName(c)} {c}
                            </label>
                          </div>
                        ))}
                      </div>
                    </div>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Competition filter */}
            <div className="flex flex-col gap-2 lg:col-span-2">
              <div className="relative">
                <Select>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder={`Competitions ${competitionFilter.length > 0 ? `(${competitionFilter.length})` : ''}`} />
                  </SelectTrigger>
                  <SelectContent className="max-h-72">
                    <div className="p-2">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">Select Competitions</span>
                        {competitionFilter.length > 0 && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setCompetitionFilter([])}
                            className="h-6 px-2 text-xs"
                          >
                            Clear all
                          </Button>
                        )}
                      </div>
                      <div className="space-y-1 max-h-48 overflow-y-auto">
                        {uniqueCompetitions.map((c) => (
                          <div key={c} className="flex items-center space-x-2 p-1 hover:bg-muted rounded">
                            <Checkbox
                              id={`competition-${c}`}
                              checked={competitionFilter.includes(c)}
                              onCheckedChange={() => {
                                handleCompetitionToggle(c)
                                setCurrentPage(1)
                              }}
                            />
                            <label
                              htmlFor={`competition-${c}`}
                              className="text-sm cursor-pointer flex-1"
                            >
                              {c}
                            </label>
                          </div>
                        ))}
                      </div>
                    </div>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Min market value and Clear button */}
            <div className="flex flex-col gap-2 lg:col-span-3">
              <div className="flex items-center gap-3">
                <Input
                  type="number"
                  placeholder="Min Market Value (€)"
                  value={minMarketValue === 0 ? '' : minMarketValue}
                  onChange={(e) => {
                    const v = Number(e.target.value)
                    setMinMarketValue(isNaN(v) ? 0 : v)
                    setCurrentPage(1)
                  }}
                  className={
                    (countryFilter.length > 0 || competitionFilter.length > 0 || minMarketValue > 0) 
                      ? "w-64" 
                      : "w-48"
                  }
                />
                {(countryFilter.length > 0 || competitionFilter.length > 0 || minMarketValue > 0) && (
                  <Button
                    onClick={clearAllFilters}
                    className="text-xs h-10 w-26"
                    style={{ 
                      backgroundColor: '#667DFF', 
                      color: 'white',
                      border: 'none'
                    }}
                  >
                    Clear all filters
                  </Button>
                )}
              </div>
            </div>
          </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card className="bg-card border-border hover:bg-card/80 transition-colors">
          <CardContent className="px-6 py-1 flex items-center gap-3">
            <Users className="flex-shrink-0 h-5 w-5 text-primary" />
            <p className="text-sm font-medium text-muted-foreground">Total Players</p>
            <p className="text-lg font-bold text-foreground ml-auto">
              {loading ? (
                <div className="h-6 w-20 bg-muted animate-pulse rounded" />
              ) : (
                new Set(filteredPlayers.map(p => p.player_id)).size.toLocaleString()
              )}
            </p>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border hover:bg-card/80 transition-colors">
          <CardContent className="px-6 py-1 flex items-center gap-3">
            <TrendingUp className="flex-shrink-0 h-5 w-5 text-green-500" />
            <p className="text-sm font-medium text-muted-foreground">With Youth Clubs</p>
            <p className="text-lg font-bold text-foreground ml-auto">
              {loading ? (
                <div className="h-6 w-20 bg-muted animate-pulse rounded" />
              ) : (
                new Set(filteredPlayers
                  .filter(p => p.youth_club && 
                    p.youth_club !== 'Not found' && 
                    !p.youth_club.includes(')'))
                  .map(p => p.player_id)
                ).size.toLocaleString()
              )}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Players Table */}
      <Card className="bg-card border-border">
        <CardContent className="pt-6">
          {loading ? (
            <div className="space-y-4">
              {Array.from({ length: 10 }).map((_, i) => (
                <div key={i} className="h-12 bg-muted animate-pulse rounded" />
              ))}
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Training Club</TableHead>
                      <TableHead>Player</TableHead>
                      <TableHead>Current Club</TableHead>
                      <TableHead>Market Value</TableHead>
                      <TableHead>Date of Birth</TableHead>
                      <TableHead>Profile</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {currentPlayers.map((player) => (
                      <TableRow key={player.originalIndex} className="hover:bg-muted/50">
                        <TableCell>
                          <div className="max-w-[200px]">
                            {player.youth_club && 
                             player.youth_club !== 'Not found' && 
                             !player.youth_club.includes(')') ? (
                              <div>
                                <div className="font-medium truncate">
                                  {player.youth_club_cleaned || player.youth_club}
                                </div>
                                {player.youth_club_country && 
                                 player.youth_club_country !== 'Not found' ? (
                                  <div className="text-sm text-muted-foreground flex items-center gap-1 mt-1">
                                    <span className="text-base">
                                      {getFlagEmojiByCountryName(player.youth_club_country)}
                                    </span>
                                    <span className="truncate" title={player.youth_club_country}>
                                      {player.youth_club_country.length > 15 
                                        ? player.youth_club_country.substring(0, 15) + '...'
                                        : player.youth_club_country
                                      }
                                    </span>
                                  </div>
                                ) : null}
                              </div>
                            ) : (
                              <span className="text-muted-foreground">N/A</span>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div>
                            <div className="font-medium text-foreground">
                              {player.full_name}
                            </div>
                            <div className="text-sm text-muted-foreground">
                              {player.nationality}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="font-medium">
                            {player.current_club || 'N/A'}
                          </div>
                          <div className="text-sm text-muted-foreground">
                            {player.competition || 'N/A'}
                          </div>
                        </TableCell>
                        <TableCell>
                          <span className="font-medium">
                            {formatMarketValue(player.latest_market_value)}
                          </span>
                        </TableCell>
                        <TableCell>
                          {formatDate(player.date_of_birth)}
                        </TableCell>
                        <TableCell>
                          <Button 
                            size="sm" 
                            variant="outline"
                            className="hover:bg-primary hover:text-primary-foreground hover:border-primary transition-colors duration-200"
                            onClick={() => {
                              // TODO: Implementar navegación al perfil del jugador
                              console.log('View profile for player:', player.player_id)
                            }}
                          >
                            View
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between mt-6">
                  <div className="text-sm text-muted-foreground">
                    Showing {startIndex + 1} to {Math.min(endIndex, filteredPlayers.length)} of{' '}
                    {filteredPlayers.length} results
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage(page => Math.max(1, page - 1))}
                      disabled={currentPage === 1}
                    >
                      <ChevronLeft className="h-4 w-4" />
                      Previous
                    </Button>
                    
                    <div className="flex items-center space-x-1">
                      {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                        const page = i + 1
                        const isActive = page === currentPage
                        
                        return (
                          <Button
                            key={page}
                            variant={isActive ? "default" : "outline"}
                            size="sm"
                            onClick={() => setCurrentPage(page)}
                            className="w-8 h-8 p-0"
                          >
                            {page}
                          </Button>
                        )
                      })}
                      
                      {totalPages > 5 && (
                        <>
                          <span className="text-muted-foreground">...</span>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setCurrentPage(totalPages)}
                            className="w-8 h-8 p-0"
                          >
                            {totalPages}
                          </Button>
                        </>
                      )}
                    </div>
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage(page => Math.min(totalPages, page + 1))}
                      disabled={currentPage === totalPages}
                    >
                      Next
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
