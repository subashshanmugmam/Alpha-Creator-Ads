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
import AnalyticsDashboard from '@/components/AnalyticsDashboard';
import EthicalAIControls from '@/components/EthicalAIControls';
import RealTimeCustomization from '@/components/RealTimeCustomization';
import { useAdStore } from '@/stores/adStore';
import { useUserStore } from '@/stores/userStore';
import { useAnalyticsStore } from '@/stores/analyticsStore';

const AdStudio = () => {
  const { generatedAds, campaigns, templates } = useAdStore();
  const { currentUser } = useUserStore();
  const analytics = useAnalyticsStore(state => state.analytics);

  const totalAds = generatedAds.length;
  const activeCampaigns = campaigns.filter(c => c.status === 'active').length;

  return (
    <div className="flex-1 p-6 space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">AI Ad Generation Studio</h1>
        <Button>
          <RefreshCw className="mr-2 h-4 w-4" />
          Refresh Data
        </Button>
      </header>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="flex flex-col items-center justify-center p-6">
            <Zap className="h-10 w-10 text-primary mb-2" />
            <p className="text-4xl font-bold">{totalAds}</p>
            <p className="text-sm text-muted-foreground">Total Ads Generated</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex flex-col items-center justify-center p-6">
            <TrendingUp className="h-10 w-10 text-green-500 mb-2" />
            <p className="text-4xl font-bold">{activeCampaigns}</p>
            <p className="text-sm text-muted-foreground">Active Campaigns</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex flex-col items-center justify-center p-6">
            <Target className="h-10 w-10 text-blue-500 mb-2" />
            <p className="text-4xl font-bold">{templates.length}</p>
            <p className="text-sm text-muted-foreground">Ad Templates</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex flex-col items-center justify-center p-6">
            <Users className="h-10 w-10 text-purple-500 mb-2" />
            <p className="text-4xl font-bold">{analytics.performance.totalImpressions || 0}</p>
            <p className="text-sm text-muted-foreground">Total Reach</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="ai-ad-generator" className="space-y-4">
        <TabsList>
          <TabsTrigger value="ai-ad-generator">
            <Zap className="mr-2 h-4 w-4" />
            AI Ad Generator
          </TabsTrigger>
          <TabsTrigger value="analytics-dashboard">
            <BarChart3 className="mr-2 h-4 w-4" />
            Analytics Dashboard
          </TabsTrigger>
          <TabsTrigger value="real-time-customization">
            <Palette className="mr-2 h-4 w-4" />
            Real-Time Customization
          </TabsTrigger>
          <TabsTrigger value="ethical-ai-controls">
            <Shield className="mr-2 h-4 w-4" />
            Ethical AI Controls
          </TabsTrigger>
        </TabsList>

        <TabsContent value="ai-ad-generator">
          <AIAdGenerator />
        </TabsContent>
        <TabsContent value="analytics-dashboard">
          <AnalyticsDashboard />
        </TabsContent>
        <TabsContent value="real-time-customization">
          <RealTimeCustomization />
        </TabsContent>
        <TabsContent value="ethical-ai-controls">
          <EthicalAIControls />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdStudio;
