"use client"

import { useState, useMemo } from 'react'
import { usePlayerData } from '@/hooks/usePlayerData'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
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

const ITEMS_PER_PAGE = 20

export default function PlayersPage() {
  const { players, loading, error } = usePlayerData()
  const [currentPage, setCurrentPage] = useState(1)
  const [searchTerm, setSearchTerm] = useState('')
  const [positionFilter, setPositionFilter] = useState<string>('')

  // Filter and search players
  const filteredPlayers = useMemo(() => {
    return players.filter(player => {
      const matchesSearch = player.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           player.current_club.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           player.youth_club?.toLowerCase().includes(searchTerm.toLowerCase())
      
      const matchesPosition = !positionFilter || player.position === positionFilter
      
      return matchesSearch && matchesPosition
    })
  }, [players, searchTerm, positionFilter])

  // Pagination
  const totalPages = Math.ceil(filteredPlayers.length / ITEMS_PER_PAGE)
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE
  const endIndex = startIndex + ITEMS_PER_PAGE
  const currentPlayers = filteredPlayers.slice(startIndex, endIndex)

  // Get unique positions for filter
  const uniquePositions = useMemo(() => {
    const positions = players
      .map(player => player.position)
      .filter(position => position && position.trim() !== '')
    return Array.from(new Set(positions)).sort()
  }, [players])

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
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">
          Players Database
        </h1>
        <p className="text-muted-foreground">
          Comprehensive player information with youth development history
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Users className="h-4 w-4 text-primary" />
              <div>
                <p className="text-sm font-medium">Total Players</p>
                <p className="text-2xl font-bold">
                  {loading ? '...' : filteredPlayers.length.toLocaleString()}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-4 w-4 text-green-500" />
              <div>
                <p className="text-sm font-medium">With Youth Clubs</p>
                <p className="text-2xl font-bold">
                  {loading ? '...' : 
                    filteredPlayers.filter(p => p.youth_club && 
                      p.youth_club !== 'Not found' && 
                      !p.youth_club.includes(')')).length.toLocaleString()
                  }
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-blue-500" />
              <div>
                <p className="text-sm font-medium">Unique Positions</p>
                <p className="text-2xl font-bold">
                  {loading ? '...' : uniquePositions.length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-lg font-semibold">
            Search & Filter
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="Search players, clubs, or youth clubs..."
                  value={searchTerm}
                  onChange={(e) => {
                    setSearchTerm(e.target.value)
                    setCurrentPage(1)
                  }}
                  className="w-full pl-10 pr-4 py-2 border border-input bg-background text-foreground rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
                />
              </div>
            </div>
            
            <div className="min-w-[200px]">
              <select
                value={positionFilter}
                onChange={(e) => {
                  setPositionFilter(e.target.value)
                  setCurrentPage(1)
                }}
                className="w-full px-3 py-2 border border-input bg-background text-foreground rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="">All Positions</option>
                {uniquePositions.map(position => (
                  <option key={position} value={position}>
                    {position}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Players Table */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-lg font-semibold">
            Players ({filteredPlayers.length.toLocaleString()})
          </CardTitle>
        </CardHeader>
        <CardContent>
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
                      <TableHead>Player</TableHead>
                      <TableHead>Position</TableHead>
                      <TableHead>Current Club</TableHead>
                      <TableHead>Youth Club</TableHead>
                      <TableHead>Country</TableHead>
                      <TableHead>Market Value</TableHead>
                      <TableHead>Age</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {currentPlayers.map((player) => (
                      <TableRow key={player.player_id} className="hover:bg-muted/50">
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
                          {player.position ? (
                            <Badge variant="secondary" className="text-xs">
                              {player.position}
                            </Badge>
                          ) : (
                            <span className="text-muted-foreground">N/A</span>
                          )}
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
                          <div className="max-w-[200px]">
                            {player.youth_club && 
                             player.youth_club !== 'Not found' && 
                             !player.youth_club.includes(')') ? (
                              <div className="font-medium truncate">
                                {player.youth_club_cleaned || player.youth_club}
                              </div>
                            ) : (
                              <span className="text-muted-foreground">N/A</span>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          {player.youth_club_country && 
                           player.youth_club_country !== 'Not found' ? (
                            <span className="text-sm">
                              {player.youth_club_country}
                            </span>
                          ) : (
                            <span className="text-muted-foreground">N/A</span>
                          )}
                        </TableCell>
                        <TableCell>
                          <span className="font-medium">
                            {formatMarketValue(player.latest_market_value)}
                          </span>
                        </TableCell>
                        <TableCell>
                          {player.age || 'N/A'}
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
