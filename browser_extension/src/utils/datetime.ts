export function strFormatDate(datetime : string) : string {
    const date = new Date(datetime);

    // Options for formatting
    const options : Intl.DateTimeFormatOptions = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZoneName: 'short'
    };

    // Format the date to the user's locale and timezone
    return date.toLocaleString(undefined, options);
}