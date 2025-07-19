import { useState } from "react";
import { Star, Send, Coffee, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { Link } from "react-router-dom";
import cafeHero from "@/assets/cafe-hero.jpg";

const Index = () => {
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [reviewText, setReviewText] = useState("");
  const { toast } = useToast();

  // API configuration for deployment
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://smartcafe-ai.onrender.com';

  const handleStarClick = (starIndex: number) => {
    setRating(starIndex);
  };

  const handleSubmit = async () => {
    if (rating === 0) {
      toast({
        title: "Please add a rating",
        description: "Select at least one star to submit your review.",
        variant: "destructive",
      });
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/submit-review`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          review_text: reviewText,
          rating: rating.toString(),
        }),
      });

      const result = await response.json();

      if (result.status === "success") {
        toast({
          title: "Review submitted!",
          description: "Thank you for sharing your experience with us.",
        });
        setRating(0);
        setReviewText("");
      } else {
        toast({
          title: "Submission failed",
          description: result.message || "An error occurred.",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Network Error",
        description: "Could not reach the server. Try again later.",
        variant: "destructive",
      });
      console.error("Submission error:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-warm">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b shadow-warm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Coffee className="h-8 w-8 text-primary" />
            <h1 className="text-2xl font-bold text-primary">SmartCafe AI</h1>
          </div>
          <Link to="/owner">
            <Button variant="outline" className="gap-2">
              Owner Access
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-20 overflow-hidden">
        <div className="absolute inset-0">
          <img 
            src={cafeHero} 
            alt="Café atmosphere" 
            className="w-full h-full object-cover opacity-20"
          />
          <div className="absolute inset-0 bg-gradient-primary opacity-60"></div>
        </div>
        
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-4xl mx-auto text-center text-white">
            <h2 className="text-5xl font-bold mb-6 animate-fade-in">
              Share Your Experience
            </h2>
            <p className="text-xl opacity-90 animate-fade-in" style={{ animationDelay: '0.2s' }}>
              Help us serve you better by sharing your thoughts about your visit
            </p>
          </div>
        </div>
      </section>

      {/* Review Form */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl mx-auto">
            <Card className="shadow-warm border-0 animate-scale-in">
              <CardHeader className="text-center pb-6">
                <CardTitle className="text-2xl text-primary mb-2">
                  Rate Your Experience
                </CardTitle>
                <p className="text-muted-foreground">
                  Your feedback helps us improve our service
                </p>
              </CardHeader>
              
              <CardContent className="space-y-8">
                {/* Star Rating */}
                <div className="text-center space-y-4">
                  <label className="text-lg font-medium text-foreground block">
                    How would you rate your experience?
                  </label>
                  <div className="flex justify-center gap-2">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        onClick={() => handleStarClick(star)}
                        onMouseEnter={() => setHoveredRating(star)}
                        onMouseLeave={() => setHoveredRating(0)}
                        className="p-1 rounded-lg transition-all duration-200 hover:scale-110"
                      >
                        <Star
                          className={`h-10 w-10 transition-colors duration-200 ${
                            star <= (hoveredRating || rating)
                              ? "fill-accent text-accent"
                              : "text-muted"
                          }`}
                        />
                      </button>
                    ))}
                  </div>
                  {rating > 0 && (
                    <p className="text-sm text-muted-foreground animate-fade-in">
                      You rated: {rating} star{rating !== 1 ? 's' : ''}
                    </p>
                  )}
                </div>

                {/* Review Text */}
                <div className="space-y-3">
                  <label className="text-lg font-medium text-foreground">
                    Tell us more about your experience
                  </label>
                  <Textarea
                    placeholder="Share what you loved about your visit, or how we can improve..."
                    value={reviewText}
                    onChange={(e) => setReviewText(e.target.value)}
                    className="min-h-32 resize-none border-2 focus:border-primary/30"
                  />
                </div>

                {/* Submit Button */}
                <Button
                  onClick={handleSubmit}
                  className="w-full h-12 text-lg font-semibold bg-gradient-accent hover:opacity-90 transition-all duration-300 shadow-accent"
                  size="lg"
                >
                  <Send className="h-5 w-5 mr-2" />
                  Submit Review
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-primary text-primary-foreground py-12">
        <div className="container mx-auto px-4 text-center">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Coffee className="h-6 w-6" />
            <h3 className="text-xl font-semibold">SmartCafe AI</h3>
          </div>
          <p className="opacity-80">
            Enhancing café experiences through intelligent feedback analysis
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
