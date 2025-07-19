import { useState } from "react";
import { KeyRound, Coffee, ArrowLeft, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { Link, useNavigate } from "react-router-dom";

const OwnerAccess = () => {
  const [accessCode, setAccessCode] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();
  const navigate = useNavigate();

  const SECRET_CODE = "CAFE2024"; // In a real app, this would be more secure

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    // Simulate API call
    setTimeout(() => {
      if (accessCode === SECRET_CODE) {
        toast({
          title: "Access granted!",
          description: "Welcome to the owner dashboard.",
        });
        navigate("/dashboard");
      } else {
        toast({
          title: "Access denied",
          description: "Invalid access code. Please try again.",
          variant: "destructive",
        });
      }
      setIsLoading(false);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gradient-warm flex items-center justify-center p-4">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 bg-white/80 backdrop-blur-sm border-b shadow-warm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Coffee className="h-8 w-8 text-primary" />
            <h1 className="text-2xl font-bold text-primary">SmartCafe AI</h1>
          </div>
          <Link to="/">
            <Button variant="outline" className="gap-2">
              <ArrowLeft className="h-4 w-4" />
              Back to Reviews
            </Button>
          </Link>
        </div>
      </div>

      {/* Access Form */}
      <div className="w-full max-w-md pt-20">
        <Card className="shadow-warm border-0 animate-scale-in">
          <CardHeader className="text-center pb-6">
            <div className="flex justify-center mb-4">
              <div className="p-3 bg-primary/10 rounded-full">
                <Shield className="h-8 w-8 text-primary" />
              </div>
            </div>
            <CardTitle className="text-2xl text-primary mb-2">
              Owner Access
            </CardTitle>
            <p className="text-muted-foreground">
              Enter your secret access code to view the dashboard
            </p>
          </CardHeader>
          
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-3">
                <label className="text-sm font-medium text-foreground">
                  Access Code
                </label>
                <div className="relative">
                  <KeyRound className="absolute left-3 top-3 h-5 w-5 text-muted-foreground" />
                  <Input
                    type="password"
                    placeholder="Enter secret code..."
                    value={accessCode}
                    onChange={(e) => setAccessCode(e.target.value)}
                    className="pl-10 h-12 border-2 focus:border-primary/30"
                    required
                  />
                </div>
              </div>

              <Button
                type="submit"
                disabled={isLoading || !accessCode.trim()}
                className="w-full h-12 text-lg font-semibold bg-gradient-primary hover:opacity-90 transition-all duration-300 shadow-warm"
                size="lg"
              >
                {isLoading ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Verifying...
                  </div>
                ) : (
                  <>
                    <KeyRound className="h-5 w-5 mr-2" />
                    Access Dashboard
                  </>
                )}
              </Button>
            </form>

            <div className="mt-6 p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground text-center">
                <strong>Demo Code:</strong> CAFE2024
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default OwnerAccess;
