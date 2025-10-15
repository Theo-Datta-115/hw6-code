'use client'

import { useState, useEffect } from 'react'

interface Candidate {
  id: number
  name: string
  party: string
  office: string
  state: string
  district: string | null
  incumbent: boolean
  total_receipts: number | null
  opponent_total_receipts: number | null
  funding_gap: number | null
  donation_leverage_score: number | null
  overall_impact_score: number | null
  recommendation_tier: string | null
  small_dollar_percentage: number | null
}

interface Issue {
  id: number
  name: string
  category: string
  candidate_count: number
}

interface Stats {
  total_candidates: number
  total_races: number
  high_impact_candidates: number
  competitive_races: number
  last_updated: string
}

export default function Home() {
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [issues, setIssues] = useState<Issue[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedParty, setSelectedParty] = useState<string>('all')
  const [selectedState, setSelectedState] = useState<string>('all')
  const [selectedTier, setSelectedTier] = useState<string>('all')
  const [minImpactScore, setMinImpactScore] = useState<number>(0)
  
  useEffect(() => {
    // Load data
    Promise.all([
      fetch('/candidates.json').then(r => r.json()),
      fetch('/issues.json').then(r => r.json()),
      fetch('/stats.json').then(r => r.json()),
    ]).then(([candidatesData, issuesData, statsData]) => {
      setCandidates(candidatesData)
      setIssues(issuesData)
      setStats(statsData)
      setLoading(false)
    }).catch(err => {
      console.error('Error loading data:', err)
      setLoading(false)
    })
  }, [])
  
  // Filter candidates
  const filteredCandidates = candidates.filter(c => {
    if (searchTerm && !c.name.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false
    }
    if (selectedParty !== 'all' && c.party !== selectedParty) {
      return false
    }
    if (selectedState !== 'all' && c.state !== selectedState) {
      return false
    }
    if (selectedTier !== 'all' && c.recommendation_tier !== selectedTier) {
      return false
    }
    if (c.overall_impact_score && c.overall_impact_score < minImpactScore) {
      return false
    }
    return true
  })
  
  // Get unique values for filters
  const parties = Array.from(new Set(candidates.map(c => c.party).filter(Boolean))).sort()
  const states = Array.from(new Set(candidates.map(c => c.state).filter(Boolean))).sort()
  const tiers = Array.from(new Set(candidates.map(c => c.recommendation_tier).filter(Boolean))).sort()
  
  const formatCurrency = (amount: number | null) => {
    if (!amount) return 'N/A'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }
  
  const getTierColor = (tier: string | null) => {
    if (!tier) return 'bg-gray-100 text-gray-800'
    if (tier.includes('High')) return 'bg-green-100 text-green-800'
    if (tier.includes('Medium')) return 'bg-yellow-100 text-yellow-800'
    return 'bg-gray-100 text-gray-800'
  }
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading data...</div>
      </div>
    )
  }
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-blue-600 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold">Strategic Political Donation Platform</h1>
          <p className="text-blue-100 mt-2">GiveWell for Politics - Find high-impact donation opportunities</p>
        </div>
      </header>
      
      {/* Stats Bar */}
      {stats && (
        <div className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <div className="text-2xl font-bold text-blue-600">{stats.total_candidates}</div>
                <div className="text-sm text-gray-600">Total Candidates</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">{stats.high_impact_candidates}</div>
                <div className="text-sm text-gray-600">High Impact</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-purple-600">{stats.total_races}</div>
                <div className="text-sm text-gray-600">Total Races</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-orange-600">{stats.competitive_races}</div>
                <div className="text-sm text-gray-600">Competitive Races</div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold mb-4">Filters</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Search */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search by name
              </label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Enter candidate name..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            {/* Party */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Party
              </label>
              <select
                value={selectedParty}
                onChange={(e) => setSelectedParty(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Parties</option>
                {parties.map(party => (
                  <option key={party} value={party}>{party}</option>
                ))}
              </select>
            </div>
            
            {/* State */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                State
              </label>
              <select
                value={selectedState}
                onChange={(e) => setSelectedState(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All States</option>
                {states.map(state => (
                  <option key={state} value={state}>{state}</option>
                ))}
              </select>
            </div>
            
            {/* Recommendation Tier */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Recommendation Tier
              </label>
              <select
                value={selectedTier}
                onChange={(e) => setSelectedTier(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Tiers</option>
                {tiers.map(tier => (
                  <option key={tier} value={tier}>{tier}</option>
                ))}
              </select>
            </div>
            
            {/* Min Impact Score */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Min Impact Score: {minImpactScore}
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={minImpactScore}
                onChange={(e) => setMinImpactScore(Number(e.target.value))}
                className="w-full"
              />
            </div>
          </div>
          
          <div className="mt-4 text-sm text-gray-600">
            Showing {filteredCandidates.length} of {candidates.length} candidates
          </div>
        </div>
        
        {/* Candidates List */}
        <div className="space-y-4">
          {filteredCandidates.map(candidate => (
            <div key={candidate.id} className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">
                    {candidate.name}
                    {candidate.incumbent && (
                      <span className="ml-2 text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        Incumbent
                      </span>
                    )}
                  </h3>
                  <p className="text-gray-600 mt-1">
                    {candidate.office} • {candidate.state}
                    {candidate.district && `-${candidate.district}`} • {candidate.party}
                  </p>
                </div>
                
                {candidate.recommendation_tier && (
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getTierColor(candidate.recommendation_tier)}`}>
                    {candidate.recommendation_tier}
                  </span>
                )}
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                {candidate.overall_impact_score !== null && (
                  <div>
                    <div className="text-sm text-gray-600">Impact Score</div>
                    <div className="text-2xl font-bold text-blue-600">
                      {candidate.overall_impact_score.toFixed(1)}
                    </div>
                  </div>
                )}
                
                {candidate.donation_leverage_score !== null && (
                  <div>
                    <div className="text-sm text-gray-600">Leverage Score</div>
                    <div className="text-2xl font-bold text-green-600">
                      {candidate.donation_leverage_score.toFixed(1)}
                    </div>
                  </div>
                )}
                
                {candidate.total_receipts !== null && (
                  <div>
                    <div className="text-sm text-gray-600">Total Raised</div>
                    <div className="text-lg font-bold text-gray-900">
                      {formatCurrency(candidate.total_receipts)}
                    </div>
                  </div>
                )}
                
                {candidate.funding_gap !== null && (
                  <div>
                    <div className="text-sm text-gray-600">Funding Gap</div>
                    <div className={`text-lg font-bold ${candidate.funding_gap < 0 ? 'text-red-600' : 'text-gray-900'}`}>
                      {formatCurrency(candidate.funding_gap)}
                    </div>
                  </div>
                )}
              </div>
              
              {candidate.small_dollar_percentage !== null && (
                <div className="mt-4 pt-4 border-t">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Grassroots Support</span>
                    <span className="text-sm font-medium text-gray-900">
                      {candidate.small_dollar_percentage.toFixed(1)}% small-dollar
                    </span>
                  </div>
                  <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{ width: `${Math.min(100, candidate.small_dollar_percentage)}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          ))}
          
          {filteredCandidates.length === 0 && (
            <div className="bg-white rounded-lg shadow p-12 text-center">
              <p className="text-gray-600">No candidates match your filters</p>
            </div>
          )}
        </div>
      </main>
      
      {/* Footer */}
      <footer className="bg-gray-800 text-white mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center">
          <p className="text-sm">
            Strategic Political Donation Platform • GiveWell for Politics
          </p>
          <p className="text-xs text-gray-400 mt-2">
            Data from FEC, Census, Wikipedia, and Ballotpedia
          </p>
        </div>
      </footer>
    </div>
  )
}
