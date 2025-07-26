import axios from 'axios';
import toast from 'react-hot-toast';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.NODE_ENV === 'production' 
    ? 'https://your-api-domain.com' 
    : 'http://localhost:8000',
  timeout: 120000, // 2 minutes for analysis
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || 
                   error.message || 
                   'Something went wrong';
    
    // Show user-friendly error messages
    if (error.response?.status === 400) {
      toast.error(`Validation Error: ${message}`);
    } else if (error.response?.status === 500) {
      toast.error('Server error. Please try again later.');
    } else if (error.code === 'ECONNABORTED') {
      toast.error('Request timed out. Please try again.');
    } else {
      toast.error(message);
    }
    
    return Promise.reject(error);
  }
);

const apiService = {
  // Health check
  async checkHealth() {
    return api.get('/health');
  },

  // Get zodiac signs
  async getZodiacSigns() {
    return api.get('/zodiac-signs');
  },

  // Main analysis endpoint
  async analyzeTeam(profiles) {
    const loadingToast = toast.loading('🌟 Analyzing cosmic compatibility...');
    
    try {
      const response = await api.post('/analyze-team', { profiles });
      
      toast.dismiss(loadingToast);
      toast.success('✨ Cosmic analysis complete!');
      
      return response;
    } catch (error) {
      toast.dismiss(loadingToast);
      throw error;
    }
  },

  // Get existing report
  async getReport(reportId) {
    return api.get(`/report/${reportId}`);
  },

  // Get report summary for sharing
  async getReportSummary(reportId) {
    return api.get(`/report/${reportId}/summary`);
  },

  // Validate profile input
  async validateProfile(linkedinUrl, zodiacSign) {
    return api.post('/validate-profile', null, {
      params: { linkedin_url: linkedinUrl, zodiac_sign: zodiacSign }
    });
  },

  // Get compatibility between two signs
  async getSignCompatibility(sign1, sign2) {
    return api.get(`/compatibility/${sign1}/${sign2}`);
  },

  // Delete report
  async deleteReport(reportId) {
    return api.delete(`/report/${reportId}`);
  },

  // Utility function to extract LinkedIn username from URL
  extractLinkedInUsername(url) {
    const match = url.match(/\/in\/([a-zA-Z0-9\-]+)/);
    return match ? match[1] : null;
  },

  // Validate LinkedIn URL format
  validateLinkedInUrl(url) {
    const patterns = [
      /^https?:\/\/(www\.)?linkedin\.com\/in\/[a-zA-Z0-9\-]+\/?$/,
      /^https?:\/\/(www\.)?linkedin\.com\/pub\/[a-zA-Z0-9\-\/]+\/?$/
    ];
    
    return patterns.some(pattern => pattern.test(url));
  },

  // Format URL for consistency
  formatLinkedInUrl(url) {
    // Remove trailing slash
    url = url.replace(/\/$/, '');
    
    // Ensure https
    if (!url.startsWith('http')) {
      url = 'https://' + url;
    }
    
    // Ensure www.linkedin.com format
    url = url.replace(/linkedin\.com/, 'www.linkedin.com');
    
    return url;
  },

  // Create shareable link
  createShareableLink(reportId) {
    const baseUrl = window.location.origin;
    return `${baseUrl}/report/${reportId}`;
  },

  // Generate social sharing URLs
  generateSocialShareUrls(reportData) {
    const shareUrl = this.createShareableLink(reportData.report_id);
    const social = reportData.social_sharing;
    
    const encodedTitle = encodeURIComponent(social.title);
    const encodedDescription = encodeURIComponent(social.description);
    const encodedUrl = encodeURIComponent(shareUrl);
    const encodedHashtags = encodeURIComponent(social.hashtags);
    
    return {
      twitter: `https://twitter.com/intent/tweet?text=${encodedTitle}&url=${encodedUrl}&hashtags=${encodedHashtags.replace('#', '')}`,
      linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`,
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`,
      email: `mailto:?subject=${encodedTitle}&body=${encodedDescription}%0A%0A${encodedUrl}`,
      copy: shareUrl
    };
  }
};

export default apiService;