import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  FolderOpen, 
  Plus, 
  Search,
  Filter,
  Eye,
  Edit,
  MoreHorizontal,
  BarChart3,
  Users,
  Clock,
  Target
} from "lucide-react";

const Campaigns = () => {
  const campaigns = [
    {
      id: 1,
      name: "Summer Sale Blitz",
      status: "Active",
      objective: "Sales",
      ads: 15,
      spend: "$2,847",
      ctr: "8.7%",
      conversions: 234,
      reach: "45.2K",
      created: "2024-01-15",
      lastModified: "2 hours ago"
    },
    {
      id: 2,
      name: "Brand Awareness Q1",
      status: "Active",
      objective: "Awareness",
      ads: 8,
      spend: "$1,230",
      ctr: "6.2%",
      conversions: 89,
      reach: "78.1K",
      created: "2024-01-10",
      lastModified: "1 day ago"
    },
    {
      id: 3,
      name: "Product Launch Campaign",
      status: "Paused",
      objective: "Lead Generation",
      ads: 12,
      spend: "$3,456",
      ctr: "9.1%",
      conversions: 345,
      reach: "32.7K",
      created: "2024-01-05",
      lastModified: "3 days ago"
    },
    {
      id: 4,
      name: "Holiday Promotion",
      status: "Completed",
      objective: "Sales",
      ads: 20,
      spend: "$5,678",
      ctr: "7.8%",
      conversions: 456,
      reach: "89.3K",
      created: "2023-12-01",
      lastModified: "2 weeks ago"
    },
    {
      id: 5,
      name: "Mobile App Downloads",
      status: "Draft",
      objective: "App Downloads",
      ads: 6,
      spend: "$0",
      ctr: "0%",
      conversions: 0,
      reach: "0",
      created: "2024-01-20",
      lastModified: "5 minutes ago"
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Active": return "default";
      case "Paused": return "secondary";
      case "Completed": return "outline";
      case "Draft": return "secondary";
      default: return "outline";
    }
  };

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-background">
        <AppSidebar />
        
        <main className="flex-1 p-6 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">Campaign Manager</h1>
              <p className="text-muted-foreground">
                Manage and monitor your AI-powered advertising campaigns
              </p>
            </div>
            <Button variant="hero">
              <Plus className="h-4 w-4 mr-2" />
              New Campaign
            </Button>
          </div>

          {/* Stats Cards */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="p-6">
              <div className="flex items-center gap-3 mb-2">
                <FolderOpen className="h-5 w-5 text-primary" />
                <span className="text-sm font-medium">Total Campaigns</span>
              </div>
              <div className="text-2xl font-bold">5</div>
              <div className="text-sm text-muted-foreground">2 active</div>
            </Card>
            
            <Card className="p-6">
              <div className="flex items-center gap-3 mb-2">
                <Target className="h-5 w-5 text-accent" />
                <span className="text-sm font-medium">Total Ads</span>
              </div>
              <div className="text-2xl font-bold">61</div>
              <div className="text-sm text-muted-foreground">+12 this week</div>
            </Card>
            
            <Card className="p-6">
              <div className="flex items-center gap-3 mb-2">
                <BarChart3 className="h-5 w-5 text-accent-orange" />
                <span className="text-sm font-medium">Total Spend</span>
              </div>
              <div className="text-2xl font-bold">$13.2K</div>
              <div className="text-sm text-muted-foreground">This month</div>
            </Card>
            
            <Card className="p-6">
              <div className="flex items-center gap-3 mb-2">
                <Users className="h-5 w-5 text-accent-blue" />
                <span className="text-sm font-medium">Total Reach</span>
              </div>
              <div className="text-2xl font-bold">245K</div>
              <div className="text-sm text-muted-foreground">Unique users</div>
            </Card>
          </div>

          {/* Filters and Search */}
          <div className="flex items-center gap-4">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search campaigns..." className="pl-10" />
            </div>
            <Button variant="outline">
              <Filter className="h-4 w-4 mr-2" />
              Filter
            </Button>
          </div>

          {/* Campaigns Table */}
          <Card className="overflow-hidden">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold">All Campaigns</h3>
            </div>
            <div className="overflow-x-auto">
              <div className="min-w-full">
                {/* Header */}
                <div className="grid grid-cols-12 gap-4 p-4 bg-muted/50 border-b text-sm font-medium text-muted-foreground">
                  <div className="col-span-3">Campaign</div>
                  <div className="col-span-1">Status</div>
                  <div className="col-span-1">Ads</div>
                  <div className="col-span-1">Spend</div>
                  <div className="col-span-1">CTR</div>
                  <div className="col-span-1">Conv.</div>
                  <div className="col-span-2">Reach</div>
                  <div className="col-span-1">Modified</div>
                  <div className="col-span-1">Actions</div>
                </div>

                {/* Rows */}
                {campaigns.map((campaign) => (
                  <div key={campaign.id} className="grid grid-cols-12 gap-4 p-4 border-b hover:bg-muted/30 transition-colors">
                    <div className="col-span-3 space-y-1">
                      <div className="font-medium">{campaign.name}</div>
                      <div className="text-sm text-muted-foreground">
                        {campaign.objective} • Created {new Date(campaign.created).toLocaleDateString()}
                      </div>
                    </div>
                    
                    <div className="col-span-1">
                      <Badge variant={getStatusColor(campaign.status) as any}>
                        {campaign.status}
                      </Badge>
                    </div>
                    
                    <div className="col-span-1">
                      <div className="font-medium">{campaign.ads}</div>
                    </div>
                    
                    <div className="col-span-1">
                      <div className="font-medium">{campaign.spend}</div>
                    </div>
                    
                    <div className="col-span-1">
                      <div className="font-medium">{campaign.ctr}</div>
                    </div>
                    
                    <div className="col-span-1">
                      <div className="font-medium">{campaign.conversions}</div>
                    </div>
                    
                    <div className="col-span-2">
                      <div className="font-medium">{campaign.reach}</div>
                    </div>
                    
                    <div className="col-span-1">
                      <div className="text-sm text-muted-foreground">{campaign.lastModified}</div>
                    </div>
                    
                    <div className="col-span-1">
                      <div className="flex items-center gap-1">
                        <Button variant="ghost" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm">
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>

          {/* Quick Actions */}
          <div className="grid md:grid-cols-3 gap-4">
            <Card className="p-6 hover:shadow-card transition-all cursor-pointer">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <Plus className="h-5 w-5 text-primary" />
                </div>
                <h3 className="font-semibold">Create Campaign</h3>
              </div>
              <p className="text-sm text-muted-foreground">
                Start a new AI-powered advertising campaign with our guided setup
              </p>
            </Card>
            
            <Card className="p-6 hover:shadow-card transition-all cursor-pointer">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-accent/10 rounded-lg">
                  <BarChart3 className="h-5 w-5 text-accent" />
                </div>
                <h3 className="font-semibold">Performance Report</h3>
              </div>
              <p className="text-sm text-muted-foreground">
                Generate detailed analytics report for all your campaigns
              </p>
            </Card>
            
            <Card className="p-6 hover:shadow-card transition-all cursor-pointer">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-accent-orange/10 rounded-lg">
                  <Target className="h-5 w-5 text-accent-orange" />
                </div>
                <h3 className="font-semibold">Audience Insights</h3>
              </div>
              <p className="text-sm text-muted-foreground">
                Discover new targeting opportunities and audience segments
              </p>
            </Card>
          </div>
        </main>
      </div>
    </SidebarProvider>
  );
};

export default Campaigns;