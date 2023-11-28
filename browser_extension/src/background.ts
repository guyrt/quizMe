chrome.runtime.onMessage.addListener((message, sender) => {
    if (message.action === "fa_pageLoaded") {
        // Perform action on page load
        console.log('hi background');
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            const tId = tabs[0].id ?? 1;
            chrome.tabs.sendMessage(tId, { action: "fa_accessDOM" }, function(response) {
                console.log(response.uri);
                console.log(response.body);
            });
        });
    }
});

