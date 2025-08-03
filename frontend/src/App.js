import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, MapPin, Calendar, Building2, Briefcase, ExternalLink, Filter, Loader, Users, TrendingUp } from 'lucide-react';
import { format, parseISO } from 'date-fns';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedUniversity, setSelectedUniversity] = useState('');
  const [stats, setStats] = useState(null);
  const [pagination, setPagination] = useState({});
  const [currentPage, setCurrentPage] = useState(1);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [showJobModal, setShowJobModal] = useState(false);

  const categories = ['Research', 'Teaching', 'PhD', 'Fellowship', 'Technical', 'Administrative', 'Internship'];

  useEffect(() => {
    fetchJobs();
    fetchStats();
  }, [searchTerm, selectedCategory, selectedUniversity, currentPage]);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      
      if (searchTerm) params.append('search', searchTerm);
      if (selectedCategory) params.append('category', selectedCategory);
      if (selectedUniversity) params.append('university', selectedUniversity);
      params.append('page', currentPage.toString());
      params.append('limit', '10');
      
      const response = await axios.get(`${API_BASE_URL}/api/jobs?${params.toString()}`);
      setJobs(response.data.jobs || []);
      setPagination(response.data.pagination || {});
      setError(null);
    } catch (err) {
      console.error('Error fetching jobs:', err);
      setError('Failed to fetch jobs. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/stats`);
      setStats(response.data);
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  const formatDate = (dateString) => {
    try {
      return format(parseISO(dateString), 'MMM dd, yyyy');
    } catch (err) {
      return dateString;
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      'Research': 'bg-blue-100 text-blue-800 border-blue-200',
      'Teaching': 'bg-green-100 text-green-800 border-green-200',
      'PhD': 'bg-purple-100 text-purple-800 border-purple-200',
      'Fellowship': 'bg-orange-100 text-orange-800 border-orange-200',
      'Technical': 'bg-gray-100 text-gray-800 border-gray-200',
      'Administrative': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'Internship': 'bg-pink-100 text-pink-800 border-pink-200',
      'General': 'bg-slate-100 text-slate-800 border-slate-200'
    };
    return colors[category] || colors['General'];
  };

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= (pagination.total_pages || 1)) {
      setCurrentPage(newPage);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const openJobModal = (job) => {
    setSelectedJob(job);
    setShowJobModal(true);
  };

  const closeJobModal = () => {
    setSelectedJob(null);
    setShowJobModal(false);
  };

  const resetFilters = () => {
    setSearchTerm('');
    setSelectedCategory('');
    setSelectedUniversity('');
    setCurrentPage(1);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Job Details Modal */}
      {showJobModal && selectedJob && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-card rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-border">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h2 className="text-2xl font-bold text-foreground mb-2">{selectedJob.title}</h2>
                  <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                    <div className="flex items-center">
                      <Building2 className="w-4 h-4 mr-1" />
                      <span>{selectedJob.university}</span>
                    </div>
                    <div className="flex items-center">
                      <MapPin className="w-4 h-4 mr-1" />
                      <span>{selectedJob.location}</span>
                    </div>
                    {selectedJob.deadline && (
                      <div className="flex items-center">
                        <Calendar className="w-4 h-4 mr-1" />
                        <span>Deadline: {formatDate(selectedJob.deadline)}</span>
                      </div>
                    )}
                  </div>
                </div>
                <button
                  onClick={closeJobModal}
                  className="ml-4 p-2 hover:bg-accent rounded-lg transition-colors"
                >
                  ✕
                </button>
              </div>
            </div>
            <div className="p-6">
              <div className="mb-4">
                <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getCategoryColor(selectedJob.category)}`}>
                  {selectedJob.category}
                </span>
              </div>
              
              {selectedJob.summary && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-foreground mb-3">Summary</h3>
                  <p className="text-foreground leading-relaxed">{selectedJob.summary}</p>
                </div>
              )}
              
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-foreground mb-3">Full Description</h3>
                <div className="prose prose-sm max-w-none text-foreground">
                  <p className="leading-relaxed whitespace-pre-line">{selectedJob.description}</p>
                </div>
              </div>
              
              <div className="flex justify-between items-center pt-4 border-t border-border">
                <div className="text-sm text-muted-foreground">
                  Posted: {formatDate(selectedJob.date_added)}
                </div>
                <a
                  href={selectedJob.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
                >
                  Apply Now
                  <ExternalLink className="w-4 h-4 ml-2" />
                </a>
              </div>
            </div>
          </div>
        </div>
      )}
      {/* Header */}
      <header className="bg-card border-b border-border shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-foreground font-serif">London Academic Jobs</h1>
              <p className="text-muted-foreground mt-1">Discover your next academic opportunity in London</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center text-sm text-muted-foreground">
                <MapPin className="w-4 h-4 mr-1" />
                <span>London, UK</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Stats Bar */}
      {stats && (
        <div className="bg-muted/50 border-b border-border">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center">
                <Briefcase className="w-5 h-5 text-primary mr-2" />
                <span className="text-sm font-medium">{stats.total_jobs} Total Jobs</span>
              </div>
              <div className="flex items-center">
                <MapPin className="w-5 h-5 text-primary mr-2" />
                <span className="text-sm font-medium">{stats.london_jobs} London Jobs</span>
              </div>
              <div className="flex items-center">
                <Building2 className="w-5 h-5 text-primary mr-2" />
                <span className="text-sm font-medium">{stats.top_universities?.length || 0} Universities</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Search and Filters */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-card rounded-lg shadow-sm border border-border p-6">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-5 h-5" />
              <input
                type="text"
                placeholder="Search jobs, keywords, or universities..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-input rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>

            {/* Category Filter */}
            <div className="lg:w-48">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full py-3 px-4 border border-input rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="">All Categories</option>
                {categories.map(category => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
            </div>

            {/* University Filter */}
            <div className="lg:w-64">
              <select
                value={selectedUniversity}
                onChange={(e) => setSelectedUniversity(e.target.value)}
                className="w-full py-3 px-4 border border-input rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="">All Universities</option>
                {stats?.top_universities?.map(uni => (
                  <option key={uni.university} value={uni.university}>
                    {uni.university} ({uni.count})
                  </option>
                ))}
              </select>
            </div>

            {/* Filter Toggle Button */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="lg:hidden flex items-center justify-center px-4 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
            >
              <Filter className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar - Categories */}
          <div className="lg:col-span-1">
            <div className="bg-card rounded-lg shadow-sm border border-border p-6 sticky top-6">
              <h3 className="font-semibold text-foreground mb-4">Categories</h3>
              <div className="space-y-2">
                {stats?.top_categories?.map(cat => (
                  <button
                    key={cat.category}
                    onClick={() => setSelectedCategory(selectedCategory === cat.category ? '' : cat.category)}
                    className={`w-full text-left px-3 py-2 rounded-md transition-colors ${
                      selectedCategory === cat.category
                        ? 'bg-primary text-primary-foreground'
                        : 'hover:bg-accent text-foreground'
                    }`}
                  >
                    <div className="flex justify-between items-center">
                      <span className="text-sm">{cat.category}</span>
                      <span className="text-xs opacity-75">{cat.count}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Job Listings */}
          <div className="lg:col-span-3">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader className="w-8 h-8 animate-spin text-primary" />
                <span className="ml-3 text-muted-foreground">Loading jobs...</span>
              </div>
            ) : error ? (
              <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-6 text-center">
                <p className="text-destructive">{error}</p>
                <button
                  onClick={fetchJobs}
                  className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
                >
                  Try Again
                </button>
              </div>
            ) : jobs.length === 0 ? (
              <div className="bg-muted/50 rounded-lg p-12 text-center">
                <Briefcase className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium text-foreground mb-2">No jobs found</h3>
                <p className="text-muted-foreground">Try adjusting your search criteria or filters.</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold text-foreground">
                    {pagination.total_count || 0} Job{(pagination.total_count || 0) !== 1 ? 's' : ''} Found
                    {searchTerm || selectedCategory || selectedUniversity ? (
                      <button
                        onClick={resetFilters}
                        className="ml-4 text-sm text-primary hover:text-primary/80 underline"
                      >
                        Clear Filters
                      </button>
                    ) : null}
                  </h2>
                  <div className="text-sm text-muted-foreground">
                    Page {pagination.current_page || 1} of {pagination.total_pages || 1}
                  </div>
                </div>

                {jobs.map((job) => (
                  <div key={job.id} className="bg-card rounded-lg shadow-sm border border-border p-6 hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-foreground mb-2">{job.title}</h3>
                        <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground mb-3">
                          <div className="flex items-center">
                            <Building2 className="w-4 h-4 mr-1" />
                            <span>{job.university}</span>
                          </div>
                          <div className="flex items-center">
                            <MapPin className="w-4 h-4 mr-1" />
                            <span>{job.location}</span>
                          </div>
                          {job.deadline && (
                            <div className="flex items-center">
                              <Calendar className="w-4 h-4 mr-1" />
                              <span>Deadline: {formatDate(job.deadline)}</span>
                            </div>
                          )}
                        </div>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getCategoryColor(job.category)}`}>
                        {job.category}
                      </span>
                    </div>

                    <div className="mb-4">
                      {job.summary ? (
                        <p className="text-foreground leading-relaxed">{job.summary}</p>
                      ) : (
                        <p className="text-foreground leading-relaxed">
                          {job.description.length > 300 
                            ? `${job.description.substring(0, 300)}...` 
                            : job.description
                          }
                        </p>
                      )}
                    </div>

                    <div className="flex justify-between items-center">
                      <div className="text-sm text-muted-foreground">
                        Posted: {formatDate(job.date_added)}
                      </div>
                      <div className="flex gap-3">
                        <button
                          onClick={() => openJobModal(job)}
                          className="inline-flex items-center px-4 py-2 bg-secondary text-secondary-foreground rounded-lg hover:bg-secondary/80 transition-colors"
                        >
                          View Full Details
                        </button>
                        <a
                          href={job.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
                        >
                          Apply Now
                          <ExternalLink className="w-4 h-4 ml-2" />
                        </a>
                      </div>
                    </div>
                  </div>
                ))}

                {/* Pagination */}
                {pagination.total_pages > 1 && (
                  <div className="flex items-center justify-center space-x-2 mt-8">
                    <button
                      onClick={() => handlePageChange(currentPage - 1)}
                      disabled={!pagination.has_prev}
                      className="px-4 py-2 text-sm font-medium text-foreground bg-card border border-border rounded-lg hover:bg-accent disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Previous
                    </button>
                    
                    {/* Page numbers */}
                    {Array.from({ length: Math.min(5, pagination.total_pages) }, (_, i) => {
                      const pageNum = Math.max(1, Math.min(
                        pagination.current_page - 2 + i,
                        pagination.total_pages - 4 + i
                      ));
                      
                      if (pageNum > pagination.total_pages) return null;
                      
                      return (
                        <button
                          key={pageNum}
                          onClick={() => handlePageChange(pageNum)}
                          className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                            pageNum === pagination.current_page
                              ? 'bg-primary text-primary-foreground'
                              : 'text-foreground bg-card border border-border hover:bg-accent'
                          }`}
                        >
                          {pageNum}
                        </button>
                      );
                    })}
                    
                    <button
                      onClick={() => handlePageChange(currentPage + 1)}
                      disabled={!pagination.has_next}
                      className="px-4 py-2 text-sm font-medium text-foreground bg-card border border-border rounded-lg hover:bg-accent disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Next
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-card border-t border-border mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <p className="text-sm text-muted-foreground">
              © 2024 London Academic Jobs. Connecting talent with opportunity.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;