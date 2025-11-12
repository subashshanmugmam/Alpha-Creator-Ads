import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  BarChart3, 
  Users, 
  TrendingUp, 
  Target,
  Shield,
  AlertTriangle,
  CheckCircle,
  Download
} from "lucide-react";

const Analytics = () => {
  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-background">
        <AppSidebar />
        
        <main className="flex-1 p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">Performance Analytics</h1>
              <p className="text-muted-foreground">
                Comprehensive insights into your AI-powered advertising performance
              </p>
            </div>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export Report
            </Button>
          </div>

          {/* Key Metrics */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="p-6 bg-gradient-to-br from-primary/10 to-primary/5 border-primary/20">
              <div className="flex items-center gap-3 mb-3">
                <BarChart3 className="h-5 w-5 text-primary" />
                <span className="text-sm font-medium text-primary">Total Revenue</span>
              </div>
              <div className="text-2xl font-bold">$47,234</div>
              <div className="text-sm text-muted-foreground">+23% vs last month</div>
            </Card>
            
            <Card className="p-6 bg-gradient-to-br from-accent/10 to-accent/5 border-accent/20">
              <div className="flex items-center gap-3 mb-3">
                <Users className="h-5 w-5 text-accent" />
                <span className="text-sm font-medium text-accent">Total Reach</span>
              </div>
              <div className="text-2xl font-bold">2.4M</div>
              <div className="text-sm text-muted-foreground">Unique users reached</div>
            </Card>
            
            <Card className="p-6 bg-gradient-to-br from-accent-orange/10 to-accent-orange/5 border-accent-orange/20">
              <div className="flex items-center gap-3 mb-3">
                <Target className="h-5 w-5 text-accent-orange" />
                <span className="text-sm font-medium text-accent-orange">Avg CTR</span>
              </div>
              <div className="text-2xl font-bold">8.7%</div>
              <div className="text-sm text-muted-foreground">Industry: 2.3%</div>
            </Card>
            
            <Card className="p-6 bg-gradient-to-br from-accent-blue/10 to-accent-blue/5 border-accent-blue/20">
              <div className="flex items-center gap-3 mb-3">
                <TrendingUp className="h-5 w-5 text-accent-blue" />
                <span className="text-sm font-medium text-accent-blue">ROAS</span>
              </div>
              <div className="text-2xl font-bold">4.2x</div>
              <div className="text-sm text-muted-foreground">Return on ad spend</div>
            </Card>
          </div>

          {/* AI Ethics Dashboard */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">AI Ethics & Bias Monitoring</h3>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="flex items-center gap-3 p-4 bg-accent/10 rounded-lg">
                <CheckCircle className="h-6 w-6 text-accent" />
                <div>
                  <div className="font-medium">Fairness Score</div>
                  <div className="text-sm text-muted-foreground">94% - Excellent</div>
                </div>
              </div>
              <div className="flex items-center gap-3 p-4 bg-accent-orange/10 rounded-lg">
                <AlertTriangle className="h-6 w-6 text-accent-orange" />
                <div>
                  <div className="font-medium">Bias Detection</div>
                  <div className="text-sm text-muted-foreground">2 minor issues found</div>
                </div>
              </div>
              <div className="flex items-center gap-3 p-4 bg-primary/10 rounded-lg">
                <Shield className="h-6 w-6 text-primary" />
                <div>
                  <div className="font-medium">Compliance</div>
                  <div className="text-sm text-muted-foreground">IEEE 7003-2024</div>
                </div>
              </div>
            </div>
          </Card>

          {/* Charts Placeholder */}
          <div className="grid lg:grid-cols-2 gap-6">
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Performance Trends</h3>
              <div className="h-64 bg-muted/30 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
                  <p className="text-muted-foreground">Interactive performance charts</p>
                </div>
              </div>
            </Card>
            
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Audience Insights</h3>
              <div className="h-64 bg-muted/30 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <Users className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
                  <p className="text-muted-foreground">Demographic analysis</p>
                </div>
              </div>
            </Card>
          </div>
        </main>
      </div>
    </SidebarProvider>
  );
};

export default Analytics;