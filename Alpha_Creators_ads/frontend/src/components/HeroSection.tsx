import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles, Zap, Target } from "lucide-react";
import heroImage from "@/assets/hero-ai-bg.jpg";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";

export const HeroSection = () => {
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleStartCreating = () => {
    console.log("Button clicked! Navigating to /generate");
    console.log("Current location:", window.location.href);
    try {
      navigate("/generate");
      console.log("Navigation called successfully");
    } catch (error) {
      console.error("Navigation error:", error);
    }
  };

  const handleWatchDemo = () => {
    toast({
      title: "Coming Soon!",
      description: "The demo video is not yet available.",
    });
  };

  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-background via-primary/5 to-accent/10">
      <div className="absolute inset-0 opacity-20">
        <img 
          src={heroImage} 
          alt="AI Technology Background" 
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-accent/20" />
      </div>
      
      <div className="relative container mx-auto px-4 py-24 lg:py-32">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div className="text-center lg:text-left">
            <div className="inline-flex items-center gap-2 bg-primary/10 border border-primary/20 rounded-full px-4 py-2 mb-6">
              <Sparkles className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium text-primary">AI-Powered Advertising</span>
            </div>
            
            <h1 className="text-4xl lg:text-6xl font-bold leading-tight mb-6">
              Create{" "}
              <span className="bg-gradient-hero bg-clip-text text-transparent">
                Personalized Ads
              </span>{" "}
              with AI
            </h1>
            
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl">
              Transform your advertising with intelligent personalization. Generate compelling, 
              targeted ads that resonate with your audience using advanced AI technology.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 mb-12">
              <Button variant="premium" size="lg" className="group" onClick={handleStartCreating}>
                Start Creating Ads
                <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Button>
              <Button variant="glass" size="lg" onClick={handleWatchDemo}>
                Watch Demo
              </Button>
            </div>
            
            <div className="grid grid-cols-3 gap-6 max-w-md mx-auto lg:mx-0">
              <div className="text-center">
                <div className="text-2xl font-bold text-primary">95%</div>
                <div className="text-sm text-muted-foreground">Accuracy</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-accent">3x</div>
                <div className="text-sm text-muted-foreground">Faster</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-accent-orange">50%</div>
                <div className="text-sm text-muted-foreground">Better CTR</div>
              </div>
            </div>
          </div>
          
          <div className="relative">
            <div className="bg-gradient-card rounded-2xl p-8 shadow-elevated border">
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">AI Ad Generator</h3>
                  <div className="flex items-center gap-2 text-accent">
                    <div className="h-2 w-2 bg-accent rounded-full animate-pulse" />
                    <span className="text-sm">Live</span>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div className="flex items-center gap-3 p-3 bg-background rounded-lg border">
                    <Target className="h-5 w-5 text-primary" />
                    <span className="text-sm">Audience: Tech Professionals, 25-40</span>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-background rounded-lg border">
                    <Zap className="h-5 w-5 text-accent" />
                    <span className="text-sm">Campaign: SaaS Product Launch</span>
                  </div>
                </div>
                
                <div className="bg-gradient-primary rounded-lg p-4 text-primary-foreground">
                  <h4 className="font-medium mb-2">Generated Ad Copy:</h4>
                  <p className="text-sm opacity-90">
                    "Revolutionize your workflow with our AI-powered platform. 
                    Join 10,000+ professionals who've transformed their productivity."
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
