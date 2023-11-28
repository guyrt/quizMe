document.getElementById('save')?.addEventListener('click', function() {
    const setting1Input = document.getElementById('setting1') as HTMLInputElement;
    const setting1 = setting1Input?.value;

    const allSettings = {
        setting1: setting1
    };

    chrome.storage.sync.set(allSettings, () => {
        console.log('Settings saved');
    });
});

document.addEventListener('DOMContentLoaded', () => {
    chrome.storage.sync.get(['setting1'], (items) => {
        const setting1Input = document.getElementById('setting1') as HTMLInputElement;

        if (setting1Input) setting1Input.value = items.setting1 || '';
    });
});
