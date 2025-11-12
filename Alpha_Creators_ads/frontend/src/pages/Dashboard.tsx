import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  BarChart3, 
  Users, 
  TrendingUp, 
  Sparkles,
  Plus,
  Eye,
  Clock,
  Target
} from "lucide-react";

const Dashboard = () => {
  const recentCampaigns = [
    {
      id: 1,
      name: "Summer Sale Campaign",
      status: "Active",
      ads: 12,
      ctr: "8.7%",
      reach: "24.3K",
      created: "2 days ago"
    },
    {
      id: 2,
      name: "Product Launch Ads",
      status: "Paused",
      ads: 8,
      ctr: "6.2%",
      reach: "18.1K",
      created: "1 week ago"
    },
    {
      id: 3,
      name: "Brand Awareness",
      status: "Completed",
      ads: 15,
      ctr: "9.1%",
      reach: "45.7K",
      created: "2 weeks ago"
    }
  ];

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-background">
        <AppSidebar />
        
        <main className="flex-1 p-6 space-y-8">
          {/* Welcome Header */}
          <div className="space-y-2">
            <h1 className="text-3xl font-bold">Welcome back, John! 👋</h1>
            <p className="text-muted-foreground">
              Here's what's happening with your AI-powered advertising campaigns.
            </p>
          </div>

          {/* Quick Stats */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="p-6 bg-gradient-to-br from-primary/10 to-primary/5 border-primary/20">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-primary/20 rounded-lg">
                  <Sparkles className="h-5 w-5 text-primary" />
                </div>
                <span className="text-sm font-medium text-primary">Ads Generated</span>
              </div>
              <div className="text-2xl font-bold mb-1">147</div>
              <div className="text-sm text-muted-foreground">+23 this week</div>
            </Card>
            
            <Card className="p-6 bg-gradient-to-br from-accent/10 to-accent/5 border-accent/20">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-accent/20 rounded-lg">
                  <BarChart3 className="h-5 w-5 text-accent" />
                </div>
                <span className="text-sm font-medium text-accent">Active Campaigns</span>
              </div>
              <div className="text-2xl font-bold mb-1">8</div>
              <div className="text-sm text-muted-foreground">2 launching soon</div>
            </Card>
            
            <Card className="p-6 bg-gradient-to-br from-accent-orange/10 to-accent-orange/5 border-accent-orange/20">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-accent-orange/20 rounded-lg">
                  <TrendingUp className="h-5 w-5 text-accent-orange" />
                </div>
                <span className="text-sm font-medium text-accent-orange">Avg. CTR</span>
              </div>
              <div className="text-2xl font-bold mb-1">7.8%</div>
              <div className="text-sm text-muted-foreground">+12% vs industry</div>
            </Card>
            
            <Card className="p-6 bg-gradient-to-br from-accent-blue/10 to-accent-blue/5 border-accent-blue/20">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-accent-blue/20 rounded-lg">
                  <Users className="h-5 w-5 text-accent-blue" />
                </div>
                <span className="text-sm font-medium text-accent-blue">Total Reach</span>
              </div>
              <div className="text-2xl font-bold mb-1">284K</div>
              <div className="text-sm text-muted-foreground">This month</div>
            </Card>
          </div>

          {/* Quick Actions */}
          <div className="grid md:grid-cols-3 gap-4">
            <Button variant="hero" size="lg" className="h-auto p-6 flex-col gap-3">
              <Plus className="h-8 w-8" />
              <div className="text-center">
                <div className="font-semibold">Generate New Ad</div>
                <div className="text-sm opacity-90">Create with AI in minutes</div>
              </div>
            </Button>
            
            <Button variant="outline" size="lg" className="h-auto p-6 flex-col gap-3">
              <Target className="h-8 w-8" />
              <div className="text-center">
                <div className="font-semibold">New Campaign</div>
                <div className="text-sm text-muted-foreground">Plan your next campaign</div>
              </div>
            </Button>
            
            <Button variant="outline" size="lg" className="h-auto p-6 flex-col gap-3">
              <BarChart3 className="h-8 w-8" />
              <div className="text-center">
                <div className="font-semibold">View Analytics</div>
                <div className="text-sm text-muted-foreground">Deep dive into performance</div>
              </div>
            </Button>
          </div>

          {/* Recent Campaigns */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Recent Campaigns</h2>
              <Button variant="outline" size="sm">
                View All
              </Button>
            </div>
            
            <div className="grid gap-4">
              {recentCampaigns.map((campaign) => (
                <Card key={campaign.id} className="p-6 hover:shadow-card transition-all cursor-pointer">
                  <div className="flex items-center justify-between">
                    <div className="space-y-2">
                      <div className="flex items-center gap-3">
                        <h3 className="font-semibold text-lg">{campaign.name}</h3>
                        <Badge 
                          variant={campaign.status === "Active" ? "default" : 
                                  campaign.status === "Paused" ? "secondary" : "outline"}
                        >
                          {campaign.status}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-6 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Sparkles className="h-4 w-4" />
                          {campaign.ads} ads
                        </div>
                        <div className="flex items-center gap-1">
                          <Eye className="h-4 w-4" />
                          {campaign.ctr} CTR
                        </div>
                        <div className="flex items-center gap-1">
                          <Users className="h-4 w-4" />
                          {campaign.reach} reach
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock className="h-4 w-4" />
                          {campaign.created}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm">
                        Edit
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Eye className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>

          {/* AI Insights Widget */}
          <Card className="p-6 bg-gradient-primary border-primary/20">
            <div className="text-primary-foreground space-y-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-primary-foreground/20 rounded-lg">
                  <TrendingUp className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="font-semibold">AI Optimization Suggestion</h3>
                  <p className="text-primary-foreground/80 text-sm">
                    Based on your recent performance data
                  </p>
                </div>
              </div>
              <p className="text-primary-foreground/90">
                Your "Summer Sale Campaign" could benefit from adjusting the target age range to 25-40. 
                This demographic shows 31% higher engagement with similar content.
              </p>
              <Button variant="glass" size="sm">
                Apply Suggestion
              </Button>
            </div>
          </Card>
        </main>
      </div>
    </SidebarProvider>
  );
};

export default Dashboard;