import { useParams } from "react-router-dom";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  ArrowLeft,
  Play,
  Pause,
  Edit,
  BarChart3,
  Users,
  Target,
  Eye,
  Download,
  Settings,
  TrendingUp,
  Clock
} from "lucide-react";

const CampaignDetail = () => {
  const { id } = useParams();

  const campaign = {
    id: 1,
    name: "Summer Sale Blitz",
    status: "Active",
    objective: "Sales",
    created: "2024-01-15",
    description: "Comprehensive summer sale campaign targeting tech professionals with AI-generated personalized content across multiple channels.",
    metrics: {
      spend: "$2,847",
      impressions: "245.2K",
      clicks: "21.3K",
      ctr: "8.7%",
      conversions: 234,
      cpa: "$12.17",
      roas: "4.2x"
    },
    ads: [
      {
        id: 1,
        name: "Tech Professional Ad",
        format: "Display",
        status: "Active",
        impressions: "89.2K",
        clicks: "7.8K",
        ctr: "8.7%",
        conversions: 89,
        spend: "$987"
      },
      {
        id: 2,
        name: "Young Entrepreneur Ad",
        format: "Social",
        status: "Active",
        impressions: "67.1K",
        clicks: "6.2K",
        ctr: "9.2%",
        conversions: 76,
        spend: "$743"
      },
      {
        id: 3,
        name: "Corporate Executive Ad",
        format: "Search",
        status: "Paused",
        impressions: "43.5K",
        clicks: "3.1K",
        ctr: "7.1%",
        conversions: 34,
        spend: "$456"
      }
    ]
  };

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-background">
        <AppSidebar />
        
        <main className="flex-1 p-6 space-y-6">
          {/* Header */}
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Campaigns
            </Button>
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <h1 className="text-3xl font-bold">{campaign.name}</h1>
                <Badge variant={campaign.status === "Active" ? "default" : "secondary"}>
                  {campaign.status}
                </Badge>
              </div>
              <p className="text-muted-foreground">{campaign.description}</p>
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <span>Created: {new Date(campaign.created).toLocaleDateString()}</span>
                <span>•</span>
                <span>Objective: {campaign.objective}</span>
                <span>•</span>
                <span>{campaign.ads.length} ads</span>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Button variant="outline">
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Button>
              <Button variant="outline">
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </Button>
              <Button variant={campaign.status === "Active" ? "secondary" : "hero"}>
                {campaign.status === "Active" ? (
                  <>
                    <Pause className="h-4 w-4 mr-2" />
                    Pause
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    Resume
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="p-6">
              <div className="flex items-center gap-3 mb-2">
                <BarChart3 className="h-5 w-5 text-primary" />
                <span className="text-sm font-medium">Total Spend</span>
              </div>
              <div className="text-2xl font-bold">{campaign.metrics.spend}</div>
              <div className="text-sm text-muted-foreground">+12% vs last month</div>
            </Card>
            
            <Card className="p-6">
              <div className="flex items-center gap-3 mb-2">
                <Eye className="h-5 w-5 text-accent" />
                <span className="text-sm font-medium">Impressions</span>
              </div>
              <div className="text-2xl font-bold">{campaign.metrics.impressions}</div>
              <div className="text-sm text-muted-foreground">Reach: {campaign.metrics.impressions}</div>
            </Card>
            
            <Card className="p-6">
              <div className="flex items-center gap-3 mb-2">
                <Target className="h-5 w-5 text-accent-orange" />
                <span className="text-sm font-medium">CTR</span>
              </div>
              <div className="text-2xl font-bold">{campaign.metrics.ctr}</div>
              <div className="text-sm text-muted-foreground">Above industry avg</div>
            </Card>
            
            <Card className="p-6">
              <div className="flex items-center gap-3 mb-2">
                <TrendingUp className="h-5 w-5 text-accent-blue" />
                <span className="text-sm font-medium">ROAS</span>
              </div>
              <div className="text-2xl font-bold">{campaign.metrics.roas}</div>
              <div className="text-sm text-muted-foreground">{campaign.metrics.conversions} conversions</div>
            </Card>
          </div>

          {/* Tabs */}
          <Tabs defaultValue="overview" className="space-y-6">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="ads">Ads ({campaign.ads.length})</TabsTrigger>
              <TabsTrigger value="analytics">Analytics</TabsTrigger>
              <TabsTrigger value="insights">AI Insights</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-6">
              {/* Performance Chart Placeholder */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Performance Overview</h3>
                <div className="h-64 bg-muted/30 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
                    <p className="text-muted-foreground">Performance charts and trends</p>
                    <p className="text-sm text-muted-foreground">Interactive analytics visualization</p>
                  </div>
                </div>
              </Card>

              {/* Recent Activity */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
                <div className="space-y-3">
                  <div className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">Ad performance optimization applied</p>
                      <p className="text-xs text-muted-foreground">2 hours ago</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg">
                    <TrendingUp className="h-4 w-4 text-accent" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">CTR increased by 15%</p>
                      <p className="text-xs text-muted-foreground">Yesterday</p>
                    </div>
                  </div>
                </div>
              </Card>
            </TabsContent>

            <TabsContent value="ads" className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Campaign Ads</h3>
                <Button variant="hero">
                  <Target className="h-4 w-4 mr-2" />
                  Generate New Ad
                </Button>
              </div>

              <div className="grid gap-4">
                {campaign.ads.map((ad) => (
                  <Card key={ad.id} className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="space-y-1">
                        <div className="flex items-center gap-3">
                          <h4 className="font-semibold">{ad.name}</h4>
                          <Badge variant={ad.status === "Active" ? "default" : "secondary"}>
                            {ad.status}
                          </Badge>
                          <Badge variant="outline">{ad.format}</Badge>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="sm">
                          <Edit className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="grid md:grid-cols-5 gap-4">
                      <div>
                        <div className="text-sm text-muted-foreground">Impressions</div>
                        <div className="font-semibold">{ad.impressions}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">Clicks</div>
                        <div className="font-semibold">{ad.clicks}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">CTR</div>
                        <div className="font-semibold">{ad.ctr}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">Conversions</div>
                        <div className="font-semibold">{ad.conversions}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">Spend</div>
                        <div className="font-semibold">{ad.spend}</div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="analytics" className="space-y-6">
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Detailed Analytics</h3>
                <div className="h-80 bg-muted/30 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <BarChart3 className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                    <p className="text-lg font-medium">Advanced Analytics Dashboard</p>
                    <p className="text-muted-foreground">Deep dive into campaign performance</p>
                  </div>
                </div>
              </Card>
            </TabsContent>

            <TabsContent value="insights" className="space-y-6">
              <Card className="p-6 bg-gradient-primary border-primary/20">
                <div className="text-primary-foreground space-y-4">
                  <h3 className="text-lg font-semibold">AI Performance Insights</h3>
                  <div className="space-y-3">
                    <div className="bg-primary-foreground/10 rounded-lg p-4">
                      <h4 className="font-medium mb-2">Optimization Recommendation</h4>
                      <p className="text-sm opacity-90">
                        Your ads perform 23% better with audiences aged 28-35. Consider increasing budget allocation for this segment.
                      </p>
                    </div>
                    <div className="bg-primary-foreground/10 rounded-lg p-4">
                      <h4 className="font-medium mb-2">Creative Performance</h4>
                      <p className="text-sm opacity-90">
                        Headlines with emotion-driven language show 31% higher engagement. Try incorporating more emotional triggers.
                      </p>
                    </div>
                  </div>
                  <Button variant="glass" size="sm">
                    Apply All Suggestions
                  </Button>
                </div>
              </Card>
            </TabsContent>
          </Tabs>
        </main>
      </div>
    </SidebarProvider>
  );
};

export default CampaignDetail;