"use client"

import { usePlayerData } from '@/hooks/usePlayerData'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Users, Building2, TrendingUp, Globe, BarChart3 } from 'lucide-react'
import { useMemo } from 'react'

// Componente para gráfico de barras verticales futurista
function FuturisticBarChart({ 
  data, 
  title, 
  subtitle,
  color = "primary",
  icon: Icon 
}: {
  data: Array<{ name: string; value: number; percentage: number }>
  title: string
  subtitle: string
  color?: "primary" | "secondary" | "accent" | "success"
  icon: React.ElementType
}) {
  const maxValue = Math.max(...data.map(d => d.value))
  
  const colorClasses = {
    primary: "from-blue-500 to-purple-600",
    secondary: "from-emerald-500 to-teal-600", 
    accent: "from-orange-500 to-red-600",
    success: "from-green-500 to-emerald-600"
  }

  return (
    <Card className="bg-card border-border hover:bg-card/80 transition-all duration-300 hover:shadow-2xl hover:shadow-primary/10">
      <CardHeader className="pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-gradient-to-r from-primary/20 to-primary/10">
            <Icon className="h-5 w-5 text-primary" />
          </div>
          <div>
            <CardTitle className="text-xl font-bold bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text text-transparent">
              {title}
            </CardTitle>
            <p className="text-sm text-muted-foreground mt-1">{subtitle}</p>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="space-y-4">
          {data.map((item, index) => (
            <div key={item.name} className="group">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <span className="text-xs font-medium text-muted-foreground w-6 text-right">
                    {index + 1}
                  </span>
                  <span className="text-sm font-medium text-foreground truncate">
                    {item.name}
                  </span>
                </div>
                <div className="flex items-center gap-2 ml-3">
                  <span className="text-sm font-bold text-foreground">
                    {item.value.toLocaleString()}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    ({item.percentage.toFixed(1)}%)
                  </span>
                </div>
              </div>
              
              <div className="relative h-8 bg-muted/30 rounded-full overflow-hidden">
                <div 
                  className={`h-full bg-gradient-to-r ${colorClasses[color]} rounded-full transition-all duration-1000 ease-out group-hover:shadow-lg group-hover:shadow-primary/20 relative overflow-hidden`}
                  style={{ 
                    width: `${(item.value / maxValue) * 100}%`,
                    animationDelay: `${index * 100}ms`
                  }}
                >
                  {/* Efecto de brillo animado */}
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse" />
                  
                  {/* Partículas flotantes */}
                  <div className="absolute inset-0">
                    <div className="absolute top-1 left-1/4 w-1 h-1 bg-white/40 rounded-full animate-ping" style={{ animationDelay: `${index * 200}ms` }} />
                    <div className="absolute top-2 right-1/3 w-0.5 h-0.5 bg-white/60 rounded-full animate-ping" style={{ animationDelay: `${index * 300}ms` }} />
                  </div>
                </div>
                
                {/* Efecto de resplandor en hover */}
                <div className="absolute inset-0 bg-gradient-to-r from-primary/0 via-primary/10 to-primary/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-full" />
              </div>
            </div>
          ))}
        </div>
        
        {/* Estadísticas adicionales */}
        <div className="mt-6 pt-4 border-t border-border/50">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="space-y-1">
              <p className="text-xs text-muted-foreground">Total</p>
              <p className="text-lg font-bold text-foreground">
                {data.reduce((sum, item) => sum + item.value, 0).toLocaleString()}
              </p>
            </div>
            <div className="space-y-1">
              <p className="text-xs text-muted-foreground">Promedio</p>
              <p className="text-lg font-bold text-foreground">
                {Math.round(data.reduce((sum, item) => sum + item.value, 0) / data.length).toLocaleString()}
              </p>
            </div>
            <div className="space-y-1">
              <p className="text-xs text-muted-foreground">Máximo</p>
              <p className="text-lg font-bold text-foreground">
                {maxValue.toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

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
  const { players, loading, error, totalPlayers, playersWithYouthClub } = usePlayerData()

  // Top 10 clubes con más jugadores únicos
  const topClubs = useMemo(() => {
    if (!players.length) return []
    
    const clubCounts = new Map<string, number>()
    
    players.forEach(player => {
      if (player.youth_club && 
          player.youth_club !== 'Not found' && 
          player.youth_club.trim() !== '' &&
          !player.youth_club.includes(')')) {
        const clubName = player.youth_club_cleaned || player.youth_club
        clubCounts.set(clubName, (clubCounts.get(clubName) || 0) + 1)
      }
    })
    
    return Array.from(clubCounts.entries())
      .map(([name, value]) => ({
        name: name.length > 25 ? name.substring(0, 25) + '...' : name,
        value,
        percentage: (value / totalPlayers) * 100
      }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 10)
  }, [players, totalPlayers])

  // Top 10 países con más jugadores únicos
  const topCountries = useMemo(() => {
    if (!players.length) return []
    
    const countryCounts = new Map<string, number>()
    
    players.forEach(player => {
      if (player.youth_club_country && 
          player.youth_club_country !== 'Not found' && 
          player.youth_club_country.trim() !== '') {
        countryCounts.set(player.youth_club_country, (countryCounts.get(player.youth_club_country) || 0) + 1)
      }
    })
    
    return Array.from(countryCounts.entries())
      .map(([name, value]) => ({
        name: name.length > 20 ? name.substring(0, 20) + '...' : name,
        value,
        percentage: (value / totalPlayers) * 100
      }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 10)
  }, [players, totalPlayers])

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
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-foreground via-primary to-foreground bg-clip-text text-transparent">
          Prime Players Football Analytics Center
        </h1>
        <p className="text-muted-foreground">
          Advanced insights and data visualization for football analytics
        </p>
      </div>

      {/* Métricas rápidas */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="bg-card border-border hover:bg-card/80 transition-colors">
          <CardContent className="px-4 py-3 flex items-center gap-3">
            <Users className="flex-shrink-0 h-5 w-5 text-primary" />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Total Players</p>
              <p className="text-lg font-bold text-foreground">
                {loading ? (
                  <div className="h-6 w-20 bg-muted animate-pulse rounded" />
                ) : (
                  totalPlayers.toLocaleString()
                )}
              </p>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border hover:bg-card/80 transition-colors">
          <CardContent className="px-4 py-3 flex items-center gap-3">
            <BarChart3 className="flex-shrink-0 h-5 w-5 text-emerald-500" />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Unique Clubs</p>
              <p className="text-lg font-bold text-foreground">
                {loading ? (
                  <div className="h-6 w-20 bg-muted animate-pulse rounded" />
                ) : (
                  new Set(players.map(p => p.youth_club_cleaned || p.youth_club).filter(Boolean)).size.toLocaleString()
                )}
              </p>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border hover:bg-card/80 transition-colors">
          <CardContent className="px-4 py-3 flex items-center gap-3">
            <Globe className="flex-shrink-0 h-5 w-5 text-orange-500" />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Countries</p>
              <p className="text-lg font-bold text-foreground">
                {loading ? (
                  <div className="h-6 w-20 bg-muted animate-pulse rounded" />
                ) : (
                  new Set(players.map(p => p.youth_club_country).filter(Boolean)).size.toLocaleString()
                )}
              </p>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border hover:bg-card/80 transition-colors">
          <CardContent className="px-4 py-3 flex items-center gap-3">
            <TrendingUp className="flex-shrink-0 h-5 w-5 text-purple-500" />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Coverage</p>
              <p className="text-lg font-bold text-foreground">
                {loading ? (
                  <div className="h-6 w-20 bg-muted animate-pulse rounded" />
                ) : (
                  `${((playersWithYouthClub / totalPlayers) * 100).toFixed(1)}%`
                )}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Gráficos principales */}
      <div className="space-y-8">
        <FuturisticBarChart
          data={topClubs}
          title="Top 10 Training Clubs"
          subtitle="Clubes formadores con más jugadores únicos"
          color="primary"
          icon={BarChart3}
        />
        
        <FuturisticBarChart
          data={topCountries}
          title="Top 10 Countries"
          subtitle="Países con más jugadores únicos"
          color="secondary"
          icon={Globe}
        />
        </div>
    </div>
  )
}
