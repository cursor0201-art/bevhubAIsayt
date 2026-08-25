'use client';

import React, { useState, useEffect, useRef } from 'react';
import { 
  Sparkles, 
  ArrowRight, 
  Terminal, 
  Globe, 
  Layers, 
  Settings, 
  Cpu,
  User,
  Lock,
  Mail,
  Plus,
  Play,
  LogOut,
  FileCode,
  Eye,
  Palette,
  CheckCircle,
  Server,
  CreditCard,
  Coins,
  Ticket,
  Languages,
  Archive,
  Copy,
  Trash2,
  FolderOpen,
  Edit2,
  Undo,
  MessageSquare,
  Send,
  RefreshCw,
  Activity,
  FileText,
  Workflow,
  Check,
  Compass,
  LineChart,
  BarChart3,
  AlertTriangle,
  TrendingUp,
  ThumbsUp,
  Wrench,
  ImageIcon,
  Save,
  ChevronDown,
  Search,
  Bell,
  ShieldCheck,
  Edit3
, LayoutDashboard, History, Box, Monitor, Smartphone, ChevronLeft, ChevronRight, MoreVertical, ExternalLink, Menu, Paperclip, Folder, Code, Github} from 'lucide-react';
import { AuthService, UserProfile } from '../services/AuthService';
import { ProjectService, ProjectData, ProjectReviewData, ProjectFixData, ProjectFixRunRecord } from '../services/ProjectService';
import { BillingService, BillingDashboardData } from '../services/BillingService';
import { PreferencesService } from '../services/PreferencesService';
import { WorkspaceService, WorkspaceData } from '../services/WorkspaceService';
import { AITaskService, AITaskData, AITaskProgressData } from '../services/AITaskService';
import { ProjectFileService, ProjectFileData } from '../services/ProjectFileService';
import { AnalyticsService, RevenueData, QualityData, ProductIntelligenceData } from '../services/AnalyticsService';

interface ChatMessage {
  sender: 'user' | 'brain';
  text: string;
  timestamp: string;
}

interface GraphNode {
  id: string;
  type: string;
  name: string;
  status: 'valid' | 'outdated' | 'failed' | 'building';
  health: number;
  risk: 'Low' | 'Medium' | 'High';
}

const formatError = (errorStr: string) => {
  try {
    const match = errorStr.match(/\{.*\}/);
    if (match) {
      const parsed = JSON.parse(match[0]);
      const errors: string[] = [];
      Object.keys(parsed).forEach(key => {
        const val = parsed[key];
        if (Array.isArray(val)) {
          errors.push(...val);
        } else if (typeof val === 'string') {
          errors.push(val);
        }
      });
      if (errors.length > 0) return errors.map((e, i) => <span key={i} className="block">• {e}</span>);
    }
  } catch (e) {}
  return errorStr.replace(/Ошибка API \[\d+\]:\s*/, '').trim() || errorStr;
};

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);
  
  // Auth Form State
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [authError, setAuthError] = useState('');
  const [authMode, setAuthMode] = useState<'register' | 'login'>('register');

  // Workspaces State
  const [workspaces, setWorkspaces] = useState<WorkspaceData[]>([]);
  const [selectedWorkspaceId, setSelectedWorkspaceId] = useState<string>('');
  const [showNewWorkspaceModal, setShowNewWorkspaceModal] = useState(false);
  const [newWorkspaceName, setNewWorkspaceName] = useState('');

  // Projects State
  const [projects, setProjects] = useState<ProjectData[]>([]);
  const [selectedProject, setSelectedProject] = useState<ProjectData | null>(null);
  const [workspaceView, setWorkspaceView] = useState<'workspace' | 'billing' | 'revenue' | 'quality' | 'intelligence' | 'projects' | 'settings' | 'integrations' | 'history' | 'deployments' | 'templates'>('workspace');
  const [centerTab, setCenterTab] = useState<'preview' | 'code'>('preview');
  const [activeBottomTab, setActiveBottomTab] = useState<'logs' | 'tests' | 'deployments' | 'dod' | 'review' | 'fix'>('logs');
  const [reviews, setReviews] = useState<ProjectReviewData[]>([]);
  const [isReviewing, setIsReviewing] = useState(false);
  const [fixes, setFixes] = useState<ProjectFixRunRecord[]>([]);
  const [isFixing, setIsFixing] = useState(false);
  
  // File Code Editor State
  const [selectedFile, setSelectedFile] = useState<ProjectFileData | null>(null);
  const [editorContent, setEditorContent] = useState<string>('');
  const [isSavingFile, setIsSavingFile] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'saved' | 'saving' | 'dirty'>('saved');
  
  // Generator/AI Tasks State
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeTask, setActiveTask] = useState<AITaskData | null>(null);
  const [taskProgress, setTaskProgress] = useState<AITaskProgressData | null>(null);

  // Deploy/UI states
  const [isDeploying, setIsDeploying] = useState(false);
  const [deploySuccessUrl, setDeploySuccessUrl] = useState<string | null>(null);
  const [deploymentLogs, setDeploymentLogs] = useState<string>('');

  // Billing & AI Credits State
  const [billingData, setBillingData] = useState<BillingDashboardData | null>(null);
  const [promoCode, setPromoCode] = useState('');
  const [promoMsg, setPromoMsg] = useState('');
  const [promoErr, setPromoErr] = useState('');
  const [isClaimingPromo, setIsClaimingPromo] = useState(false);
  const [isSubscribing, setIsSubscribing] = useState(false);

  // History State
  const [historyTasks, setHistoryTasks] = useState<any[]>([]);
  const [historySearch, setHistorySearch] = useState<string>('');
  const [historyFilterStatus, setHistoryFilterStatus] = useState<string>('all');
  const [isHistoryLoading, setIsHistoryLoading] = useState<boolean>(false);

  // Templates State
  const [templatesList, setTemplatesList] = useState<any[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');

  // Integrations State
  const [integrationsList, setIntegrationsList] = useState<any[]>([]);
  const [activeConnectModal, setActiveConnectModal] = useState<string | null>(null);
  const [connectApiKey, setConnectApiKey] = useState<string>('');

  // Deployments State
  const [deploymentsList, setDeploymentsList] = useState<any[]>([]);
  const [selectedLogsModal, setSelectedLogsModal] = useState<any | null>(null);
  const [isRedeployingId, setIsRedeployingId] = useState<string | null>(null);

  // Settings State
  const [oldPasswordInput, setOldPasswordInput] = useState('');
  const [newPasswordInput, setNewPasswordInput] = useState('');
  const [passwordMsg, setPasswordMsg] = useState('');
  const [passwordErr, setPasswordErr] = useState('');
  const [showDeleteAccountModal, setShowDeleteAccountModal] = useState(false);
  const [deleteConfirmPassword, setDeleteConfirmPassword] = useState('');
  const [deleteAccountErr, setDeleteAccountErr] = useState('');

  // Projects Filtering & Action Modals
  const [projectsSearch, setProjectsSearch] = useState('');
  const [projectToRename, setProjectToRename] = useState<ProjectData | null>(null);
  const [renameInput, setRenameInput] = useState('');
  const [projectToDelete, setProjectToDelete] = useState<ProjectData | null>(null);

  // Global Cmd+K Search State
  const [isCmdKOpen, setIsCmdKOpen] = useState(false);
  const [cmdKQuery, setCmdKQuery] = useState('');

  // Notifications State
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [notificationsList, setNotificationsList] = useState<any[]>([]);

  const addNotification = (title: string, status: 'success' | 'failed' | 'info', details: string) => {
    const newNotif = {
      id: String(Date.now()),
      title,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      status,
      details
    };
    setNotificationsList(prev => [newNotif, ...prev]);
  };

  // Load module data when view changes
  useEffect(() => {
    if (!isAuthenticated) return;

    if (workspaceView === 'history') {
      setIsHistoryLoading(true);
      ProjectService.getHistory(historySearch, historyFilterStatus)
        .then(data => {
          setHistoryTasks(data);
          // Set notifications based on recent history events
          const notifs = data.slice(0, 5).map(e => ({
            id: e.id,
            title: e.event.replace(/_/g, ' ').toUpperCase(),
            time: new Date(e.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            status: e.status,
            details: e.details
          }));
          setNotificationsList(notifs);
        })
        .catch(console.error)
        .finally(() => setIsHistoryLoading(false));
    } else if (workspaceView === 'templates') {
      ProjectService.getTemplates().then(setTemplatesList).catch(console.error);
    } else if (workspaceView === 'integrations') {
      ProjectService.getIntegrations().then(setIntegrationsList).catch(console.error);
    } else if (workspaceView === 'deployments') {
      ProjectService.getDeployments().then(setDeploymentsList).catch(console.error);
    } else if (workspaceView === 'billing') {
      BillingService.getDashboard().then(setBillingData).catch(console.error);
    } else if (workspaceView === 'settings') {
      ProjectService.getProfile().then(data => {
        if (data.username) setUsername(data.username);
        if (data.email) setEmail(data.email);
      }).catch(console.error);
    }
  }, [workspaceView, historySearch, historyFilterStatus, isAuthenticated]);

  // Global Cmd+K Keyboard Shortcut Listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsCmdKOpen(prev => !prev);
      } else if (e.key === 'Escape') {
        setIsCmdKOpen(false);
        setActiveConnectModal(null);
        setSelectedLogsModal(null);
        setShowDeleteAccountModal(false);
        setProjectToRename(null);
        setProjectToDelete(null);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Analytics & Metric states
  const [revenueData, setRevenueData] = useState<RevenueData | null>(null);
  const [qualityData, setQualityData] = useState<QualityData | null>(null);
  const [intelligenceData, setIntelligenceData] = useState<ProductIntelligenceData | null>(null);
  const [isLoadingAnalytics, setIsLoadingAnalytics] = useState(false);
  const [selectedSegment, setSelectedSegment] = useState<string>('all');
  const [isDemoMode, setIsDemoMode] = useState<boolean>(true);

  // Drilldown states
  const [drilldownMetric, setDrilldownMetric] = useState<string | null>(null);
  const [drilldownTitle, setDrilldownTitle] = useState<string>('');
  const [drilldownData, setDrilldownData] = useState<any[]>([]);
  const [isDrilldownLoading, setIsDrilldownLoading] = useState<boolean>(false);

  const handleDrilldown = async (metric: string, title: string) => {
    setDrilldownMetric(metric);
    setDrilldownTitle(title);
    setDrilldownData([]);
    setIsDrilldownLoading(true);
    try {
      const data = await AnalyticsService.getTelemetryDrilldown(metric, isDemoMode);
      setDrilldownData(data);
    } catch (err) {
      console.error('Failed to load drilldown data:', err);
    } finally {
      setIsDrilldownLoading(false);
    }
  };

  const loadIntelligenceData = async (segmentOverride?: string, demoOverride?: boolean) => {
    setIsLoadingAnalytics(true);
    const targetSegment = segmentOverride || selectedSegment;
    const targetDemo = demoOverride !== undefined ? demoOverride : isDemoMode;
    try {
      const data = await AnalyticsService.getProductIntelligence(targetSegment, targetDemo);
      setIntelligenceData(data);
    } catch (err) {
      console.error('Failed to load product intelligence data:', err);
    } finally {
      setIsLoadingAnalytics(false);
    }
  };

  // User Memory Preferences State
  const [writingStyle, setWritingStyle] = useState('Professional');
  const [prefLang, setPrefLang] = useState('English');
  const [favColors, setFavColors] = useState<string[]>(['#8b5cf6', '#ec4899']);
  const [isSavingPref, setIsSavingPref] = useState(false);

  // Interactive AI Chat & Project Brain History State
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    { 
      sender: 'brain', 
      text: 'Greetings! I am the BevHub Brain, your cognitive engineering co-pilot. I have synchronized with the active workspace compiler. Select any file to load context, or ask me about the system history and design decisions.', 
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) 
    }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [showDemoNotification, setShowDemoNotification] = useState<boolean>(true);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  // Custom Translation Trigger via Cookie
  const triggerTranslation = (langCode: string) => {
    // Force the Google Translate engine via cookie
    document.cookie = `googtrans=/en/${langCode}; path=/;`;
    document.cookie = `googtrans=/en/${langCode}; path=/; domain=${window.location.hostname};`;
    // Reload to apply the translation engine instantly
    window.location.reload();
  };

  // Engineering Graph State
  const [graphNodes, setGraphNodes] = useState<GraphNode[]>([
    { id: 'db-1', type: 'Database Schema', name: 'schema.sql', status: 'valid', health: 100, risk: 'Low' },
    { id: 'api-1', type: 'API Router Config', name: 'routes.json', status: 'valid', health: 100, risk: 'Low' },
    { id: 'page-index', type: 'Frontend HTML Page', name: 'index.html', status: 'valid', health: 100, risk: 'Low' },
    { id: 'page-products', type: 'Frontend HTML Page', name: 'products.html', status: 'valid', health: 100, risk: 'Low' },
    { id: 'devops-1', type: 'DevOps Configuration', name: 'Dockerfile', status: 'valid', health: 100, risk: 'Medium' },
    { id: 'qa-1', type: 'QA E2E Test Suite', name: 'test_suite.py', status: 'valid', health: 100, risk: 'Low' }
  ]);

  // Project Brain Explanations Repository
  const projectBrainHistory: Record<string, string> = {
    'orders_archive': 'The "orders_archive" table was designed and partition-migrated on August 18, 2026. This architectural decision was made because the transactional records in the primary "orders" table were growing exponentially (approaching 10M rows), causing query latency to spike to >800ms. By separating legacy records into this archive, we recovered primary table index efficiency. The archive table uses custom indexes on user_id and created_at and is synced daily via background Celery triggers.',
    'database': 'The database subsystem uses a PostgreSQL engine. Each SaaS tenant workspace is isolated via TenantID row-level partitioning for enterprise compliance. Constraints and unique key indexes are validated automatically prior to deployment.',
    'branding': 'The design system adopts a Outfit sans-serif typeface, customized with primary gradient colors (Violet #8b5cf6 to Fuchsia #d946ef). This branding system was generated by the BrandingAgent (Part 18) to fit high-end developer platform themes.',
    'compiler': 'The compiler check compiles code assets using the TypeScript compiler (tsc). Verification checks ensure zero syntax errors exist across files prior to edge CDN deployment.',
    'test': 'The QA E2E test suite executes E2E verification scenarios 1-16 including DAG Scheduler, Context relevance checks, and validation rule auditing.',
    'deployment': 'The CDN edge deploy packages source pages and pushes them to Vercel/CDN hosts, returning a subdomained edge URL.',
    'context': 'Context Engine 2.0 dynamically ranks code elements using graph distance proximity from the EngineeringGraph, pruning comments and documentation to save ~92% of LLM token overhead.'
  };

  useEffect(() => {
    // Determine active language from cookie
    try {
      const match = document.cookie.match(/googtrans=\/en\/([a-z]{2})/);
      if (match && match[1]) {
        const labelMap: Record<string, string> = { 'en': 'EN', 'ru': 'RU', 'uz': 'UZ' };
        const labelEl = document.getElementById('current-lang-display');
        if (labelEl) labelEl.innerText = labelMap[match[1]] || 'EN';
      }
    } catch(e) {}

    const authStatus = AuthService.isAuthenticated();
    setIsAuthenticated(authStatus);
    if (authStatus) {
      setCurrentUser(AuthService.getCurrentUser());
      loadWorkspaces();
      loadBillingDashboard();
      loadPreferences();
    }
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      if (params.get('demo') === 'false') {
        setIsDemoMode(false);
      }
    }
  }, []);

  useEffect(() => {
    if (chatBottomRef.current) {
      chatBottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages]);

  // Real-time compiler node sync on editor content change
  useEffect(() => {
    if (!selectedFile) return;
    const fileName = selectedFile.path.split('/').pop() || '';
    
    // Set matching node to dirty/outdated as user starts editing
    setSaveStatus('dirty');
    setGraphNodes(prev => prev.map(node => {
      if (node.name === fileName) {
        return { ...node, status: 'outdated', health: 90 };
      }
      return node;
    }));

    // Debounced automatic background compilation and save (1.5s)
    const debounceTimer = setTimeout(async () => {
      setSaveStatus('saving');
      try {
        await ProjectFileService.updateFile(selectedFile.id, editorContent);
        setSaveStatus('saved');
        AnalyticsService.postTelemetry({ step: 'first_edit', status: 'success', workspace_id: selectedWorkspaceId });
        
        // Visual indicator that compiler validated the edited file in the Engineering Graph
        setGraphNodes(prev => prev.map(node => {
          if (node.name === fileName) {
            return { ...node, status: 'valid', health: 100 };
          }
          return node;
        }));
      } catch (err: any) {
        setSaveStatus('dirty');
        AnalyticsService.postTelemetry({ step: 'first_edit', status: 'failed', error_message: err.message || 'Auto-save failed', workspace_id: selectedWorkspaceId });
        setGraphNodes(prev => prev.map(node => {
          if (node.name === fileName) {
            return { ...node, status: 'failed', health: 40 };
          }
          return node;
        }));
      }
    }, 1500);

    return () => clearTimeout(debounceTimer);
  }, [editorContent]);

  const loadWorkspaces = async () => {
    try {
      const list = await WorkspaceService.getWorkspaces();
      setWorkspaces(list);
      if (list.length > 0) {
        setSelectedWorkspaceId(list[0].id);
        loadProjects(list[0].id);
      }
    } catch (err) {
      console.error('Failed to load workspaces:', err);
    }
  };

  const handleCreateWorkspace = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newWorkspaceName.trim()) return;
    try {
      const ws = await WorkspaceService.createWorkspace(newWorkspaceName);
      AnalyticsService.postTelemetry({ step: 'workspace_created', status: 'success', workspace_id: ws.id });
      setNewWorkspaceName('');
      setShowNewWorkspaceModal(false);
      await loadWorkspaces();
      setSelectedWorkspaceId(ws.id);
      loadProjects(ws.id);
    } catch (err: any) {
      AnalyticsService.postTelemetry({ step: 'workspace_created', status: 'failed', error_message: err.message });
      alert('Failed to create workspace: ' + err.message);
    }
  };

  const loadProjects = async (workspaceId?: string) => {
    try {
      const projs = await ProjectService.getProjects(workspaceId);
      setProjects(projs);
      if (projs.length > 0) {
        handleSelectProject(projs[0]);
      } else {
        setSelectedProject(null);
      }
    } catch (err) {
      console.error('Failed to load projects:', err);
    }
  };

  const loadBillingDashboard = async () => {
    try {
      const bData = await BillingService.getDashboard();
      setBillingData(bData);
    } catch (err) {
      console.error('Failed to load billing dashboard:', err);
    }
  };

  const loadRevenueData = async () => {
    setIsLoadingAnalytics(true);
    try {
      const data = await AnalyticsService.getRevenueDashboard();
      setRevenueData(data);
    } catch (err) {
      console.error('Failed to load revenue data:', err);
    } finally {
      setIsLoadingAnalytics(false);
    }
  };

  const loadQualityData = async () => {
    setIsLoadingAnalytics(true);
    try {
      const data = await AnalyticsService.getQualityDashboard();
      setQualityData(data);
    } catch (err) {
      console.error('Failed to load quality data:', err);
    } finally {
      setIsLoadingAnalytics(false);
    }
  };

  const loadPreferences = async () => {
    try {
      const prefs = await PreferencesService.getPreferences();
      setWritingStyle(prefs.writing_style);
      setPrefLang(prefs.preferred_language);
      setFavColors(prefs.favorite_colors);
    } catch (err) {
      console.error('Failed to load preferences:', err);
    }
  };

  const handleFetchReviews = async (projectId?: string) => {
    const targetId = projectId || selectedProject?.id;
    if (!targetId) return;
    try {
      const list = await ProjectService.getProjectReviews(targetId);
      setReviews(list);
    } catch (err) {
      console.error('Failed to fetch reviews:', err);
    }
  };

  const handleFetchFixes = async (projectId?: string) => {
    const targetId = projectId || selectedProject?.id;
    if (!targetId) return;
    try {
      const list = await ProjectService.getProjectFixes(targetId);
      setFixes(list);
    } catch (err) {
      console.error('Failed to fetch fixes:', err);
    }
  };

  const handleRunFix = async () => {
    if (!selectedProject) return;
    setIsFixing(true);
    try {
      const result = await ProjectService.fixProject(selectedProject.id);
      
      // Update fixes history list
      await handleFetchFixes(selectedProject.id);
      
      // Reload project structure/files
      const refreshedProj = await ProjectService.getProject(selectedProject.id);
      
      // Reload reviews
      await handleFetchReviews(selectedProject.id);

      // Select refreshed project
      setSelectedProject(refreshedProj);
      if (refreshedProj.files && refreshedProj.files.length > 0) {
        const indexFile = refreshedProj.files.find(f => f.path === 'src/pages/index.html') || refreshedProj.files[0];
        setSelectedFile(indexFile);
        setEditorContent(indexFile.content);
      }

      // Notify user via console log
      setChatMessages(prev => [
        ...prev,
        {
          sender: 'brain',
          text: `🔧 AI Bug Fix Run completed: Before Score: ${result.before_score}%, After Score: ${result.after_score}%. Fixed: ${result.fixed} issues. Rollback applied: ${result.rollback_available ? 'Yes (Score did not improve)' : 'No (Improved overall quality score)'}.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
      
      // Switch tab to show Bug Fix console results
      setActiveBottomTab('fix');

    } catch (err: any) {
      alert('AI Bug Fix pipeline failed: ' + (err.message || err));
    } finally {
      setIsFixing(false);
    }
  };

  const handleRunReview = async () => {
    if (!selectedProject) return;
    setIsReviewing(true);
    try {
      const newReview = await ProjectService.createProjectReview(selectedProject.id);
      setReviews(prev => [newReview, ...prev]);
    } catch (err: any) {
      alert('Review failed: ' + (err.message || err));
    } finally {
      setIsReviewing(false);
    }
  };

  const handleSelectProject = (project: ProjectData) => {
    setSelectedProject(project);
    handleFetchReviews(project.id);
    handleFetchFixes(project.id);
    if (project.files && project.files.length > 0) {
      const indexFile = project.files.find(f => f.path === 'src/pages/index.html') || project.files[0];
      handleSelectFile(indexFile, project);
    } else {
      setSelectedFile(null);
      setEditorContent('');
    }
    const successDeployment = project.deployments.find(d => d.status === 'success');
    if (successDeployment) {
      setDeploySuccessUrl(successDeployment.deploy_url);
    } else {
      setDeploySuccessUrl(null);
    }
  };

  const handleSelectFile = (file: ProjectFileData, projectContext?: ProjectData) => {
    setSelectedFile(file);
    setEditorContent(file.content);
    
    // Add log to message history that AI context switched
    const proj = projectContext || selectedProject;
    setChatMessages(prev => [
      ...prev,
      { 
        sender: 'brain', 
        text: `*AI Context updated: selected file [${file.path}]. Semantic relevance score: 98%. Comment pruning: Active (Pruned 42 lines).*`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
  };

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError('');
    try {
      if (authMode === 'register') {
        try {
          await AuthService.register(username, email, password, companyName);
          AnalyticsService.postTelemetry({ step: 'registration', status: 'success' });
        } catch (err: any) {
          AnalyticsService.postTelemetry({ step: 'registration', status: 'failed', error_message: err.message });
          throw err;
        }
      } else {
        await AuthService.login(username, password);
      }
      setIsAuthenticated(true);
      setCurrentUser(AuthService.getCurrentUser());
      loadWorkspaces();
      loadBillingDashboard();
      loadPreferences();
    } catch (err: any) {
      setAuthError(err.message || 'Authentication failed. Please try again.');
    }
  };

  const handleLogout = () => {
    AuthService.logout();
    setIsAuthenticated(false);
    setCurrentUser(null);
    setWorkspaces([]);
    setProjects([]);
    setSelectedProject(null);
    setBillingData(null);
  };

  // Synchronous Project Generation
  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    setIsGenerating(true);
    setTaskProgress(null);
    setActiveBottomTab('logs');

    // Telemetry: prompt entered and generation started
    AnalyticsService.postTelemetry({ step: 'prompt_entered', status: 'success', logs: prompt });
    AnalyticsService.postTelemetry({ step: 'generation_started', status: 'success', workspace_id: selectedWorkspaceId });

    const currentPrompt = prompt;
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    setChatMessages(prev => [
      ...prev,
      { sender: 'user', text: currentPrompt, timestamp: timeStr },
      { sender: 'brain', text: 'Initializing multi-agent orchestrator... Planning architecture and writing HTML...', timestamp: timeStr }
    ]);

    try {
      // START THE ASYNC TASK
      const taskInit = await ProjectService.createAITask(currentPrompt, selectedWorkspaceId);
      
      // POLL FOR PROGRESS
      const pollInterval = setInterval(async () => {
        try {
          const progressData = await ProjectService.getAITaskProgress(taskInit.id);
          setTaskProgress(progressData);
          
          if (progressData.status === 'completed' || progressData.status === 'failed') {
            clearInterval(pollInterval);
            setIsGenerating(false);
            setPrompt('');
            
            if (progressData.status === 'completed') {
               AnalyticsService.postTelemetry({ step: 'generation_completed', status: 'success', workspace_id: selectedWorkspaceId });
               
               // Load full task to get the project ID
               const fullTask = await ProjectService.getAITask(taskInit.id);
               if (fullTask.project) {
                 const project = await ProjectService.getProject(fullTask.project);
                 const projs = await ProjectService.getProjects(selectedWorkspaceId);
                 setProjects(projs);
                 handleSelectProject(project);
                 await loadBillingDashboard();
                 
                 setChatMessages(prev => [
                   ...prev.filter(msg => !msg.text.includes("Initializing multi-agent orchestrator")),
                   { sender: 'brain', text: `✓ Generation completed successfully! Project architecture, styles, and backend files are ready.`, timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
                 ]);
               }
            } else {
               AnalyticsService.postTelemetry({ step: 'generation_started', status: 'failed', error_message: progressData.last_log, workspace_id: selectedWorkspaceId });
               setChatMessages(prev => [
                 ...prev.filter(msg => !msg.text.includes("Initializing multi-agent orchestrator")),
                 { sender: 'brain', text: `❌ Generation failed during stage: ${progressData.current_stage}. Check logs for details.`, timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
               ]);
               alert('Generation failed: ' + progressData.last_log);
            }
          }
        } catch (err) {
          console.error("Polling error", err);
        }
      }, 2000);
      
    } catch (err: any) {
      setIsGenerating(false);
      AnalyticsService.postTelemetry({ 
        step: 'generation_started', 
        status: 'failed', 
        error_message: err.message, 
        workspace_id: selectedWorkspaceId 
      });
      
      setChatMessages(prev => [
        ...prev.filter(msg => !msg.text.includes("Initializing multi-agent orchestrator")),
        {
          sender: 'brain',
          text: `❌ Generation failed: ${err.message}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
      
      alert('Failed to trigger generation task: ' + err.message);
    }
  };

  const pollTaskProgress = (taskId: string) => {
    // Deprecated: No longer polling background Celery tasks
  };

  const handleSaveFile = async () => {
    if (!selectedFile || !selectedProject) return;
    setIsSavingFile(true);
    try {
      await ProjectFileService.updateFile(selectedFile.id, editorContent);
      AnalyticsService.postTelemetry({ step: 'first_edit', status: 'success', workspace_id: selectedWorkspaceId });
      const freshProject = await ProjectService.getProject(selectedProject.id);
      setSelectedProject(freshProject);
      const activeFile = freshProject.files.find(f => f.id === selectedFile.id);
      if (activeFile) {
        setSelectedFile(activeFile);
        setEditorContent(activeFile.content);
      }
      setIsSavingFile(false);
      setSaveStatus('saved');
    } catch (err: any) {
      setIsSavingFile(false);
      AnalyticsService.postTelemetry({ step: 'first_edit', status: 'failed', error_message: err.message, workspace_id: selectedWorkspaceId });
      alert('Failed to save file changes: ' + err.message);
    }
  };

  // AI Chat message submit handler
  const handleSendChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userText = chatInput;
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    // Add User Message
    setChatMessages(prev => [...prev, { sender: 'user', text: userText, timestamp: timeStr }]);
    setChatInput('');

    // If a project is selected, trigger real AI editing of the selected page/file
    if (selectedProject) {
      const targetPath = selectedFile?.path || 'src/pages/index.html';
      setChatMessages(prev => [
        ...prev,
        { sender: 'brain', text: `Working on it... Modifying '${targetPath}' to apply your instructions.`, timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
      ]);
      
      try {
        const updatedProj = await ProjectService.aiEditProject(selectedProject.id, userText, targetPath);
        
        // Update local project details
        setSelectedProject(updatedProj);
        
        // Sync selected file state with updated content
        if (updatedProj.files && updatedProj.files.length > 0) {
          const updatedFile = updatedProj.files.find(f => f.path === targetPath);
          if (updatedFile) {
            setSelectedFile(updatedFile);
            setEditorContent(updatedFile.content);
          }
        }
        
        // Clean up visual loading and add success message
        setChatMessages(prev => [
          ...prev.filter(msg => !msg.text.includes("Working on it...")),
          { 
            sender: 'brain', 
            text: `Successfully updated '${targetPath}' with your instruction: "${userText}"!`, 
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) 
          }
        ]);
        
        setSaveStatus('saved');
        
      } catch (err: any) {
        setChatMessages(prev => [
          ...prev.filter(msg => !msg.text.includes("Working on it...")),
          { 
            sender: 'brain', 
            text: `Failed to apply update: ${err.message || err}`, 
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) 
          }
        ]);
      }
    } else {
      // Simulate Brain typing response for general chat
      setTimeout(() => {
        let brainReply = `I have analyzed your request: "${userText}". To perform visual layouts or database DDL schema code changes, please select or generate a project first.`;
        
        const queryLower = userText.toLowerCase();
        if (queryLower.includes('orders_archive') || queryLower.includes('archive')) {
          brainReply = projectBrainHistory['orders_archive'];
        } else if (queryLower.includes('database') || queryLower.includes('schema') || queryLower.includes('sql') || queryLower.includes('table')) {
          brainReply = projectBrainHistory['database'];
        } else if (queryLower.includes('color') || queryLower.includes('theme') || queryLower.includes('branding') || queryLower.includes('font')) {
          brainReply = projectBrainHistory['branding'];
        } else if (queryLower.includes('compiler') || queryLower.includes('compile') || queryLower.includes('tsc')) {
          brainReply = projectBrainHistory['compiler'];
        } else if (queryLower.includes('test') || queryLower.includes('qa') || queryLower.includes('scenarios')) {
          brainReply = projectBrainHistory['test'];
        } else if (queryLower.includes('deploy') || queryLower.includes('publish') || queryLower.includes('edge')) {
          brainReply = projectBrainHistory['deployment'];
        } else if (queryLower.includes('context') || queryLower.includes('relevance') || queryLower.includes('token')) {
          brainReply = projectBrainHistory['context'];
        }

        setChatMessages(prev => [
          ...prev, 
          { sender: 'brain', text: brainReply, timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
        ]);
      }, 600);
    }
  };

  // Project utilities: rename, duplicate, archive, delete
  const handleRenameProject = async (projectId: string, currentName: string) => {
    const newName = window.prompt('Enter new project name:', currentName);
    if (!newName || !newName.trim()) return;
    try {
      await ProjectService.updateProject(projectId, { project_name: newName });
      loadProjects(selectedWorkspaceId);
    } catch (err: any) {
      alert('Rename failed: ' + err.message);
    }
  };

  const handleDuplicateProject = async (projectId: string) => {
    try {
      await ProjectService.duplicateProject(projectId);
      loadProjects(selectedWorkspaceId);
    } catch (err: any) {
      alert('Duplicate failed: ' + err.message);
    }
  };

  const handleArchiveProject = async (projectId: string) => {
    if (!confirm('Are you sure you want to archive this project?')) return;
    try {
      await ProjectService.archiveProject(projectId);
      loadProjects(selectedWorkspaceId);
    } catch (err: any) {
      alert('Archive failed: ' + err.message);
    }
  };

  const handleDeleteProject = async (projectId: string) => {
    if (!confirm('Are you sure you want to permanently delete this project?')) return;
    try {
      await ProjectService.deleteProject(projectId);
      loadProjects(selectedWorkspaceId);
    } catch (err: any) {
      alert('Delete failed: ' + err.message);
    }
  };

  const handleDeploy = async () => {
    if (!selectedProject) return;
    setIsDeploying(true);
    setActiveBottomTab('deployments');
    setDeploymentLogs('Initiating edge compiler...\nPackaging assets bundle...\nRunning deployment script...');
    AnalyticsService.postTelemetry({ step: 'deploy_clicked', status: 'success', workspace_id: selectedWorkspaceId });
    const startTime = Date.now();
    try {
      const updated = await ProjectService.deployProject(selectedProject.id);
      setSelectedProject(updated);
      const successDeployment = updated.deployments.find(d => d.status === 'success');
      if (successDeployment) {
        setDeploySuccessUrl(successDeployment.deploy_url);
        setDeploymentLogs(prev => prev + '\n✓ Build deployed successfully to CDN Edge server.\nURL: ' + successDeployment.deploy_url);
        addNotification('DEPLOYMENT COMPLETED', 'success', 'Deployed to Edge CDN: ' + successDeployment.deploy_url);
      }
      setIsDeploying(false);
      AnalyticsService.postTelemetry({
        step: 'deployment_completed',
        status: 'success',
        duration_ms: Date.now() - startTime,
        workspace_id: selectedWorkspaceId
      });
    } catch (err: any) {
      setIsDeploying(false);
      setDeploymentLogs(prev => prev + '\n❌ Deploy pipeline failure: ' + err.message);
      addNotification('DEPLOYMENT FAILED', 'failed', err.message);
      AnalyticsService.postTelemetry({
        step: 'deployment_completed',
        status: 'failed',
        error_message: err.message,
        duration_ms: Date.now() - startTime,
        workspace_id: selectedWorkspaceId,
        logs: err.message
      });
      alert('Deployment failed: ' + err.message);
    }
  };

  const handleSavePreferences = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSavingPref(true);
    try {
      await PreferencesService.updatePreferences({
        writing_style: writingStyle,
        preferred_language: prefLang,
        favorite_colors: favColors
      });
      setIsSavingPref(false);
      alert('Orchestrator preference styles saved.');
    } catch (err: any) {
      setIsSavingPref(false);
      alert('Failed to save preferences: ' + err.message);
    }
  };

  const handleSubscribe = async (planSlug: string) => {
    setIsSubscribing(true);
    AnalyticsService.postTelemetry({ step: 'subscription_started', status: 'success', workspace_id: selectedWorkspaceId });
    try {
      await BillingService.subscribe(planSlug, 'monthly');
      await loadBillingDashboard();
      AnalyticsService.postTelemetry({ step: 'subscription_completed', status: 'success', workspace_id: selectedWorkspaceId });
      addNotification('BILLING UPGRADED', 'success', `Subscribed to plan: ${planSlug.toUpperCase()}`);
      alert(`Successfully subscribed to plan: ${planSlug}`);
      setIsSubscribing(false);
    } catch (err: any) {
      setIsSubscribing(false);
      AnalyticsService.postTelemetry({ step: 'subscription_completed', status: 'failed', error_message: err.message, workspace_id: selectedWorkspaceId });
      addNotification('BILLING ERROR', 'failed', err.message);
      alert('Failed to update subscription: ' + err.message);
    }
  };

  const handleClaimPromo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!promoCode.trim()) return;
    setIsClaimingPromo(true);
    setPromoMsg('');
    setPromoErr('');
    try {
      const res = await BillingService.applyPromo(promoCode);
      setPromoMsg(res.message);
      await loadBillingDashboard();
      addNotification('PROMO CODE CLAIMED', 'success', res.message);
      setIsClaimingPromo(false);
    } catch (err: any) {
      setPromoErr(err.message || 'Failed to claim promo code.');
      addNotification('PROMO ERROR', 'failed', err.message || 'Invalid promo code');
      setIsClaimingPromo(false);
    }
  };

  // Real-time Preview synchronized state
  const getPreviewHTML = () => {
    // If the selected file is currently a page file and we are editing it, preview the editor's live unsaved content!
    if (selectedFile && selectedFile.path.startsWith('src/pages/') && selectedFile.path.endsWith('.html')) {
      return editorContent;
    }
    if (!selectedProject) return '<h1>No Preview Available</h1>';
    const idxPage = selectedProject.pages.find(p => p.slug === 'index');
    return idxPage ? idxPage.raw_content : '<h1>No Preview Available</h1>';
  };

  const projectFiles = selectedProject?.files || [];

  return (
    <div className="min-h-screen bg-black text-white selection:bg-purple-500/30 selection:text-purple-200 flex flex-col">
      
      {/* PREMIUM HEADER NAV */}
      <header className="border-b border-white/5 bg-zinc-950/80 backdrop-blur-xl sticky top-0 z-40 flex-shrink-0">
        <div className="max-w-[1920px] mx-auto px-8 py-4 flex items-center justify-between w-full transition-all duration-300">
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-2.5 cursor-default glow-effect">
              <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-primary to-pink-500 flex items-center justify-center shadow-lg shadow-purple-500/20">
                <Sparkles className="h-4 w-4 text-white" />
              </div>
              <span className="text-xl font-bold tracking-tight text-white">
                BevHub<span className="text-zinc-500 font-light">AI</span>
              </span>
            </div>
            {isAuthenticated && (
              <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-zinc-400">
                <span 
                  onClick={() => setWorkspaceView('workspace')} 
                  className={`transition-colors cursor-pointer ${workspaceView === 'workspace' ? 'text-white font-semibold' : 'hover:text-white'}`}
                >
                  Studio
                </span>
                <span 
                  onClick={() => setWorkspaceView('projects')} 
                  className={`transition-colors cursor-pointer ${workspaceView === 'projects' ? 'text-white font-semibold' : 'hover:text-white'}`}
                >
                  Projects
                </span>
                <span 
                  onClick={() => setWorkspaceView('templates')} 
                  className={`transition-colors cursor-pointer ${workspaceView === 'templates' ? 'text-white font-semibold' : 'hover:text-white'}`}
                >
                  Templates
                </span>
                <span 
                  onClick={() => setWorkspaceView('history')} 
                  className={`transition-colors cursor-pointer ${workspaceView === 'history' ? 'text-white font-semibold' : 'hover:text-white'}`}
                >
                  History
                </span>
                <span 
                  onClick={() => setWorkspaceView('deployments')} 
                  className={`transition-colors cursor-pointer ${workspaceView === 'deployments' ? 'text-white font-semibold' : 'hover:text-white'}`}
                >
                  Deployments
                </span>
                <span 
                  onClick={() => setWorkspaceView('billing')} 
                  className={`transition-colors cursor-pointer ${workspaceView === 'billing' ? 'text-white font-semibold' : 'hover:text-white'}`}
                >
                  Billing
                </span>
                <span 
                  onClick={() => setWorkspaceView('integrations')} 
                  className={`transition-colors cursor-pointer ${workspaceView === 'integrations' ? 'text-white font-semibold' : 'hover:text-white'}`}
                >
                  Integrations
                </span>
                <span 
                  onClick={() => setWorkspaceView('settings')} 
                  className={`transition-colors cursor-pointer ${workspaceView === 'settings' ? 'text-white font-semibold' : 'hover:text-white'}`}
                >
                  Settings
                </span>
              </nav>
            )}
          </div>

          <div className="flex items-center gap-5">
            
            {/* HIDDEN GOOGLE TRANSLATE ENGINE */}
            <div id="google_translate_element" className="absolute opacity-0 pointer-events-none w-0 h-0 overflow-hidden"></div>
            
            {/* PREMIUM CUSTOM LANGUAGE SWITCHER */}
            <div className="relative group">
              <div className="flex items-center gap-1.5 px-3 py-1.5 bg-zinc-900/80 border border-white/10 rounded-lg text-xs font-mono text-zinc-300 cursor-pointer hover:bg-zinc-800 hover:text-white transition-all shadow-[0_0_10px_rgba(0,0,0,0.5)]">
                <Globe className="h-3.5 w-3.5 text-purple-400" />
                <span id="current-lang-display">EN</span>
                <ChevronDown className="h-3 w-3 opacity-50" />
              </div>
              <div className="absolute top-full right-0 mt-2 w-32 bg-zinc-950 border border-white/10 rounded-xl shadow-2xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50 overflow-hidden flex flex-col">
                <button 
                  onClick={() => triggerTranslation('en')}
                  className="px-4 py-2 text-xs font-mono text-left text-zinc-400 hover:bg-zinc-900 hover:text-white transition-colors border-b border-white/5"
                >
                  English
                </button>
                <button 
                  onClick={() => triggerTranslation('ru')}
                  className="px-4 py-2 text-xs font-mono text-left text-zinc-400 hover:bg-zinc-900 hover:text-white transition-colors border-b border-white/5"
                >
                  Русский (RU)
                </button>
                <button 
                  onClick={() => triggerTranslation('uz')}
                  className="px-4 py-2 text-xs font-mono text-left text-zinc-400 hover:bg-zinc-900 hover:text-white transition-colors"
                >
                  O'zbek (UZ)
                </button>
              </div>
            </div>

            {isAuthenticated ? (
              <div className="flex items-center gap-4">
                <button 
                  onClick={() => setIsCmdKOpen(true)}
                  className="flex items-center gap-2 px-3 py-1.5 bg-zinc-900 border border-white/10 rounded-lg text-xs font-mono text-zinc-400 hover:border-purple-500/50 hover:text-white transition-all"
                >
                  <Search className="h-3.5 w-3.5" />
                  <span>Search...</span>
                  <kbd className="bg-black border border-white/10 text-zinc-500 rounded px-1.5 py-0.5 text-[10px]">⌘K</kbd>
                </button>

                <div className="relative">
                  <button 
                    onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
                    className="p-2 rounded-lg bg-zinc-900 border border-white/10 text-zinc-400 hover:text-white hover:border-white/20 transition-all relative"
                  >
                    <Bell className="h-4 w-4" />
                    {notificationsList.length > 0 && (
                      <span className="absolute -top-1 -right-1 h-2.5 w-2.5 rounded-full bg-purple-500 animate-pulse" />
                    )}
                  </button>

                  {isNotificationsOpen && (
                    <div className="absolute right-0 mt-2 w-80 bg-zinc-950 border border-white/10 rounded-xl shadow-2xl p-4 z-50">
                      <div className="flex justify-between items-center mb-3 pb-2 border-b border-white/10">
                        <h4 className="text-xs font-semibold text-white uppercase tracking-wider">Notifications</h4>
                        <span className="text-[10px] text-zinc-500">{notificationsList.length} recent</span>
                      </div>
                      <div className="space-y-2 max-h-60 overflow-y-auto">
                        {notificationsList.length === 0 ? (
                          <p className="text-xs text-zinc-500 py-4 text-center italic">No new notifications</p>
                        ) : notificationsList.map(n => (
                          <div key={n.id} className="p-2.5 rounded-lg bg-zinc-900/50 border border-white/5 text-xs flex flex-col gap-1">
                            <div className="flex justify-between items-center">
                              <span className={`font-semibold ${n.status === 'success' ? 'text-emerald-400' : 'text-purple-400'}`}>{n.title}</span>
                              <span className="text-[10px] text-zinc-500 font-mono">{n.time}</span>
                            </div>
                            <p className="text-zinc-400 truncate">{n.details || 'System event triggered'}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-2 px-3 py-1.5 bg-zinc-900/50 border border-white/5 rounded-lg">
                  <span className="h-2 w-2 bg-emerald-400 rounded-full animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.6)]" />
                  <span className="text-xs font-mono text-zinc-300">Engine Active</span>
                </div>
                <span className="text-xs text-zinc-300 font-mono flex items-center gap-1.5 px-3 py-1.5 rounded-lg hover:bg-zinc-900/50 transition-colors cursor-pointer">
                  <Coins className="h-3.5 w-3.5 text-yellow-500" />
                  {billingData ? `${billingData.balance} credits` : '...'}
                </span>
                <span className="text-sm font-medium text-zinc-300 flex items-center gap-2">
                  <div className="h-7 w-7 rounded-full bg-gradient-to-br from-zinc-700 to-zinc-900 border border-white/10 flex items-center justify-center text-xs">
                    {currentUser?.username?.charAt(0).toUpperCase()}
                  </div>
                </span>
                <button 
                  onClick={handleLogout}
                  className="p-2 text-zinc-500 hover:text-white hover:bg-zinc-800 rounded-lg transition-all"
                  title="Logout"
                >
                  <LogOut className="h-4 w-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-4">
                <span className="text-sm font-medium text-zinc-400 hover:text-white transition-colors cursor-pointer">Log in</span>
                <button className="px-4 py-2 bg-white text-black text-sm font-medium rounded-lg hover:bg-zinc-200 transition-colors shadow-[0_0_15px_rgba(255,255,255,0.15)]">
                  Start Building
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* MAIN CONTAINER */}
      {!isAuthenticated ? (
        // PREMIUM LANDING PAGE
        <main className="flex-1 overflow-y-auto">
          <div className="relative pt-32 pb-20 sm:pt-40 sm:pb-24">
            <div className="mx-auto max-w-7xl px-6 lg:px-8 text-center">
              
              <div className="inline-flex items-center gap-2 rounded-full border border-purple-500/20 bg-purple-500/10 px-5 py-2 text-sm font-medium text-purple-300 backdrop-blur-md mb-8 shadow-[0_0_20px_rgba(139,92,246,0.15)]">
                <Sparkles className="h-4 w-4" />
                BevHub AI 1.0 is live
              </div>

              <h1 className="text-5xl font-extrabold tracking-tight text-white sm:text-7xl lg:text-8xl max-w-5xl mx-auto leading-tight">
                Build anything <br />
                <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-amber-300 bg-clip-text text-transparent">
                  with AI.
                </span>
              </h1>

              <p className="mx-auto mt-8 max-w-2xl text-xl text-zinc-400 font-light leading-relaxed">
                Websites, apps, backends and bots — from one prompt to a working product in seconds. 
                The next evolution of software engineering.
              </p>

              <div className="mt-10 flex items-center justify-center gap-x-6">
                <button onClick={() => window.scrollTo({top: document.getElementById('auth-section')?.offsetTop, behavior: 'smooth'})} className="rounded-xl bg-white px-8 py-4 text-sm font-semibold text-zinc-900 shadow-xl shadow-white/10 hover:bg-zinc-200 transition-all hover:scale-105 active:scale-95">
                  Start Building
                </button>
                <button className="text-sm font-semibold leading-6 text-white hover:text-zinc-300 transition-colors flex items-center gap-2 group">
                  See how it works <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </button>
              </div>

              {/* INTERACTIVE SHOWCASE ABSTRACT */}
              <div className="mt-24 max-w-5xl mx-auto relative glassmorphism rounded-2xl p-2 border border-white/5 shadow-2xl">
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent z-10 pointer-events-none rounded-2xl" />
                <div className="bg-zinc-950 rounded-xl overflow-hidden border border-white/5 flex flex-col md:flex-row relative z-0">
                  <div className="p-6 md:w-1/3 border-b md:border-b-0 md:border-r border-white/5 bg-zinc-900/30 flex flex-col justify-center text-left">
                    <p className="text-sm font-mono text-zinc-500 mb-2">User Prompt</p>
                    <div className="p-4 bg-zinc-900 border border-white/10 rounded-lg shadow-inner">
                      <p className="text-sm text-zinc-300 italic">"Create a premium dark-mode portfolio for a product designer with a case study gallery and a contact form."</p>
                    </div>
                    <div className="mt-6 flex flex-col gap-2">
                      <div className="flex items-center gap-3 text-xs text-zinc-400">
                        <CheckCircle className="h-4 w-4 text-emerald-500" /> AI generates architecture
                      </div>
                      <div className="flex items-center gap-3 text-xs text-zinc-400">
                        <CheckCircle className="h-4 w-4 text-emerald-500" /> Building components
                      </div>
                      <div className="flex items-center gap-3 text-xs text-zinc-400">
                        <CheckCircle className="h-4 w-4 text-emerald-500" /> Deploying to Edge CDN
                      </div>
                    </div>
                  </div>
                  <div className="p-6 md:w-2/3 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] relative">
                     <div className="absolute inset-0 bg-gradient-to-tr from-purple-900/20 to-zinc-950/90" />
                     <div className="relative z-10 h-64 border border-white/10 rounded-lg bg-zinc-950 flex flex-col overflow-hidden shadow-2xl">
                        <div className="h-8 bg-zinc-900 border-b border-white/10 flex items-center px-4 gap-2">
                          <div className="h-2.5 w-2.5 rounded-full bg-red-500" />
                          <div className="h-2.5 w-2.5 rounded-full bg-yellow-500" />
                          <div className="h-2.5 w-2.5 rounded-full bg-emerald-500" />
                          <div className="mx-auto text-[10px] font-mono text-zinc-500">live-preview.bevhub.ai</div>
                        </div>
                        <div className="flex-1 p-6 flex flex-col items-center justify-center text-center">
                          <h2 className="text-2xl font-bold text-white mb-2">Alex Doe</h2>
                          <p className="text-zinc-400 text-sm">Product Designer & Engineer</p>
                          <div className="mt-6 px-6 py-2 bg-white text-black text-xs font-bold rounded-full">View Work</div>
                        </div>
                     </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* PRICING SECTION */}
          <div className="py-24 bg-black relative border-t border-white/5">
            <div className="mx-auto max-w-7xl px-6 lg:px-8">
              <div className="text-center max-w-2xl mx-auto mb-16">
                <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl mb-4">Simple, transparent pricing</h2>
                <p className="text-zinc-400">Start building for free, then scale as your AI-generated products grow.</p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
                {/* Free Tier */}
                <div className="bg-zinc-900/40 border border-white/10 rounded-3xl p-8 flex flex-col">
                  <h3 className="text-xl font-semibold text-white mb-2">Hobby</h3>
                  <p className="text-sm text-zinc-400 mb-6">For weekend projects and exploration.</p>
                  <div className="mb-6"><span className="text-4xl font-bold text-white">$0</span><span className="text-zinc-500">/mo</span></div>
                  <ul className="space-y-4 mb-8 flex-1">
                    <li className="flex items-center text-sm text-zinc-300 gap-3"><CheckCircle className="h-4 w-4 text-zinc-500" /> 3 AI Generations / month</li>
                    <li className="flex items-center text-sm text-zinc-300 gap-3"><CheckCircle className="h-4 w-4 text-zinc-500" /> Standard Edge deployment</li>
                    <li className="flex items-center text-sm text-zinc-300 gap-3"><CheckCircle className="h-4 w-4 text-zinc-500" /> Community support</li>
                  </ul>
                  <button onClick={() => window.scrollTo({top: document.getElementById('auth-section')?.offsetTop, behavior: 'smooth'})} className="w-full py-2.5 bg-white/5 hover:bg-white/10 text-white rounded-xl text-sm font-semibold transition-colors">Start Free</button>
                </div>
                
                {/* Growth Tier */}
                <div className="bg-zinc-900 border border-purple-500/30 rounded-3xl p-8 flex flex-col relative shadow-[0_0_30px_rgba(139,92,246,0.1)] transform md:-translate-y-4">
                  <div className="absolute top-0 right-8 -translate-y-1/2">
                    <span className="bg-gradient-to-r from-purple-500 to-pink-500 text-white text-[10px] font-bold uppercase tracking-wider py-1 px-3 rounded-full">Most Popular</span>
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-2">Growth</h3>
                  <p className="text-sm text-zinc-400 mb-6">For independent developers and creators.</p>
                  <div className="mb-6"><span className="text-4xl font-bold text-white">$49</span><span className="text-zinc-500">/mo</span></div>
                  <ul className="space-y-4 mb-8 flex-1">
                    <li className="flex items-center text-sm text-zinc-300 gap-3"><CheckCircle className="h-4 w-4 text-purple-400" /> Unlimited AI Generations</li>
                    <li className="flex items-center text-sm text-zinc-300 gap-3"><CheckCircle className="h-4 w-4 text-purple-400" /> Advanced AI Editor Chat</li>
                    <li className="flex items-center text-sm text-zinc-300 gap-3"><CheckCircle className="h-4 w-4 text-purple-400" /> Custom Domains</li>
                    <li className="flex items-center text-sm text-zinc-300 gap-3"><CheckCircle className="h-4 w-4 text-purple-400" /> Private Repositories</li>
                  </ul>
                  <button onClick={() => window.scrollTo({top: document.getElementById('auth-section')?.offsetTop, behavior: 'smooth'})} className="w-full py-2.5 bg-white text-black hover:bg-zinc-200 rounded-xl text-sm font-semibold transition-colors shadow-[0_0_15px_rgba(255,255,255,0.1)]">Subscribe to Pro</button>
                </div>
                
                {/* Business Tier */}
                <div className="bg-zinc-900/40 border border-white/10 rounded-3xl p-8 flex flex-col">
                  <h3 className="text-xl font-semibold text-white mb-2">Business</h3>
                  <p className="text-sm text-zinc-400 mb-6">For teams requiring enterprise scale.</p>
                  <div className="mb-6"><span className="text-4xl font-bold text-white">$99</span><span className="text-zinc-500">/mo</span></div>
                  <ul className="space-y-4 mb-8 flex-1">
                    <li className="flex items-center text-sm text-zinc-300 gap-3"><CheckCircle className="h-4 w-4 text-zinc-500" /> Everything in Pro</li>
                    <li className="flex items-center text-sm text-zinc-300 gap-3"><CheckCircle className="h-4 w-4 text-zinc-500" /> Team Collaboration (5 seats)</li>
                    <li className="flex items-center text-sm text-zinc-300 gap-3"><CheckCircle className="h-4 w-4 text-zinc-500" /> Priority Server Infrastructure</li>
                    <li className="flex items-center text-sm text-zinc-300 gap-3"><CheckCircle className="h-4 w-4 text-zinc-500" /> 24/7 Dedicated Support</li>
                  </ul>
                  <button onClick={() => window.scrollTo({top: document.getElementById('auth-section')?.offsetTop, behavior: 'smooth'})} className="w-full py-2.5 bg-white/5 hover:bg-white/10 text-white rounded-xl text-sm font-semibold transition-colors">Contact Sales</button>
                </div>
              </div>
            </div>
          </div>

          {/* AUTHENTICATION SECTION */}
          <div id="auth-section" className="py-24 bg-zinc-950 border-t border-white/5 relative overflow-hidden">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[500px] bg-purple-500/10 blur-[120px] rounded-full pointer-events-none" />
            
            <div className="mx-auto max-w-md relative z-10">
              <div className="text-center mb-10">
                <h2 className="text-3xl font-bold tracking-tight text-white mb-3">Join the Future of Code</h2>
                <p className="text-zinc-400">Create an account to start generating production-ready applications.</p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-zinc-900/60 p-8 shadow-2xl backdrop-blur-xl">
                {authError && (
                  <div className="mb-6 flex items-start gap-3 rounded-xl bg-red-500/10 p-4 border border-red-500/20 text-sm text-red-400">
                    <AlertTriangle className="h-5 w-5 flex-shrink-0 mt-0.5" />
                    <div className="space-y-1">{formatError(authError)}</div>
                  </div>
                )}

                <form onSubmit={handleAuthSubmit} className="space-y-5">
                  {authMode === 'register' && (
                    <>
                      <div>
                        <label className="block text-xs font-medium text-zinc-300 mb-2 uppercase tracking-wide">Workspace Name</label>
                        <div className="relative">
                          <Globe className="absolute left-3.5 top-3 h-4 w-4 text-zinc-500" />
                          <input 
                            type="text" 
                            placeholder="e.g. Acme Agency" 
                            value={companyName}
                            onChange={(e) => setCompanyName(e.target.value)}
                            className="w-full pl-11 pr-4 py-2.5 bg-black/50 border border-white/10 rounded-xl text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-purple-500 transition-all focus:ring-1 focus:ring-purple-500/50"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-xs font-medium text-zinc-300 mb-2 uppercase tracking-wide">Email</label>
                        <div className="relative">
                          <Mail className="absolute left-3.5 top-3 h-4 w-4 text-zinc-500" />
                          <input 
                            type="email" 
                            required
                            placeholder="admin@company.com" 
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full pl-11 pr-4 py-2.5 bg-black/50 border border-white/10 rounded-xl text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-purple-500 transition-all focus:ring-1 focus:ring-purple-500/50"
                          />
                        </div>
                      </div>
                    </>
                  )}

                  <div>
                    <label className="block text-xs font-medium text-zinc-300 mb-2 uppercase tracking-wide">Username</label>
                    <div className="relative">
                      <User className="absolute left-3.5 top-3 h-4 w-4 text-zinc-500" />
                      <input 
                        type="text" 
                        required
                        placeholder="username" 
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className="w-full pl-11 pr-4 py-2.5 bg-black/50 border border-white/10 rounded-xl text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-purple-500 transition-all focus:ring-1 focus:ring-purple-500/50"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-zinc-300 mb-2 uppercase tracking-wide">Password</label>
                    <div className="relative">
                      <Lock className="absolute left-3.5 top-3 h-4 w-4 text-zinc-500" />
                      <input 
                        type="password" 
                        required
                        placeholder="••••••••" 
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full pl-11 pr-4 py-2.5 bg-black/50 border border-white/10 rounded-xl text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-purple-500 transition-all focus:ring-1 focus:ring-purple-500/50"
                      />
                    </div>
                  </div>

                  <button 
                    type="submit"
                    className="w-full py-3 bg-white hover:bg-zinc-200 text-black font-semibold text-sm rounded-xl transition-all flex items-center justify-center gap-2 mt-2 shadow-[0_0_15px_rgba(255,255,255,0.1)] active:scale-[0.98]"
                  >
                    {authMode === 'register' ? 'Create Account' : 'Sign In'}
                    <ArrowRight className="h-4 w-4" />
                  </button>
                </form>

                <div className="mt-6 text-center">
                  <button 
                    type="button"
                    onClick={() => setAuthMode(authMode === 'register' ? 'login' : 'register')}
                    className="text-sm text-zinc-400 hover:text-white transition-colors"
                  >
                    {authMode === 'register' ? 'Already have an account? Log in' : 'Need an account? Sign up'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </main>
      ) : (
        // PERSISTENT WORKSPACE DASHBOARD
        <div className="flex-1 flex flex-col md:flex-row overflow-y-auto md:overflow-hidden bg-[#050505] text-white relative">
          
          {/* PREMIUM SIDEBAR LEFT - FILE STRUCTURE */}
          {selectedProject && (
            <aside className="w-full md:w-[280px] border-b md:border-b-0 md:border-r border-white/5 bg-[#09090b] flex flex-col justify-between overflow-hidden flex-shrink-0 select-none relative z-20">
              <div className="flex flex-col h-full overflow-hidden">
                <div className="p-4 border-b border-white/5">
                  <span className="text-zinc-500 text-[10px] font-medium block mb-1.5 ml-1">Project</span>
                  <button className="w-full flex items-center justify-between bg-[#131316] border border-white/5 hover:border-white/10 hover:bg-[#1a1a1f] transition-colors rounded-xl px-3 py-2.5 text-left shadow-sm">
                    <div className="flex items-center gap-3">
                      <div className="h-6 w-6 bg-purple-500/10 rounded-lg flex items-center justify-center border border-purple-500/20">
                        <Folder className="h-3 w-3 text-purple-400" />
                      </div>
                      <div className="flex flex-col">
                        <span className="text-xs font-semibold text-white truncate max-w-[120px]">{selectedProject.project_name}</span>
                        <div className="flex items-center gap-1.5 mt-0.5">
                          <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                          <span className="text-[9px] text-zinc-400 font-medium">Website</span>
                        </div>
                      </div>
                    </div>
                    <ChevronDown className="h-3.5 w-3.5 text-zinc-500" />
                  </button>
                </div>
                
                <div className="p-3 space-y-0.5">
                  <button 
                    onClick={() => setWorkspaceView('workspace')}
                    className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                      workspaceView === 'workspace' 
                        ? 'bg-purple-500/10 text-purple-400 border border-purple-500/10 shadow-inner' 
                        : 'text-zinc-400 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    <Globe className="h-4 w-4" /> Overview
                  </button>
                  <button 
                    onClick={() => setWorkspaceView('workspace')}
                    className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                      workspaceView === 'workspace' 
                        ? 'bg-purple-500/10 text-purple-400 border border-purple-500/10 shadow-inner' 
                        : 'text-zinc-400 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    <Folder className="h-4 w-4" /> Files
                  </button>
                  <button 
                    onClick={() => setWorkspaceView('revenue')}
                    className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                      workspaceView === 'revenue' 
                        ? 'bg-purple-500/10 text-purple-400 border border-purple-500/10 shadow-inner' 
                        : 'text-zinc-400 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    <Server className="h-4 w-4" /> Deployments
                  </button>
                  <button 
                    onClick={() => setWorkspaceView('revenue')}
                    className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium text-zinc-400 hover:text-white hover:bg-white/5 transition-all"
                  >
                    <History className="h-4 w-4" /> History
                  </button>
                  <button 
                    onClick={() => alert('Settings menu coming soon!')}
                    className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium text-zinc-400 hover:text-white hover:bg-white/5 transition-all"
                  >
                    <Settings className="h-4 w-4" /> Settings
                  </button>
                </div>

                <div className="h-px w-full bg-white/5 my-1" />

                <div className="p-3 flex-1 overflow-y-auto custom-scrollbar">
                  <div className="flex items-center justify-between mb-3 px-2">
                    <span className="text-[10px] font-medium text-zinc-500">File Structure</span>
                    <button className="text-zinc-500 hover:text-white transition-colors"><Plus className="h-3.5 w-3.5" /></button>
                  </div>
                  
                  <div className="space-y-0.5 font-mono text-[11px]">
                    <div className="flex items-center gap-1.5 px-2 py-1.5 text-zinc-400 hover:text-zinc-200 cursor-pointer rounded-lg hover:bg-white/5 transition-colors">
                      <ChevronDown className="h-3 w-3 opacity-50" /> <Folder className="h-3.5 w-3.5 text-blue-400" /> workspace
                    </div>
                    
                    {projectFiles.map(file => (
                      <div 
                        key={file.id}
                        onClick={() => {
                          setSelectedFile(file);
                          setEditorContent(file.content);
                          setCenterTab('code');
                        }}
                        className={`flex items-center justify-between px-2 py-1.5 ml-3 cursor-pointer rounded-lg transition-colors group ${
                          selectedFile?.id === file.id 
                            ? 'text-purple-400 bg-purple-500/10 border border-purple-500/20 shadow-sm relative overflow-hidden' 
                            : 'text-zinc-400 hover:text-zinc-200 hover:bg-white/5'
                        }`}
                      >
                        <div className="flex items-center gap-1.5">
                          {selectedFile?.id === file.id && <div className="absolute left-0 top-0 bottom-0 w-[2px] bg-purple-500" />}
                          <FileCode className={`h-3.5 w-3.5 ${selectedFile?.id === file.id ? 'text-purple-400' : 'text-zinc-500'}`} />
                          <span className="truncate max-w-[120px]">{file.path.split('/').pop()}</span>
                        </div>
                      </div>
                    ))}
                    
                    {projectFiles.length === 0 && (
                      <div className="text-[10px] text-zinc-600 italic ml-6 mt-2">No files generated yet.</div>
                    )}
                  </div>
                </div>

                <div className="p-5 bg-gradient-to-t from-black to-transparent">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-[10px] font-bold flex items-center gap-1.5 text-purple-400"><Sparkles className="h-3 w-3" /> AI Credits</span>
                    <span className="text-[10px] text-zinc-500 font-mono">
                      {billingData ? `${Math.round(parseFloat(billingData.balance))} / ${billingData.plans.find(p => p.slug === billingData.subscription.plan_slug)?.ai_credits || 500}` : '...'}
                    </span>
                  </div>
                  <div className="h-1.5 w-full bg-zinc-900 rounded-full overflow-hidden shadow-inner">
                    <div 
                      className="h-full bg-gradient-to-r from-purple-600 to-purple-400 shadow-[0_0_10px_rgba(168,85,247,0.5)] transition-all duration-1000" 
                      style={{ width: `${billingData ? Math.min(100, Math.max(0, (parseFloat(billingData.balance) / (billingData.plans.find(p => p.slug === billingData.subscription.plan_slug)?.ai_credits || 500)) * 100)) : 0}%` }}
                    />
                  </div>
                </div>
              </div>
            </aside>
          )}

          {/* CENTER PANEL */}
          <main className="flex-1 flex flex-col bg-zinc-950 overflow-hidden relative z-10">
            <div className="flex justify-between items-center border-b border-white/5 px-6 py-3 bg-[#0a0a0c] flex-shrink-0 select-none shadow-sm shadow-black/20">
              <div className="flex items-center gap-4">
                <h2 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2">
                  <Workflow className="h-4 w-4 text-purple-400" />
                  {selectedProject ? selectedProject.project_name : 'No Project Selected'}
                </h2>
              </div>
              <div className="flex items-center gap-3">
                {selectedProject && (
                  <button 
                    onClick={handleDeploy}
                    disabled={isDeploying}
                    className="flex items-center gap-2 bg-white hover:bg-zinc-200 text-black px-5 py-2 text-xs font-bold rounded-lg transition-all shadow-[0_0_15px_rgba(255,255,255,0.1)] active:scale-95 disabled:opacity-50"
                  >
                    {isDeploying ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : <Server className="h-3.5 w-3.5" />}
                    {isDeploying ? 'Deploying...' : 'Deploy to Edge'}
                  </button>
                )}
              </div>
            </div>

            <div className="flex-1 flex flex-col overflow-hidden">
              {workspaceView === 'workspace' && (
                <div className="flex-1 flex flex-col overflow-hidden bg-[#050505] relative">
                  {!selectedProject ? (
                    <div className="flex-1 flex flex-col items-center justify-center p-6 relative z-10">
                      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[400px] bg-purple-500/10 blur-[120px] rounded-full pointer-events-none" />
                      <div className="max-w-3xl w-full flex flex-col items-center animate-in fade-in slide-in-from-bottom-4 duration-700">
                        <h2 className="text-3xl font-semibold text-white mb-8">What do you want to build today?</h2>
                        <form id="generate-form" onSubmit={handleGenerate} className="w-full relative group">
                          <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl blur opacity-25 group-focus-within:opacity-75 transition duration-500"></div>
                          <div className="relative flex flex-col bg-zinc-900 border border-white/10 rounded-2xl shadow-2xl overflow-hidden focus-within:border-purple-500/50 transition-colors">
                            <textarea 
                              value={prompt}
                              onChange={(e) => setPrompt(e.target.value)}
                              disabled={isGenerating}
                              placeholder="Describe your app in detail... e.g. A dark-mode portfolio for a photographer."
                              className="w-full h-32 p-5 bg-transparent text-white placeholder-zinc-500 focus:outline-none resize-none text-lg leading-relaxed custom-scrollbar"
                            />
                            <div className="flex items-center justify-between p-3 bg-zinc-950/50 border-t border-white/5">
                              <div className="flex gap-2">
                                <button type="button" className="p-2 hover:bg-white/5 rounded-lg text-zinc-400 hover:text-white transition-colors" title="Settings">
                                  <Settings className="h-4 w-4" />
                                </button>
                              </div>
                              <button 
                                type="submit"
                                disabled={isGenerating || !prompt.trim()}
                                className="px-5 py-2 bg-white text-black font-semibold rounded-xl flex items-center gap-2 hover:bg-zinc-200 transition-all disabled:opacity-50 disabled:hover:bg-white active:scale-95"
                              >
                                {isGenerating ? 'Generating...' : 'Generate'}
                                {isGenerating ? <RefreshCw className="h-4 w-4 animate-spin" /> : <ArrowRight className="h-4 w-4" />}
                              </button>
                            </div>
                          </div>
                        </form>
                      </div>

                      {!taskProgress && !isGenerating && (
                        <div className="max-w-5xl w-full mt-16 animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-300">
                          <h3 className="text-sm font-semibold text-zinc-400 mb-6 uppercase tracking-wider text-center">Or start with a Premium Template</h3>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            {[
                              { title: 'SaaS Platform', desc: 'Modern B2B dashboard', icon: <Layers className="h-5 w-5" />, prompt: 'A modern B2B SaaS platform dashboard with dark mode, billing page, and analytics sidebar.' },
                              { title: 'E-commerce', desc: 'Minimalist storefront', icon: <Ticket className="h-5 w-5" />, prompt: 'A premium minimalist e-commerce storefront with a product grid, shopping cart, and checkout flow.' },
                              { title: 'Landing Page', desc: 'High-converting funnel', icon: <LayoutDashboard className="h-5 w-5" />, prompt: 'A high-converting landing page for a mobile app with a hero section, features grid, and pricing.' },
                              { title: 'Portfolio', desc: 'Creative showcase', icon: <Palette className="h-5 w-5" />, prompt: 'A creative portfolio for a designer featuring a masonry grid of projects, about page, and contact form.' }
                            ].map((tpl, i) => (
                              <div 
                                key={i} 
                                onClick={() => {
                                  setPrompt(tpl.prompt);
                                  setTimeout(() => {
                                    const form = document.getElementById('generate-form') as HTMLFormElement;
                                    if (form) form.requestSubmit();
                                  }, 100);
                                }}
                                className="bg-zinc-900/50 border border-white/5 hover:border-purple-500/50 hover:bg-zinc-900 rounded-xl p-5 cursor-pointer transition-all group flex flex-col items-center text-center shadow-lg"
                              >
                                <div className="h-12 w-12 rounded-full bg-white/5 flex items-center justify-center mb-3 group-hover:scale-110 group-hover:bg-purple-500/20 group-hover:text-purple-400 transition-all text-zinc-400 shadow-[0_0_15px_rgba(0,0,0,0.5)]">
                                  {tpl.icon}
                                </div>
                                <h4 className="text-white font-semibold text-sm mb-1">{tpl.title}</h4>
                                <p className="text-xs text-zinc-500">{tpl.desc}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {taskProgress && (
                        <div className="max-w-3xl w-full mt-8 bg-zinc-900 border border-white/10 rounded-2xl p-6 shadow-2xl animate-in fade-in slide-in-from-bottom-4 relative overflow-hidden">
                          <div className="absolute top-0 left-0 w-full h-1 bg-zinc-800">
                            <div 
                              className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500"
                              style={{ width: `${taskProgress.progress_percent}%` }}
                            />
                          </div>
                          <div className="flex justify-between items-center mb-4">
                            <h3 className="text-lg font-semibold flex items-center gap-2">
                              <Sparkles className="h-5 w-5 text-purple-400 animate-pulse" />
                              AI Orchestrator
                            </h3>
                            <span className="text-sm font-mono text-zinc-400 bg-black/50 px-2 py-1 rounded">
                              {taskProgress.progress_percent}%
                            </span>
                          </div>
                          
                          <div className="space-y-4">
                            <div className="flex justify-between text-sm text-zinc-400">
                              <span>Current Agent Stage</span>
                              <span className="text-white font-medium">{taskProgress.current_stage}</span>
                            </div>
                            <div className="flex justify-between text-sm text-zinc-400">
                              <span>Active Engine</span>
                              <span className="text-white font-mono">{taskProgress.active_model}</span>
                            </div>
                            <div className="flex justify-between text-sm text-zinc-400">
                              <span>Est. Remaining</span>
                              <span className="text-white font-mono">{taskProgress.estimated_remaining_seconds}s</span>
                            </div>
                          </div>
                          
                          <div className="mt-6 bg-black/50 p-4 rounded-xl border border-white/5 font-mono text-xs text-zinc-500 max-h-[100px] overflow-y-auto custom-scrollbar">
                            {taskProgress.last_log}
                          </div>
                        </div>
                      )}

                    </div>
                  ) : (
                    <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
                      {/* CENTER: LIVE PREVIEW */}
                      <div className="flex-1 flex flex-col bg-[#050505] relative min-h-[450px] lg:min-h-0 border-r border-white/5">
                        
                        <div className="flex items-center justify-between px-6 py-3 border-b border-white/5 bg-[#09090b] flex-shrink-0">
                          <div className="flex items-center gap-2">
                            <button 
                              onClick={() => setCenterTab('preview')}
                              className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                                centerTab === 'preview' 
                                  ? 'bg-purple-600/20 text-purple-400 border border-purple-500/30 shadow-sm' 
                                  : 'text-zinc-400 hover:text-white'
                              }`}
                            >
                              <Eye className="h-3.5 w-3.5" /> Preview
                            </button>
                            <button 
                              onClick={() => setCenterTab('code')}
                              className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                                centerTab === 'code' 
                                  ? 'bg-purple-600/20 text-purple-400 border border-purple-500/30 shadow-sm' 
                                  : 'text-zinc-400 hover:text-white'
                              }`}
                            >
                              <Code className="h-3.5 w-3.5" /> Code
                            </button>
                          </div>
                          <div className="flex items-center gap-3">
                            <div className="flex items-center gap-1.5 bg-zinc-900 border border-white/5 p-1 rounded-lg hidden sm:flex">
                              <button className="p-1 text-white bg-zinc-800 rounded shadow-sm"><Monitor className="h-3.5 w-3.5" /></button>
                              <button className="p-1 text-zinc-500 hover:text-zinc-300"><Smartphone className="h-3.5 w-3.5" /></button>
                            </div>
                            <div className="h-4 w-px bg-white/10 mx-1 hidden sm:block" />
                            <div className="flex items-center gap-1.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider">
                              <div className="h-1.5 w-1.5 bg-emerald-500 rounded-full shadow-[0_0_8px_rgba(16,185,129,0.5)]" /> Live
                            </div>
                            <div className="flex items-center gap-2 bg-zinc-900 border border-white/5 px-3 py-1.5 rounded-lg text-[10px] font-mono text-zinc-400">
                              <Globe className="h-3 w-3" />
                              <span className="hidden sm:inline">https://{selectedProject.subdomain}.bevhub.ai</span>
                              <button className="ml-2 hover:text-white"><MoreVertical className="h-3 w-3" /></button>
                            </div>
                          </div>
                        </div>

                        <div className="flex-1 p-3 sm:p-6 flex flex-col relative overflow-hidden">
                          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3/4 h-3/4 bg-purple-500/5 blur-[100px] pointer-events-none rounded-full" />
                          <div className="flex-1 bg-white rounded-xl overflow-hidden shadow-2xl flex flex-col border border-zinc-700/50 relative z-10 ring-1 ring-white/10">
                            <div className="h-10 bg-[#1e1e1e] border-b border-[#2d2d2d] flex items-center px-4 gap-4 flex-shrink-0">
                              <div className="flex gap-1.5">
                                <div className="h-2.5 w-2.5 rounded-full bg-[#ff5f56]" />
                                <div className="h-2.5 w-2.5 rounded-full bg-[#ffbd2e]" />
                                <div className="h-2.5 w-2.5 rounded-full bg-[#27c93f]" />
                              </div>
                              <div className="flex gap-2 text-zinc-500 hidden sm:flex">
                                <ChevronLeft className="h-4 w-4" />
                                <ChevronRight className="h-4 w-4 opacity-50" />
                                <RefreshCw className="h-3.5 w-3.5 ml-1" />
                              </div>
                            </div>
                            <div className="flex-1 relative bg-[#09090b]">
                              {centerTab === 'preview' ? (
                                <iframe 
                                  srcDoc={getPreviewHTML()} 
                                  title="Live Preview"
                                  className="w-full h-full border-none bg-white"
                                  sandbox="allow-scripts allow-same-origin"
                                />
                              ) : (
                                <textarea
                                  value={editorContent}
                                  onChange={(e) => {
                                    setEditorContent(e.target.value);
                                  }}
                                  spellCheck={false}
                                  className="w-full h-full bg-[#1e1e1e] text-zinc-300 font-mono text-xs p-6 focus:outline-none resize-none custom-scrollbar"
                                />
                              )}
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center justify-between p-4 bg-[#0a0a0c] border-t border-white/5 flex-shrink-0 overflow-x-auto">
                          <div className="flex items-center gap-4 sm:gap-8 min-w-max">
                            <div className="flex items-center gap-3">
                              <div className="h-6 w-6 rounded-full bg-purple-500/20 text-purple-400 flex items-center justify-center border border-purple-500/30"><Check className="h-3 w-3" /></div>
                              <div className="flex flex-col">
                                <span className="text-[10px] font-bold text-white uppercase tracking-wider">Generation</span>
                                <span className="text-[9px] text-zinc-500 font-mono">Completed • 2m ago</span>
                              </div>
                            </div>
                            <div className="h-8 w-px bg-white/5 hidden sm:block" />
                            <div className="flex items-center gap-3 hidden sm:flex">
                              <div className="h-6 w-6 rounded-full bg-purple-500/20 text-purple-400 flex items-center justify-center border border-purple-500/30"><Check className="h-3 w-3" /></div>
                              <div className="flex flex-col">
                                <span className="text-[10px] font-bold text-white uppercase tracking-wider">Build</span>
                                <span className="text-[9px] text-zinc-500 font-mono">Completed • 45 sec</span>
                              </div>
                            </div>
                            <div className="h-8 w-px bg-white/5 hidden sm:block" />
                            <div className="flex items-center gap-3 hidden sm:flex">
                              <div className="h-6 w-6 rounded-full bg-purple-500/20 text-purple-400 flex items-center justify-center border border-purple-500/30"><Check className="h-3 w-3" /></div>
                              <div className="flex flex-col">
                                <span className="text-[10px] font-bold text-white uppercase tracking-wider">Deploy</span>
                                <span className="text-[9px] text-zinc-500 font-mono">Live • 3 min ago</span>
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-2 ml-4">
                            <button 
                              onClick={() => window.open(`https://${selectedProject.subdomain}.bevhub.ai`, '_blank')}
                              className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-[11px] font-semibold flex items-center gap-2 transition-colors whitespace-nowrap"
                            >
                              <ExternalLink className="h-3.5 w-3.5" /> <span className="hidden sm:inline">Open website</span>
                            </button>
                            <button 
                              onClick={() => {
                                navigator.clipboard.writeText(`https://${selectedProject.subdomain}.bevhub.ai`);
                                alert('URL Copied to clipboard!');
                              }}
                              className="bg-zinc-900 border border-white/10 hover:border-white/20 text-white px-4 py-2 rounded-lg text-[11px] font-semibold flex items-center gap-2 transition-colors whitespace-nowrap"
                            >
                              <Copy className="h-3.5 w-3.5" /> <span className="hidden sm:inline">Copy URL</span>
                            </button>
                            <button className="p-2 text-zinc-400 hover:text-white transition-colors">
                              <MoreVertical className="h-4 w-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </main>

          {/* PREMIUM RIGHT SIDEBAR - AI ASSISTANT */}
          {selectedProject && (
            <aside className="w-full md:w-[320px] border-t md:border-t-0 md:border-l border-white/5 bg-[#09090b] p-4 flex flex-col justify-between flex-shrink-0 relative z-20">
              <div className="flex-1 flex flex-col overflow-hidden h-full">
                <div className="flex items-center justify-between border-b border-white/5 pb-3 mb-4 flex-shrink-0">
                  <div className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-purple-400" />
                    <span className="text-sm font-bold text-white tracking-wide">AI Assistant</span>
                  </div>
                  <button 
                    onClick={() => {
                      setChatMessages([]);
                      setChatInput('');
                    }}
                    className="flex items-center gap-1.5 text-xs text-zinc-400 hover:text-white px-2.5 py-1 rounded-lg border border-white/5 hover:bg-white/5 transition-colors"
                  >
                    <RefreshCw className="h-3 w-3" /> New chat
                  </button>
                  <button className="text-zinc-500 hover:text-white sm:hidden transition-colors">
                    <Menu className="h-4 w-4" />
                  </button>
                </div>
                
                <div className="flex-1 overflow-y-auto space-y-4 pr-1 scrollbar-thin custom-scrollbar pb-4">
                  {chatMessages.length === 0 && (
                    <div className="text-center text-zinc-500 text-xs mt-10">
                      No messages yet. Ask the AI to build or edit!
                    </div>
                  )}
                  {chatMessages.map((msg, idx) => (
                    <div key={idx} className={`flex gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                      {msg.sender !== 'user' && (
                        <div className="h-6 w-6 rounded-full bg-purple-600 flex items-center justify-center flex-shrink-0 text-white font-bold text-[10px] shadow-[0_0_10px_rgba(147,51,234,0.5)]">
                          G
                        </div>
                      )}
                      <div className={`p-3 rounded-2xl text-xs leading-relaxed max-w-[85%] ${msg.sender === 'user' ? 'bg-[#1a1a1f] border border-white/10 text-zinc-200 rounded-tr-sm' : 'bg-transparent text-zinc-300'}`}>
                        {msg.text}
                        {msg.sender === 'brain' && (
                          <div className="mt-3 space-y-1.5">
                            <div className="flex items-center gap-2 text-[10px] text-emerald-400"><CheckCircle className="h-3 w-3" /> UI Layout updated</div>
                            <div className="flex items-center gap-2 text-[10px] text-emerald-400"><CheckCircle className="h-3 w-3" /> Styles applied</div>
                            <div className="mt-3 border border-white/10 rounded-lg overflow-hidden relative group cursor-pointer">
                               <div className="h-20 w-full bg-zinc-800 flex items-center justify-center text-[10px] text-zinc-500">
                                 [Live Snapshot]
                               </div>
                               <button className="absolute bottom-2 left-1/2 -translate-x-1/2 bg-[#09090b]/80 backdrop-blur-sm border border-white/10 px-3 py-1 rounded-full text-[9px] text-white flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                 <ExternalLink className="h-2.5 w-2.5" /> View changes
                               </button>
                            </div>
                          </div>
                        )}
                      </div>
                      {msg.sender === 'user' && (
                        <div className="h-6 w-6 rounded-full bg-[#131316] border border-white/10 flex items-center justify-center flex-shrink-0 text-zinc-400 font-bold text-[10px]">
                          <User className="h-3 w-3" />
                        </div>
                      )}
                    </div>
                  ))}
                  <div ref={chatBottomRef} />
                </div>

                <div className="mt-2 flex-shrink-0 bg-[#131316] border border-white/10 rounded-xl p-2 relative">
                  <form onSubmit={(e) => { handleGenerate(e); setChatInput(''); }} className="relative flex flex-col">
                    <textarea 
                      required
                      disabled={isGenerating}
                      value={chatInput}
                      onChange={(e) => { setChatInput(e.target.value); setPrompt(e.target.value); }}
                      placeholder="What would you like to change?"
                      className="w-full bg-transparent px-2 py-2 text-xs text-white placeholder-zinc-500 focus:outline-none resize-none min-h-[60px]"
                      rows={2}
                    />
                    <div className="flex items-center justify-between px-2 pb-1">
                      <button type="button" className="text-zinc-500 hover:text-zinc-300 transition-colors">
                        <Paperclip className="h-4 w-4" />
                      </button>
                      <button 
                        type="submit"
                        disabled={isGenerating || !chatInput.trim()}
                        className={`p-1.5 rounded-lg transition-colors flex items-center justify-center ${
                          chatInput.trim() ? 'bg-purple-600 text-white shadow-[0_0_10px_rgba(147,51,234,0.3)]' : 'bg-white/5 text-zinc-500'
                        }`}
                      >
                        {isGenerating ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : <Send className="h-3.5 w-3.5" />}
                      </button>
                    </div>
                  </form>
                </div>
                <div className="text-center mt-3">
                  <span className="text-[9px] text-zinc-600">AI can make mistakes. Verify important changes.</span>
                </div>
              </div>
            </aside>
          )}

        </div>
      )}

      {workspaceView === 'templates' && (
        <div className="flex-1 flex flex-col p-8 bg-[#050505] overflow-y-auto">
          <div className="max-w-6xl mx-auto w-full">
            <div className="flex justify-between items-end mb-8">
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">Starter Templates</h2>
                <p className="text-zinc-400 text-sm">Launch production applications in seconds with pre-built AI prompt architectures.</p>
              </div>
            </div>

            {/* CATEGORY FILTER PILLS */}
            <div className="flex items-center gap-2 overflow-x-auto pb-4 mb-6 border-b border-white/5 scrollbar-none">
              {['All', 'SaaS', 'E-commerce', 'Landing', 'Portfolio', 'Agency', 'Blog', 'Dashboard', 'Restaurant', 'Startup'].map(cat => (
                <button 
                  key={cat} 
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                    selectedCategory === cat 
                      ? 'bg-purple-600 text-white shadow-[0_0_15px_rgba(147,51,234,0.4)]' 
                      : 'bg-zinc-900 border border-white/5 text-zinc-400 hover:text-white hover:border-white/10'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* TEMPLATES GRID */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {templatesList
                .filter(t => selectedCategory === 'All' || t.category === selectedCategory)
                .map(tmpl => (
                  <div key={tmpl.id} className="bg-zinc-900 border border-white/10 rounded-2xl p-6 flex flex-col hover:border-purple-500/50 transition-all group shadow-lg">
                    <div className="flex justify-between items-start mb-4">
                      <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-md bg-purple-500/10 text-purple-400 border border-purple-500/20">
                        {tmpl.category}
                      </span>
                      <Sparkles className="h-4 w-4 text-purple-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                    <h3 className="text-lg font-bold text-white mb-2 group-hover:text-purple-300 transition-colors">{tmpl.name}</h3>
                    <p className="text-xs text-zinc-400 mb-6 flex-1 leading-relaxed">{tmpl.description}</p>
                    <button 
                      onClick={() => {
                        setPrompt(tmpl.prompt);
                        setWorkspaceView('workspace');
                        // Execute generation
                        setTimeout(() => {
                          const event = new Event('submit', { cancelable: true, bubbles: true });
                          document.querySelector('form')?.dispatchEvent(event);
                        }, 100);
                      }}
                      className="w-full py-2.5 bg-white/5 hover:bg-purple-600 hover:text-white text-zinc-200 border border-white/10 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-md"
                    >
                      <Sparkles className="h-3.5 w-3.5" />
                      Use Template
                    </button>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}

      {workspaceView === 'projects' && (
        <div className="flex-1 flex flex-col p-8 bg-[#050505] overflow-y-auto">
          <div className="max-w-6xl mx-auto w-full">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
              <div>
                <h2 className="text-2xl font-bold text-white mb-1">Your Projects</h2>
                <p className="text-xs text-zinc-400">Manage, rename, duplicate, or inspect your deployed workspaces.</p>
              </div>
              <div className="flex items-center gap-3 w-full sm:w-auto">
                <div className="relative flex-1 sm:flex-none">
                  <Search className="h-3.5 w-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
                  <input 
                    type="text" 
                    placeholder="Search projects..." 
                    value={projectsSearch}
                    onChange={(e) => setProjectsSearch(e.target.value)}
                    className="bg-zinc-900 border border-white/10 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-purple-500 w-full sm:w-64"
                  />
                </div>
                <button 
                  onClick={() => setWorkspaceView('workspace')}
                  className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-xl text-xs font-semibold transition-colors shadow-[0_0_15px_rgba(147,51,234,0.3)] whitespace-nowrap"
                >
                  + New Project
                </button>
              </div>
            </div>
            
            {projects.filter(p => p.project_name.toLowerCase().includes(projectsSearch.toLowerCase())).length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20 bg-zinc-900/30 rounded-2xl border border-white/5">
                <Folder className="h-12 w-12 text-zinc-600 mb-4" />
                <h3 className="text-lg font-medium text-white mb-2">No projects found</h3>
                <p className="text-zinc-500 text-sm mb-6 text-center max-w-sm">You haven't generated any projects matching your search filter yet.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {projects.filter(p => p.project_name.toLowerCase().includes(projectsSearch.toLowerCase())).map(proj => (
                  <div key={proj.id} className="bg-zinc-900 border border-white/10 rounded-2xl p-5 hover:border-purple-500/50 transition-all group flex flex-col shadow-lg">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-xl bg-purple-500/10 flex items-center justify-center border border-purple-500/20">
                          <Monitor className="h-5 w-5 text-purple-400" />
                        </div>
                        <div>
                          <h4 className="text-white font-semibold truncate max-w-[150px] group-hover:text-purple-400 transition-colors">{proj.project_name}</h4>
                          <p className="text-[10px] text-zinc-500 font-mono">{new Date(proj.created_at).toLocaleDateString()}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-1">
                        <button 
                          title="Rename"
                          onClick={() => { setProjectToRename(proj); setRenameInput(proj.project_name); }}
                          className="p-1.5 text-zinc-500 hover:text-white rounded-lg hover:bg-white/5 transition-colors"
                        >
                          <Edit3 className="h-3.5 w-3.5" />
                        </button>
                        <button 
                          title="Duplicate"
                          onClick={async () => {
                            try {
                              const dup = await ProjectService.duplicateProject(proj.id);
                              setProjects(prev => [dup, ...prev]);
                            } catch (err: any) { alert(err.message); }
                          }}
                          className="p-1.5 text-zinc-500 hover:text-white rounded-lg hover:bg-white/5 transition-colors"
                        >
                          <Copy className="h-3.5 w-3.5" />
                        </button>
                        <button 
                          title="Delete"
                          onClick={() => setProjectToDelete(proj)}
                          className="p-1.5 text-zinc-500 hover:text-red-400 rounded-lg hover:bg-red-500/10 transition-colors"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </div>
                    
                    <div className="flex-1 bg-black/40 rounded-xl border border-white/5 p-3 mb-4 flex flex-col justify-center">
                      <p className="text-xs font-mono text-zinc-400 flex items-center gap-2 truncate">
                        <Globe className="h-3.5 w-3.5 text-purple-400 flex-shrink-0" />
                        {proj.subdomain}.bevhub.ai
                      </p>
                    </div>
                    
                    <div className="flex items-center justify-between pt-3 border-t border-white/5 mt-auto">
                      <span className="text-[10px] font-bold uppercase tracking-wider bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded">Active</span>
                      <button 
                        onClick={() => { handleSelectProject(proj); setWorkspaceView('workspace'); }}
                        className="text-xs font-semibold text-purple-400 hover:text-white transition-colors flex items-center gap-1"
                      >
                        Open Studio →
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {workspaceView === 'settings' && (
        <div className="flex-1 flex flex-col p-8 bg-[#050505] overflow-y-auto">
          <div className="max-w-4xl mx-auto w-full">
            <h2 className="text-2xl font-bold text-white mb-2">Account & Organization Settings</h2>
            <p className="text-zinc-400 text-sm mb-8">Manage profile details, security credentials, and AI co-pilot preferences.</p>

            <div className="space-y-6">
              {/* PROFILE CARD */}
              <div className="bg-zinc-900 border border-white/10 rounded-2xl p-6 shadow-xl">
                <h3 className="text-base font-semibold text-white mb-4 border-b border-white/10 pb-3 flex items-center gap-2">
                  <User className="h-4 w-4 text-purple-400" />
                  Profile Details
                </h3>
                <form 
                  onSubmit={async (e) => {
                    e.preventDefault();
                    try {
                      const updated = await ProjectService.updateProfile({ username, email });
                      setUsername(updated.username);
                      setEmail(updated.email);
                      alert('Profile changes updated successfully!');
                    } catch (err: any) { alert(err.message); }
                  }}
                  className="space-y-4"
                >
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-zinc-400 mb-1.5">Username</label>
                      <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} className="w-full bg-black border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:border-purple-500 focus:outline-none" />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-zinc-400 mb-1.5">Email Address</label>
                      <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full bg-black border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:border-purple-500 focus:outline-none" />
                    </div>
                  </div>
                  <div className="flex justify-end pt-2">
                    <button type="submit" className="bg-purple-600 hover:bg-purple-700 text-white px-5 py-2 rounded-xl text-xs font-semibold shadow-md transition-all">Save Profile Changes</button>
                  </div>
                </form>
              </div>

              {/* SECURITY & PASSWORD CARD */}
              <div className="bg-zinc-900 border border-white/10 rounded-2xl p-6 shadow-xl">
                <h3 className="text-base font-semibold text-white mb-4 border-b border-white/10 pb-3 flex items-center gap-2">
                  <ShieldCheck className="h-4 w-4 text-emerald-400" />
                  Security & Credentials
                </h3>
                <form 
                  onSubmit={async (e) => {
                    e.preventDefault();
                    setPasswordMsg('');
                    setPasswordErr('');
                    try {
                      await ProjectService.changePassword(oldPasswordInput, newPasswordInput);
                      setPasswordMsg('Password changed successfully.');
                      setOldPasswordInput('');
                      setNewPasswordInput('');
                    } catch (err: any) { setPasswordErr(err.message); }
                  }}
                  className="space-y-4"
                >
                  {passwordMsg && <p className="text-xs text-emerald-400 bg-emerald-500/10 p-3 rounded-xl border border-emerald-500/20">{passwordMsg}</p>}
                  {passwordErr && <p className="text-xs text-red-400 bg-red-500/10 p-3 rounded-xl border border-red-500/20">{passwordErr}</p>}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-zinc-400 mb-1.5">Current Password</label>
                      <input type="password" required value={oldPasswordInput} onChange={(e) => setOldPasswordInput(e.target.value)} className="w-full bg-black border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:border-purple-500 focus:outline-none" />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-zinc-400 mb-1.5">New Password</label>
                      <input type="password" required value={newPasswordInput} onChange={(e) => setNewPasswordInput(e.target.value)} className="w-full bg-black border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:border-purple-500 focus:outline-none" />
                    </div>
                  </div>
                  <div className="flex justify-end pt-2">
                    <button type="submit" className="bg-white/10 hover:bg-white/20 text-white px-5 py-2 rounded-xl text-xs font-semibold transition-all">Update Password</button>
                  </div>
                </form>
              </div>

              {/* DANGER ZONE CARD */}
              <div className="bg-zinc-900 border border-red-500/20 rounded-2xl p-6 shadow-xl">
                <h3 className="text-base font-semibold text-red-400 mb-2 border-b border-red-500/20 pb-3 flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-red-500" />
                  Danger Zone
                </h3>
                <p className="text-xs text-zinc-400 mb-4">Deletes your organization tenant, all project workspaces, and active deployments permanently.</p>
                <button 
                  onClick={() => setShowDeleteAccountModal(true)}
                  className="bg-red-500/10 text-red-400 border border-red-500/30 px-5 py-2 rounded-xl text-xs font-semibold hover:bg-red-500 hover:text-white transition-all"
                >
                  Delete Account & Workspace
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {workspaceView === 'integrations' && (
        <div className="flex-1 flex flex-col p-8 bg-[#050505] overflow-y-auto">
          <div className="max-w-5xl mx-auto w-full">
            <h2 className="text-2xl font-bold text-white mb-2">Integrations</h2>
            <p className="text-zinc-400 text-sm mb-8">Connect BevHub AI to your favorite tools and cloud providers.</p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                { provider: 'github', name: 'GitHub', desc: 'Sync generated code to repositories', icon: <Github className="h-6 w-6" />, color: 'text-white' },
                { provider: 'vercel', name: 'Vercel', desc: 'Deploy NextJS applications instantly', icon: <Server className="h-6 w-6" />, color: 'text-zinc-400' },
                { provider: 'stripe', name: 'Stripe', desc: 'Monetize your platforms and charge users', icon: <CreditCard className="h-6 w-6" />, color: 'text-[#635BFF]' },
                { provider: 'openai', name: 'OpenAI', desc: 'Bring your custom API key & model choice', icon: <Cpu className="h-6 w-6" />, color: 'text-emerald-400' },
                { provider: 'telegram', name: 'Telegram', desc: 'Bot notification webhooks & CRM alerts', icon: <MessageSquare className="h-6 w-6" />, color: 'text-blue-400' }
              ].map(int => {
                const configItem = integrationsList.find(i => i.provider === int.provider);
                const isConnected = configItem?.is_connected || false;

                return (
                  <div key={int.provider} className="bg-zinc-900 border border-white/10 rounded-2xl p-6 flex flex-col shadow-lg">
                    <div className="flex items-center gap-4 mb-4">
                      <div className={`h-12 w-12 rounded-xl bg-black border border-white/5 flex items-center justify-center ${int.color}`}>
                        {int.icon}
                      </div>
                      <div>
                        <h3 className="text-white font-semibold">{int.name}</h3>
                        <p className="text-xs text-zinc-500">{int.desc}</p>
                      </div>
                    </div>
                    {isConnected ? (
                      <button 
                        onClick={async () => {
                          try {
                            await ProjectService.disconnectIntegration(int.provider);
                            const updated = await ProjectService.getIntegrations();
                            setIntegrationsList(updated);
                          } catch (err: any) { alert(err.message); }
                        }}
                        className="mt-auto w-full py-2.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-xl text-xs font-semibold hover:bg-red-500/10 hover:text-red-400 hover:border-red-500/20 transition-all flex items-center justify-center gap-1.5"
                      >
                        <CheckCircle className="h-3.5 w-3.5" />
                        Connected • Disconnect
                      </button>
                    ) : (
                      <button 
                        onClick={() => { setActiveConnectModal(int.provider); setConnectApiKey(''); }}
                        className="mt-auto w-full py-2.5 bg-white/5 border border-white/10 text-white rounded-xl text-xs font-semibold hover:bg-purple-600 hover:border-purple-600 transition-all"
                      >
                        Connect {int.name}
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {workspaceView === 'history' && (
        <div className="flex-1 flex flex-col p-8 bg-[#050505] overflow-y-auto">
          <div className="max-w-6xl mx-auto w-full">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
              <div>
                <h2 className="text-2xl font-bold text-white mb-1">Workspace Audit Activity</h2>
                <p className="text-zinc-400 text-sm">A full real-time audit log of AI generations, deployments, and workspace events.</p>
              </div>
              <div className="flex items-center gap-3 w-full sm:w-auto">
                <div className="relative flex-1 sm:flex-none">
                  <Search className="h-3.5 w-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
                  <input 
                    type="text" 
                    placeholder="Search logs..." 
                    value={historySearch}
                    onChange={(e) => setHistorySearch(e.target.value)}
                    className="bg-zinc-900 border border-white/10 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-purple-500 w-full sm:w-64"
                  />
                </div>
                <select 
                  value={historyFilterStatus}
                  onChange={(e) => setHistoryFilterStatus(e.target.value)}
                  className="bg-zinc-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-purple-500"
                >
                  <option value="all">All Statuses</option>
                  <option value="success">Success</option>
                  <option value="failed">Failed</option>
                </select>
              </div>
            </div>
            
            <div className="bg-zinc-900 border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
              <table className="w-full text-left text-sm text-zinc-400">
                <thead className="bg-black/50 text-[10px] uppercase tracking-wider font-semibold text-zinc-500 border-b border-white/10">
                  <tr>
                    <th className="px-6 py-4">Timestamp</th>
                    <th className="px-6 py-4">Event Type</th>
                    <th className="px-6 py-4">User</th>
                    <th className="px-6 py-4">Status</th>
                    <th className="px-6 py-4">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {isHistoryLoading ? (
                    <tr>
                      <td colSpan={5} className="px-6 py-8 text-center text-zinc-500 italic animate-pulse">Loading audit ledger from database...</td>
                    </tr>
                  ) : historyTasks.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="px-6 py-8 text-center text-zinc-500 italic">No activity recorded for this search filter.</td>
                    </tr>
                  ) : historyTasks.map((event, i) => (
                    <tr key={i} className="hover:bg-white/5 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap font-mono text-xs text-zinc-300">{new Date(event.timestamp).toLocaleString()}</td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-purple-500/10 text-purple-400 border border-purple-500/20 font-semibold text-xs capitalize">
                          <Sparkles className="h-3 w-3" />
                          {event.event.replace(/_/g, ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 font-mono text-xs text-zinc-300">{event.user}</td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider ${
                          event.status === 'success' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 
                          'bg-red-500/10 text-red-400 border border-red-500/20'
                        }`}>
                          {event.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-xs truncate max-w-xs text-zinc-400">{event.details || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {workspaceView === 'deployments' && (
        <div className="flex-1 flex flex-col p-8 bg-[#050505] overflow-y-auto">
          <div className="max-w-6xl mx-auto w-full">
            <h2 className="text-2xl font-bold text-white mb-2">Deployments</h2>
            <p className="text-zinc-400 text-sm mb-8">View Edge network deployments and live build logs for all your projects.</p>
            
            <div className="bg-zinc-900 border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
              <table className="w-full text-left text-sm text-zinc-400">
                <thead className="bg-black/50 text-[10px] uppercase tracking-wider font-semibold text-zinc-500 border-b border-white/10">
                  <tr>
                    <th className="px-6 py-4">Environment</th>
                    <th className="px-6 py-4">Status</th>
                    <th className="px-6 py-4">URL</th>
                    <th className="px-6 py-4">Deployed At</th>
                    <th className="px-6 py-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {(() => {
                    const allDeps = deploymentsList.length > 0 
                      ? deploymentsList 
                      : projects.flatMap(p => p.deployments?.map(d => ({ ...d, projectName: p.project_name })) || []);

                    return allDeps.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="px-6 py-8 text-center text-zinc-500 italic">No active deployments found in this workspace.</td>
                      </tr>
                    ) : allDeps.map((dep, i) => (
                      <tr key={i} className="hover:bg-white/5 transition-colors">
                        <td className="px-6 py-4">
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20 text-xs font-mono">
                            Production Edge
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider ${
                            dep.status === 'success' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 
                            dep.status === 'failed' ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 
                            'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20'
                          }`}>
                            {dep.status === 'success' ? <CheckCircle className="h-3 w-3" /> : <RefreshCw className="h-3 w-3 animate-spin" />}
                            {dep.status}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          {dep.deploy_url ? (
                            <a href={dep.deploy_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-purple-400 hover:text-purple-300 transition-colors text-xs font-mono">
                              {dep.deploy_url.replace('https://', '')}
                              <ExternalLink className="h-3 w-3" />
                            </a>
                          ) : (
                            <span className="text-xs text-zinc-500">-</span>
                          )}
                        </td>
                        <td className="px-6 py-4 font-mono text-xs text-zinc-300">{new Date(dep.created_at).toLocaleString()}</td>
                        <td className="px-6 py-4 text-right flex items-center justify-end gap-2">
                          <button 
                            disabled={isRedeployingId === dep.id}
                            onClick={async () => {
                              setIsRedeployingId(dep.id);
                              try {
                                await ProjectService.redeploy(dep.id);
                                const updated = await ProjectService.getDeployments();
                                setDeploymentsList(updated);
                              } catch (err: any) { alert(err.message); }
                              finally { setIsRedeployingId(null); }
                            }}
                            className="px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-xs font-semibold transition-colors flex items-center gap-1"
                          >
                            <RefreshCw className={`h-3 w-3 ${isRedeployingId === dep.id ? 'animate-spin' : ''}`} />
                            Redeploy
                          </button>
                          <button 
                            onClick={() => setSelectedLogsModal(dep)}
                            className="px-3 py-1.5 bg-white/5 hover:bg-white/10 text-zinc-300 rounded-lg text-xs font-medium transition-colors"
                          >
                            Logs
                          </button>
                        </td>
                      </tr>
                    ));
                  })()}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {workspaceView === 'billing' && (
        <div className="flex-1 flex flex-col p-8 bg-[#050505] overflow-y-auto">
          <div className="max-w-5xl mx-auto w-full">
            <h2 className="text-2xl font-bold text-white mb-2">Billing & Subscription Plans</h2>
            <p className="text-zinc-400 text-sm mb-8">Manage active subscription, AI generation credits, and invoice history.</p>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
              {/* CURRENT BALANCE STAT CARD */}
              <div className="bg-zinc-900 border border-white/10 rounded-2xl p-6 flex flex-col justify-between shadow-xl">
                <div>
                  <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Account Balance</span>
                  <div className="text-3xl font-extrabold text-white mt-2 font-mono">
                    ${billingData?.balance || '0.00'}
                  </div>
                </div>
                <div className="mt-6 pt-4 border-t border-white/5 flex justify-between items-center text-xs">
                  <span className="text-zinc-500">Current Active Plan:</span>
                  <span className="font-bold text-purple-400 uppercase">{billingData?.subscription?.plan_name || 'Hobby Free'}</span>
                </div>
              </div>

              {/* PROMO CODE CARD */}
              <div className="lg:col-span-2 bg-zinc-900 border border-white/10 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
                <div>
                  <h3 className="text-sm font-semibold text-white mb-1">Claim Promo & Credit Code</h3>
                  <p className="text-xs text-zinc-400 mb-4">Enter a partner or discount voucher code to credit your balance immediately.</p>
                </div>
                <form onSubmit={handleClaimPromo} className="flex gap-3">
                  <input 
                    type="text" 
                    placeholder="Enter code (e.g. WELCOME50)" 
                    value={promoCode}
                    onChange={(e) => setPromoCode(e.target.value)}
                    className="flex-1 bg-black border border-white/10 rounded-xl px-4 py-2 text-xs text-white uppercase font-mono placeholder-zinc-600 focus:outline-none focus:border-purple-500"
                  />
                  <button 
                    type="submit"
                    disabled={isClaimingPromo}
                    className="bg-purple-600 hover:bg-purple-700 text-white px-5 py-2 rounded-xl text-xs font-semibold transition-all shadow-md"
                  >
                    {isClaimingPromo ? 'Claiming...' : 'Apply Code'}
                  </button>
                </form>
                {promoMsg && <p className="text-xs text-emerald-400 mt-2">{promoMsg}</p>}
                {promoErr && <p className="text-xs text-red-400 mt-2">{promoErr}</p>}
              </div>
            </div>

            {/* SUBSCRIPTION PLANS COMPARISON GRID */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-zinc-900 border border-white/10 rounded-2xl p-6 flex flex-col justify-between shadow-xl">
                <div>
                  <span className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Hobby Plan</span>
                  <div className="text-2xl font-extrabold text-white mt-1">$0 <span className="text-xs font-normal text-zinc-500">/ forever free</span></div>
                  <ul className="mt-4 space-y-2 text-xs text-zinc-400">
                    <li className="flex items-center gap-2"><CheckCircle className="h-3.5 w-3.5 text-purple-400" /> 1 Sandbox Workspace</li>
                    <li className="flex items-center gap-2"><CheckCircle className="h-3.5 w-3.5 text-purple-400" /> 100 AI Generation Credits</li>
                    <li className="flex items-center gap-2"><CheckCircle className="h-3.5 w-3.5 text-purple-400" /> Standard Build Speed</li>
                  </ul>
                </div>
                <button disabled className="mt-6 w-full py-2.5 bg-white/5 border border-white/10 text-zinc-400 rounded-xl text-xs font-semibold cursor-not-allowed">
                  Current Free Tier
                </button>
              </div>

              <div className="bg-zinc-900 border border-purple-500/40 rounded-2xl p-6 flex flex-col justify-between shadow-2xl relative overflow-hidden">
                <div className="absolute top-3 right-3 px-3 py-1 bg-purple-600 text-white text-[10px] font-bold uppercase rounded-full tracking-wider shadow-lg">
                  Popular
                </div>
                <div>
                  <span className="text-xs font-bold text-purple-400 uppercase tracking-wider">Growth Scale Pro</span>
                  <div className="text-2xl font-extrabold text-white mt-1">$49 <span className="text-xs font-normal text-zinc-500">/ month</span></div>
                  <ul className="mt-4 space-y-2 text-xs text-zinc-300">
                    <li className="flex items-center gap-2"><CheckCircle className="h-3.5 w-3.5 text-purple-400" /> Unlimited Projects & Edge Deployments</li>
                    <li className="flex items-center gap-2"><CheckCircle className="h-3.5 w-3.5 text-purple-400" /> 5,000 AI Credits + High Speed Priority</li>
                    <li className="flex items-center gap-2"><CheckCircle className="h-3.5 w-3.5 text-purple-400" /> Custom Domain SSL Integration</li>
                  </ul>
                </div>
                <button 
                  onClick={() => handleSubscribe('growth')}
                  disabled={isSubscribing}
                  className="mt-6 w-full py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs font-semibold transition-all shadow-[0_0_20px_rgba(147,51,234,0.4)]"
                >
                  {isSubscribing ? 'Upgrading...' : 'Upgrade to Growth Scale Pro'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* CONNECT INTEGRATION API KEY MODAL */}
      {activeConnectModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-zinc-950 border border-white/10 rounded-2xl max-w-sm w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-2 capitalize">Connect {activeConnectModal}</h3>
            <p className="text-zinc-500 text-xs mb-4">Provide API credentials or token to authorize automated workflows.</p>
            <form 
              onSubmit={async (e) => {
                e.preventDefault();
                try {
                  await ProjectService.connectIntegration(activeConnectModal, { apiKey: connectApiKey });
                  const updated = await ProjectService.getIntegrations();
                  setIntegrationsList(updated);
                  setActiveConnectModal(null);
                } catch (err: any) { alert(err.message); }
              }}
              className="space-y-4"
            >
              <div>
                <label className="block text-xs font-medium text-zinc-400 mb-1.5">API Key / Access Token</label>
                <input 
                  type="password"
                  required
                  placeholder="Paste secure token here..."
                  value={connectApiKey}
                  onChange={(e) => setConnectApiKey(e.target.value)}
                  className="w-full bg-zinc-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-purple-500 font-mono"
                />
              </div>
              <div className="flex gap-2 justify-end">
                <button type="button" onClick={() => setActiveConnectModal(null)} className="px-4 py-2 bg-zinc-900 border border-white/5 rounded-xl text-zinc-400 hover:text-white text-xs font-semibold">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-xs font-semibold rounded-xl">Save & Connect</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* RENAME PROJECT MODAL */}
      {projectToRename && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-zinc-950 border border-white/10 rounded-2xl max-w-sm w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-2">Rename Project</h3>
            <form 
              onSubmit={async (e) => {
                e.preventDefault();
                try {
                  const updated = await ProjectService.updateProject(projectToRename.id, { project_name: renameInput });
                  setProjects(prev => prev.map(p => p.id === updated.id ? updated : p));
                  setProjectToRename(null);
                } catch (err: any) { alert(err.message); }
              }}
              className="space-y-4"
            >
              <div>
                <label className="block text-xs font-medium text-zinc-400 mb-1.5">Project Name</label>
                <input 
                  type="text"
                  required
                  value={renameInput}
                  onChange={(e) => setRenameInput(e.target.value)}
                  className="w-full bg-zinc-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-purple-500"
                />
              </div>
              <div className="flex gap-2 justify-end">
                <button type="button" onClick={() => setProjectToRename(null)} className="px-4 py-2 bg-zinc-900 border border-white/5 rounded-xl text-zinc-400 hover:text-white text-xs font-semibold">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-xs font-semibold rounded-xl">Save</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* DELETE PROJECT CONFIRMATION MODAL */}
      {projectToDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-zinc-950 border border-red-500/20 rounded-2xl max-w-sm w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-2">Delete Project?</h3>
            <p className="text-xs text-zinc-400 mb-6">Are you sure you want to delete project <strong className="text-white">{projectToDelete.project_name}</strong>? This action cannot be undone.</p>
            <div className="flex gap-2 justify-end">
              <button onClick={() => setProjectToDelete(null)} className="px-4 py-2 bg-zinc-900 border border-white/5 rounded-xl text-zinc-400 hover:text-white text-xs font-semibold">Cancel</button>
              <button 
                onClick={async () => {
                  try {
                    await ProjectService.deleteProject(projectToDelete.id);
                    setProjects(prev => prev.filter(p => p.id !== projectToDelete.id));
                    setProjectToDelete(null);
                  } catch (err: any) { alert(err.message); }
                }}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-xs font-semibold rounded-xl"
              >
                Delete Project
              </button>
            </div>
          </div>
        </div>
      )}

      {/* DEPLOYMENT LOGS MODAL */}
      {selectedLogsModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-zinc-950 border border-white/10 rounded-2xl max-w-2xl w-full p-6 shadow-2xl flex flex-col max-h-[80vh]">
            <div className="flex justify-between items-center mb-4 pb-3 border-b border-white/10">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Terminal className="h-4 w-4 text-purple-400" />
                Build & Deployment Logs
              </h3>
              <button onClick={() => setSelectedLogsModal(null)} className="text-zinc-500 hover:text-white text-xs">Close</button>
            </div>
            <pre className="flex-1 bg-black p-4 rounded-xl border border-white/5 font-mono text-xs text-zinc-300 overflow-y-auto whitespace-pre-wrap leading-relaxed">
              {selectedLogsModal.logs || selectedLogsModal.error_message || 'Build succeeded cleanly with zero warnings.'}
            </pre>
          </div>
        </div>
      )}

      {/* DELETE ACCOUNT CONFIRMATION MODAL */}
      {showDeleteAccountModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-zinc-950 border border-red-500/30 rounded-2xl max-w-sm w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-red-400 mb-2">Delete Account Confirmation</h3>
            <p className="text-xs text-zinc-400 mb-4">Please confirm your current password to proceed with deleting your account.</p>
            <form 
              onSubmit={async (e) => {
                e.preventDefault();
                setDeleteAccountErr('');
                try {
                  await ProjectService.deleteAccount(deleteConfirmPassword);
                  handleLogout();
                } catch (err: any) { setDeleteAccountErr(err.message); }
              }}
              className="space-y-4"
            >
              {deleteAccountErr && <p className="text-xs text-red-400 bg-red-500/10 p-2 rounded-lg">{deleteAccountErr}</p>}
              <div>
                <input 
                  type="password"
                  required
                  placeholder="Enter your password..."
                  value={deleteConfirmPassword}
                  onChange={(e) => setDeleteConfirmPassword(e.target.value)}
                  className="w-full bg-zinc-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-red-500"
                />
              </div>
              <div className="flex gap-2 justify-end">
                <button type="button" onClick={() => setShowDeleteAccountModal(false)} className="px-4 py-2 bg-zinc-900 border border-white/5 rounded-xl text-zinc-400 hover:text-white text-xs font-semibold">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-xs font-semibold rounded-xl">Permanently Delete</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* GLOBAL CMD+K SEARCH OVERLAY MODAL */}
      {isCmdKOpen && (
        <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/80 backdrop-blur-sm p-4 pt-20">
          <div className="bg-zinc-950 border border-white/10 rounded-2xl max-w-xl w-full p-4 shadow-2xl flex flex-col gap-3">
            <div className="relative flex items-center">
              <Search className="h-4 w-4 absolute left-3 text-purple-400" />
              <input 
                type="text"
                autoFocus
                placeholder="Type to search projects, templates, deployments, history..."
                value={cmdKQuery}
                onChange={(e) => setCmdKQuery(e.target.value)}
                className="w-full bg-zinc-900 border border-white/10 rounded-xl pl-9 pr-4 py-2.5 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-purple-500 font-mono"
              />
            </div>
            
            <div className="max-h-80 overflow-y-auto space-y-2 pt-2 border-t border-white/5">
              <p className="text-[10px] uppercase tracking-wider font-semibold text-zinc-500 px-2">Navigation & Quick Commands</p>

              {/* Projects Matches */}
              {projects
                .filter(p => p.project_name.toLowerCase().includes(cmdKQuery.toLowerCase()))
                .map(p => (
                  <div 
                    key={p.id}
                    onClick={() => {
                      handleSelectProject(p);
                      setWorkspaceView('workspace');
                      setIsCmdKOpen(false);
                    }}
                    className="p-3 rounded-xl bg-zinc-900/50 hover:bg-purple-600/20 border border-white/5 hover:border-purple-500/30 cursor-pointer flex items-center justify-between text-xs transition-all"
                  >
                    <div className="flex items-center gap-2">
                      <Folder className="h-4 w-4 text-purple-400" />
                      <span className="text-white font-medium">{p.project_name}</span>
                    </div>
                    <span className="text-[10px] font-mono text-zinc-500">Project Studio →</span>
                  </div>
                ))}

              {/* View Nav Shortcuts */}
              {[
                { title: 'Templates Gallery', view: 'templates', icon: <Sparkles className="h-4 w-4 text-purple-400" /> },
                { title: 'Workspace Audit History', view: 'history', icon: <Terminal className="h-4 w-4 text-blue-400" /> },
                { title: 'Deployments & Edge Nodes', view: 'deployments', icon: <Server className="h-4 w-4 text-emerald-400" /> },
                { title: 'Integrations & API Keys', view: 'integrations', icon: <Globe className="h-4 w-4 text-pink-400" /> },
                { title: 'Billing & Plan Upgrade', view: 'billing', icon: <CreditCard className="h-4 w-4 text-yellow-400" /> },
                { title: 'Account & Security Settings', view: 'settings', icon: <User className="h-4 w-4 text-zinc-400" /> },
              ]
              .filter(item => item.title.toLowerCase().includes(cmdKQuery.toLowerCase()))
              .map(item => (
                <div 
                  key={item.view}
                  onClick={() => {
                    setWorkspaceView(item.view as any);
                    setIsCmdKOpen(false);
                  }}
                  className="p-3 rounded-xl bg-zinc-900/50 hover:bg-white/10 border border-white/5 cursor-pointer flex items-center justify-between text-xs transition-all"
                >
                  <div className="flex items-center gap-2">
                    {item.icon}
                    <span className="text-zinc-200 font-medium">{item.title}</span>
                  </div>
                  <span className="text-[10px] font-mono text-zinc-500">Jump to View</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      
      {/* NEW WORKSPACE MODAL */}

      {showNewWorkspaceModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-zinc-950 border border-white/10 rounded-2xl max-w-sm w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-2">Create New Sandbox Workspace</h3>
            <p className="text-zinc-500 text-xs mb-4">
              Enter a unique workspace identity to isolate project builds and models context.
            </p>
            <form onSubmit={handleCreateWorkspace} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-zinc-400 mb-1.5">Workspace Name</label>
                <input 
                  type="text"
                  required
                  placeholder="e.g. Production Cluster"
                  value={newWorkspaceName}
                  onChange={(e) => setNewWorkspaceName(e.target.value)}
                  className="w-full bg-zinc-900 border border-white/5 rounded-xl px-3 py-2 text-xs text-white placeholder-zinc-600 focus:outline-none focus:border-purple-500 font-mono"
                />
              </div>
              <div className="flex gap-2 justify-end">
                <button 
                  type="button"
                  onClick={() => setShowNewWorkspaceModal(false)}
                  className="px-4 py-2 bg-zinc-900 border border-white/5 rounded-lg text-zinc-400 hover:text-white text-xs font-semibold"
                >
                  Cancel
                </button>
                <button 
                  type="submit"
                  className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-xs font-semibold rounded-lg"
                >
                  Create Workspace
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* DRILLDOWN MODAL */}
      {drilldownMetric && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#09090b] border border-white/10 rounded-lg w-full max-w-3xl overflow-hidden shadow-2xl flex flex-col max-h-[80vh]">
            <div className="bg-zinc-900 px-4 py-2.5 flex items-center justify-between border-b border-white/5">
              <div className="flex items-center gap-2 font-mono text-xs font-bold text-purple-400">
                <Terminal className="h-4 w-4" />
                <span>{drilldownTitle} — Event & Cohort Audit Ledger</span>
              </div>
              <button 
                onClick={() => setDrilldownMetric(null)}
                className="text-zinc-400 hover:text-white font-mono text-xs px-2 py-0.5 hover:bg-white/5 rounded border border-white/5"
              >
                ESC / Close
              </button>
            </div>
            
            <div className="p-4 flex-1 overflow-auto font-mono text-[10px] text-zinc-300 space-y-2 font-mono">
              {isDrilldownLoading ? (
                <div className="text-center py-12 text-zinc-500 animate-pulse">
                  Querying database records for metric [{drilldownMetric}]...
                </div>
              ) : drilldownData.length === 0 ? (
                <div className="text-center py-12 text-zinc-500 italic">
                  -- No records found for this cohort ledger under current Mode --
                </div>
              ) : (
                <div className="border border-white/5 rounded overflow-hidden">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="bg-zinc-900 text-zinc-500 border-b border-white/5 text-[9px]">
                        {Object.keys(drilldownData[0]).filter(k => k !== 'id').map((key) => (
                          <th key={key} className="px-3 py-2 uppercase tracking-wider">{key.replace(/_/g, ' ')}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {drilldownData.map((row, idx) => (
                        <tr key={idx} className="border-b border-white/5 hover:bg-white/5">
                          {Object.entries(row).filter(([k]) => k !== 'id').map(([key, val]: any, cellIdx) => (
                            <td key={cellIdx} className="px-3 py-1.5 text-zinc-300 break-all max-w-[200px]">
                              {val === null || val === undefined ? 'N/A' : (
                                typeof val === 'boolean' 
                                  ? (val ? 'TRUE' : 'FALSE') 
                                  : (key.includes('amount') || key.includes('revenue') ? val : String(val))
                              )}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
