import { 
  Brain, 
  Target, 
  BarChart3, 
  Shield, 
  Sparkles, 
  Users,
  Clock,
  TrendingUp 
} from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "AI-Powered Generation",
    description: "Advanced machine learning creates personalized ad content that resonates with your target audience.",
    color: "text-primary"
  },
  {
    icon: Target,
    title: "Precise Targeting",
    description: "Multi-dimensional user profiling ensures your ads reach the right people at the right time.",
    color: "text-accent"
  },
  {
    icon: BarChart3,
    title: "Real-time Analytics",
    description: "Comprehensive dashboards track performance metrics and optimize campaigns automatically.",
    color: "text-accent-orange"
  },
  {
    icon: Shield,
    title: "Ethical AI",
    description: "Built-in bias detection and transparency tools ensure responsible advertising practices.",
    color: "text-accent-blue"
  },
  {
    icon: Sparkles,
    title: "Multi-Modal Content",
    description: "Generate coordinated text, images, and video content for comprehensive campaigns.",
    color: "text-primary-glow"
  },
  {
    icon: Users,
    title: "User Segmentation",
    description: "Advanced clustering algorithms identify distinct audience segments for targeted messaging.",
    color: "text-accent"
  },
  {
    icon: Clock,
    title: "Real-time Optimization",
    description: "Reinforcement learning continuously improves ad performance based on user interactions.",
    color: "text-accent-orange"
  },
  {
    icon: TrendingUp,
    title: "Performance Prediction",
    description: "AI-powered forecasting predicts campaign success before launch to maximize ROI.",
    color: "text-primary"
  }
];

export const FeaturesSection = () => {
  return (
    <section id="features" className="py-24 bg-muted/30">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl lg:text-5xl font-bold mb-6">
            Powerful AI Features for{" "}
            <span className="bg-gradient-hero bg-clip-text text-transparent">
              Modern Advertising
            </span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Our comprehensive platform combines cutting-edge AI technologies to deliver 
            personalized advertising experiences that drive real results.
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div 
              key={index}
              className="group bg-gradient-card rounded-xl p-6 shadow-card hover:shadow-elevated transition-all duration-300 border hover:border-primary/20"
            >
              <div className="flex flex-col items-center text-center">
                <div className={`p-3 rounded-lg bg-background shadow-sm mb-4 group-hover:scale-110 transition-transform duration-300`}>
                  <feature.icon className={`h-6 w-6 ${feature.color}`} />
                </div>
                <h3 className="text-lg font-semibold mb-3 group-hover:text-primary transition-colors">
                  {feature.title}
                </h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {feature.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};