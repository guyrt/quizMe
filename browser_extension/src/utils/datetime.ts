import { formatDistance } from 'date-fns'


export function strFormatDate(datetime : string) : string {
    const date = new Date(datetime);

    return formatDistance(datetime, new Date(), {addSuffix: true});
}