"use client"

import { usePlayerData } from '@/hooks/usePlayerData'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Users, Building2, TrendingUp, Globe } from 'lucide-react'

function MetricCard({ 
  title, 
  value, 
  icon: Icon, 
  description, 
  loading 
}: {
  title: string
  value: string | number
  icon: React.ElementType
  description: string
  loading: boolean
}) {
  return (
    <Card className="bg-card border-border hover:bg-card/80 transition-colors">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-foreground">
          {loading ? (
            <div className="h-8 w-24 bg-muted animate-pulse rounded" />
          ) : (
            value.toLocaleString()
          )}
        </div>
        <p className="text-xs text-muted-foreground">
          {description}
        </p>
      </CardContent>
    </Card>
  )
}

export default function Home() {
  const { 
    players, 
    loading, 
    error, 
    totalPlayers, 
    playersWithYouthClub, 
    marketValueSum 
  } = usePlayerData()

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

  const youthClubPercentage = totalPlayers > 0 
    ? ((playersWithYouthClub / totalPlayers) * 100).toFixed(1)
    : 0

  const uniqueCountries = new Set(
    players
      .map(player => player.youth_club_country)
      .filter(country => country && country !== 'Not found' && country.trim() !== '')
  ).size

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">
          Football Analytics Dashboard
        </h1>
        <p className="text-muted-foreground">
          Comprehensive insights into player development and youth academy data
        </p>
      </div>

      {/* Metrics Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Total Players"
          value={totalPlayers}
          icon={Users}
          description="Registered players in database"
          loading={loading}
        />
        
        <MetricCard
          title="With Youth Clubs"
          value={playersWithYouthClub}
          icon={Building2}
          description={`${youthClubPercentage}% have youth club data`}
          loading={loading}
        />
        
        <MetricCard
          title="Total Market Value"
          value={`€${(marketValueSum / 1000000).toFixed(0)}M`}
          icon={TrendingUp}
          description="Combined market value"
          loading={loading}
        />
        
        <MetricCard
          title="Countries"
          value={uniqueCountries}
          icon={Globe}
          description="Youth club countries represented"
          loading={loading}
        />
      </div>

      {/* Additional Cards */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-lg font-semibold">
              Youth Development Coverage
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">
                  Players with youth club data
                </span>
                <span className="text-sm font-medium">
                  {youthClubPercentage}%
                </span>
              </div>
              <div className="w-full bg-muted rounded-full h-2">
                <div 
                  className="bg-primary h-2 rounded-full transition-all duration-500"
                  style={{ width: `${youthClubPercentage}%` }}
                />
              </div>
              <p className="text-xs text-muted-foreground">
                Strong youth development tracking with comprehensive data coverage
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-lg font-semibold">
              Market Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">
                  Average market value
                </span>
                <span className="text-sm font-medium">
                  €{totalPlayers > 0 ? ((marketValueSum / totalPlayers) / 1000).toFixed(0) + 'K' : '0'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">
                  Total portfolio value
                </span>
                <span className="text-sm font-medium">
                  €{(marketValueSum / 1000000).toFixed(1)}M
                </span>
              </div>
              <p className="text-xs text-muted-foreground">
                Comprehensive market valuation across all tracked players
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
