import { create } from 'zustand';

export interface AdTemplate {
  id: string;
  name: string;
  category: string;
  format: 'text' | 'display' | 'video' | 'social';
  platform: 'google' | 'facebook' | 'instagram' | 'linkedin' | 'twitter' | 'generic';
  template: {
    headline: string;
    description: string;
    callToAction: string;
    visualElements?: {
      backgroundColor: string;
      textColor: string;
      accentColor: string;
      imageUrl?: string;
      logoUrl?: string;
    };
  };
  targetingParameters: {
    demographics: string[];
    interests: string[];
    behaviors: string[];
  };
}

export interface GeneratedAd {
  id: string;
  templateId: string;
  userId: string;
  campaignId?: string;
  
  // Generated content
  content: {
    headline: string;
    description: string;
    callToAction: string;
    visualElements: {
      backgroundColor: string;
      textColor: string;
      accentColor: string;
      imageUrl?: string;
      generatedImage?: string;
    };
    videoScript?: string;
  };
  
  // Targeting
  targeting: {
    demographics: any;
    psychographics: any;
    behaviors: any;
    context: any;
  };
  
  // AI generation metadata
  generation: {
    aiModel: string;
    prompt: string;
    generationTime: number;
    confidence: number;
    variations: number;
  };
  
  // Performance predictions
  predictions: {
    expectedCTR: number;
    expectedEngagement: number;
    expectedConversion: number;
    confidenceScore: number;
  };
  
  // Performance metrics (actual)
  performance?: {
    impressions: number;
    clicks: number;
    conversions: number;
    ctr: number;
    cost: number;
    roi: number;
  };
  
  createdAt: Date;
  updatedAt: Date;
  status: 'draft' | 'active' | 'paused' | 'completed';
}

export interface Campaign {
  id: string;
  name: string;
  description: string;
  objective: 'awareness' | 'engagement' | 'conversion' | 'retention';
  budget: number;
  startDate: Date;
  endDate: Date;
  status: 'draft' | 'active' | 'paused' | 'completed';
  
  // Targeting
  targetAudience: {
    demographics: any;
    interests: string[];
    behaviors: string[];
    customSegments: string[];
  };
  
  // Ads in campaign
  ads: string[]; // Ad IDs
  
  // Performance
  performance: {
    totalImpressions: number;
    totalClicks: number;
    totalConversions: number;
    totalSpend: number;
    averageCTR: number;
    averageCPC: number;
    roi: number;
  };
  
  createdAt: Date;
  updatedAt: Date;
}

interface AdStore {
  // Templates
  templates: AdTemplate[];
  selectedTemplate: AdTemplate | null;
  
  // Generated ads
  generatedAds: GeneratedAd[];
  currentAd: GeneratedAd | null;
  
  // Campaigns
  campaigns: Campaign[];
  currentCampaign: Campaign | null;
  
  // UI state
  isGenerating: boolean;
  generationProgress: number;
  
  // Actions for templates
  loadTemplates: () => void;
  selectTemplate: (template: AdTemplate) => void;
  
  // Actions for ads
  generateAd: (templateId: string, userProfile: any, customizations?: any) => Promise<GeneratedAd>;
  saveAd: (ad: GeneratedAd) => void;
  updateAd: (adId: string, updates: Partial<GeneratedAd>) => void;
  deleteAd: (adId: string) => void;
  duplicateAd: (adId: string) => GeneratedAd;
  
  // Actions for campaigns
  createCampaign: (campaign: Omit<Campaign, 'id' | 'createdAt' | 'updatedAt'>) => Campaign;
  updateCampaign: (campaignId: string, updates: Partial<Campaign>) => void;
  deleteCampaign: (campaignId: string) => void;
  addAdToCampaign: (campaignId: string, adId: string) => void;
  removeAdFromCampaign: (campaignId: string, adId: string) => void;
  
  // Bulk operations
  generateBulkAds: (templateIds: string[], userProfile: any, variations: number) => Promise<GeneratedAd[]>;
  
  // Performance tracking
  updateAdPerformance: (adId: string, performance: GeneratedAd['performance']) => void;
  updateCampaignPerformance: (campaignId: string, performance: Campaign['performance']) => void;
  
  // Optimization
  optimizeAd: (adId: string) => Promise<GeneratedAd>;
  suggestOptimizations: (adId: string) => Promise<string[]>;
  
  // Export/Import
  exportAd: (adId: string, format: 'png' | 'pdf' | 'html') => Promise<Blob>;
  exportCampaign: (campaignId: string) => Promise<any>;
}

export const useAdStore = create<AdStore>((set, get) => ({
  // Initial state
  templates: [],
  selectedTemplate: null,
  generatedAds: [],
  currentAd: null,
  campaigns: [],
  currentCampaign: null,
  isGenerating: false,
  generationProgress: 0,
  
  // Template actions
  loadTemplates: () => {
    // Load default templates
    const defaultTemplates: AdTemplate[] = [
      {
        id: '1',
        name: 'E-commerce Product Ad',
        category: 'retail',
        format: 'display',
        platform: 'google',
        template: {
          headline: 'Discover {{product}} - Perfect for {{audience}}',
          description: 'Get {{discount}}% off on {{product}}. {{benefit}} that {{audience}} love. Free shipping on orders over ${{threshold}}.',
          callToAction: 'Shop Now'
        },
        targetingParameters: {
          demographics: ['age', 'gender', 'income'],
          interests: ['shopping', 'fashion', 'technology'],
          behaviors: ['recent purchases', 'browsing history']
        }
      },
      {
        id: '2',
        name: 'Service Promotion',
        category: 'services',
        format: 'text',
        platform: 'facebook',
        template: {
          headline: '{{service}} for {{location}} - {{unique_value}}',
          description: 'Professional {{service}} with {{experience}} years of experience. {{guarantee}} and {{special_offer}}.',
          callToAction: 'Get Quote'
        },
        targetingParameters: {
          demographics: ['age', 'location', 'income'],
          interests: ['home improvement', 'professional services'],
          behaviors: ['service searches', 'local business engagement']
        }
      },
      {
        id: '3',
        name: 'App Download',
        category: 'technology',
        format: 'social',
        platform: 'instagram',
        template: {
          headline: 'Download {{app_name}} - {{main_benefit}}',
          description: 'Join {{user_count}} users who {{achievement}}. {{key_feature}} that makes {{daily_task}} easier.',
          callToAction: 'Download Free'
        },
        targetingParameters: {
          demographics: ['age', 'device_type'],
          interests: ['mobile apps', 'productivity', 'technology'],
          behaviors: ['app downloads', 'mobile usage']
        }
      }
    ];
    
    set({ templates: defaultTemplates });
  },
  
  selectTemplate: (template) => set({ selectedTemplate: template }),
  
  // Ad generation
  generateAd: async (templateId, userProfile, customizations = {}) => {
    set({ isGenerating: true, generationProgress: 0 });
    
    try {
      // Simulate AI generation process
      const template = get().templates.find(t => t.id === templateId);
      if (!template) throw new Error('Template not found');
      
      // Progress simulation
      for (let i = 0; i <= 100; i += 10) {
        set({ generationProgress: i });
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      
      // Generate personalized content based on user profile
      const generatedAd: GeneratedAd = {
        id: Math.random().toString(36).substr(2, 9),
        templateId,
        userId: userProfile.id,
        content: {
          headline: personalizeText(template.template.headline, userProfile),
          description: personalizeText(template.template.description, userProfile),
          callToAction: template.template.callToAction,
          visualElements: {
            backgroundColor: customizations.backgroundColor || '#ffffff',
            textColor: customizations.textColor || '#000000',
            accentColor: customizations.accentColor || '#007bff',
            ...customizations.visualElements
          }
        },
        targeting: {
          demographics: userProfile.demographics,
          psychographics: userProfile.psychographics,
          behaviors: userProfile.behaviors,
          context: userProfile.context
        },
        generation: {
          aiModel: 'gpt-4',
          prompt: `Generate ad for ${template.name} targeting ${userProfile.demographics.age}-year-old ${userProfile.demographics.gender}`,
          generationTime: Date.now(),
          confidence: 0.85 + Math.random() * 0.15,
          variations: 1
        },
        predictions: {
          expectedCTR: 0.02 + Math.random() * 0.05,
          expectedEngagement: 0.15 + Math.random() * 0.20,
          expectedConversion: 0.01 + Math.random() * 0.03,
          confidenceScore: 0.80 + Math.random() * 0.20
        },
        createdAt: new Date(),
        updatedAt: new Date(),
        status: 'draft'
      };
      
      set((state) => ({
        generatedAds: [...state.generatedAds, generatedAd],
        currentAd: generatedAd,
        isGenerating: false,
        generationProgress: 100
      }));
      
      return generatedAd;
    } catch (error) {
      set({ isGenerating: false, generationProgress: 0 });
      throw error;
    }
  },
  
  saveAd: (ad) => set((state) => ({
    generatedAds: [...state.generatedAds, ad]
  })),
  
  updateAd: (adId, updates) => set((state) => ({
    generatedAds: state.generatedAds.map(ad => 
      ad.id === adId ? { ...ad, ...updates, updatedAt: new Date() } : ad
    ),
    currentAd: state.currentAd?.id === adId 
      ? { ...state.currentAd, ...updates, updatedAt: new Date() } 
      : state.currentAd
  })),
  
  deleteAd: (adId) => set((state) => ({
    generatedAds: state.generatedAds.filter(ad => ad.id !== adId),
    currentAd: state.currentAd?.id === adId ? null : state.currentAd
  })),
  
  duplicateAd: (adId) => {
    const state = get();
    const originalAd = state.generatedAds.find(ad => ad.id === adId);
    if (!originalAd) throw new Error('Ad not found');
    
    const duplicatedAd: GeneratedAd = {
      ...originalAd,
      id: Math.random().toString(36).substr(2, 9),
      createdAt: new Date(),
      updatedAt: new Date(),
      status: 'draft'
    };
    
    set((state) => ({
      generatedAds: [...state.generatedAds, duplicatedAd]
    }));
    
    return duplicatedAd;
  },
  
  // Campaign actions
  createCampaign: (campaignData) => {
    const campaign: Campaign = {
      ...campaignData,
      id: Math.random().toString(36).substr(2, 9),
      createdAt: new Date(),
      updatedAt: new Date(),
      ads: [],
      performance: {
        totalImpressions: 0,
        totalClicks: 0,
        totalConversions: 0,
        totalSpend: 0,
        averageCTR: 0,
        averageCPC: 0,
        roi: 0
      }
    };
    
    set((state) => ({
      campaigns: [...state.campaigns, campaign],
      currentCampaign: campaign
    }));
    
    return campaign;
  },
  
  updateCampaign: (campaignId, updates) => set((state) => ({
    campaigns: state.campaigns.map(campaign =>
      campaign.id === campaignId 
        ? { ...campaign, ...updates, updatedAt: new Date() }
        : campaign
    ),
    currentCampaign: state.currentCampaign?.id === campaignId
      ? { ...state.currentCampaign, ...updates, updatedAt: new Date() }
      : state.currentCampaign
  })),
  
  deleteCampaign: (campaignId) => set((state) => ({
    campaigns: state.campaigns.filter(campaign => campaign.id !== campaignId),
    currentCampaign: state.currentCampaign?.id === campaignId ? null : state.currentCampaign
  })),
  
  addAdToCampaign: (campaignId, adId) => set((state) => ({
    campaigns: state.campaigns.map(campaign =>
      campaign.id === campaignId
        ? { ...campaign, ads: [...campaign.ads, adId], updatedAt: new Date() }
        : campaign
    )
  })),
  
  removeAdFromCampaign: (campaignId, adId) => set((state) => ({
    campaigns: state.campaigns.map(campaign =>
      campaign.id === campaignId
        ? { ...campaign, ads: campaign.ads.filter(id => id !== adId), updatedAt: new Date() }
        : campaign
    )
  })),
  
  // Bulk operations
  generateBulkAds: async (templateIds, userProfile, variations) => {
    const generatedAds: GeneratedAd[] = [];
    
    for (const templateId of templateIds) {
      for (let i = 0; i < variations; i++) {
        const ad = await get().generateAd(templateId, userProfile, {
          variation: i
        });
        generatedAds.push(ad);
      }
    }
    
    return generatedAds;
  },
  
  // Performance tracking
  updateAdPerformance: (adId, performance) => set((state) => ({
    generatedAds: state.generatedAds.map(ad =>
      ad.id === adId
        ? { ...ad, performance, updatedAt: new Date() }
        : ad
    )
  })),
  
  updateCampaignPerformance: (campaignId, performance) => set((state) => ({
    campaigns: state.campaigns.map(campaign =>
      campaign.id === campaignId
        ? { ...campaign, performance, updatedAt: new Date() }
        : campaign
    )
  })),
  
  // Optimization (placeholder implementations)
  optimizeAd: async (adId) => {
    // AI-powered optimization logic would go here
    const state = get();
    const ad = state.generatedAds.find(a => a.id === adId);
    if (!ad) throw new Error('Ad not found');
    
    // Return optimized version
    return { ...ad, updatedAt: new Date() };
  },
  
  suggestOptimizations: async (adId) => {
    // Return AI-generated optimization suggestions
    return [
      'Try a more action-oriented headline',
      'Consider using emotional triggers in the description',
      'Test different call-to-action buttons',
      'Optimize for mobile viewing'
    ];
  },
  
  // Export functions (placeholder implementations)
  exportAd: async (adId, format) => {
    // Implementation would generate actual files
    return new Blob(['exported ad content'], { type: 'application/octet-stream' });
  },
  
  exportCampaign: async (campaignId) => {
    const campaign = get().campaigns.find(c => c.id === campaignId);
    return campaign;
  }
}));

// Helper function to personalize text based on user profile
function personalizeText(template: string, userProfile: any): string {
  let personalized = template;
  
  // Replace common placeholders
  const replacements = {
    '{{audience}}': userProfile.demographics.occupation || 'professionals',
    '{{location}}': userProfile.demographics.location || 'your area',
    '{{age_group}}': getAgeGroup(userProfile.demographics.age),
    '{{interest}}': userProfile.psychographics.interests[0] || 'quality products',
    '{{product}}': 'premium products',
    '{{service}}': 'our services',
    '{{discount}}': Math.floor(Math.random() * 30 + 10).toString(),
    '{{benefit}}': 'Quality and reliability',
    '{{threshold}}': '50',
    '{{unique_value}}': 'Best Value in Town',
    '{{experience}}': Math.floor(Math.random() * 15 + 5).toString(),
    '{{guarantee}}': 'Money-back guarantee',
    '{{special_offer}}': '20% off for new customers',
    '{{app_name}}': 'Our App',
    '{{main_benefit}}': 'Save Time Daily',
    '{{user_count}}': '1M+',
    '{{achievement}}': 'save 2 hours daily',
    '{{key_feature}}': 'Smart automation',
    '{{daily_task}}': 'daily tasks'
  };
  
  Object.entries(replacements).forEach(([placeholder, value]) => {
    personalized = personalized.replace(new RegExp(placeholder, 'g'), value);
  });
  
  return personalized;
}

function getAgeGroup(age: number): string {
  if (age < 25) return 'young adults';
  if (age < 35) return 'millennials';
  if (age < 50) return 'professionals';
  if (age < 65) return 'experienced professionals';
  return 'seniors';
}
