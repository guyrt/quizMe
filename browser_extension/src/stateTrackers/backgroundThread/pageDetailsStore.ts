import { MaybeSinglePageDetails, SinglePageDetails } from '../../interfaces'

type PageDetailsMap = {
  [key: number]: MaybeSinglePageDetails
}

const storageEngine = chrome.storage.local

/// Storage that wraps a local cache and chrome storage of SinglePageDetails.
class PageDetailsStore {
  private pageDetails: PageDetailsMap = {}

  public async getPageDetails(tabId: number): Promise<MaybeSinglePageDetails> {
    if (tabId in this.pageDetails) {
      return Promise.resolve(this.pageDetails[tabId])
    }

    // try to return from storage
    const storageKey = this.makeKey(tabId)
    const storeResults = await storageEngine.get(storageKey)
    const v = storeResults[storageKey]
    if (v != undefined) {
      this.pageDetails[tabId] = v
      return v
    }
    return { error: 'cachemiss' }
  }

  /**
   *
   * @param tabId
   * @param page
   * @param broadcast Only set to true if you are the current active tab.
   */
  public setPageDetails(
    tabId: number,
    page: MaybeSinglePageDetails,
    broadcast: boolean = true,
  ) {
    const storageKey = this.makeKey(tabId)
    storageEngine.set({ [storageKey]: page }, () => {})
    this.pageDetails[tabId] = page
    if (broadcast) {
      console.log(`Sending message activeSinglePageDetailsChange with`, page)
      chrome.runtime.sendMessage({
        action: 'fa_activeSinglePageDetailsChange',
        payload: page,
      })
    }
  }

  public async deletePageDetails(tabId: number) {
    delete this.pageDetails[tabId]
    await storageEngine.remove(this.makeKey(tabId))
  }

  public async deleteAllPageDetails() {
    const kPrefix = this.keyPrefix
    chrome.storage.local.get(null, function (items) {
      const keysToDelete = Object.keys(items).filter(key =>
        key.startsWith(kPrefix),
      )

      if (keysToDelete.length > 0) {
        chrome.storage.local.remove(keysToDelete, function () {})
      }
    })
    this.pageDetails = {}
  }

  private makeKey(tabId: number | string): string {
    return `${this.keyPrefix}.${tabId}`
  }

  private keyPrefix = 'singlepagedetails'
}

export const pageDetailsStore = new PageDetailsStore()
