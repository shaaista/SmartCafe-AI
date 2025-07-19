import { useState, useEffect } from "react";

import { 
  Coffee, 
  BarChart3, 
  MessageSquare, 
  Upload, 
  FileText,
  TrendingUp,
  Users,
  Star,
  Bot,
  ArrowLeft,
  Download,
  Filter,
  Send,
  User
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Link } from "react-router-dom";
import { Doughnut, Bar } from "react-chartjs-2";
import { 
  Chart, 
  ArcElement, 
  Tooltip, 
  Legend, 
  CategoryScale, 
  LinearScale, 
  BarElement 
} from "chart.js";
Chart.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

// Chat message interface
interface ChatMessage {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
}

const OwnerDashboard = () => {
  // API configuration for deployment
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://smartcafe-ai.onrender.com';

  const [uploadedFiles, setUploadedFiles] = useState([
    { name: "orders_jan_2024.csv", date: "2024-01-15", size: "2.3 MB" },
    { name: "orders_dec_2023.csv", date: "2023-12-30", size: "1.8 MB" }
  ]);

  // Add these new state variables
  const [suggestions, setSuggestions] = useState<string>('');
  const [loadingSuggestions, setLoadingSuggestions] = useState<boolean>(true);

  // Reviews state
  const [reviews, setReviews] = useState([]);
  const [loadingReviews, setLoadingReviews] = useState(true);
  const [ratingFilter, setRatingFilter] = useState<number | null>(null);

  // Chat state - Updated for conversational chat
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [loadingChatbot, setLoadingChatbot] = useState(false);

  // Add this useEffect for fetching suggestions
  useEffect(() => {
    const fetchSuggestions = async () => {
      try {
        setLoadingSuggestions(true);
        const response = await fetch(`${API_BASE_URL}/suggestions`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        setSuggestions(data.suggestions);
      } catch (error) {
        console.error('Error fetching suggestions:', error);
        setSuggestions('Unable to load AI suggestions at this time.');
      } finally {
        setLoadingSuggestions(false);
      }
    };

    fetchSuggestions();
  }, [API_BASE_URL]);

  // Add this useEffect for fetching reviews
  useEffect(() => {
    const fetchReviews = async () => {
      try {
        setLoadingReviews(true);
        const response = await fetch(`${API_BASE_URL}/get-reviews`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Handle the response structure from your backend
        if (data.status === 'success' && data.data) {
          setReviews(data.data);
        } else {
          setReviews([]);
        }
      } catch (error) {
        console.error('Error fetching reviews:', error);
        setReviews([]);
      } finally {
        setLoadingReviews(false);
      }
    };

    fetchReviews();
  }, [API_BASE_URL]);

  const [sentimentData, setSentimentData] = useState({ positive: 0, neutral: 0, negative: 0 });
  const [loadingSentiment, setLoadingSentiment] = useState(true);

  useEffect(() => {
    const fetchSentiment = async () => {
      setLoadingSentiment(true);
      try {
        const resp = await fetch(`${API_BASE_URL}/sentiment`);
        if (!resp.ok) throw new Error('Could not fetch sentiment');
        const data = await resp.json();
        setSentimentData(data.counts || { positive: 0, neutral: 0, negative: 0 });
      } catch {
        setSentimentData({ positive: 0, neutral: 0, negative: 0 });
      } finally {
        setLoadingSentiment(false);
      }
    };
    fetchSentiment();
  }, [API_BASE_URL]);

  // Keyword trends state
  const [keywords, setKeywords] = useState<{ keyword: string; count: number }[]>([]);
  const [loadingKeywords, setLoadingKeywords] = useState(true);

  useEffect(() => {
    const fetchKeywords = async () => {
      try {
        setLoadingKeywords(true);
        const resp = await fetch(`${API_BASE_URL}/keyword-trends`);
        if (!resp.ok) throw new Error("Unable to fetch keyword trends");
        const data = await resp.json();
        if (data.keywords && Array.isArray(data.keywords)) {
          setKeywords(data.keywords.slice(0, 10)); // top-10 only for clarity
        }
      } catch (e) {
        console.error(e);
        setKeywords([]);
      } finally {
        setLoadingKeywords(false);
      }
    };
    fetchKeywords();
  }, [API_BASE_URL]);

  // Doughnut chart configuration
  const doughnutData = {
    labels: ['Positive', 'Neutral', 'Negative'],
    datasets: [
      {
        label: 'Review Sentiment',
        data: [
          sentimentData.positive,
          sentimentData.neutral,
          sentimentData.negative,
        ],
        backgroundColor: [
          'rgba(186, 230, 253, 0.75)', // pastel blue
          'rgba(253, 230, 138, 0.75)', // pastel yellow
          'rgba(254, 202, 202, 0.75)', // pastel red
        ],
        borderColor: [
          'rgba(59,130,246,0.15)',
          'rgba(250,204,21,0.15)',
          'rgba(239,68,68,0.15)',
        ],
        borderWidth: 2,
        hoverOffset: 18,
      },
    ],
  };

  const doughnutOptions = {
    plugins: {
      legend: {
        display: false, // Hide the default legend
      },
    },
    cutout: '72%',
    responsive: true,
    maintainAspectRatio: false,
  };

  // Keyword bar chart configuration
  const keywordBarData = {
    labels: keywords.map((k) => k.keyword),
    datasets: [
      {
        label: "Mentions",
        data: keywords.map((k) => k.count),
        backgroundColor: [
          "rgba(186,230,253,0.6)",
          "rgba(253,230,138,0.6)",
          "rgba(254,202,202,0.6)",
          "rgba(221,214,254,0.6)",
          "rgba(196,240,213,0.6)",
          "rgba(255,221,244,0.6)",
          "rgba(255,237,213,0.6)",
          "rgba(207,250,254,0.6)",
          "rgba(254,226,226,0.6)",
          "rgba(229,231,235,0.6)",
        ],
        borderRadius: 6,
        maxBarThickness: 28,
      },
    ],
  };

  const keywordBarOptions = {
    indexAxis: "y" as const,
    plugins: { legend: { display: false } },
    maintainAspectRatio: false,
    scales: {
      x: { ticks: { stepSize: 1 } },
      y: { grid: { display: false } },
    },
  };

  // Helper function to filter and limit reviews
  const getDisplayedReviews = () => {
    let filteredReviews = reviews;
    
    if (ratingFilter !== null) {
      filteredReviews = reviews.filter(review => review.rating === ratingFilter);
    }
    
    return filteredReviews.slice(0, 5);
  };

  // Helper function to format date
  const formatDate = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return 'Unknown date';
    }
  };

  // Helper function to determine sentiment based on rating
  const getSentiment = (rating: number) => {
    if (rating >= 4) return 'positive';
    if (rating >= 3) return 'neutral';
    return 'negative';
  };

  // Enhanced chatbot function for conversational chat
  const handleSendMessage = async () => {
    if (!currentMessage.trim()) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString() + '-user',
      type: 'user',
      content: currentMessage,
      timestamp: new Date()
    };

    setChatMessages(prev => [...prev, userMessage]);
    const messageToSend = currentMessage;
    setCurrentMessage('');
    setLoadingChatbot(true);

    try {
      // Send the entire chat history for context
      const chatHistory = [...chatMessages, userMessage].map(msg => ({
        role: msg.type === 'user' ? 'user' : 'assistant',
        content: msg.content
      }));

      const response = await fetch(`${API_BASE_URL}/chatbot/reviews`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          question: messageToSend,
          chat_history: chatHistory,
          coffee_shop_name: "SmartCafe AI" // You can make this dynamic
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.status === 'success' && data.answer) {
        const botMessage: ChatMessage = {
          id: Date.now().toString() + '-bot',
          type: 'bot',
          content: data.answer,
          timestamp: new Date()
        };
        setChatMessages(prev => [...prev, botMessage]);
      } else {
        throw new Error('Invalid response format');
      }
    } catch (error) {
      console.error('Error with chatbot request:', error);
      const errorMessage: ChatMessage = {
        id: Date.now().toString() + '-error',
        type: 'bot',
        content: 'I apologize, but I encountered an error. Please try asking your question again. I can help with menu suggestions, review analysis, business insights, and much more!',
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoadingChatbot(false);
    }
  };

  // Handle Enter key press
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Helper function to parse suggestions
  const parseSuggestions = (suggestionsText: string) => {
    const lines = suggestionsText.split('\n');
    let positiveFeedback = '';
    let areasForImprovement = '';
    let currentSection = '';

    for (const line of lines) {
      if (line.toLowerCase().includes('positive feedback trends')) {
        currentSection = 'positive';
      } else if (line.toLowerCase().includes('areas for improvement')) {
        currentSection = 'improvement';
      } else if (line.trim() && currentSection === 'positive') {
        positiveFeedback += line + '\n';
      } else if (line.trim() && currentSection === 'improvement') {
        areasForImprovement += line + '\n';
      }
    }

    return {
      positiveFeedback: positiveFeedback.trim() || 'Customers consistently praise your coffee quality and friendly service. Continue emphasizing these strengths in your marketing.',
      areasForImprovement: areasForImprovement.trim() || 'Some customers mention longer wait times during peak hours. Consider implementing a mobile ordering system to reduce wait times.'
    };
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const newFile = {
        name: file.name,
        date: new Date().toISOString().split('T')[0],
        size: `${(file.size / 1024 / 1024).toFixed(1)} MB`
      };
      setUploadedFiles(prev => [newFile, ...prev]);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-warm">
      {/* Header */}
      <header className="bg-white/90 backdrop-blur-sm border-b shadow-warm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Coffee className="h-8 w-8 text-primary" />
              <div>
                <h1 className="text-2xl font-bold text-primary">SmartCafe AI</h1>
                <p className="text-sm text-muted-foreground">Owner Dashboard</p>
              </div>
            </div>
            <Link to="/">
              <Button variant="outline" className="gap-2">
                <ArrowLeft className="h-4 w-4" />
                Exit Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Dashboard Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8 animate-fade-in">
          <h2 className="text-3xl font-bold text-primary mb-2">Welcome back!</h2>
          <p className="text-muted-foreground">Here's what's happening with your café today.</p>
        </div>

        <Tabs defaultValue="orders" className="space-y-6">
          <TabsList className="grid w-full grid-cols-2 h-12 bg-white shadow-warm border">
            <TabsTrigger value="orders" className="gap-2 h-10">
              <BarChart3 className="h-4 w-4" />
              Order Insights
            </TabsTrigger>
            <TabsTrigger value="reviews" className="gap-2 h-10">
              <MessageSquare className="h-4 w-4" />
              Review Insights
            </TabsTrigger>
          </TabsList>

          {/* Order Insights Tab */}
          <TabsContent value="orders" className="space-y-6 animate-fade-in">
            {/* Upload Section */}
            <Card className="shadow-warm border-0">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="h-5 w-5 text-primary" />
                  Upload Order Data
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="border-2 border-dashed border-border rounded-lg p-8 text-center">
                  <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">Upload CSV File</h3>
                  <p className="text-muted-foreground mb-4">
                    Upload your order data to generate insights and AI recommendations
                  </p>
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload">
                    <Button className="cursor-pointer bg-gradient-accent hover:opacity-90">
                      Choose CSV File
                    </Button>
                  </label>
                </div>
              </CardContent>
            </Card>

            {/* Uploaded Files */}
            <Card className="shadow-warm border-0">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-primary" />
                  Uploaded Files
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {uploadedFiles.map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <FileText className="h-5 w-5 text-muted-foreground" />
                        <div>
                          <p className="font-medium">{file.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {file.date} • {file.size}
                          </p>
                        </div>
                      </div>
                      <Button variant="outline" size="sm" className="gap-2">
                        <Download className="h-4 w-4" />
                        Process
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Dashboard Placeholder */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="shadow-warm border-0">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-primary" />
                    Sales Analytics
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-48 bg-muted/30 rounded-lg flex items-center justify-center">
                    <div className="text-center">
                      <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                      <p className="text-muted-foreground">Chart visualization will appear here</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="shadow-warm border-0">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Bot className="h-5 w-5 text-primary" />
                    AI Suggestions
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="p-3 bg-primary/10 rounded-lg">
                      <p className="text-sm font-medium">💡 Peak Hours Insight</p>
                      <p className="text-sm text-muted-foreground mt-1">
                        Your busiest time is 2-4 PM. Consider adding more staff during this period.
                      </p>
                    </div>
                    <div className="p-3 bg-accent/10 rounded-lg">
                      <p className="text-sm font-medium">📊 Menu Optimization</p>
                      <p className="text-sm text-muted-foreground mt-1">
                        Iced coffee sales increase by 40% on warm days. Promote seasonal drinks!
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Chatbot Placeholder */}
            <Card className="shadow-warm border-0">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bot className="h-5 w-5 text-primary" />
                  AI Assistant
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-32 bg-muted/30 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <Bot className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                    <p className="text-muted-foreground">Interactive AI chatbot will be available here</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Review Insights Tab */}
          <TabsContent value="reviews" className="space-y-6 animate-fade-in">
            {/* Review Analytics */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="shadow-warm border-0">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-primary" />
                    Sentiment Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-48 flex items-center justify-center">
                    {loadingSentiment ? (
                      <div className="flex flex-col items-center justify-center w-full h-full animate-pulse">
                        <div className="w-24 h-24 rounded-full bg-blue-100 mb-4"></div>
                        <div className="h-4 w-36 bg-gray-100 rounded-full mb-2"></div>
                        <div className="h-3 w-20 bg-gray-100 rounded-full"></div>
                      </div>
                    ) : (
                      <div className="flex items-center justify-between w-full px-4">
                        {/* Left side - Doughnut Chart */}
                        <div className="relative w-32 h-32 flex-shrink-0">
                          <Doughnut data={doughnutData} options={doughnutOptions} />
                        </div>
                        
                        {/* Right side - Total Reviews and Legend */}
                        <div className="flex flex-col items-center ml-6">
                          {/* Total Reviews Display */}
                          <div className="text-center mb-4">
                            <span className="text-3xl font-bold text-primary block">
                              {sentimentData.positive + sentimentData.neutral + sentimentData.negative}
                            </span>
                            <span className="text-sm text-muted-foreground">Total Reviews</span>
                          </div>
                          
                          {/* Color-coded Legend */}
                          <div className="space-y-2">
                            <div className="flex items-center gap-3">
                              <span className="inline-block w-3 h-3 rounded-full" style={{backgroundColor: 'rgba(186,230,253,0.75)'}}></span>
                              <span className="text-sm text-blue-700 font-medium">Positive</span>
                              <span className="text-sm text-muted-foreground ml-2">({sentimentData.positive})</span>
                            </div>
                            <div className="flex items-center gap-3">
                              <span className="inline-block w-3 h-3 rounded-full" style={{backgroundColor: 'rgba(253,230,138,0.75)'}}></span>
                              <span className="text-sm text-yellow-700 font-medium">Neutral</span>
                              <span className="text-sm text-muted-foreground ml-2">({sentimentData.neutral})</span>
                            </div>
                            <div className="flex items-center gap-3">
                              <span className="inline-block w-3 h-3 rounded-full" style={{backgroundColor: 'rgba(254,202,202,0.75)'}}></span>
                              <span className="text-sm text-red-700 font-medium">Negative</span>
                              <span className="text-sm text-muted-foreground ml-2">({sentimentData.negative})</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              <Card className="shadow-warm border-0">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Star className="h-5 w-5 text-primary" />
                    Keyword Trends
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {loadingKeywords ? (
                    <div className="h-48 flex items-center justify-center animate-pulse">
                      <div className="space-y-2 w-full">
                        <div className="h-4 w-48 bg-gray-100 rounded" />
                        <div className="h-4 w-40 bg-gray-100 rounded" />
                        <div className="h-4 w-56 bg-gray-100 rounded" />
                        <div className="h-4 w-44 bg-gray-100 rounded" />
                        <div className="h-4 w-52 bg-gray-100 rounded" />
                      </div>
                    </div>
                  ) : keywords.length === 0 ? (
                    <div className="h-48 flex items-center justify-center">
                      <p className="text-muted-foreground text-sm">
                        No keyword data available yet.
                      </p>
                    </div>
                  ) : (
                    <div className="relative h-48 w-full">
                      <Bar data={keywordBarData} options={keywordBarOptions} />
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* UPDATED: Reviews Table with Real Backend Data */}
            <Card className="shadow-warm border-0">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <MessageSquare className="h-5 w-5 text-primary" />
                    Recent Reviews
                  </div>
                  <div className="flex items-center gap-2">
                    <Filter className="h-4 w-4 text-muted-foreground" />
                    <select
                      value={ratingFilter || ''}
                      onChange={(e) => setRatingFilter(e.target.value ? parseInt(e.target.value) : null)}
                      className="text-sm border border-border rounded-md px-3 py-1.5 bg-white focus:outline-none focus:ring-2 focus:ring-primary/20"
                    >
                      <option value="">All Ratings</option>
                      <option value="5">5 Stars</option>
                      <option value="4">4 Stars</option>
                      <option value="3">3 Stars</option>
                      <option value="2">2 Stars</option>
                      <option value="1">1 Star</option>
                    </select>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {loadingReviews ? (
                  <div className="space-y-4">
                    {[...Array(3)].map((_, index) => (
                      <div key={index} className="border border-border rounded-lg p-4 animate-pulse">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <div className="flex gap-1">
                              {[...Array(5)].map((_, i) => (
                                <div key={i} className="h-4 w-4 bg-muted rounded-full" />
                              ))}
                            </div>
                            <div className="h-5 w-16 bg-muted rounded" />
                          </div>
                          <div className="h-4 w-20 bg-muted rounded" />
                        </div>
                        <div className="h-4 bg-muted rounded w-3/4" />
                      </div>
                    ))}
                  </div>
                ) : getDisplayedReviews().length > 0 ? (
                  <div className="space-y-4">
                    {getDisplayedReviews().map((review, index) => (
                      <div key={index} className="border border-border rounded-lg p-4">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <div className="flex">
                              {[...Array(5)].map((_, i) => (
                                <Star
                                  key={i}
                                  className={`h-4 w-4 ${
                                    i < review.rating
                                      ? "text-accent fill-accent"
                                      : "text-muted"
                                  }`}
                                />
                              ))}
                            </div>
                            <Badge 
                              variant={getSentiment(review.rating) === "positive" ? "default" : getSentiment(review.rating) === "negative" ? "destructive" : "secondary"}
                              className="text-xs"
                            >
                              {getSentiment(review.rating)}
                            </Badge>
                          </div>
                          <span className="text-sm text-muted-foreground">{formatDate(review.timestamp)}</span>
                        </div>
                        <p className="text-sm">{review.review_text}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    {ratingFilter ? `No reviews with ${ratingFilter} star rating found.` : 'No reviews available.'}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* AI Suggestions for Reviews - UPDATED WITH BACKEND DATA */}
            <Card className="shadow-warm border-0">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bot className="h-5 w-5 text-primary" />
                  AI-Generated Suggestions
                </CardTitle>
              </CardHeader>
              <CardContent>
                {loadingSuggestions ? (
                  <div className="space-y-3">
                    <div className="p-4 bg-green-50 border border-green-200 rounded-lg animate-pulse">
                      <div className="h-4 bg-green-200 rounded w-3/4 mb-2"></div>
                      <div className="h-3 bg-green-200 rounded w-full mb-1"></div>
                      <div className="h-3 bg-green-200 rounded w-5/6"></div>
                    </div>
                    <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg animate-pulse">
                      <div className="h-4 bg-amber-200 rounded w-2/3 mb-2"></div>
                      <div className="h-3 bg-amber-200 rounded w-full mb-1"></div>
                      <div className="h-3 bg-amber-200 rounded w-4/5"></div>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                      <h4 className="font-semibold text-green-800 mb-2">Positive Feedback Trends</h4>
                      <div className="text-sm text-green-700 whitespace-pre-line">
                        {parseSuggestions(suggestions).positiveFeedback}
                      </div>
                    </div>
                    <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
                      <h4 className="font-semibold text-amber-800 mb-2">Areas for Improvement</h4>
                      <div className="text-sm text-amber-700 whitespace-pre-line">
                        {parseSuggestions(suggestions).areasForImprovement}
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* ENHANCED: Conversational Chat Interface */}
            <Card className="shadow-warm border-0">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bot className="h-5 w-5 text-primary" />
                  AI Business Assistant
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Chat History */}
                  <div className="h-96 overflow-y-auto border border-border rounded-lg p-4 bg-muted/10">
                    {chatMessages.length === 0 ? (
                      <div className="flex items-center justify-center h-full text-muted-foreground">
                        <div className="text-center">
                          <Bot className="h-8 w-8 mx-auto mb-2" />
                          <p className="text-sm font-semibold mb-2">Your AI Business Consultant is ready! 🚀</p>
                          <div className="text-xs space-y-1">
                            <p>• "What are the worst reviews and how can I improve?"</p>
                            <p>• "Suggest trending drinks to add to my menu"</p>
                            <p>• "What drinks should I stop selling?"</p>
                            <p>• "How can I reduce wait times during peak hours?"</p>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {chatMessages.map((message) => (
                          <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[85%] rounded-lg p-3 ${
                              message.type === 'user' 
                                ? 'bg-primary text-primary-foreground ml-4' 
                                : 'bg-white border border-border mr-4'
                            }`}>
                              <div className="flex items-start gap-2">
                                {message.type === 'bot' && <Bot className="h-4 w-4 mt-0.5 flex-shrink-0 text-primary" />}
                                {message.type === 'user' && <User className="h-4 w-4 mt-0.5 flex-shrink-0" />}
                                <div className="text-sm whitespace-pre-line leading-relaxed">{message.content}</div>
                              </div>
                              <div className={`text-xs mt-2 ${message.type === 'user' ? 'text-primary-foreground/70' : 'text-muted-foreground'}`}>
                                {message.timestamp.toLocaleTimeString()}
                              </div>
                            </div>
                          </div>
                        ))}
                        {loadingChatbot && (
                          <div className="flex justify-start">
                            <div className="bg-white border border-border rounded-lg p-3 mr-4">
                              <div className="flex items-center gap-2">
                                <Bot className="h-4 w-4 text-primary" />
                                <div className="flex space-x-1">
                                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
                                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                                </div>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Input Section */}
                  <div className="flex gap-2">
                    <textarea
                      value={currentMessage}
                      onChange={(e) => setCurrentMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Ask me anything about your business, reviews, menu, or just say 'simplify that' or 'tell me more'..."
                      className="flex-1 min-h-[80px] p-3 text-sm border border-border rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-primary/20 resize-none"
                      disabled={loadingChatbot}
                    />
                    <Button 
                      onClick={handleSendMessage}
                      disabled={loadingChatbot || !currentMessage.trim()}
                      className="bg-gradient-accent hover:opacity-90 px-6 self-end"
                    >
                      {loadingChatbot ? (
                        <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                      ) : (
                        <Send className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default OwnerDashboard;
