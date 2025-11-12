import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  DollarSign, 
  Eye, 
  MousePointer, 
  Target,
  Calendar,
  Download,
  RefreshCw,
  Filter,
  Share,
  AlertCircle,
  CheckCircle,
  Zap
} from 'lucide-react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { useAnalyticsStore } from '@/stores/analyticsStore';
import { useToast } from '@/hooks/use-toast';

interface AnalyticsDashboardProps {
  className?: string;
}

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ className }) => {
  const { toast } = useToast();
  
  const {
    analytics,
    realTimeData,
    isLoading,
    selectedDateRange,
    comparisonData,
    comparisonEnabled,
    fetchAnalytics,
    fetchRealTimeData,
    setDateRange,
    enableComparison,
    disableComparison,
    exportData
  } = useAnalyticsStore();
  
  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null);
  const [selectedMetric, setSelectedMetric] = useState('impressions');
  
  // Initialize analytics data
  useEffect(() => {
    const initialConfig = {
      dateRange: selectedDateRange,
      metrics: ['impressions', 'clicks', 'conversions', 'spend'],
      dimensions: ['date'],
      filters: {},
      groupBy: 'day' as const
    };
    
    fetchAnalytics(initialConfig);
    fetchRealTimeData();
    
    // Set up real-time data refresh
    const interval = setInterval(() => {
      fetchRealTimeData();
    }, 30000); // Refresh every 30 seconds
    
    setRefreshInterval(interval);
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, []);
  
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };
  
  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(2)}%`;
  };
  
  const formatNumber = (value: number) => {
    return new Intl.NumberFormat('en-US').format(value);
  };
  
  const getChangeColor = (current: number, previous: number) => {
    const change = ((current - previous) / previous) * 100;
    if (change > 0) return 'text-green-600';
    if (change < 0) return 'text-red-600';
    return 'text-gray-600';
  };
  
  const getChangeIcon = (current: number, previous: number) => {
    const change = ((current - previous) / previous) * 100;
    if (change > 0) return <TrendingUp className="h-4 w-4" />;
    return <TrendingUp className="h-4 w-4 rotate-180" />;
  };
  
  const handleDateRangeChange = (preset: string) => {
    const now = new Date();
    let start: Date;
    
    switch (preset) {
      case 'today':
        start = new Date(now.setHours(0, 0, 0, 0));
        break;
      case 'yesterday':
        start = new Date(now.setDate(now.getDate() - 1));
        start.setHours(0, 0, 0, 0);
        break;
      case '7days':
        start = new Date(now.setDate(now.getDate() - 7));
        break;
      case '30days':
        start = new Date(now.setDate(now.getDate() - 30));
        break;
      case '90days':
        start = new Date(now.setDate(now.getDate() - 90));
        break;
      default:
        return;
    }
    
    const dateRange = {
      start,
      end: new Date(),
      preset: preset as any
    };
    
    setDateRange(dateRange);
    
    // Refetch data
    fetchAnalytics({
      dateRange,
      metrics: ['impressions', 'clicks', 'conversions', 'spend'],
      dimensions: ['date'],
      filters: {},
      groupBy: 'day'
    });
  };
  
  const exportReport = async (format: 'csv' | 'xlsx' | 'pdf') => {
    try {
      await exportData(format);
      toast({
        title: "Export Complete",
        description: `Report exported as ${format.toUpperCase()}.`
      });
    } catch (error) {
      toast({
        title: "Export Failed",
        description: "Failed to export report. Please try again.",
        variant: "destructive"
      });
    }
  };
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading analytics data...</p>
        </div>
      </div>
    );
  }
  
  if (!analytics) {
    return (
      <div className="text-center py-12">
        <BarChart3 className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
        <p className="text-muted-foreground">No analytics data available</p>
      </div>
    );
  }
  
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];
  
  return (
    <div className={`w-full space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <BarChart3 className="h-8 w-8 text-blue-600" />
            Analytics Dashboard
          </h1>
          <p className="text-muted-foreground mt-1">
            Track and analyze your ad performance
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <Select value={selectedDateRange.preset || 'custom'} onValueChange={handleDateRangeChange}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Select date range" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="today">Today</SelectItem>
              <SelectItem value="yesterday">Yesterday</SelectItem>
              <SelectItem value="7days">Last 7 days</SelectItem>
              <SelectItem value="30days">Last 30 days</SelectItem>
              <SelectItem value="90days">Last 90 days</SelectItem>
            </SelectContent>
          </Select>
          
          <Button
            variant={comparisonEnabled ? "default" : "outline"}
            onClick={() => comparisonEnabled ? disableComparison() : enableComparison('previous_period')}
          >
            <TrendingUp className="h-4 w-4 mr-2" />
            Compare
          </Button>
          
          <Button variant="outline" onClick={() => exportReport('csv')}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>
      
      {/* Real-time Metrics */}
      {realTimeData && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-orange-500" />
              Real-time Metrics
            </CardTitle>
            <CardDescription>
              Live data updated every 30 seconds
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {formatNumber(realTimeData.currentUsers)}
                </div>
                <div className="text-sm text-muted-foreground">Active Users</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">
                  {formatNumber(realTimeData.todayImpressions)}
                </div>
                <div className="text-sm text-muted-foreground">Today's Impressions</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">
                  {formatNumber(realTimeData.todayClicks)}
                </div>
                <div className="text-sm text-muted-foreground">Today's Clicks</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">
                  {formatCurrency(realTimeData.todaySpend)}
                </div>
                <div className="text-sm text-muted-foreground">Today's Spend</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Key Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Impressions</p>
                <div className="flex items-center gap-2">
                  <p className="text-2xl font-bold">{formatNumber(analytics.performance.totalImpressions)}</p>
                  {comparisonData && (
                    <div className={`flex items-center text-sm ${getChangeColor(analytics.performance.totalImpressions, comparisonData.performance.totalImpressions)}`}>
                      {getChangeIcon(analytics.performance.totalImpressions, comparisonData.performance.totalImpressions)}
                      {Math.abs(((analytics.performance.totalImpressions - comparisonData.performance.totalImpressions) / comparisonData.performance.totalImpressions) * 100).toFixed(1)}%
                    </div>
                  )}
                </div>
              </div>
              <Eye className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Clicks</p>
                <div className="flex items-center gap-2">
                  <p className="text-2xl font-bold">{formatNumber(analytics.performance.totalClicks)}</p>
                  {comparisonData && (
                    <div className={`flex items-center text-sm ${getChangeColor(analytics.performance.totalClicks, comparisonData.performance.totalClicks)}`}>
                      {getChangeIcon(analytics.performance.totalClicks, comparisonData.performance.totalClicks)}
                      {Math.abs(((analytics.performance.totalClicks - comparisonData.performance.totalClicks) / comparisonData.performance.totalClicks) * 100).toFixed(1)}%
                    </div>
                  )}
                </div>
              </div>
              <MousePointer className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Conversions</p>
                <div className="flex items-center gap-2">
                  <p className="text-2xl font-bold">{formatNumber(analytics.performance.totalConversions)}</p>
                  {comparisonData && (
                    <div className={`flex items-center text-sm ${getChangeColor(analytics.performance.totalConversions, comparisonData.performance.totalConversions)}`}>
                      {getChangeIcon(analytics.performance.totalConversions, comparisonData.performance.totalConversions)}
                      {Math.abs(((analytics.performance.totalConversions - comparisonData.performance.totalConversions) / comparisonData.performance.totalConversions) * 100).toFixed(1)}%
                    </div>
                  )}
                </div>
              </div>
              <Target className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Spend</p>
                <div className="flex items-center gap-2">
                  <p className="text-2xl font-bold">{formatCurrency(analytics.performance.totalSpend)}</p>
                  {comparisonData && (
                    <div className={`flex items-center text-sm ${getChangeColor(analytics.performance.totalSpend, comparisonData.performance.totalSpend)}`}>
                      {getChangeIcon(analytics.performance.totalSpend, comparisonData.performance.totalSpend)}
                      {Math.abs(((analytics.performance.totalSpend - comparisonData.performance.totalSpend) / comparisonData.performance.totalSpend) * 100).toFixed(1)}%
                    </div>
                  )}
                </div>
              </div>
              <DollarSign className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Performance Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Performance Trends</CardTitle>
            <CardDescription>Daily performance metrics over time</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analytics.timeSeries}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="impressions" stroke="#8884d8" name="Impressions" />
                <Line type="monotone" dataKey="clicks" stroke="#82ca9d" name="Clicks" />
                <Line type="monotone" dataKey="conversions" stroke="#ffc658" name="Conversions" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Platform Performance</CardTitle>
            <CardDescription>Performance breakdown by platform</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={Object.entries(analytics.platforms).map(([platform, data]) => ({
                platform,
                ...data
              }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="platform" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="impressions" fill="#8884d8" name="Impressions" />
                <Bar dataKey="clicks" fill="#82ca9d" name="Clicks" />
                <Bar dataKey="conversions" fill="#ffc658" name="Conversions" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
      
      {/* Detailed Analytics Tabs */}
      <Card>
        <CardContent className="p-6">
          <Tabs defaultValue="demographics" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="demographics">Demographics</TabsTrigger>
              <TabsTrigger value="devices">Devices</TabsTrigger>
              <TabsTrigger value="top-ads">Top Ads</TabsTrigger>
              <TabsTrigger value="insights">Insights</TabsTrigger>
            </TabsList>
            
            <TabsContent value="demographics" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Age Distribution</h3>
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie
                        data={Object.entries(analytics.demographics.age).map(([age, value]) => ({
                          name: age,
                          value
                        }))}
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {Object.entries(analytics.demographics.age).map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold mb-4">Gender Distribution</h3>
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie
                        data={Object.entries(analytics.demographics.gender).map(([gender, value]) => ({
                          name: gender,
                          value
                        }))}
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        fill="#82ca9d"
                        dataKey="value"
                      >
                        {Object.entries(analytics.demographics.gender).map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </TabsContent>
            
            <TabsContent value="devices" className="space-y-4">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={Object.entries(analytics.demographics.device).map(([device, value]) => ({
                  device,
                  percentage: value
                }))}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="device" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="percentage" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </TabsContent>
            
            <TabsContent value="top-ads" className="space-y-4">
              <div className="space-y-4">
                {analytics.topAds.map((ad, index) => (
                  <Card key={ad.id}>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-semibold">{ad.name}</h4>
                          <div className="flex gap-4 mt-2 text-sm text-muted-foreground">
                            <span>Impressions: {formatNumber(ad.impressions)}</span>
                            <span>Clicks: {formatNumber(ad.clicks)}</span>
                            <span>Conversions: {formatNumber(ad.conversions)}</span>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-bold">CTR: {formatPercentage(ad.ctr)}</div>
                          <Badge variant={ad.roi > 200 ? "default" : ad.roi > 100 ? "secondary" : "destructive"}>
                            ROI: {ad.roi}%
                          </Badge>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>
            
            <TabsContent value="insights" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Top Interests</h3>
                  <div className="space-y-2">
                    {analytics.audienceInsights.interests.map((interest, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <span className="text-sm">{interest.name}</span>
                        <div className="flex items-center gap-2">
                          <Progress value={interest.engagement * 100} className="w-20" />
                          <span className="text-xs text-muted-foreground">
                            {(interest.engagement * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold mb-4">Top Behaviors</h3>
                  <div className="space-y-2">
                    {analytics.audienceInsights.behaviors.map((behavior, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <span className="text-sm">{behavior.name}</span>
                        <div className="flex items-center gap-2">
                          <Progress value={behavior.conversionRate * 100} className="w-20" />
                          <span className="text-xs text-muted-foreground">
                            {(behavior.conversionRate * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold mb-4">Psychographics</h3>
                  <div className="space-y-2">
                    {analytics.audienceInsights.psychographics.map((trait, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <span className="text-sm">{trait.trait}</span>
                        <div className="flex items-center gap-2">
                          <Progress value={trait.performance * 100} className="w-20" />
                          <span className="text-xs text-muted-foreground">
                            {(trait.performance * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
      
      {/* A/B Test Results */}
      {analytics.abTests.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              A/B Test Results
            </CardTitle>
          </CardHeader>
          <CardContent>
            {analytics.abTests.map((test) => (
              <div key={test.id} className="border rounded-lg p-4 mb-4">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="font-semibold">{test.name}</h4>
                  <Badge variant={test.status === 'completed' ? 'default' : 'secondary'}>
                    {test.status}
                  </Badge>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {test.variants.map((variant) => (
                    <div key={variant.id} className="p-3 border rounded">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium">{variant.name}</span>
                        {test.winner === variant.id && (
                          <Badge variant="default">Winner</Badge>
                        )}
                      </div>
                      <div className="space-y-1 text-sm">
                        <div>Traffic: {variant.traffic}%</div>
                        <div>Conversions: {variant.conversions}</div>
                        <div>Rate: {formatPercentage(variant.conversionRate)}</div>
                        <div>Significance: {variant.significance}%</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
      
      {/* Predictions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            Performance Predictions
          </CardTitle>
          <CardDescription>
            AI-powered predictions for next period
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h4 className="font-medium">Expected Performance</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Impressions</span>
                  <span className="font-medium">
                    {formatNumber(analytics.predictions.nextPeriod.expectedImpressions)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Clicks</span>
                  <span className="font-medium">
                    {formatNumber(analytics.predictions.nextPeriod.expectedClicks)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Conversions</span>
                  <span className="font-medium">
                    {formatNumber(analytics.predictions.nextPeriod.expectedConversions)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Spend</span>
                  <span className="font-medium">
                    {formatCurrency(analytics.predictions.nextPeriod.expectedSpend)}
                  </span>
                </div>
              </div>
              <div className="pt-2">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">Confidence:</span>
                  <Progress value={analytics.predictions.nextPeriod.confidence * 100} className="flex-1" />
                  <span className="text-sm font-medium">
                    {(analytics.predictions.nextPeriod.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h4 className="font-medium">Optimization Recommendations</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Recommended Budget</span>
                  <span className="font-medium">
                    {formatCurrency(analytics.predictions.optimization.recommendedBudget)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Bidding Strategy</span>
                  <span className="font-medium">
                    {analytics.predictions.optimization.recommendedBidding}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Expected Improvement</span>
                  <span className="font-medium text-green-600">
                    +{(analytics.predictions.optimization.expectedImprovement * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AnalyticsDashboard;
