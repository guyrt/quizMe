// tabTracker.ts

type TabInfo = {
    tabId: number;
    startTime: number;
    endTime: number | null;
  };
  
  class TabTracker {
    private tabs: Map<number, TabInfo>;
    private currentTabId: number | null;
  
    constructor() {
      this.tabs = new Map();
      this.currentTabId = null;
  
      // Listen for tab activated events
      chrome.tabs.onActivated.addListener(this.onTabActivated.bind(this));
  
      // Listen for tab removed events
      chrome.tabs.onRemoved.addListener(this.onTabRemoved.bind(this));
 
      chrome.windows.onFocusChanged.addListener(this.onFocusChanged.bind(this));

      chrome.windows.onRemoved.addListener(this.onWindowRemoved.bind(this));

      chrome.idle.setDetectionInterval(15); // Set the idle detection interval in seconds
      chrome.idle.onStateChanged.addListener(this.onIdleState.bind(this));

      // Initialize tracking for the current tab
      this.initCurrentTab();
    }
  
    private async initCurrentTab() {
      const queryOptions = { active: true, currentWindow: true };
      const [tab] = await chrome.tabs.query(queryOptions);
      if (tab?.id !== undefined) {
        this.startTracking(tab.id);
      }
    }

    private onIdleState(newState : chrome.idle.IdleState) {
        console.log("Idle detect with ", newState);
        if (newState === "idle" && this.currentTabId !== null) {
            console.log("idle");
            this.stopTracking(this.currentTabId);
        } else if (newState === "active") {
            this.initCurrentTab();
        }
    }

    private onFocusChanged(windowId : number) {
        console.log("Window focus");

        if (windowId === chrome.windows.WINDOW_ID_NONE) {
            console.log("loss");
            if (this.currentTabId !== null) {
                this.stopTracking(this.currentTabId)
            };
        } else {
            console.log(`Changed window focus to ${windowId}`);
            this.initCurrentTab(); // Restart tracking for the new focused window's active tab
        }
    }
  
    private startTracking(tabId: number) {
      this.currentTabId = tabId;
      this.tabs.set(tabId, { tabId, startTime: Date.now(), endTime: null });
    }
  
    private stopTracking(tabId: number) {
      const tabInfo = this.tabs.get(tabId);
      if (tabInfo) {
        tabInfo.endTime = Date.now();
        this.tabs.set(tabId, tabInfo);
        this.callTabChange(tabId);
      }
    }
  
    private callTabChange(tabId: number) {
      // Implement your custom logic here
      // For example: tabChange(tabId);
      console.log("Tab change ", this.tabs.get(tabId))
    }
  
    private onTabActivated(activeInfo: { tabId: number; windowId: number }) {
      if (this.currentTabId !== null) {
        this.stopTracking(this.currentTabId);
      }
      this.startTracking(activeInfo.tabId);
    }
  
    private onTabRemoved(tabId: number, removeInfo: { windowId: number; isWindowClosing: boolean }) {
      this.stopTracking(tabId);
      this.tabs.delete(tabId);
    }

    private async onWindowRemoved(windowId : number) {
        const queryOptions = { active: true, currentWindow: true };

        const [tab] = await chrome.tabs.query(queryOptions);
        if (tab.id !== undefined) {
            this.stopTracking(tab.id)
        }
    }
  }
  
  export default TabTracker;
  