"use client"

import { usePlayerData } from '@/hooks/usePlayerData'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Zap, Target, Building2, TrendingUp, BarChart3, Users, Clock, DollarSign } from 'lucide-react'
import { useMemo } from 'react'

// Componente para gráfico de barras verticales futurista
function FuturisticBarChart({ 
  data, 
  title, 
  subtitle,
  color = "primary",
  icon: Icon 
}: {
  data: Array<{ name: string; value: number; percentage: number; efficiency?: number }>
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
                  {item.efficiency && (
                    <span className="text-xs font-bold text-primary bg-primary/10 px-2 py-1 rounded-full">
                      {item.efficiency.toFixed(1)}%
                    </span>
                  )}
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

export default function PerformancePage() {
  const { players, loading, error } = usePlayerData()

  // Development Efficiency
  const developmentEfficiency = useMemo(() => {
    if (!players.length) return []
    
    const clubStats = new Map<string, { 
      players: number; 
      avgAge: number; 
      marketValue: number; 
      efficiency: number 
    }>()
    
    players.forEach(player => {
      if (player.youth_club && player.youth_club !== 'Not found' && !player.youth_club.includes(')')) {
        const club = player.youth_club_cleaned || player.youth_club
        const stats = clubStats.get(club) || { players: 0, avgAge: 0, marketValue: 0, efficiency: 0 }
        
        stats.players++
        
        const age = player.age ? parseInt(player.age) : 0
        if (age > 0) {
          stats.avgAge = (stats.avgAge * (stats.players - 1) + age) / stats.players
        }
        
        const marketValue = player.latest_market_value ? parseFloat(player.latest_market_value.replace(/[€$,\s]/g, '')) : 0
        stats.marketValue += marketValue
        
        clubStats.set(club, stats)
      }
    })
    
    // Calcular eficiencia: (marketValue / players) / avgAge * 100
    clubStats.forEach((stats, club) => {
      if (stats.players >= 3 && stats.avgAge > 0) {
        stats.efficiency = (stats.marketValue / stats.players) / stats.avgAge * 100
      }
    })
    
    const totalPlayers = players.length
    return Array.from(clubStats.entries())
      .filter(([_, stats]) => stats.players >= 3)
      .map(([club, stats]) => ({
        name: club.length > 25 ? club.substring(0, 25) + '...' : club,
        value: Math.round(stats.efficiency * 100) / 100,
        percentage: (stats.players / totalPlayers) * 100,
        players: stats.players,
        efficiency: stats.efficiency
      }))
      .sort((a, b) => b.efficiency - a.efficiency)
      .slice(0, 10)
  }, [players])

  // Talent Retention Rate
  const talentRetentionRate = useMemo(() => {
    if (!players.length) return []
    
    const countryStats = new Map<string, { 
      total: number; 
      retained: number; 
      retentionRate: number 
    }>()
    
    players.forEach(player => {
      const nationality = player.nationality
      const youthCountry = player.youth_club_country
      
      if (nationality && youthCountry && nationality !== 'Not found' && youthCountry !== 'Not found') {
        const stats = countryStats.get(nationality) || { total: 0, retained: 0, retentionRate: 0 }
        stats.total++
        
        if (nationality === youthCountry) {
          stats.retained++
        }
        
        stats.retentionRate = (stats.retained / stats.total) * 100
        
        countryStats.set(nationality, stats)
      }
    })
    
    const totalPlayers = players.length
    return Array.from(countryStats.entries())
      .filter(([_, stats]) => stats.total >= 5)
      .map(([country, stats]) => ({
        name: country.length > 20 ? country.substring(0, 20) + '...' : country,
        value: stats.retained,
        percentage: (stats.retained / totalPlayers) * 100,
        efficiency: stats.retentionRate
      }))
      .sort((a, b) => b.efficiency - a.efficiency)
      .slice(0, 10)
  }, [players])

  // Club Success Correlation
  const clubSuccessCorrelation = useMemo(() => {
    if (!players.length) return []
    
    const clubStats = new Map<string, { 
      players: number; 
      avgMarketValue: number; 
      successScore: number 
    }>()
    
    players.forEach(player => {
      if (player.youth_club && player.youth_club !== 'Not found' && !player.youth_club.includes(')')) {
        const club = player.youth_club_cleaned || player.youth_club
        const stats = clubStats.get(club) || { players: 0, avgMarketValue: 0, successScore: 0 }
        
        stats.players++
        
        const marketValue = player.latest_market_value ? parseFloat(player.latest_market_value.replace(/[€$,\s]/g, '')) : 0
        stats.avgMarketValue = (stats.avgMarketValue * (stats.players - 1) + marketValue) / stats.players
        
        clubStats.set(club, stats)
      }
    })
    
    // Calcular score de éxito: avgMarketValue * log(players)
    clubStats.forEach((stats, club) => {
      if (stats.players >= 2) {
        stats.successScore = stats.avgMarketValue * Math.log(stats.players)
      }
    })
    
    const totalPlayers = players.length
    return Array.from(clubStats.entries())
      .filter(([_, stats]) => stats.players >= 2)
      .map(([club, stats]) => ({
        name: club.length > 25 ? club.substring(0, 25) + '...' : club,
        value: Math.round(stats.avgMarketValue),
        percentage: (stats.players / totalPlayers) * 100,
        efficiency: stats.successScore
      }))
      .sort((a, b) => b.efficiency - a.efficiency)
      .slice(0, 10)
  }, [players])

  // Age-to-Value Ratio
  const ageToValueRatio = useMemo(() => {
    if (!players.length) return []
    
    const ageGroups = new Map<string, { 
      players: number; 
      avgMarketValue: number; 
      ratio: number 
    }>()
    
    players.forEach(player => {
      const age = player.age ? parseInt(player.age) : 0
      const marketValue = player.latest_market_value ? parseFloat(player.latest_market_value.replace(/[€$,\s]/g, '')) : 0
      
      if (age > 0 && marketValue > 0) {
        let ageGroup = ''
        if (age <= 18) ageGroup = 'U18'
        else if (age <= 21) ageGroup = 'U21'
        else if (age <= 25) ageGroup = 'U25'
        else if (age <= 30) ageGroup = 'U30'
        else ageGroup = '30+'
        
        const stats = ageGroups.get(ageGroup) || { players: 0, avgMarketValue: 0, ratio: 0 }
        stats.players++
        stats.avgMarketValue = (stats.avgMarketValue * (stats.players - 1) + marketValue) / stats.players
        stats.ratio = stats.avgMarketValue / (ageGroup === 'U18' ? 18 : ageGroup === 'U21' ? 21 : ageGroup === 'U25' ? 25 : ageGroup === 'U30' ? 30 : 35)
        
        ageGroups.set(ageGroup, stats)
      }
    })
    
    const totalPlayers = players.length
    return Array.from(ageGroups.entries())
      .map(([ageGroup, stats]) => ({
        name: ageGroup,
        value: stats.players,
        percentage: (stats.players / totalPlayers) * 100,
        efficiency: stats.ratio
      }))
      .sort((a, b) => b.efficiency - a.efficiency)
  }, [players])

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
          Performance Metrics
        </h1>
        <p className="text-muted-foreground">
          Advanced performance analysis and efficiency metrics for talent development
        </p>
      </div>

      {/* Métricas rápidas */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="bg-card border-border hover:bg-card/80 transition-colors">
          <CardContent className="px-4 py-3 flex items-center gap-3">
            <Target className="flex-shrink-0 h-5 w-5 text-primary" />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Top Efficiency</p>
              <p className="text-lg font-bold text-foreground">
                {loading ? (
                  <div className="h-6 w-20 bg-muted animate-pulse rounded" />
                ) : (
                  `${developmentEfficiency[0]?.efficiency.toFixed(1)}%` || '0.0%'
                )}
              </p>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border hover:bg-card/80 transition-colors">
          <CardContent className="px-4 py-3 flex items-center gap-3">
            <Users className="flex-shrink-0 h-5 w-5 text-emerald-500" />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Retention Rate</p>
              <p className="text-lg font-bold text-foreground">
                {loading ? (
                  <div className="h-6 w-20 bg-muted animate-pulse rounded" />
                ) : (
                  `${talentRetentionRate[0]?.efficiency.toFixed(1)}%` || '0.0%'
                )}
              </p>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border hover:bg-card/80 transition-colors">
          <CardContent className="px-4 py-3 flex items-center gap-3">
            <Building2 className="flex-shrink-0 h-5 w-5 text-orange-500" />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Success Score</p>
              <p className="text-lg font-bold text-foreground">
                {loading ? (
                  <div className="h-6 w-20 bg-muted animate-pulse rounded" />
                ) : (
                  clubSuccessCorrelation[0]?.efficiency.toFixed(0) || '0'
                )}
              </p>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border hover:bg-card/80 transition-colors">
          <CardContent className="px-4 py-3 flex items-center gap-3">
            <DollarSign className="flex-shrink-0 h-5 w-5 text-purple-500" />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Age/Value Ratio</p>
              <p className="text-lg font-bold text-foreground">
                {loading ? (
                  <div className="h-6 w-20 bg-muted animate-pulse rounded" />
                ) : (
                  ageToValueRatio[0]?.efficiency.toFixed(0) || '0'
                )}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Gráficos principales */}
      <div className="space-y-8">
        <FuturisticBarChart
          data={developmentEfficiency}
          title="Development Efficiency"
          subtitle="Eficiencia de desarrollo por club (valor/edad)"
          color="primary"
          icon={Target}
        />
        
        <FuturisticBarChart
          data={talentRetentionRate}
          title="Talent Retention Rate"
          subtitle="Tasa de retención de talento por país"
          color="secondary"
          icon={Users}
        />
        
        <FuturisticBarChart
          data={clubSuccessCorrelation}
          title="Club Success Correlation"
          subtitle="Correlación de éxito del club"
          color="accent"
          icon={Building2}
        />
        
        <FuturisticBarChart
          data={ageToValueRatio}
          title="Age-to-Value Ratio"
          subtitle="Ratio edad-valor por grupo de edad"
          color="success"
          icon={DollarSign}
        />
      </div>

      {/* Metodología Detallada */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-xl font-bold text-foreground">
            📊 Metodología de Cálculo
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Detalles técnicos de cómo se calculan cada una de las métricas mostradas
          </p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Development Efficiency */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-foreground">Development Efficiency</h3>
            <div className="bg-muted/30 p-4 rounded-lg">
              <p className="text-sm text-muted-foreground mb-2">
                <strong>Fórmula:</strong> Eficiencia de desarrollo por club
              </p>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• <strong>players</strong> = número total de jugadores del club</li>
                <li>• <strong>avgAge</strong> = edad promedio de los jugadores del club</li>
                <li>• <strong>marketValue</strong> = valor total de mercado de todos los jugadores</li>
                <li>• <strong>efficiency</strong> = (marketValue / players) / avgAge &times; 100</li>
                <li>• <strong>Filtro:</strong> Solo clubes con mínimo 3 jugadores</li>
              </ul>
              <p className="text-xs text-muted-foreground mt-2">
                <strong>Columnas utilizadas:</strong> youth_club, youth_club_cleaned, age, latest_market_value
              </p>
            </div>
          </div>

          {/* Talent Retention Rate */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-foreground">Talent Retention Rate</h3>
            <div className="bg-muted/30 p-4 rounded-lg">
              <p className="text-sm text-muted-foreground mb-2">
                <strong>Fórmula:</strong> Tasa de retención de talento por país
              </p>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• <strong>total</strong> = número total de jugadores del país</li>
                <li>• <strong>retained</strong> = jugadores que se formaron en su país de nacimiento</li>
                <li>• <strong>retentionRate</strong> = (retained / total) &times; 100</li>
                <li>• <strong>Filtro:</strong> Solo países con mínimo 5 jugadores</li>
              </ul>
              <p className="text-xs text-muted-foreground mt-2">
                <strong>Columnas utilizadas:</strong> country_of_birth, youth_club_country
              </p>
            </div>
          </div>

          {/* Club Success Correlation */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-foreground">Club Success Correlation</h3>
            <div className="bg-muted/30 p-4 rounded-lg">
              <p className="text-sm text-muted-foreground mb-2">
                <strong>Fórmula:</strong> Correlación de éxito del club
              </p>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• <strong>players</strong> = número total de jugadores del club</li>
                <li>• <strong>avgMarketValue</strong> = valor promedio de mercado por jugador</li>
                <li>• <strong>successScore</strong> = avgMarketValue &times; log(players)</li>
                <li>• <strong>Filtro:</strong> Solo clubes con mínimo 2 jugadores</li>
              </ul>
              <p className="text-xs text-muted-foreground mt-2">
                <strong>Columnas utilizadas:</strong> youth_club, youth_club_cleaned, latest_market_value
              </p>
            </div>
          </div>

          {/* Age-to-Value Ratio */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-foreground">Age-to-Value Ratio</h3>
            <div className="bg-muted/30 p-4 rounded-lg">
              <p className="text-sm text-muted-foreground mb-2">
                <strong>Fórmula:</strong> Ratio edad-valor por grupo de edad
              </p>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• <strong>U18:</strong> age &le; 18, expectedAge = 18</li>
                <li>• <strong>U21:</strong> 18 &lt; age &le; 21, expectedAge = 21</li>
                <li>• <strong>U25:</strong> 21 &lt; age &le; 25, expectedAge = 25</li>
                <li>• <strong>U30:</strong> 25 &lt; age &le; 30, expectedAge = 30</li>
                <li>• <strong>30+:</strong> age &gt; 30, expectedAge = 35</li>
                <li>• <strong>ratio</strong> = avgMarketValue / expectedAge</li>
              </ul>
              <p className="text-xs text-muted-foreground mt-2">
                <strong>Columnas utilizadas:</strong> age, latest_market_value
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
