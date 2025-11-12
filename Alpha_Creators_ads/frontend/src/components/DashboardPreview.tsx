import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { 
  BarChart3, 
  Users, 
  TrendingUp, 
  Target,
  Play,
  Pause,
  Settings
} from "lucide-react";

export const DashboardPreview = () => {
  return (
    <section id="analytics" className="py-24">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl lg:text-5xl font-bold mb-6">
            Advanced{" "}
            <span className="bg-gradient-hero bg-clip-text text-transparent">
              Analytics Dashboard
            </span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Monitor campaign performance, user engagement, and AI model effectiveness 
            with our comprehensive analytics platform.
          </p>
        </div>
        
        <div className="max-w-6xl mx-auto">
          <div className="bg-gradient-card rounded-2xl p-8 shadow-elevated border">
            {/* Dashboard Header */}
            <div className="flex items-center justify-between mb-8">
              <div>
                <h3 className="text-2xl font-bold mb-2">Campaign Dashboard</h3>
                <p className="text-muted-foreground">Real-time insights and performance metrics</p>
              </div>
              <div className="flex items-center gap-3">
                <Button variant="outline" size="sm">
                  <Settings className="h-4 w-4 mr-2" />
                  Settings
                </Button>
                <Button variant="analytics" size="sm">
                  <Play className="h-4 w-4 mr-2" />
                  Live Mode
                </Button>
              </div>
            </div>
            
            {/* Key Metrics */}
            <div className="grid md:grid-cols-4 gap-6 mb-8">
              <Card className="p-6 bg-gradient-to-br from-primary/10 to-primary/5 border-primary/20">
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 bg-primary/20 rounded-lg">
                    <BarChart3 className="h-5 w-5 text-primary" />
                  </div>
                  <span className="text-sm font-medium text-primary">Click Rate</span>
                </div>
                <div className="text-2xl font-bold mb-1">8.7%</div>
                <div className="text-sm text-muted-foreground">+23% from last week</div>
              </Card>
              
              <Card className="p-6 bg-gradient-to-br from-accent/10 to-accent/5 border-accent/20">
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 bg-accent/20 rounded-lg">
                    <Users className="h-5 w-5 text-accent" />
                  </div>
                  <span className="text-sm font-medium text-accent">Reach</span>
                </div>
                <div className="text-2xl font-bold mb-1">124.3K</div>
                <div className="text-sm text-muted-foreground">+15% this month</div>
              </Card>
              
              <Card className="p-6 bg-gradient-to-br from-accent-orange/10 to-accent-orange/5 border-accent-orange/20">
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 bg-accent-orange/20 rounded-lg">
                    <TrendingUp className="h-5 w-5 text-accent-orange" />
                  </div>
                  <span className="text-sm font-medium text-accent-orange">Conversions</span>
                </div>
                <div className="text-2xl font-bold mb-1">2,847</div>
                <div className="text-sm text-muted-foreground">+31% vs target</div>
              </Card>
              
              <Card className="p-6 bg-gradient-to-br from-accent-blue/10 to-accent-blue/5 border-accent-blue/20">
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 bg-accent-blue/20 rounded-lg">
                    <Target className="h-5 w-5 text-accent-blue" />
                  </div>
                  <span className="text-sm font-medium text-accent-blue">Accuracy</span>
                </div>
                <div className="text-2xl font-bold mb-1">94.2%</div>
                <div className="text-sm text-muted-foreground">AI targeting score</div>
              </Card>
            </div>
            
            {/* Chart Placeholder */}
            <Card className="p-6 bg-background">
              <div className="flex items-center justify-between mb-6">
                <h4 className="text-lg font-semibold">Performance Trends</h4>
                <div className="flex items-center gap-2 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="h-3 w-3 bg-primary rounded-full"></div>
                    <span>Click Rate</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-3 w-3 bg-accent rounded-full"></div>
                    <span>Conversions</span>
                  </div>
                </div>
              </div>
              
              <div className="h-64 bg-muted/30 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
                  <p className="text-muted-foreground">Interactive charts and analytics</p>
                  <p className="text-sm text-muted-foreground">Real-time data visualization</p>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
};