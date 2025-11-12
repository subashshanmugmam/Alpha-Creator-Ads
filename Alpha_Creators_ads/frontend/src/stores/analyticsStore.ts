import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';

export interface AnalyticsData {
  // Performance metrics
  performance: {
    totalImpressions: number;
    totalClicks: number;
    totalConversions: number;
    totalSpend: number;
    totalRevenue: number;
    
    // Calculated metrics
    ctr: number;
    cpc: number;
    cpm: number;
    conversionRate: number;
    roi: number;
    roas: number; // Return on Ad Spend
  };
  
  // Time-series data
  timeSeries: {
    date: string;
    impressions: number;
    clicks: number;
    conversions: number;
    spend: number;
    revenue: number;
  }[];
  
  // Demographic breakdown
  demographics: {
    age: { [key: string]: number };
    gender: { [key: string]: number };
    location: { [key: string]: number };
    device: { [key: string]: number };
  };
  
  // Performance by platform
  platforms: {
    [platform: string]: {
      impressions: number;
      clicks: number;
      conversions: number;
      spend: number;
      ctr: number;
    };
  };
  
  // Top performing ads
  topAds: {
    id: string;
    name: string;
    impressions: number;
    clicks: number;
    conversions: number;
    ctr: number;
    roi: number;
  }[];
  
  // Audience insights
  audienceInsights: {
    interests: { name: string; engagement: number }[];
    behaviors: { name: string; conversionRate: number }[];
    psychographics: { trait: string; performance: number }[];
  };
  
  // A/B test results
  abTests: {
    id: string;
    name: string;
    status: 'running' | 'completed' | 'paused';
    variants: {
      id: string;
      name: string;
      traffic: number;
      conversions: number;
      conversionRate: number;
      significance: number;
    }[];
    winner?: string;
  }[];
  
  // Predictive analytics
  predictions: {
    nextPeriod: {
      expectedImpressions: number;
      expectedClicks: number;
      expectedConversions: number;
      expectedSpend: number;
      confidence: number;
    };
    optimization: {
      recommendedBudget: number;
      recommendedBidding: string;
      expectedImprovement: number;
    };
  };
}

export interface ReportConfig {
  dateRange: {
    start: Date;
    end: Date;
    preset?: 'today' | 'yesterday' | '7days' | '30days' | '90days' | 'custom';
  };
  metrics: string[];
  dimensions: string[];
  filters: {
    campaigns?: string[];
    platforms?: string[];
    adTypes?: string[];
    demographics?: any;
  };
  groupBy: 'day' | 'week' | 'month';
  comparison?: {
    type: 'previous_period' | 'year_over_year';
    enabled: boolean;
  };
}

export interface Dashboard {
  id: string;
  name: string;
  description: string;
  widgets: DashboardWidget[];
  layout: {
    [widgetId: string]: {
      x: number;
      y: number;
      w: number;
      h: number;
    };
  };
  filters: ReportConfig['filters'];
  createdAt: Date;
  updatedAt: Date;
}

export interface DashboardWidget {
  id: string;
  type: 'metric' | 'chart' | 'table' | 'heatmap' | 'funnel' | 'cohort';
  title: string;
  config: {
    metric?: string;
    chartType?: 'line' | 'bar' | 'pie' | 'doughnut' | 'area' | 'scatter';
    dataSource: string;
    timeRange: string;
    filters?: any;
    customization: {
      colors?: string[];
      showLegend?: boolean;
      showGrid?: boolean;
      animate?: boolean;
    };
  };
  position: {
    x: number;
    y: number;
    w: number;
    h: number;
  };
}

interface AnalyticsStore {
  // Data
  analytics: AnalyticsData | null;
  dashboards: Dashboard[];
  currentDashboard: Dashboard | null;
  reports: any[];
  
  // UI state
  isLoading: boolean;
  selectedDateRange: ReportConfig['dateRange'];
  selectedMetrics: string[];
  selectedDimensions: string[];
  appliedFilters: ReportConfig['filters'];
  
  // Comparison data
  comparisonData: AnalyticsData | null;
  comparisonEnabled: boolean;
  
  // Real-time data
  realTimeData: {
    currentUsers: number;
    todayImpressions: number;
    todayClicks: number;
    todaySpend: number;
    lastUpdated: Date;
  } | null;
  
  // Actions
  // Data fetching
  fetchAnalytics: (config: ReportConfig) => Promise<void>;
  fetchRealTimeData: () => Promise<void>;
  
  // Dashboard management
  createDashboard: (dashboard: Omit<Dashboard, 'id' | 'createdAt' | 'updatedAt'>) => Dashboard;
  updateDashboard: (dashboardId: string, updates: Partial<Dashboard>) => void;
  deleteDashboard: (dashboardId: string) => void;
  duplicateDashboard: (dashboardId: string) => Dashboard;
  setCurrentDashboard: (dashboard: Dashboard | null) => void;
  
  // Widget management
  addWidget: (dashboardId: string, widget: Omit<DashboardWidget, 'id'>) => void;
  updateWidget: (dashboardId: string, widgetId: string, updates: Partial<DashboardWidget>) => void;
  removeWidget: (dashboardId: string, widgetId: string) => void;
  updateWidgetLayout: (dashboardId: string, layout: Dashboard['layout']) => void;
  
  // Filtering and configuration
  setDateRange: (dateRange: ReportConfig['dateRange']) => void;
  setMetrics: (metrics: string[]) => void;
  setDimensions: (dimensions: string[]) => void;
  setFilters: (filters: ReportConfig['filters']) => void;
  applyFilters: () => void;
  clearFilters: () => void;
  
  // Comparison
  enableComparison: (type: 'previous_period' | 'year_over_year') => void;
  disableComparison: () => void;
  
  // Export
  exportData: (format: 'csv' | 'xlsx' | 'pdf') => Promise<Blob>;
  exportDashboard: (dashboardId: string, format: 'pdf' | 'png') => Promise<Blob>;
  
  // Alerts and notifications
  createAlert: (config: any) => void;
  updateAlert: (alertId: string, updates: any) => void;
  deleteAlert: (alertId: string) => void;
  
  // Advanced analytics
  performCohortAnalysis: (config: any) => Promise<any>;
  performFunnelAnalysis: (config: any) => Promise<any>;
  performAttributionAnalysis: (config: any) => Promise<any>;
}

export const useAnalyticsStore = create(subscribeWithSelector<AnalyticsStore>((set, get) => ({
  // Initial state
  analytics: null,
  dashboards: [],
  currentDashboard: null,
  reports: [],
  isLoading: false,
  selectedDateRange: {
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // 30 days ago
    end: new Date(),
    preset: '30days'
  },
  selectedMetrics: ['impressions', 'clicks', 'conversions', 'spend'],
  selectedDimensions: ['date'],
  appliedFilters: {},
  comparisonData: null,
  comparisonEnabled: false,
  realTimeData: null,
  
  // Data fetching
  fetchAnalytics: async (config) => {
    set({ isLoading: true });
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Generate mock analytics data
      const mockData: AnalyticsData = generateMockAnalyticsData(config);
      
      set({ 
        analytics: mockData, 
        isLoading: false,
        selectedDateRange: config.dateRange,
        selectedMetrics: config.metrics,
        selectedDimensions: config.dimensions,
        appliedFilters: config.filters
      });
      
      // Fetch comparison data if enabled
      if (get().comparisonEnabled) {
        const comparisonConfig = { ...config };
        // Adjust date range for comparison
        const daysDiff = Math.ceil((config.dateRange.end.getTime() - config.dateRange.start.getTime()) / (1000 * 60 * 60 * 24));
        comparisonConfig.dateRange = {
          start: new Date(config.dateRange.start.getTime() - daysDiff * 24 * 60 * 60 * 1000),
          end: config.dateRange.start,
          preset: 'custom'
        };
        
        const comparisonData = generateMockAnalyticsData(comparisonConfig);
        set({ comparisonData });
      }
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      set({ isLoading: false });
    }
  },
  
  fetchRealTimeData: async () => {
    try {
      // Simulate real-time data fetch
      const realTimeData = {
        currentUsers: Math.floor(Math.random() * 500) + 100,
        todayImpressions: Math.floor(Math.random() * 10000) + 5000,
        todayClicks: Math.floor(Math.random() * 500) + 100,
        todaySpend: Math.floor(Math.random() * 1000) + 200,
        lastUpdated: new Date()
      };
      
      set({ realTimeData });
    } catch (error) {
      console.error('Failed to fetch real-time data:', error);
    }
  },
  
  // Dashboard management
  createDashboard: (dashboardData) => {
    const dashboard: Dashboard = {
      ...dashboardData,
      id: Math.random().toString(36).substr(2, 9),
      createdAt: new Date(),
      updatedAt: new Date()
    };
    
    set((state) => ({
      dashboards: [...state.dashboards, dashboard],
      currentDashboard: dashboard
    }));
    
    return dashboard;
  },
  
  updateDashboard: (dashboardId, updates) => set((state) => ({
    dashboards: state.dashboards.map(dashboard =>
      dashboard.id === dashboardId 
        ? { ...dashboard, ...updates, updatedAt: new Date() }
        : dashboard
    ),
    currentDashboard: state.currentDashboard?.id === dashboardId
      ? { ...state.currentDashboard, ...updates, updatedAt: new Date() }
      : state.currentDashboard
  })),
  
  deleteDashboard: (dashboardId) => set((state) => ({
    dashboards: state.dashboards.filter(dashboard => dashboard.id !== dashboardId),
    currentDashboard: state.currentDashboard?.id === dashboardId ? null : state.currentDashboard
  })),
  
  duplicateDashboard: (dashboardId) => {
    const state = get();
    const originalDashboard = state.dashboards.find(d => d.id === dashboardId);
    if (!originalDashboard) throw new Error('Dashboard not found');
    
    const duplicatedDashboard: Dashboard = {
      ...originalDashboard,
      id: Math.random().toString(36).substr(2, 9),
      name: `${originalDashboard.name} (Copy)`,
      createdAt: new Date(),
      updatedAt: new Date()
    };
    
    set((state) => ({
      dashboards: [...state.dashboards, duplicatedDashboard]
    }));
    
    return duplicatedDashboard;
  },
  
  setCurrentDashboard: (dashboard) => set({ currentDashboard: dashboard }),
  
  // Widget management
  addWidget: (dashboardId, widgetData) => {
    const widget: DashboardWidget = {
      ...widgetData,
      id: Math.random().toString(36).substr(2, 9)
    };
    
    set((state) => ({
      dashboards: state.dashboards.map(dashboard =>
        dashboard.id === dashboardId
          ? {
              ...dashboard,
              widgets: [...dashboard.widgets, widget],
              layout: {
                ...dashboard.layout,
                [widget.id]: widget.position
              },
              updatedAt: new Date()
            }
          : dashboard
      )
    }));
  },
  
  updateWidget: (dashboardId, widgetId, updates) => set((state) => ({
    dashboards: state.dashboards.map(dashboard =>
      dashboard.id === dashboardId
        ? {
            ...dashboard,
            widgets: dashboard.widgets.map(widget =>
              widget.id === widgetId ? { ...widget, ...updates } : widget
            ),
            updatedAt: new Date()
          }
        : dashboard
    )
  })),
  
  removeWidget: (dashboardId, widgetId) => set((state) => ({
    dashboards: state.dashboards.map(dashboard =>
      dashboard.id === dashboardId
        ? {
            ...dashboard,
            widgets: dashboard.widgets.filter(widget => widget.id !== widgetId),
            layout: Object.fromEntries(
              Object.entries(dashboard.layout).filter(([id]) => id !== widgetId)
            ),
            updatedAt: new Date()
          }
        : dashboard
    )
  })),
  
  updateWidgetLayout: (dashboardId, layout) => set((state) => ({
    dashboards: state.dashboards.map(dashboard =>
      dashboard.id === dashboardId
        ? { ...dashboard, layout, updatedAt: new Date() }
        : dashboard
    )
  })),
  
  // Filtering and configuration
  setDateRange: (dateRange) => set({ selectedDateRange: dateRange }),
  setMetrics: (metrics) => set({ selectedMetrics: metrics }),
  setDimensions: (dimensions) => set({ selectedDimensions: dimensions }),
  setFilters: (filters) => set({ appliedFilters: filters }),
  
  applyFilters: () => {
    const state = get();
    const config: ReportConfig = {
      dateRange: state.selectedDateRange,
      metrics: state.selectedMetrics,
      dimensions: state.selectedDimensions,
      filters: state.appliedFilters,
      groupBy: 'day'
    };
    
    state.fetchAnalytics(config);
  },
  
  clearFilters: () => set({ 
    appliedFilters: {},
    selectedMetrics: ['impressions', 'clicks', 'conversions', 'spend'],
    selectedDimensions: ['date']
  }),
  
  // Comparison
  enableComparison: (type) => {
    set({ comparisonEnabled: true });
    get().applyFilters(); // Refetch with comparison
  },
  
  disableComparison: () => set({ 
    comparisonEnabled: false, 
    comparisonData: null 
  }),
  
  // Export (placeholder implementations)
  exportData: async (format) => {
    const state = get();
    if (!state.analytics) throw new Error('No data to export');
    
    // Implementation would generate actual files
    return new Blob(['exported analytics data'], { type: 'application/octet-stream' });
  },
  
  exportDashboard: async (dashboardId, format) => {
    // Implementation would generate dashboard exports
    return new Blob(['exported dashboard'], { type: 'application/octet-stream' });
  },
  
  // Alerts (placeholder implementations)
  createAlert: (config) => {
    // Implementation for creating performance alerts
  },
  
  updateAlert: (alertId, updates) => {
    // Implementation for updating alerts
  },
  
  deleteAlert: (alertId) => {
    // Implementation for deleting alerts
  },
  
  // Advanced analytics (placeholder implementations)
  performCohortAnalysis: async (config) => {
    // Implementation for cohort analysis
    return {};
  },
  
  performFunnelAnalysis: async (config) => {
    // Implementation for funnel analysis
    return {};
  },
  
  performAttributionAnalysis: async (config) => {
    // Implementation for attribution analysis
    return {};
  }
})));

// Helper function to generate mock analytics data
function generateMockAnalyticsData(config: ReportConfig): AnalyticsData {
  const days = Math.ceil((config.dateRange.end.getTime() - config.dateRange.start.getTime()) / (1000 * 60 * 60 * 24));
  const timeSeries = [];
  
  // Generate time series data
  for (let i = 0; i < days; i++) {
    const date = new Date(config.dateRange.start.getTime() + i * 24 * 60 * 60 * 1000);
    const impressions = Math.floor(Math.random() * 5000) + 1000;
    const clicks = Math.floor(impressions * (0.01 + Math.random() * 0.05));
    const conversions = Math.floor(clicks * (0.02 + Math.random() * 0.08));
    const spend = Math.floor(clicks * (0.5 + Math.random() * 2));
    const revenue = Math.floor(conversions * (20 + Math.random() * 80));
    
    timeSeries.push({
      date: date.toISOString().split('T')[0],
      impressions,
      clicks,
      conversions,
      spend,
      revenue
    });
  }
  
  // Calculate totals
  const totals = timeSeries.reduce((acc, day) => ({
    totalImpressions: acc.totalImpressions + day.impressions,
    totalClicks: acc.totalClicks + day.clicks,
    totalConversions: acc.totalConversions + day.conversions,
    totalSpend: acc.totalSpend + day.spend,
    totalRevenue: acc.totalRevenue + day.revenue
  }), {
    totalImpressions: 0,
    totalClicks: 0,
    totalConversions: 0,
    totalSpend: 0,
    totalRevenue: 0
  });
  
  return {
    performance: {
      ...totals,
      ctr: totals.totalClicks / totals.totalImpressions,
      cpc: totals.totalSpend / totals.totalClicks,
      cpm: (totals.totalSpend / totals.totalImpressions) * 1000,
      conversionRate: totals.totalConversions / totals.totalClicks,
      roi: ((totals.totalRevenue - totals.totalSpend) / totals.totalSpend) * 100,
      roas: totals.totalRevenue / totals.totalSpend
    },
    timeSeries,
    demographics: {
      age: { '18-24': 25, '25-34': 35, '35-44': 25, '45-54': 10, '55+': 5 },
      gender: { 'Male': 60, 'Female': 38, 'Other': 2 },
      location: { 'US': 50, 'CA': 15, 'UK': 10, 'AU': 8, 'Other': 17 },
      device: { 'Mobile': 70, 'Desktop': 25, 'Tablet': 5 }
    },
    platforms: {
      'Google Ads': { impressions: totals.totalImpressions * 0.4, clicks: totals.totalClicks * 0.35, conversions: totals.totalConversions * 0.3, spend: totals.totalSpend * 0.45, ctr: 0.025 },
      'Facebook': { impressions: totals.totalImpressions * 0.35, clicks: totals.totalClicks * 0.4, conversions: totals.totalConversions * 0.4, spend: totals.totalSpend * 0.3, ctr: 0.032 },
      'Instagram': { impressions: totals.totalImpressions * 0.15, clicks: totals.totalClicks * 0.15, conversions: totals.totalConversions * 0.2, spend: totals.totalSpend * 0.15, ctr: 0.028 },
      'LinkedIn': { impressions: totals.totalImpressions * 0.1, clicks: totals.totalClicks * 0.1, conversions: totals.totalConversions * 0.1, spend: totals.totalSpend * 0.1, ctr: 0.022 }
    },
    topAds: [
      { id: '1', name: 'Summer Sale Campaign', impressions: 15000, clicks: 450, conversions: 25, ctr: 0.03, roi: 250 },
      { id: '2', name: 'Product Launch Ad', impressions: 12000, clicks: 380, conversions: 20, ctr: 0.032, roi: 180 },
      { id: '3', name: 'Brand Awareness', impressions: 20000, clicks: 400, conversions: 15, ctr: 0.02, roi: 120 }
    ],
    audienceInsights: {
      interests: [
        { name: 'Technology', engagement: 0.85 },
        { name: 'Shopping', engagement: 0.78 },
        { name: 'Travel', engagement: 0.72 }
      ],
      behaviors: [
        { name: 'Online Shoppers', conversionRate: 0.08 },
        { name: 'Mobile Users', conversionRate: 0.06 },
        { name: 'Social Media Active', conversionRate: 0.05 }
      ],
      psychographics: [
        { trait: 'Early Adopters', performance: 0.82 },
        { trait: 'Price Conscious', performance: 0.65 },
        { trait: 'Brand Loyal', performance: 0.78 }
      ]
    },
    abTests: [
      {
        id: '1',
        name: 'Headline A/B Test',
        status: 'completed',
        variants: [
          { id: 'A', name: 'Original', traffic: 50, conversions: 25, conversionRate: 0.05, significance: 95 },
          { id: 'B', name: 'Variant', traffic: 50, conversions: 32, conversionRate: 0.064, significance: 95 }
        ],
        winner: 'B'
      }
    ],
    predictions: {
      nextPeriod: {
        expectedImpressions: totals.totalImpressions * 1.1,
        expectedClicks: totals.totalClicks * 1.05,
        expectedConversions: totals.totalConversions * 1.15,
        expectedSpend: totals.totalSpend * 1.08,
        confidence: 0.78
      },
      optimization: {
        recommendedBudget: totals.totalSpend * 1.2,
        recommendedBidding: 'Target CPA',
        expectedImprovement: 0.15
      }
    }
  };
}
