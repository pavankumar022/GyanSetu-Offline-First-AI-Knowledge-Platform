import React, { useState, useEffect, useRef } from 'react';
import {
  DashboardIcon,
  ChatIcon,
  KnowledgePacksIcon,
  SyncIcon,
  SettingsIcon,
  CloudOffIcon,
  StorageIcon,
  SearchIcon,
  UpdateIcon,
  SuccessIcon,
  ErrorIcon,
  DownloadIcon,
  AutoAwesomeIcon,
  ArrowForwardIcon,
  HistoryIcon,
  EditSquareIcon,
  SmartToyIcon,
  DescriptionIcon,
  PolicyIcon,
  AttachFileIcon,
  SendIcon,
  VerifiedIcon,
  CloseIcon,
  OpenInNewIcon,
  ExpandMoreIcon,
  SdStorageIcon,
  LanguageIcon,
  NotificationsIcon,
  ShieldPersonIcon,
  CalendarIcon,
  VisibilityIcon,
  CleaningServicesIcon,
  InfoIcon,
  PackIcon
} from './components/Icons';

const API_BASE = 'http://localhost:8001/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('Dashboard');
  const [localStatus, setLocalStatus] = useState({
    installed_packs: [],
    storage_used_gb: 4.2,
    storage_total_gb: 16,
    storage_percent: 26.3,
    last_sync_time: '2 hours ago',
    offline_mode: false,
    queries_count: 1248
  });
  
  const [cloudPacks, setCloudPacks] = useState([]);
  const [syncHistory, setSyncHistory] = useState([]);
  const [syncUpdates, setSyncUpdates] = useState([]);
  const [isSyncChecking, setIsSyncChecking] = useState(false);
  const [errorToast, setErrorToast] = useState(null);
  
  // Chat state
  const [chats, setChats] = useState([
    { id: 1, title: 'Agricultural Subsidy FAQ', excerpt: 'Details regarding the newly announced...', date: 'Today' },
    { id: 2, title: 'Rural Health Guidelines', excerpt: 'Standard operating procedures for...', date: 'Today' },
    { id: 3, title: 'Water Conservation Setup', excerpt: 'Step-by-step guide to installing...', date: 'Yesterday' }
  ]);
  const [activeChatId, setActiveChatId] = useState(1);
  const [chatMessages, setChatMessages] = useState({
    1: [
      { sender: 'user', text: 'What are the eligibility criteria for the recent agricultural subsidy aimed at marginal farmers in the eastern district?' },
      {
        sender: 'ai',
        text: 'Based on the localized knowledge pack for the Eastern District (v.2.4), the eligibility criteria for the Marginal Farmer Agricultural Subsidy are as follows:\n\n• **Land Holding**: Must own and cultivate less than 2 hectares (approx. 5 acres) of land.\n• **Residency**: Must be a registered resident of the designated eastern district for at least 5 consecutive years.\n• **Crop Type**: The subsidy primarily targets farmers cultivating drought-resistant crops or engaging in approved multi-cropping practices.\n• **Income Threshold**: Total annual household income from all sources must not exceed ₹1,50,000.\n\nApplicants must provide a valid Farmer ID and recent land records to the local agricultural extension office during the application window.',
        citations: [
          { title: 'Min. of Agriculture Order 2023-A', filepath: 'KP-AGRI-ED-09/soil_health.txt', excerpt: '...subsidy intended for marginal farmers owning < 2 ha. Must prove 5-yr residency...', confidence: 98 },
          { title: 'District Subsidy Guidelines v2.4', filepath: 'KP-AGRI-ED-09/pest_control.txt', excerpt: '...Income cap set at ₹1.5L p.a. from all aggregated sources for eligibility...', confidence: 95 }
        ]
      }
    ],
    2: [
      { sender: 'user', text: 'Tell me about rural medical emergency protocol.' },
      {
        sender: 'ai',
        text: 'Rural medical guidelines outline basic emergency SOPs including first-aid for heat stroke (shading, cool damp cloth) and snake bites (immobilization, transport). Refer to rural health guidelines pack.',
        citations: []
      }
    ],
    3: [
      { sender: 'user', text: 'How to harvest rainwater in rural areas?' },
      {
        sender: 'ai',
        text: 'Rainwater harvesting in rural areas involves setting up a basic catchment surface, filter media, and offline storage tanks. Consult water conservation pack.',
        citations: []
      }
    ]
  });
  
  const [currentMessage, setCurrentMessage] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeCitation, setActiveCitation] = useState(null);
  const [quickAskText, setQuickAskText] = useState('');
  
  // Modals
  const [viewingFullDoc, setViewingFullDoc] = useState(null);
  
  // Search state
  const [packSearchQuery, setPackSearchQuery] = useState('');

  // Fetch status on startup and intervals
  useEffect(() => {
    fetchLocalStatus();
    fetchCloudPacks();
    fetchSyncHistory();
  }, []);

  const showToast = (message) => {
    setErrorToast(message);
    setTimeout(() => setErrorToast(null), 5000);
  };

  const fetchLocalStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/local/status`);
      if (res.ok) {
        const data = await res.json();
        setLocalStatus(data);
      }
    } catch (e) {
      console.error('Error fetching local status', e);
    }
  };

  const fetchCloudPacks = async () => {
    try {
      const res = await fetch(`${API_BASE}/packs`);
      if (res.ok) {
        const data = await res.json();
        setCloudPacks(data);
      } else if (res.status === 503) {
        setCloudPacks([]);
      }
    } catch (e) {
      console.error('Error fetching cloud packs', e);
    }
  };

  const fetchSyncHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/sync/history`);
      if (res.ok) {
        const data = await res.json();
        setSyncHistory(data);
      } else if (res.status === 503) {
        setSyncHistory([]);
      }
    } catch (e) {
      console.error('Error fetching sync history', e);
    }
  };

  const handleToggleOffline = async (newOfflineState) => {
    try {
      const res = await fetch(`${API_BASE}/local/toggle-offline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ offline: newOfflineState })
      });
      if (res.ok) {
        const data = await res.json();
        setLocalStatus(prev => ({ ...prev, offline_mode: data.offline }));
        if (data.offline) {
          showToast('Simulated Offline Mode enabled. Cloud server is unreachable.');
          setCloudPacks([]);
          setSyncHistory([]);
        } else {
          showToast('Online mode active. Synchronized with simulated cloud server.');
          fetchCloudPacks();
          fetchSyncHistory();
        }
      }
    } catch (e) {
      console.error('Error toggling offline mode', e);
    }
  };

  const handleSendMessage = async (e) => {
    if (e) e.preventDefault();
    if (!currentMessage.trim()) return;

    const userMsgText = currentMessage;
    setCurrentMessage('');
    
    // Add to state
    const currentChatMsgs = chatMessages[activeChatId] || [];
    const updatedMessages = [...currentChatMsgs, { sender: 'user', text: userMsgText }];
    setChatMessages({
      ...chatMessages,
      [activeChatId]: updatedMessages
    });

    setIsGenerating(true);
    
    try {
      const res = await fetch(`${API_BASE}/local/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsgText })
      });
      
      if (res.ok) {
        const data = await res.json();
        setChatMessages(prev => ({
          ...prev,
          [activeChatId]: [...updatedMessages, {
            sender: 'ai',
            text: data.answer,
            citations: data.citations || []
          }]
        }));
        
        // Auto-select first citation if available
        if (data.citations && data.citations.length > 0) {
          setActiveCitation(data.citations[0]);
        } else {
          setActiveCitation(null);
        }
      } else {
        setChatMessages(prev => ({
          ...prev,
          [activeChatId]: [...updatedMessages, {
            sender: 'ai',
            text: 'Error generating offline AI response. Please ensure local storage database is initialized.',
            citations: []
          }]
        }));
      }
    } catch (e) {
      setChatMessages(prev => ({
        ...prev,
        [activeChatId]: [...updatedMessages, {
          sender: 'ai',
          text: 'Local AI process is unreachable. Check backend terminal.',
          citations: []
        }]
      }));
    } finally {
      setIsGenerating(false);
      fetchLocalStatus(); // refresh query counts
    }
  };

  const handleQuickAsk = () => {
    if (!quickAskText.trim()) return;
    
    // Create new chat
    const newId = chats.length + 1;
    const title = quickAskText.length > 25 ? quickAskText.substring(0, 25) + '...' : quickAskText;
    setChats([{ id: newId, title: title, excerpt: quickAskText, date: 'Today' }, ...chats]);
    setChatMessages({
      ...chatMessages,
      [newId]: [{ sender: 'user', text: quickAskText }]
    });
    setActiveChatId(newId);
    setQuickAskText('');
    setActiveTab('Chat / Ask AI');
    
    // Trigger response after activeTab switches and focus happens
    setTimeout(() => {
      // Simulate click send trigger
      setCurrentMessage(quickAskText);
    }, 100);
  };

  useEffect(() => {
    if (activeTab === 'Chat / Ask AI' && currentMessage) {
      handleSendMessage();
    }
  }, [activeTab]);

  const handleDownloadPack = async (packId) => {
    try {
      showToast(`Downloading pack ${packId}...`);
      const res = await fetch(`${API_BASE}/local/sync-pack/${packId}`, {
        method: 'POST'
      });
      if (res.ok) {
        showToast(`Successfully downloaded pack ${packId}. Indexed in vector store.`);
        fetchLocalStatus();
        fetchCloudPacks();
        fetchSyncHistory();
      } else {
        const err = await res.json();
        showToast(`Sync failed: ${err.detail}`);
      }
    } catch (e) {
      showToast('Network error: cloud server is unreachable.');
    }
  };

  const handleDeletePack = async (packId) => {
    try {
      const res = await fetch(`${API_BASE}/local/delete-pack/${packId}`, {
        method: 'POST'
      });
      if (res.ok) {
        showToast(`Deleted pack ${packId} from device.`);
        fetchLocalStatus();
        fetchCloudPacks();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const checkDeltaUpdates = async () => {
    if (localStatus.offline_mode) {
      showToast('Cannot check for updates while offline.');
      return;
    }
    setIsSyncChecking(true);
    try {
      const installedInfo = localStatus.installed_packs.map(p => ({ id: p.id, version: p.version }));
      const res = await fetch(`${API_BASE}/sync/check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ installed_packs: installedInfo })
      });
      if (res.ok) {
        const data = await res.json();
        setSyncUpdates(data.updates);
        if (data.updates.length === 0) {
          showToast('All local packs are up to date!');
        } else {
          showToast(`Found ${data.updates.length} updates available.`);
        }
      }
    } catch (e) {
      showToast('Error checking for updates.');
    } finally {
      setIsSyncChecking(false);
    }
  };

  const handleSyncAll = async () => {
    if (localStatus.offline_mode) {
      showToast('Cannot sync. Offline mode active.');
      return;
    }
    
    // Pull updates first
    try {
      const installedInfo = localStatus.installed_packs.map(p => ({ id: p.id, version: p.version }));
      const checkRes = await fetch(`${API_BASE}/sync/check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ installed_packs: installedInfo })
      });
      
      if (checkRes.ok) {
        const checkData = await checkRes.json();
        const updatesList = checkData.updates;
        
        if (updatesList.length === 0) {
          showToast('Already up to date.');
          return;
        }
        
        // Sync each updated pack
        for (const update of updatesList) {
          await handleDownloadPack(update.pack_id);
        }
        
        setSyncUpdates([]);
      }
    } catch (e) {
      showToast('Error performing sync.');
    }
  };

  const handleFreeSpace = async () => {
    try {
      const res = await fetch(`${API_BASE}/local/clear-space`, { method: 'POST' });
      if (res.ok) {
        showToast('Local cache and sync history cleared.');
        fetchLocalStatus();
        fetchSyncHistory();
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Helper to check if pack is installed on device
  const getPackInstallationState = (packId) => {
    const installed = localStatus.installed_packs.find(p => p.id === packId);
    if (!installed) return 'Not Downloaded';
    
    // Check if there is an update
    const cloudCopy = cloudPacks.find(p => p.id === packId);
    if (cloudCopy && cloudCopy.version !== installed.version) {
      return 'Needs Update';
    }
    return 'Installed';
  };

  // Filter cloud packs by search query
  const filteredPacks = (cloudPacks.length > 0 ? cloudPacks : [
    { id: 'KP-AGRI-ED-09', title: 'Agricultural Best Practices & Crop Data', icon: 'agriculture', category: 'Agriculture', version: 'v2.0', size_mb: 850 },
    { id: 'KP-SCHOLAR-2024', title: 'Government Scholarship Schemes 2024', icon: 'account_balance', category: 'Education', version: 'v2.1', size_mb: 420 },
    { id: 'KP-HEALTH-RURAL', title: 'Rural Healthcare First-Aid Guide', icon: 'local_hospital', category: 'Healthcare', version: 'v1.0', size_mb: 1228 },
    { id: 'KP-EDU-PRIMARY', title: 'Primary Education Curriculum Offline', icon: 'school', category: 'Education', version: 'v1.2', size_mb: 2450 },
    { id: 'KP-LEGAL-BASIC', title: 'Basic Legal Rights & Procedures Manual', icon: 'gavel', category: 'Governance', version: 'v3.4', size_mb: 620 }
  ]).filter(p => p.title.toLowerCase().includes(packSearchQuery.toLowerCase()));

  // Dynamic Navigation setup
  const navItems = [
    { name: 'Dashboard', icon: <DashboardIcon /> },
    { name: 'Chat / Ask AI', icon: <ChatIcon /> },
    { name: 'Knowledge Packs', icon: <KnowledgePacksIcon /> },
    { name: 'Sync & Updates', icon: <SyncIcon /> },
    { name: 'Settings', icon: <SettingsIcon /> }
  ];

  return (
    <div className="bg-background text-on-surface flex min-h-screen font-body-md w-full selection:bg-primary-container selection:text-on-primary-container">
      
      {/* Toast Alert */}
      {errorToast && (
        <div className="fixed bottom-6 right-6 z-[999] max-w-md bg-inverse-surface text-inverse-on-surface px-6 py-4 rounded-xl shadow-lg border border-outline-variant flex items-center gap-3 animate-bounce">
          <InfoIcon className="text-secondary-container" />
          <span className="font-semibold text-sm">{errorToast}</span>
        </div>
      )}

      {/* SideNavBar (Shared Component) */}
      <nav aria-label="Main Navigation" className="hidden md:flex flex-col h-full w-[240px] py-gutter px-4 bg-surface border-r border-outline-variant shadow-sm fixed left-0 top-0 z-50">
        <div className="mb-8 px-4 flex flex-col">
          <h1 className="font-headline-md text-headline-md font-bold text-primary">GyanSetu</h1>
          <span className="font-label-sm text-label-sm text-on-surface-variant font-medium">Offline AI Knowledge</span>
        </div>
        
        <div className="flex-1 space-y-2">
          {navItems.map(item => {
            const isActive = activeTab === item.name;
            return (
              <button
                key={item.name}
                onClick={() => setActiveTab(item.name)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-all duration-200 ease-in-out active:scale-95 ${
                  isActive 
                    ? 'bg-primary-container text-on-primary-container font-bold shadow-sm' 
                    : 'text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface'
                }`}
              >
                {React.cloneElement(item.icon, { 
                  className: isActive ? 'text-on-primary-container' : 'text-outline' 
                })}
                <span className="font-label-sm text-label-sm">{item.name}</span>
              </button>
            );
          })}
        </div>

        {/* Side Storage Widget */}
        <div className="mt-auto px-4 py-4 border-t border-outline-variant flex flex-col gap-2">
          <div className="flex items-center justify-between font-label-sm text-label-sm text-on-surface-variant font-semibold">
            <span className="flex items-center gap-2">
              <StorageIcon size={16} />
              Local Storage
            </span>
            <span className="text-primary">{localStatus.storage_percent}%</span>
          </div>
          <div className="w-full bg-surface-container-highest rounded-full h-2">
            <div 
              className="bg-primary-container h-2 rounded-full transition-all duration-500" 
              style={{ width: `${localStatus.storage_percent}%` }}
            ></div>
          </div>
          <p className="text-[11px] text-on-surface-variant">{localStatus.storage_used_gb}GB used of {localStatus.storage_total_gb}GB</p>
        </div>
      </nav>

      {/* Main Content Area */}
      <div className="flex-1 md:ml-[240px] flex flex-col min-h-screen w-full">
        
        {/* TopAppBar (Shared Component) */}
        <header className="flex justify-between items-center px-container-padding h-16 z-40 bg-surface border-b border-outline-variant shadow-sm w-full sticky top-0">
          <div>
            <h2 className="font-title-sm text-title-sm font-bold text-primary">{activeTab}</h2>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              <label htmlFor="offline-toggle" className="font-label-sm text-label-sm text-on-surface-variant font-semibold cursor-pointer">
                Simulate Offline
              </label>
              <button 
                id="offline-toggle"
                onClick={() => handleToggleOffline(!localStatus.offline_mode)}
                className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                  localStatus.offline_mode ? 'bg-secondary-container' : 'bg-primary-container'
                }`}
              >
                <span 
                  className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                    localStatus.offline_mode ? 'translate-x-5' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>

            <div className="flex items-center">
              {localStatus.offline_mode ? (
                <span className="inline-flex items-center px-3 py-1 rounded-full bg-secondary-container/10 border border-secondary-container/40 text-on-secondary-container font-label-sm text-label-sm font-semibold">
                  <span className="w-2 h-2 rounded-full bg-[#feae2c] mr-2 animate-pulse"></span>
                  Offline Mode
                </span>
              ) : (
                <span className="inline-flex items-center px-3 py-1 rounded-full bg-primary-container text-[#acf4a4] font-label-sm text-label-sm font-semibold">
                  <span className="w-2 h-2 rounded-full bg-[#acf4a4] mr-2"></span>
                  Online — Synced
                </span>
              )}
            </div>
          </div>
        </header>

        {/* Dynamic Canvas Container */}
        <main className="flex-1 p-container-padding pb-24 w-full bg-background overflow-y-auto">
          <div className="max-w-max-content-width mx-auto w-full">

            {/* TAB CONTENT: DASHBOARD */}
            {activeTab === 'Dashboard' && (
              <div className="space-y-gutter w-full">
                {/* Stats row */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-gutter w-full">
                  <div className="bg-surface-container-lowest rounded-xl p-6 shadow-sm border border-outline-variant flex flex-col gap-2">
                    <div className="flex items-center gap-2 text-on-surface-variant mb-2">
                      <KnowledgePacksIcon className="text-outline" />
                      <span className="font-label-sm text-label-sm font-semibold">Packs Installed</span>
                    </div>
                    <div className="font-display-lg text-display-lg text-on-surface">{localStatus.installed_packs.length} Packs</div>
                  </div>
                  
                  <div className="bg-surface-container-lowest rounded-xl p-6 shadow-sm border border-outline-variant flex flex-col gap-2">
                    <div className="flex items-center gap-2 text-on-surface-variant mb-2">
                      <StorageIcon className="text-outline" />
                      <span className="font-label-sm text-label-sm font-semibold">Storage Used</span>
                    </div>
                    <div className="font-display-lg text-display-lg text-on-surface">{localStatus.storage_used_gb}GB</div>
                    <div className="w-full bg-surface-variant rounded-full h-2 mt-2">
                      <div className="bg-primary-container h-2 rounded-full" style={{ width: `${localStatus.storage_percent}%` }}></div>
                    </div>
                    <span className="font-label-sm text-label-sm text-on-surface-variant">of {localStatus.storage_total_gb}GB total</span>
                  </div>

                  <div className="bg-surface-container-lowest rounded-xl p-6 shadow-sm border border-outline-variant flex flex-col gap-2">
                    <div className="flex items-center gap-2 text-on-surface-variant mb-2">
                      <SyncIcon className="text-outline" />
                      <span className="font-label-sm text-label-sm font-semibold">Last Synced</span>
                    </div>
                    <div className="font-display-lg text-display-lg text-on-surface leading-tight truncate">{localStatus.last_sync_time}</div>
                  </div>

                  <div className="bg-surface-container-lowest rounded-xl p-6 shadow-sm border border-outline-variant flex flex-col gap-2">
                    <div className="flex items-center gap-2 text-on-surface-variant mb-2">
                      <ChatIcon className="text-outline" />
                      <span className="font-label-sm text-label-sm font-semibold">Offline Queries</span>
                    </div>
                    <div className="font-display-lg text-display-lg text-on-surface">{localStatus.queries_count}</div>
                  </div>
                </div>

                {/* Main Content row */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter w-full">
                  {/* Recent Activity */}
                  <div className="lg:col-span-7 bg-surface-container-lowest rounded-xl p-6 shadow-sm border border-outline-variant flex flex-col h-full">
                    <h3 className="font-title-sm text-title-sm text-primary mb-6 flex items-center gap-2 border-b border-outline-variant pb-3">
                      <HistoryIcon />
                      Recent Sync & Updates Activity
                    </h3>
                    <div className="flex flex-col gap-4 flex-1">
                      {syncHistory.length === 0 ? (
                        <div className="flex flex-col items-center justify-center p-8 text-on-surface-variant bg-surface rounded-lg">
                          <p>No recent synchronization logs available.</p>
                          {localStatus.offline_mode && <p className="text-xs mt-1 text-error">Connect to simulated server to view cloud logs.</p>}
                        </div>
                      ) : (
                        syncHistory.map((item, i) => (
                          <div key={item.id || i} className="flex gap-4 items-start pb-4 border-b border-outline-variant last:border-b-0">
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                              item.status === 'Success' ? 'bg-[#E8F5E9] text-[#2E7D32]' : 'bg-[#FFEBEE] text-[#C62828]'
                            }`}>
                              <SuccessIcon size={18} />
                            </div>
                            <div className="flex-1">
                              <p className="font-body-lg text-body-lg text-on-surface">{item.pack_title}</p>
                              <p className="font-body-md text-body-md text-on-surface-variant">{item.details}</p>
                            </div>
                            <span className="font-label-sm text-label-sm text-on-surface-variant whitespace-nowrap">{item.timestamp}</span>
                          </div>
                        ))
                      )}
                    </div>
                  </div>

                  {/* Quick Ask */}
                  <div className="lg:col-span-5 bg-surface-container-lowest rounded-xl overflow-hidden shadow-sm border border-outline-variant flex flex-col">
                    <div className="h-40 bg-gradient-to-br from-primary-container to-[#0c5216] flex items-center justify-center relative overflow-hidden">
                      <div className="absolute inset-0 opacity-10 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-white via-transparent to-transparent"></div>
                      <AutoAwesomeIcon size={64} className="text-primary-fixed z-10" />
                    </div>
                    <div className="p-6 flex flex-col gap-4">
                      <h3 className="font-title-sm text-title-sm text-primary">Quick Ask AI</h3>
                      <p className="font-body-md text-body-md text-on-surface-variant mb-2">Query your offline knowledge base instantly.</p>
                      
                      <div className="relative w-full">
                        <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 text-outline" />
                        <input 
                          type="text" 
                          placeholder="Ask AI anything..." 
                          value={quickAskText}
                          onChange={(e) => setQuickAskText(e.target.value)}
                          onKeyDown={(e) => { if (e.key === 'Enter') handleQuickAsk(); }}
                          className="w-full pl-10 pr-4 py-3 rounded-lg border border-outline-variant bg-surface focus:ring-2 focus:ring-primary-container focus:border-primary-container font-body-md text-body-md outline-none transition-all"
                        />
                      </div>
                      
                      <button 
                        onClick={handleQuickAsk}
                        className="w-full mt-2 py-3 bg-[#F5A623] hover:bg-[#e0951f] text-white rounded-lg font-label-numeric text-label-numeric transition-colors flex items-center justify-center gap-2 shadow-sm font-semibold"
                      >
                        <span>Ask Now</span>
                        <ArrowForwardIcon size={18} />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* TAB CONTENT: CHAT / ASK AI */}
            {activeTab === 'Chat / Ask AI' && (
              <div className="fixed top-16 right-0 w-[calc(100%-240px)] h-[calc(100vh-64px)] flex bg-surface-bright overflow-hidden">
                {/* Chat History Panel (20%) */}
                <aside className="w-1/5 border-r border-outline-variant bg-surface flex flex-col h-full shrink-0">
                  <div className="p-4 border-b border-outline-variant flex justify-between items-center bg-surface-container-lowest shadow-sm z-10 relative">
                    <h3 className="font-title-sm text-title-sm text-on-surface font-bold">History</h3>
                    <button 
                      onClick={() => {
                        const newId = chats.length + 1;
                        setChats([{ id: newId, title: 'New Chat', excerpt: 'Ask offline query...', date: 'Today' }, ...chats]);
                        setChatMessages({ ...chatMessages, [newId]: [] });
                        setActiveChatId(newId);
                      }}
                      className="p-1.5 rounded hover:bg-surface-container-high transition-colors text-primary"
                    >
                      <EditSquareIcon />
                    </button>
                  </div>
                  
                  <div className="flex-1 overflow-y-auto custom-scrollbar p-3 flex flex-col gap-2">
                    <span className="font-label-sm text-label-sm text-on-surface-variant px-2 pt-2 pb-1 uppercase tracking-wider font-semibold">Today</span>
                    {chats.filter(c => c.date === 'Today').map(chat => {
                      const isActive = activeChatId === chat.id;
                      return (
                        <div 
                          key={chat.id}
                          onClick={() => { setActiveChatId(chat.id); setActiveCitation(null); }}
                          className={`p-3 rounded-lg cursor-pointer border flex flex-col gap-1 transition-all ${
                            isActive 
                              ? 'bg-surface-container-high border-outline-variant border-l-4 border-l-primary' 
                              : 'bg-surface-container-lowest border-transparent hover:border-outline-variant hover:bg-surface-container-low'
                          }`}
                        >
                          <h4 className="font-body-md text-body-md font-semibold text-on-surface truncate">{chat.title}</h4>
                          <span className="text-xs text-on-surface-variant truncate">{chat.excerpt}</span>
                        </div>
                      );
                    })}

                    <span className="font-label-sm text-label-sm text-on-surface-variant px-2 pt-4 pb-1 uppercase tracking-wider font-semibold">Yesterday</span>
                    {chats.filter(c => c.date === 'Yesterday').map(chat => {
                      const isActive = activeChatId === chat.id;
                      return (
                        <div 
                          key={chat.id}
                          onClick={() => { setActiveChatId(chat.id); setActiveCitation(null); }}
                          className={`p-3 rounded-lg cursor-pointer border flex flex-col gap-1 transition-all ${
                            isActive 
                              ? 'bg-surface-container-high border-outline-variant border-l-4 border-l-primary' 
                              : 'bg-surface-container-lowest border-transparent hover:border-outline-variant hover:bg-surface-container-low'
                          }`}
                        >
                          <h4 className="font-body-md text-body-md font-semibold text-on-surface truncate">{chat.title}</h4>
                          <span className="text-xs text-on-surface-variant truncate">{chat.excerpt}</span>
                        </div>
                      );
                    })}
                  </div>
                </aside>

                {/* Conversation Box (50% or 80% depending on Citation details) */}
                <section className="flex-1 flex flex-col h-full bg-background relative z-0">
                  {/* Messages list */}
                  <div className="flex-1 overflow-y-auto custom-scrollbar p-6 flex flex-col gap-6">
                    <div className="flex items-center justify-center my-2">
                      <div className="bg-surface-container-high px-3 py-1 rounded-full border border-outline-variant text-xs text-on-surface-variant font-medium">
                        Today
                      </div>
                    </div>

                    {(chatMessages[activeChatId] || []).length === 0 ? (
                      <div className="flex-1 flex flex-col items-center justify-center p-12 text-center text-on-surface-variant">
                        <AutoAwesomeIcon size={48} className="text-primary-container mb-4" />
                        <h4 className="font-title-sm text-title-sm text-on-surface mb-2 font-bold">Ask GyanSetu Offline AI</h4>
                        <p className="max-w-md text-sm">Enter a question below. The system will consult the vector index on your local storage to generate a cited response completely offline.</p>
                      </div>
                    ) : (
                      (chatMessages[activeChatId] || []).map((msg, index) => (
                        <div key={index} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                          {msg.sender === 'user' ? (
                            <div className="bg-surface-container border border-outline-variant text-on-surface p-4 rounded-xl rounded-tr-sm max-w-[85%] shadow-sm">
                              <p className="font-body-md text-body-md whitespace-pre-wrap">{msg.text}</p>
                            </div>
                          ) : (
                            <div className="bg-surface-container-lowest border border-outline-variant text-on-surface p-5 rounded-xl rounded-tl-sm max-w-[90%] shadow-sm flex flex-col gap-4">
                              <div className="flex items-center gap-2 mb-1">
                                <div className="w-6 h-6 rounded bg-primary-container text-on-primary-container flex items-center justify-center shrink-0">
                                  <SmartToyIcon size={14} className="text-[#acf4a4]" />
                                </div>
                                <span className="font-label-sm text-label-sm font-bold text-primary">GyanSetu AI</span>
                              </div>
                              
                              <div className="font-body-md text-body-md whitespace-pre-wrap leading-relaxed text-on-surface break-words space-y-3">
                                {msg.text}
                              </div>

                              {/* Citation chips */}
                              {msg.citations && msg.citations.length > 0 && (
                                <div className="flex flex-wrap gap-2 pt-2 border-t border-outline-variant mt-2">
                                  {msg.citations.map((cite, ci) => {
                                    const isSelected = activeCitation && activeCitation.filepath === cite.filepath;
                                    return (
                                      <button 
                                        key={ci}
                                        onClick={() => setActiveCitation(cite)}
                                        className={`inline-flex items-center gap-1.5 px-2.5 py-1.5 border rounded-md text-xs font-medium transition-colors cursor-pointer group shadow-sm ${
                                          isSelected
                                            ? 'bg-primary/10 border-primary/40 text-primary'
                                            : 'bg-surface-container-high hover:bg-surface-variant border-outline-variant text-on-surface-variant'
                                        }`}
                                      >
                                        <DescriptionIcon size={12} className={isSelected ? 'text-primary' : 'text-outline'} />
                                        <span className="whitespace-normal break-words text-left font-semibold">{cite.title}</span>
                                      </button>
                                    );
                                  })}
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      ))
                    )}

                    {isGenerating && (
                      <div className="flex justify-start">
                        <div className="bg-surface-container-lowest border border-outline-variant text-on-surface p-5 rounded-xl rounded-tl-sm max-w-[90%] shadow-sm flex flex-col gap-4 opacity-70">
                          <div className="flex items-center gap-2 mb-1">
                            <div className="w-6 h-6 rounded bg-primary-container text-on-primary-container flex items-center justify-center shrink-0">
                              <SmartToyIcon size={14} className="text-[#acf4a4]" />
                            </div>
                            <span className="font-label-sm text-label-sm font-bold text-primary">GyanSetu AI</span>
                          </div>
                          <div className="flex gap-1 items-center h-5">
                            <span className="w-2 h-2 rounded-full bg-outline-variant animate-pulse"></span>
                            <span className="w-2 h-2 rounded-full bg-outline-variant animate-pulse delay-75"></span>
                            <span className="w-2 h-2 rounded-full bg-outline-variant animate-pulse delay-150"></span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Message Input Box */}
                  <div className="p-4 bg-surface border-t border-outline-variant shadow-md z-10">
                    <form onSubmit={handleSendMessage} className="flex flex-col gap-2 max-w-4xl mx-auto">
                      <div className="relative flex items-end gap-2 bg-surface-container-lowest border border-outline-variant rounded-xl p-2 focus-within:border-primary focus-within:ring-1 focus-within:ring-primary transition-all shadow-sm">
                        <button type="button" className="p-2 text-on-surface-variant hover:text-primary hover:bg-surface-container-high rounded-lg transition-colors shrink-0">
                          <AttachFileIcon />
                        </button>
                        <textarea 
                          value={currentMessage}
                          onChange={(e) => setCurrentMessage(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                              e.preventDefault();
                              handleSendMessage();
                            }
                          }}
                          placeholder="Ask a question about the loaded knowledge packs..."
                          rows="1"
                          className="w-full bg-transparent border-none focus:ring-0 resize-none max-h-32 min-h-[44px] py-3 px-2 font-body-md text-body-md text-on-surface placeholder:text-on-surface-variant outline-none custom-scrollbar"
                        />
                        <button 
                          type="submit" 
                          disabled={isGenerating || !currentMessage.trim()}
                          className="p-3 bg-primary text-on-primary rounded-lg hover:bg-primary/90 transition-colors shrink-0 shadow-sm flex items-center justify-center h-[44px] w-[44px] disabled:opacity-50"
                        >
                          <SendIcon />
                        </button>
                      </div>
                      <div className="flex justify-between items-center px-2">
                        <span className="text-[10px] text-on-surface-variant font-semibold">Press Enter to send, Shift+Enter for new line.</span>
                        <div className="flex gap-2">
                          <span className="text-[10px] bg-surface-container-high px-1.5 py-0.5 rounded border border-outline-variant text-on-surface-variant font-semibold">Model: Offline-Instruct-v3 (Phi-3 fallback)</span>
                        </div>
                      </div>
                    </form>
                  </div>
                </section>

                {/* Source Verification Sidebar (30%) */}
                {activeCitation && (
                  <aside className="w-[30%] border-l border-outline-variant bg-surface flex flex-col h-full shrink-0 shadow-[-4px_0_12px_rgba(0,0,0,0.02)] z-10 relative">
                    <div className="p-4 border-b border-outline-variant flex justify-between items-center bg-surface-container-lowest shadow-sm z-10">
                      <h3 className="font-title-sm text-title-sm text-on-surface flex items-center gap-2 font-bold">
                        <VerifiedIcon className="text-primary" />
                        Source Verification
                      </h3>
                      <button onClick={() => setActiveCitation(null)} className="p-1 rounded hover:bg-surface-container-high text-on-surface-variant transition-colors">
                        <CloseIcon />
                      </button>
                    </div>
                    
                    <div className="flex-1 overflow-y-auto custom-scrollbar p-5 flex flex-col gap-6 bg-surface-bright">
                      <div className="bg-surface-container-lowest border border-primary/30 rounded-xl overflow-hidden shadow-sm">
                        <div className="bg-primary/5 px-4 py-3 border-b border-primary/20 flex items-start gap-3">
                          <PolicyIcon className="text-primary mt-0.5" />
                          <div className="flex flex-col">
                            <h4 className="font-body-md text-body-md font-bold text-primary leading-tight break-words">{activeCitation.title}</h4>
                            <span className="text-xs text-on-surface-variant mt-1">Section excerpt details</span>
                          </div>
                        </div>
                        
                        <div className="p-4 flex flex-col gap-4">
                          <div>
                            <span className="text-xs font-semibold uppercase tracking-wider text-on-surface-variant mb-2 block">Extracted Text</span>
                            <div className="bg-surface-container border-l-4 border-l-secondary-container p-3 rounded-r text-xs text-on-surface font-mono leading-relaxed whitespace-pre-wrap break-words">
                              "{activeCitation.excerpt}"
                            </div>
                          </div>
                          
                          <div>
                            <span className="text-xs font-semibold uppercase tracking-wider text-on-surface-variant mb-2 block">Document Metadata</span>
                            <div className="grid grid-cols-1 gap-y-2 border border-outline-variant rounded-lg p-3 bg-surface text-xs">
                              <div className="flex border-b border-outline-variant pb-2">
                                <span className="w-1/3 text-on-surface-variant font-medium">Source Path</span>
                                <span className="w-2/3 text-on-surface break-words font-mono text-[10px] bg-surface-container px-1 py-0.5 rounded">{activeCitation.filepath}</span>
                              </div>
                              <div className="flex border-b border-outline-variant pb-2 pt-1">
                                <span className="w-1/3 text-on-surface-variant font-medium">Synced version</span>
                                <span className="w-2/3 text-on-surface font-semibold text-primary">Verified Cryptographically</span>
                              </div>
                              <div className="flex pt-1 items-center">
                                <span className="w-1/3 text-on-surface-variant font-medium">Retrieval Match</span>
                                <div className="w-2/3 flex items-center gap-2">
                                  <div className="flex-1 h-1.5 bg-surface-variant rounded-full overflow-hidden">
                                    <div className="h-full bg-primary-container" style={{ width: `${activeCitation.confidence}%` }}></div>
                                  </div>
                                  <span className="text-xs font-bold text-primary">{activeCitation.confidence}%</span>
                                </div>
                              </div>
                            </div>
                          </div>
                          
                          <button 
                            onClick={() => setViewingFullDoc(activeCitation)}
                            className="w-full py-2 bg-surface-container-high hover:bg-surface-variant border border-outline-variant rounded-lg text-sm font-semibold text-on-surface transition-colors flex items-center justify-center gap-2 mt-2"
                          >
                            <VisibilityIcon size={18} />
                            View Full Document
                          </button>
                        </div>
                      </div>
                    </div>
                  </aside>
                )}
              </div>
            )}

            {/* TAB CONTENT: KNOWLEDGE PACKS */}
            {activeTab === 'Knowledge Packs' && (
              <div className="space-y-gutter w-full">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4 mb-6">
                  <div>
                    <h3 className="font-headline-md text-headline-md text-on-surface mb-2 font-bold">Available &amp; Installed Packs</h3>
                    <p className="font-body-md text-body-md text-on-surface-variant max-w-2xl">
                      Manage your offline knowledge repositories. Download packs to ensure access without internet connectivity. Update existing packs to get the latest information.
                    </p>
                  </div>
                  
                  <div className="relative">
                    <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant" />
                    <input 
                      type="text" 
                      placeholder="Search packs..."
                      value={packSearchQuery}
                      onChange={(e) => setPackSearchQuery(e.target.value)}
                      className="pl-10 pr-4 py-2 bg-surface-container-lowest border border-outline-variant rounded-lg font-body-md text-body-md text-on-surface focus:outline-none focus:border-primary-container focus:ring-1 focus:ring-primary-container transition-shadow w-64"
                    />
                  </div>
                </div>

                {/* Packs Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-gutter w-full">
                  {filteredPacks.map(pack => {
                    const status = getPackInstallationState(pack.id);
                    return (
                      <div key={pack.id} className="bg-surface-container-lowest rounded-xl p-6 shadow-sm border border-outline-variant flex flex-col h-full hover:shadow-md transition-shadow">
                        <div className="flex justify-between items-start mb-4">
                          <div className="p-3 bg-surface-container rounded-lg text-primary">
                            <PackIcon name={pack.icon} size={30} />
                          </div>
                          <span className={`px-2.5 py-0.5 rounded text-xs font-bold border ${
                            status === 'Installed' 
                              ? 'bg-[#E8F5E9] text-[#2E7D32] border-[#A5D6A7]' 
                              : status === 'Needs Update'
                                ? 'bg-secondary-container/10 text-on-secondary-container border-secondary-container/30'
                                : 'bg-surface-container-high border-outline-variant text-on-surface-variant'
                          }`}>
                            {status}
                          </span>
                        </div>
                        
                        <h4 className="font-title-sm text-title-sm text-on-surface mb-2 font-bold flex-grow">{pack.title}</h4>
                        
                        <div className="flex flex-col gap-3 mt-4 pt-4 border-t border-surface-variant">
                          <div className="flex justify-between items-center font-label-sm text-label-sm text-on-surface-variant font-semibold">
                            <span>Version: {
                              status === 'Needs Update' 
                                ? `${localStatus.installed_packs.find(p => p.id === pack.id)?.version} → ${pack.version}`
                                : pack.version
                            }</span>
                            <span>{pack.size_mb}MB</span>
                          </div>
                          
                          {status === 'Installed' && (
                            <div className="flex gap-2 w-full">
                              <button className="flex-1 py-2 px-4 rounded-lg bg-surface-container-highest text-on-surface-variant font-semibold font-label-sm text-label-sm flex items-center justify-center gap-1.5 cursor-default opacity-70">
                                <SuccessIcon size={14} className="text-primary" />
                                Up to Date
                              </button>
                              <button 
                                onClick={() => handleDeletePack(pack.id)}
                                className="p-2 bg-error/10 hover:bg-error/20 text-error rounded-lg transition-colors"
                                title="Remove Pack"
                              >
                                <CloseIcon size={14} />
                              </button>
                            </div>
                          )}
                          
                          {status === 'Needs Update' && (
                            <button 
                              onClick={() => handleDownloadPack(pack.id)}
                              className="w-full py-2 px-4 rounded-lg bg-[#F5A623] hover:bg-[#E09612] text-white font-semibold font-label-sm text-label-sm flex items-center justify-center gap-1.5 transition-colors shadow-sm"
                            >
                              <UpdateIcon size={14} />
                              Update Available
                            </button>
                          )}
                          
                          {status === 'Not Downloaded' && (
                            <button 
                              onClick={() => handleDownloadPack(pack.id)}
                              disabled={localStatus.offline_mode}
                              className="w-full py-2 px-4 rounded-lg bg-primary-container text-on-primary border border-primary-container font-semibold font-label-sm text-label-sm flex items-center justify-center gap-1.5 hover:bg-primary transition-colors shadow-sm disabled:opacity-50"
                            >
                              <DownloadIcon size={14} />
                              Download Pack
                            </button>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* TAB CONTENT: SYNC & UPDATES */}
            {activeTab === 'Sync & Updates' && (
              <div className="flex flex-col md:flex-row gap-gutter w-full">
                {/* Left Column */}
                <section className="w-full md:w-[40%] flex flex-col gap-stack-gap">
                  <div className="bg-surface-container-lowest rounded-xl p-6 shadow-sm border border-outline-variant flex flex-col">
                    <div className="flex items-center gap-3 mb-6">
                      <SyncIcon className="text-primary animate-spin" />
                      <h3 className="font-title-sm text-title-sm text-on-surface font-bold">Storage &amp; Sync Status</h3>
                    </div>
                    
                    <div className="mb-8">
                      <div className="flex justify-between items-end mb-2">
                        <span className="font-body-md text-body-md text-on-surface-variant font-medium">Local Storage Used</span>
                        <span className="font-label-numeric text-label-numeric text-on-surface font-bold">
                          {localStatus.storage_used_gb}GB <span className="font-body-md text-body-md text-on-surface-variant font-normal">of {localStatus.storage_total_gb}GB</span>
                        </span>
                      </div>
                      <div className="w-full bg-surface-container h-2 rounded-full overflow-hidden">
                        <div className="bg-primary-container h-full rounded-full transition-all duration-500" style={{ width: `${localStatus.storage_percent}%` }}></div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between mb-8 pb-6 border-b border-surface-variant">
                      <div>
                        <p className="font-title-sm text-title-sm text-on-surface mb-1 font-bold">Wi-Fi Only Sync</p>
                        <p className="font-body-md text-body-md text-on-surface-variant">Prevent data charges on mobile networks</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" defaultChecked className="sr-only peer" />
                        <div className="w-11 h-6 bg-surface-variant peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-container"></div>
                      </label>
                    </div>

                    <div className="flex flex-col gap-2">
                      <button 
                        onClick={checkDeltaUpdates}
                        disabled={localStatus.offline_mode || isSyncChecking}
                        className="w-full bg-surface border border-outline text-primary font-bold py-3 px-6 rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                      >
                        <SearchIcon size={18} />
                        Check for Updates
                      </button>
                      <button 
                        onClick={handleSyncAll}
                        disabled={localStatus.offline_mode}
                        className="w-full bg-[#F5A623] hover:bg-[#E09612] text-white font-title-sm text-title-sm py-3 px-6 rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-50 font-bold shadow-sm"
                      >
                        <UpdateIcon size={18} />
                        Update All Available
                      </button>
                    </div>
                    <p className="text-center font-label-sm text-label-sm text-on-surface-variant mt-4 font-semibold">Last Checked: {localStatus.last_sync_time}</p>
                  </div>
                </section>

                {/* Right Column */}
                <section className="w-full md:w-[60%] flex flex-col">
                  <div className="bg-surface-container-lowest rounded-xl p-6 shadow-sm border border-outline-variant flex flex-col h-full">
                    <div className="flex items-center gap-3 mb-6">
                      <HistoryIcon className="text-primary" />
                      <h3 className="font-title-sm text-title-sm text-on-surface font-bold">Sync History</h3>
                    </div>
                    
                    <div className="overflow-x-auto custom-scrollbar">
                      <table className="w-full text-left border-collapse">
                        <thead>
                          <tr className="border-b border-surface-variant">
                            <th className="py-3 px-4 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">Timestamp</th>
                            <th className="py-3 px-4 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">Knowledge Pack</th>
                            <th className="py-3 px-4 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">Status</th>
                            <th className="py-3 px-4 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold text-right">Data Size</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-surface-variant">
                          {syncHistory.length === 0 ? (
                            <tr>
                              <td colSpan="4" className="py-8 text-center text-on-surface-variant">No sync records found.</td>
                            </tr>
                          ) : (
                            syncHistory.map((log, li) => (
                              <tr key={log.id || li} className="hover:bg-surface-container-low transition-colors">
                                <td className="py-4 px-4 font-body-md text-body-md text-on-surface font-semibold">{log.timestamp}</td>
                                <td className="py-4 px-4 font-body-md text-body-md text-on-surface font-semibold">{log.pack_title}</td>
                                <td className="py-4 px-4">
                                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full font-label-sm text-label-sm font-bold text-white ${
                                    log.status === 'Success' ? 'bg-[#2E7D32]' : 'bg-[#C62828]'
                                  }`}>
                                    {log.status}
                                  </span>
                                </td>
                                <td className="py-4 px-4 font-label-numeric text-label-numeric text-on-surface text-right font-bold">{log.size_mb} MB</td>
                              </tr>
                            ))
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </section>
              </div>
            )}

            {/* TAB CONTENT: SETTINGS */}
            {activeTab === 'Settings' && (
              <div className="flex gap-gutter flex-1 items-stretch w-full">
                {/* Left Pane Categories (30%) */}
                <aside className="w-[30%] min-w-[280px] bg-surface-container-lowest shadow-sm rounded-xl p-6 flex flex-col gap-2 border border-outline-variant">
                  <button className="w-full flex items-center gap-3 p-4 rounded-lg bg-primary-container text-on-primary-container text-left transition-colors font-bold shadow-sm">
                    <SdStorageIcon className="text-on-primary-container" />
                    <span className="font-label-numeric text-label-numeric font-bold">Storage &amp; Data</span>
                  </button>
                  <button className="w-full flex items-center gap-3 p-4 rounded-lg text-on-surface hover:bg-surface-container-high text-left transition-colors font-semibold">
                    <LanguageIcon className="text-outline" />
                    <span className="font-body-md text-body-md">Language &amp; Region</span>
                  </button>
                  <button className="w-full flex items-center gap-3 p-4 rounded-lg text-on-surface hover:bg-surface-container-high text-left transition-colors font-semibold">
                    <NotificationsIcon className="text-outline" />
                    <span className="font-body-md text-body-md">Notifications</span>
                  </button>
                  <button className="w-full flex items-center gap-3 p-4 rounded-lg text-on-surface hover:bg-surface-container-high text-left transition-colors font-semibold">
                    <ShieldPersonIcon className="text-outline" />
                    <span className="font-body-md text-body-md">Account &amp; Security</span>
                  </button>
                </aside>

                {/* Right Pane Detail Panel (70%) */}
                <section className="flex-1 bg-surface-container-lowest shadow-sm rounded-xl p-6 border border-outline-variant flex flex-col">
                  <header className="mb-8 flex items-center gap-3 border-b border-outline-variant pb-4">
                    <SdStorageIcon size={30} className="text-primary-container" />
                    <h2 className="font-headline-md text-headline-md text-on-surface font-bold">Storage Management</h2>
                  </header>
                  
                  <div className="grid grid-cols-1 xl:grid-cols-2 gap-12 mb-12 items-center">
                    {/* SVG Donut Chart */}
                    <div className="flex flex-col items-center justify-center p-8 bg-surface rounded-xl border border-outline-variant">
                      <div className="relative w-48 h-48 mb-6">
                        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                          <path 
                            className="text-surface-variant stroke-current" 
                            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" 
                            fill="none" 
                            strokeWidth="3.5"
                          ></path>
                          <path 
                            className="text-primary-container stroke-current" 
                            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" 
                            fill="none" 
                            strokeWidth="4"
                            strokeDasharray={`${localStatus.storage_percent}, 100`}
                            strokeLinecap="round"
                          ></path>
                        </svg>
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                          <span className="font-display-lg text-display-lg text-on-surface">{localStatus.storage_percent}%</span>
                          <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider mt-1 font-semibold">Utilized</span>
                        </div>
                      </div>
                    </div>
                    
                    {/* Stats details */}
                    <div className="flex flex-col justify-center gap-6">
                      <div className="flex justify-between items-baseline border-b border-outline-variant pb-4">
                        <div>
                          <p className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider mb-1 font-semibold">Total Used</p>
                          <p className="font-display-lg text-display-lg text-primary flex items-baseline gap-2">
                            {localStatus.storage_used_gb} <span className="font-title-sm text-title-sm text-on-surface-variant">GB</span>
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider mb-1 font-semibold">Total Free</p>
                          <p className="font-display-lg text-display-lg text-on-surface flex items-baseline gap-2 justify-end">
                            {roundValue(localStatus.storage_total_gb - localStatus.storage_used_gb)} <span className="font-title-sm text-title-sm text-on-surface-variant font-bold">GB</span>
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex flex-col gap-4 mt-2">
                        <h3 className="font-title-sm text-title-sm text-on-surface font-bold">Allocation Breakdown</h3>
                        
                        <div className="flex items-center justify-between p-3 rounded-lg hover:bg-surface border border-transparent hover:border-outline-variant">
                          <div className="flex items-center gap-3">
                            <div className="w-3 h-3 rounded-full bg-primary-container"></div>
                            <span className="font-body-md text-body-md font-semibold">Knowledge Packs</span>
                          </div>
                          <span className="font-label-numeric text-label-numeric font-bold">3.1 GB</span>
                        </div>

                        <div className="flex items-center justify-between p-3 rounded-lg hover:bg-surface border border-transparent hover:border-outline-variant">
                          <div className="flex items-center gap-3">
                            <div className="w-3 h-3 rounded-full bg-[#feae2c]"></div>
                            <span className="font-body-md text-body-md font-semibold">Chat History &amp; Logs</span>
                          </div>
                          <span className="font-label-numeric text-label-numeric font-bold">0.8 GB</span>
                        </div>

                        <div className="flex items-center justify-between p-3 rounded-lg hover:bg-surface border border-transparent hover:border-outline-variant">
                          <div className="flex items-center gap-3">
                            <div className="w-3 h-3 rounded-full bg-[#dbdad7]"></div>
                            <span className="font-body-md text-body-md font-semibold">System / Cache</span>
                          </div>
                          <span className="font-label-numeric text-label-numeric font-bold">0.3 GB</span>
                        </div>
                      </div>

                      <div className="mt-4 pt-4 border-t border-outline-variant flex justify-end">
                        <button 
                          onClick={handleFreeSpace}
                          className="px-6 py-2.5 rounded-lg bg-surface border border-outline text-primary font-bold hover:bg-surface-container-high transition-colors flex items-center gap-2"
                        >
                          <CleaningServicesIcon size={16} />
                          Free Up Space
                        </button>
                      </div>
                    </div>
                  </div>
                </section>
              </div>
            )}

          </div>
        </main>
      </div>

      {/* FULL DOCUMENT VIEWING MODAL */}
      {viewingFullDoc && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
          <div className="bg-surface-container-lowest w-full max-w-[720px] rounded-xl shadow-lg border border-outline-variant flex flex-col max-h-[90vh] overflow-hidden animate-in fade-in zoom-in duration-200">
            {/* Header */}
            <div className="flex justify-between items-start p-container-padding border-b border-outline-variant shrink-0">
              <div>
                <h2 className="font-headline-md text-headline-md text-on-surface mb-2 font-bold">{viewingFullDoc.title}</h2>
                <div className="flex items-center gap-4 text-on-surface-variant font-label-sm text-label-sm font-semibold">
                  <span className="flex items-center gap-1">
                    <VerifiedIcon size={14} className="text-primary" />
                    Cryptographically Verified
                  </span>
                  <span className="flex items-center gap-1">
                    <CalendarIcon size={14} />
                    October 2023
                  </span>
                </div>
              </div>
              <button 
                onClick={() => setViewingFullDoc(null)} 
                className="text-on-surface-variant hover:text-on-surface transition-colors p-2 rounded-full hover:bg-surface-container-high"
              >
                <CloseIcon />
              </button>
            </div>
            
            {/* Body */}
            <div className="p-container-padding overflow-y-auto grow custom-scrollbar">
              <div className="prose max-w-none text-on-surface">
                <h3 className="font-title-sm text-title-sm text-on-surface mb-4 font-bold">Document Excerpt</h3>
                <p className="font-body-md text-body-md text-on-surface-variant whitespace-pre-line leading-relaxed">
                  {viewingFullDoc.excerpt}
                  {"\n\n"}
                  This policy outlines strategic agricultural interventions aimed at rural digital empowerment. Standard agricultural advisories prioritize soil health improvement, teacher-guided farming methods, and the deployment of local vector indices. Funding allocations target structural compost enhancements, bio-fertilizer usage, and pest-deterrent cropping configurations. The guidelines mandate block-level reviews to verify implementation efficacy.
                  {"\n\n"}
                  Furthermore, community-driven agricultural centers are established to foster ownership, linking localized extension workers to technical databases concerning fertilizers and pest remedies in connectivity-deprived environments.
                </p>
              </div>
              
              <div className="mt-8 p-4 bg-surface-container-high rounded-lg border border-outline-variant flex gap-4 items-start">
                <InfoIcon className="text-primary mt-0.5 flex-shrink-0" />
                <div>
                  <h4 className="font-label-sm text-label-sm text-on-surface font-bold mb-1">Verification Status</h4>
                  <p className="font-body-md text-body-md text-on-surface-variant">This document has been fully synced and cryptographically verified against the national repository offline cache.</p>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="p-container-padding border-t border-outline-variant shrink-0 flex justify-end gap-3 bg-surface">
              <button 
                onClick={() => setViewingFullDoc(null)}
                className="px-6 py-2 rounded-lg font-semibold font-label-sm text-label-sm text-primary border border-primary hover:bg-surface-container-high transition-colors"
              >
                Close
              </button>
              <button className="px-6 py-2 rounded-lg font-semibold font-label-sm text-label-sm bg-primary-container text-on-primary hover:opacity-90 transition-opacity flex items-center gap-2">
                <VisibilityIcon size={16} />
                Open Original PDF
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

// Math rounded values helper
function roundValue(val) {
  return Math.round(val * 10) / 10;
}
