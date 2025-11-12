import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  BarChart3,
  Zap,
  Shield,
  Palette,
  Users,
  TrendingUp,
  Target,
  RefreshCw
} from 'lucide-react';
import { AIAdGenerator } from '@/components/AIAdGenerator';
import { AnalyticsDashboard } from '@/components/AnalyticsDashboard';
import { EthicalAIControls } from '@/components/EthicalAIControls';
import { RealTimeCustomization } from '@/components/RealTimeCustomization';
import { useAdStore } from '@/stores/adStore';
import { useUserStore } from '@/stores/userStore';
import { useAnalyticsStore } from '@/stores/analyticsStore';

const Generate = () => {
  const { generatedAds, campaigns, templates } = useAdStore();
  const { currentUser } = useUserStore();
  const { analytics } = useAnalyticsStore();

  const totalAds = generatedAds.length;
  const activeCampaigns = campaigns.filter(c => c.status === 'active').length;
  const avgPerformance = analytics?.performance?.totalClicks && analytics?.performance?.totalImpressions
    ? ((analytics.performance.totalClicks / analytics.performance.totalImpressions) * 100).toFixed(2)
    : '0.00';

  return (
    <div className="container mx-auto px-4 py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">AI Ad Generation Studio</h1>
          <p className="text-muted-foreground">
            Create, customize, and optimize your ads with AI assistance
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="secondary">Free Plan</Badge>
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Sync Data
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Ads</p>
                <p className="text-2xl font-bold">{totalAds}</p>
              </div>
              <Zap className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Active Campaigns</p>
                <p className="text-2xl font-bold">{activeCampaigns}</p>
              </div>
              <Target className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Avg CTR</p>
                <p className="text-2xl font-bold">{avgPerformance}%</p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Templates</p>
                <p className="text-2xl font-bold">{templates.length}</p>
              </div>
              <Users className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="generator" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="generator" className="flex items-center gap-2">
            <Zap className="h-4 w-4" />
            AI Generator
          </TabsTrigger>
          <TabsTrigger value="customization" className="flex items-center gap-2">
            <Palette className="h-4 w-4" />
            Customize
          </TabsTrigger>
          <TabsTrigger value="analytics" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Analytics
          </TabsTrigger>
          <TabsTrigger value="ethics" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Ethics & AI
          </TabsTrigger>
        </TabsList>

        <TabsContent value="generator" className="mt-6">
          <AIAdGenerator />
        </TabsContent>

        <TabsContent value="customization" className="mt-6">
          <RealTimeCustomization />
        </TabsContent>

        <TabsContent value="analytics" className="mt-6">
          <AnalyticsDashboard />
        </TabsContent>

        <TabsContent value="ethics" className="mt-6">
          <EthicalAIControls />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Generate;